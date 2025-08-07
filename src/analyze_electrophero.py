"""

Main functions for electropherogram analysis. \n
Author: Anja Hess \n
Date: 2025-AUG-06 \n

"""

import os
import numpy as np
import pandas as pd
import sys
import statistics
from scipy.signal import find_peaks
from scipy.stats import kruskal, ttest_ind
import scikit_posthocs as sp
script_path = os.path.dirname(os.path.abspath(__file__))
"""Local directory of DNAvi analyze_electrophero module"""
maindir = script_path.split("/src")[0]
"""Local directory of DNAvi (MAIN)"""
sys.path.insert(0, script_path)
sys.path.insert(0, maindir)
sys.path.insert(0, f"{maindir}/src")
sys.path.insert(0, f"{maindir}/src")
from constants import YLABEL, YCOL, XCOL, XLABEL, DISTANCE, CUSTOM_MIN_PEAK_HEIGHT, HALO_FACTOR, PEAK_PROMINANCE
from plotting import lineplot, ladderplot, peakplot, gridplot
from data_checks import check_file
import logging

def wide_to_long(df, id_var="pos", var_name="sample", value_name="value"):
    """

    Function to transfer wide dataframe to long format

    :param df: pandas.DataFrame in wide format
    :param id_var: str,  the column of the wide dataframe containing the id variable
    :param var_name: str, the new column in the long dataframe containing the variable name
    :param value_name: str, the new column in the long dataframe containing the value
    :return: pandas.DataFrame

    """

    df["id"] = df.index
    df_long = pd.melt(df,
                      id_vars=["id", id_var],
                      var_name=var_name,
                      value_name=value_name)
    del df_long["id"]
    return df_long


def integrate(df, ladders_present=""):
    """

    Beta: a function that in the future will allow help handling \
    resulting "gaps" when using multiple ladders within the same signal table.

    NOTE: Not implemented yet.

    :param df: pandas dataframe
    :param ladders_present: list of strings
    :return: a new pandas dataframe that does not have nan values despite multiple ladders
    
    """

    merged_df = []
    #####################################################################
    # 1. Slice dataframe by column, and unify the y-axis label
    #####################################################################
    for i, ladder in enumerate(ladders_present):
        current = df.columns.get_loc(ladder)
        try:
            next = df.columns.get_loc(ladders_present[i + 1])
        except IndexError:
            next = None

        if i == 0:
            sub_df = df.iloc[:,:next]
        else:
            sub_df = df.iloc[:,current:next]
        sub_df.rename(columns={ladder: "ladder"}, inplace=True)
        #################################################################
        # 2. Merge dataframes (on="ladder")
        #################################################################
        if type(merged_df) == list:
            merged_df = sub_df
        else:
            merged_df = pd.merge(merged_df, sub_df, on="ladder", how="outer")

    return merged_df

def peak2basepairs(df, qc_save_dir, y_label=YLABEL, x_label=XLABEL,
                   ladder_dir="", ladder_type="custom"):
    """

    Function to infer ladder peaks from the signal table and annotate those to \
    base pair positions with the user-provided ladder-file.

    :param df: pandas dataframe
    :param qc_save_dir: directory to save qc results
    :param y_label: str, new name for the signal intensity values
    :param x_label: str, new name for the position values
    :param ladder_dir: str, path to where the ladder is located
    :param ladder_type: str, if changed to "custom" the minimum peak \
    height can be adjusted with the constants module.
    :return: a dictionary annotating each peak to a base pair position

    """
    ladder2type = {}
    peak_dict = {}
    return_df = df.copy()

    #####################################################################
    # 1. In the signal matrix: iterate through ladder columns
    #####################################################################
    ladders_present = [e for e in df.columns if "Ladder" in e]
    print(f"--- Ladder columns in data: {len(ladders_present)} ---")
    ladder_df = pd.read_csv(ladder_dir)
    parsed_ladders = ladder_df["Name"].unique()
    print(f"--- Ladder translations found: {len(parsed_ladders)} : "
          f"{parsed_ladders} ---")
    if len(ladders_present) != len(parsed_ladders):
        print(f"--- Error, {len(ladders_present)} Ladders detected in input"
              f", but only {len(parsed_ladders)} defined in ladder file.")
        exit()

    for i, ladder in enumerate([e for e in df.columns if "Ladder" in e]):
        ladder_id = ladder.replace(' ', '').replace(':', '')

        #################################################################
        # 1.1 Get values and find maxima (require at least 50% of max)
        #################################################################
        array = np.array(df[ladder].values.tolist())
        max_peak = array.max()
        min_peak_height = max_peak*0.2

        # Potential to customize ladder peak calling (for developers)
        if "adjust" in ladder_type:
            peaks, _ = find_peaks(array, distance=DISTANCE,
                                  height=CUSTOM_MIN_PEAK_HEIGHT)
        else:
            peaks, _ = find_peaks(array, distance=DISTANCE,
                                  prominence=PEAK_PROMINANCE,
                                  height=min_peak_height)
        peak_list = peaks.tolist()
        print(f"--- Ladder #{i}: {len(peak_list)} peaks detected.")

        ##################################################################
        # 1.2 Render ladder from user-provided file &
        #      Subset the dataframe (multi-ladder case)
        ##################################################################
        print(f"... Selecting {parsed_ladders[i]}")
        sub_df = (ladder_df[ladder_df["Name"] == parsed_ladders[i]]
                     .reset_index(drop=True))

        ############################## RULE: 1st Basepairs, rest "Basepairs_n"
        peak_annos = sub_df["Basepairs"].astype(int).values.tolist()[::-1]

        ##################################################################
        # Find markers and store their bp values in the dict
        ##################################################################
        print("--- Checking for marker bands")
        markers = sub_df[sub_df['Peak'].str.contains(
            'marker')]["Basepairs"].tolist()
        if markers:
            print("--- Found markers: {}".format(markers))

        peak_dict[i] = [peak_annos, markers]

        ladder2type.update({ladder: i})

        #################################################################
        # 1.3 Plot intermed results
        #################################################################
        peakplot(array, peaks, ladder_id, i, i, qc_save_dir,
                 y_label=y_label)

        ##################################################################
        # ---- SANITY CHECK ----- equals nr of detected peaks?
        ##################################################################
        if len(peak_dict[i][0]) != len(peak_list):
            error = (f"Inconsistent number of peaks between ladder file "
                     f"({len(peak_dict[i][0])}) and data input "
                     f"({len(peak_list)})."
                     f"Please check {qc_save_dir} to see what peaks are "
                     f"missing.")
            print(error)
            exit()

        #################################################################
        # 1.4 Integrate bp information into the df
        #################################################################
        peak_col = [0]
        peak_counter = 0
        for n, pos in enumerate(array):
            if n in peak_list:
                peak_col.append(peak_dict[i][0][peak_counter])
                peak_counter += 1
            else:
                peak_col.append(np.nan)

        #################################################################
        # 1.5 Interpolate missing positions between the peaks
        #################################################################
        s = pd.Series(peak_col)
        df[ladder + "_interpol"] = s.interpolate()
        return_df[ladder] = s.interpolate()

        #################################################################
        # 1.6 Plot again with the inferred base pair scale
        #################################################################
        lineplot(df, x=f"{ladder}_interpol", y=ladder,
                 save_dir=qc_save_dir, title=f"{i}_interpolated",
                 y_label=y_label,
                 x_label=x_label)
        # END OF LADDER LOOP

    #####################################################################
    # If 2 or more ladders: integrate the two dataframes to
    # have a single shared ladder column (beta)
    #####################################################################
    #if len(ladders_present) > 1:
     #   print("... Integrating bp positions from multiple ladders")
      #  return_df = integrate(return_df, ladders_present=ladders_present)
    # Todo: Take care of resulting "gaps" when handling multiple ladders

    #####################################################################
    # 2. Save the translation and ladder info
    #####################################################################
    df.to_csv(qc_save_dir + "interpolated.csv")
    return_df.to_csv(qc_save_dir + "bp_translation.csv")
    d = pd.DataFrame.from_dict(ladder2type, orient="index")
    d.to_csv(f"{qc_save_dir}info.csv")

    #####################################################################
    # 3. Plot all ladders together (if multiple)
    #####################################################################
    ladderplot(df, ladder2type, qc_save_dir, y_label=y_label, x_label=x_label)

    return peak_dict
    # END OF FUNCTION


def split_and_long_by_ladder(df):
    """

    This function allows to handle multiple ladder types in one \
    input dataframe while transferring the data into a long format \
    required for plotting. The base pair position for each set of \
    DNA samples is assigned as defined by previous marker interpolation.

    :param df: pandas.DataFrame (wide)
    :return: pandas.DataFrame (long)

    """

    final_df = []

    #####################################################################
    # 1. Split the df by each ladder (reference)
    #####################################################################
    cols = df.columns.tolist()
    indices = [idx for idx, col in enumerate(cols) if "Ladder" in col]

    for i, idx in enumerate(indices):
        # 1.1 Get for each experiment ladder + samples, set as index
        if i == len(indices) - 1:  # last one
            df_sub = df.iloc[:, idx:]
        else:
            df_sub = df.iloc[:, idx:indices[i + 1]]
        ladder_col = [col for col in df_sub.columns
                      if "Ladder" in col][0]
        df_sub.set_index(ladder_col, inplace=True)

        # 1.2 Transfer to long format after setting the Ladder as pos
        df_sub[XCOL] = df_sub.index
        df_sub_long = wide_to_long(df_sub, id_var=XCOL, value_name=YCOL)

        if type(final_df) == list:
            final_df = df_sub_long
        else:
            final_df = pd.concat([df_sub_long, final_df],
                                 sort=False, ignore_index=True)
    return final_df
    # END OF FUNCTION


def parse_meta_to_long(df, metafile, sample_col="sample", source_file="",
                       image_input=False):
    """

    Function to parse the user-provided metadata and transfer to long format

    :param df: pandas.DataFrame (wide)
    :param metafile: str, csv path
    :param sample_col: str, column name
    :param source_file: str, csv path to where the source file shall be located
    :param image_input: bool, whether this dataframe was previously generated from an image file
    :return: the source data file is written to disk (.csv)

    """

    #####################################################################
    # 1. SANITY CHECK - COMPARE SAMPLE NUMBER AND AVAILABLE LANES
    #####################################################################
    meta = pd.read_csv(metafile, header=0)
    try:
        meta["ID"] = meta["SAMPLE"]
    except:
        error = "Metafile misformatted."
        print(error)
        exit()

    samples = df[sample_col].unique().tolist()
    n_samples = len(samples)
    n_meta = len(meta.ID)

    if n_samples != n_meta:
        # Comment: this doesn't have to be a problem as long as the IDs match.
        print(f"--- WARNING: {n_samples} samples but {n_meta} metafile IDs.")

    if image_input:
        print(f"--- WARNING: Image - ONLY first {n_samples} entries "
                    f"used (out of {n_meta})")

    ######################################################################
    # 2. Parse
    ######################################################################
    cols_not_to_add = ["SAMPLE","ID"]
    for col in [e for e in meta.columns if e not in cols_not_to_add]:

        print(f"--- Adding metatadata for", col)
        if image_input:
            # CURRENT RULE FOR IMAGES (NO GROUND TRUTH
            # - TAKE FIRST N ROWS of META !
            conditions = meta[col].values.tolist()[:n_samples]
            dict_meta = dict(zip(samples,conditions))
            print(dict_meta)
        else:
            dict_meta = dict(zip(meta.ID, meta[col]))

        # Finally map
        df[col] = df[sample_col].map(dict_meta)
        ######################################################################
        # SANITY CHECK II -> Was there a successful mapping?
        ######################################################################
        if df[col].isna().all():
            print(f"--- WARNING: No metadata could be matched for {col} - are you sure"
                  f"SAMPLE names match signal table columns?")
    df.to_csv(source_file)
    # END OF FUNCTION


def remove_marker_from_df(df, peak_dict="", on=""):
    """

    Function to remove marker from dataframe including a halo, meaning \
    a defined number of base pairs around the marker band specified in the \
    constants module

    :param df: pandas.DataFrame
    :param peak_dict: dict, previously generated with peak2basepairs
    :param on: str denoting column based on which dataframe will be cut
    :return: pd.DataFrame, cleared from marker-associated data points

    """

    ######################################################################
    # 1. Define the markers (for now based on one ladder only)
    ######################################################################
    first_ladder = list(peak_dict)[0]

    if len(peak_dict[first_ladder][1]) == 1:
        if peak_dict[0][1][0] == peak_dict[0][0][0]: # if == lowest bp val
            print(f"Only lower marker {peak_dict[0][1][0]} bp.")
            lower_marker = peak_dict[0][1][0]
            lower_marker = lower_marker + (lower_marker * (HALO_FACTOR * 3))
            df = df[(df[on] > lower_marker)]
            return df
        else:
            print(f"Only higher marker {peak_dict[0][1][0]} bp."
                  f"(Not plausible but may be okay to crop view)")
            upper_marker = peak_dict[0][1][0]
            upper_marker = upper_marker - (upper_marker * HALO_FACTOR)
            df = df[(df[on] < upper_marker)]
            return df
    else:
        upper_marker = peak_dict[0][1][0]
        lower_marker = peak_dict[0][1][1]

        ###################################################################
        # 2. Calculate the halo to crop left/right from the marker band
        # (relative so this will work with different ladders)
        # Max crop: you cannot crop too much above or beyond marker to not
        # cause the df to be too small/empty
        ###################################################################
        lower_marker = lower_marker + (lower_marker * (HALO_FACTOR*3))
        upper_marker = upper_marker - (upper_marker * HALO_FACTOR)
        print(f"--- Excluding marker peaks from analysis (factor: {HALO_FACTOR})")
        logging.info("_ Excluding marker peaks from analysis")
        df = df[(df[on] > lower_marker) & (df[on] < upper_marker)]
    return df


def normalize(df, peak_dict="", include_marker=False):
    """

    Function to normalize the raw DNA fluorescence intensity \
    to a value between 0 abd 1.

    :param df: pandas.DataFrame
    :param peak_dict: dict, previously generated with peak2basepairs
    :param include_marker: bool, whether to include markers
    :return: pd.DataFrame, now with normalized DNA fluorescence intensity

    """

    ######################################################################
    # 1. Define ladder and remove markers
    ######################################################################
    ladder_field = [e for e in df.columns if "adder" in e][0]
    if not include_marker:
        df = remove_marker_from_df(df, peak_dict=peak_dict, on=ladder_field)

    ######################################################################
    # 2. Normalize to a value between 0-1 Remove the marker
    ######################################################################
    result = df.copy()
    for feature_name in df.columns:
        if "Ladder" in feature_name:
            continue
        max_value = df[feature_name].max()
        min_value = df[feature_name].min()
        result[feature_name] = ((df[feature_name] - min_value) /
                                (max_value - min_value))

    return result
    # END OF FUNCTION


def mean_from_histogram(df, unit="", size_unit=""):
    """

    Function to estimate the mean size of a patient/samples' DNA
    fragments (in base pairs) based on the fluorescence signal table.
    Strategy is to create a histogram and next infer the metrics.

    :param df: pandas.DataFrame
    :param unit: str, usually normalized fluorescence unit
    :param size_unit: str, fragment size unit (base pairs)
    :return: float, average fragment size

    """


    # Estimate the mean bp from the histogram (frequency rescaled 0-100)
    df["counts"] = df[unit] * 100
    df["product"] = df[size_unit] * df["counts"]
    mean_bp = df["product"].sum() / df["counts"].sum()

    return mean_bp
    # END OF FUNCTION

def run_kruskal(df, variable="", category=""):
    """

    Function to perform scipy.stats' the non-parametric \
    Kruskal Wallis Test to infer statistical significance for the difference \
    in mean base pair fragment size for patients/samples from different groups

    :param df: pandas.DataFrame
    :param variable: continuous variable
    :param category: categorical variable
    :return: statistics per group in a dataframe

    """

    test_performed = "Kruskal Wallis"
    kruskal_data = []

    #####################################################################
    # 1. Collect numerical values for each identified peak (or av/max)
    # for each group of the cond. variable
    #####################################################################
    for peak in df["peak_id"].unique():
        sub_df = df[df["peak_id"] == peak]
        kruskal_groups = []
        kruskal_dict = {}
        names = []
        p_value = signi = results = None
        unique_peak = False
        average_dict = {}
        mode_dict = {}
        median_dict = {}
        for group in sub_df[category].unique():
            group_data = sub_df[sub_df[category] == group][variable]
            group_data = list(group_data)
            if not group_data:
                print(f"No data found for Kruskal group {group}.")
                continue
            kruskal_groups.append(group_data)
            kruskal_dict.update({str(group): group_data})
            average_dict.update({str(group): float(statistics.mode(group_data))})
            mode_dict.update({str(group): float(statistics.mode(group_data))})
            median_dict.update({str(group): float(statistics.median(group_data))})
            names.append(str(group))

        ##################################################################
        # 2. Run Kruskal Wallis Test or ttest dep on sample size
        ##################################################################
        if len(kruskal_groups) == 2:
            test_performed = "Student's t - test (independent)"
            stats, p_value = ttest_ind(kruskal_groups[0], kruskal_groups[1])
            if p_value < 0.05:
                signi = True
            else:
                signi = False
        else:
            try:
                stats, p_value = kruskal(*kruskal_groups)
            except ValueError:
                print("Skipping Kruskal stats since "
                      f"peak {peak} only shows in one group of groups ({names})"
                      f"with values:", kruskal_groups)
                stats = p_value = 1
                unique_peak = True
                test_performed = "None (peak unique to group)"

            # 2. If the Kruskal says groups are different do a posthoc
            if p_value < 0.05:
                signi = True
                p_adjust_test = 'bonferroni'
                if len(kruskal_groups) < 3:
                    results = sp.posthoc_conover([kruskal_groups[0],
                                                  kruskal_groups[1]],
                                                 p_adjust=p_adjust_test)
                else:
                    kruskal_groups_for_posthoc = np.array(kruskal_groups)
                    results = sp.posthoc_conover(kruskal_groups_for_posthoc,
                                                 p_adjust=p_adjust_test)
                results.columns = names
                results["condition"] = names
                results.set_index("condition", inplace=True)
                test_performed = f"Kruskal Wallis with {p_adjust_test}"
            else:
                signi = False

        # Add to data storage
        kruskal_data.append([peak, unique_peak, average_dict,mode_dict, median_dict,
                             test_performed,p_value, signi, results, kruskal_dict])

    #####################################################################
    # 2. Generate df from storage
    #####################################################################
    kruskal_df = pd.DataFrame(kruskal_data,
                              columns=["peak_name", "unique_peak",
                                       "average", "modal", "median",
                                       "test_performed", "p_value",
                                       "p<0.05", "posthoc_p_values",
                                       "groups"])
    return kruskal_df

def epg_stats(df, save_dir="", unit="normalized_fluorescent_units", size_unit="bp_pos"):
    """

    Compute and output basic statistics for DNA size distributions

    :param df: pandas.DataFrame
    :param save_dir: string, where to save the statistics to
    :param unit: string (y-variable)
    :param size_unit: string (x-variable)
    :return: will save three dataframes as .csv files in stats \
    directory: basic_statistics.csv, peak_statistics.csv, \
    group_statistics_by_CATEGORICAL-VAR.csv)

    """
    #####################################################################
    # 1. Basic stats
    #####################################################################
    df["sample"].astype(object) # Make sure all sample names are type obj
    basic_stats = df.describe()
    basic_stats.to_csv(f"{save_dir}basic_statistics.csv")

    #####################################################################
    # 2. Average bp size, peak positions, and peak size per sample
    #####################################################################
    peak_info = []
    for sample in df["sample"].unique():
        # 2.1 Select data for only this sample
        sub_df = df[df["sample"] == sample]
        # 2.2 Get mean bp for the sample
        mean_bp = mean_from_histogram(sub_df, unit=unit, size_unit=size_unit)
        peak_info.append([sample, "average_size", np.nan, mean_bp])

        # 2.3 Add to array and find peaks
        array = np.array(sub_df[unit].values.tolist())
        max_peak = array.max()
        min_peak_height = max_peak * 0.2 # Define min peak height
        peaks, _ = find_peaks(array, distance=DISTANCE,  # n pos apart
                              height=min_peak_height)  # minimum height
        # Get the fluorescence val for each peak
        peak_list = [array[e] for e in peaks.tolist()]
        if not peak_list:
            print(f"No peaks found for sample {sample}.")
            print("Ignoring this sample.")
            continue
        max_peak = max(peak_list)

        # 2.4 Assign the basepair position for each peak
        for i, peak in enumerate(peak_list):
            bp = sub_df.loc[sub_df[unit] == peak, size_unit].iloc[0]
            peak_info.append([sample, i, peak, bp])
            if peak == max_peak:
                peak_info.append([sample, "max_peak", peak, bp])

    peak_df = pd.DataFrame(peak_info, columns=["sample", "peak_id",
                                               "peak_fluorescence", "bp"])

    ######################################################################
    # 3. Optional: Grouped stats (Mean sizes)
    ######################################################################
    cols_not_to_plot = [size_unit, "sample", unit]
    mean_info = []

    for categorical_variable in [c for c in df.columns if c not in
                                                          cols_not_to_plot]:
        print(f"--- Stats by {categorical_variable}")
        # Extract sample-to-condition info
        sample2cat = df.set_index("sample").to_dict()[categorical_variable]
        unannotated = {k:v for k,v in sample2cat.items() if v is np.nan}
        if unannotated:
            print("")
            print(f"--- Warning. Sample without value in {categorical_variable}.\n"
                  f"{unannotated}\n"
                  f"Please add a category in metadata file and try again.")
            exit()
        peak_df[categorical_variable] = peak_df["sample"].map(sample2cat)
        peak_df.to_csv(f"{save_dir}peak_statistics.csv")
        kruskal_df = run_kruskal(peak_df, variable="bp", category=categorical_variable)
        kruskal_df.to_csv(f"{save_dir}group_statistics_by_{categorical_variable}.csv")
        # END LOOP

    peak_df.to_csv(f"{save_dir}peak_statistics.csv")
    # END OF FUNCTION


def epg_analysis(path_to_file, path_to_ladder, path_to_meta, run_id=None,
                 include_marker=False, image_input=False, save_dir=False):
    """
    Core function to analyze DNA distribution from a signal table.

    :param path_to_file: str, path where the signal table is stored
    :param path_to_ladder: str, path to where the ladder file is stored
    :param path_to_meta: str, path to metadata file
    :param run_id: str, name for the analysis, based on user input or name of \
    the signal table file
    :param include_marker: bool, whether to include the marker in the analysis
    :param image_input: bool, whether to the signal table was generated based on an image
    :param save_dir: bool or str, where to save the statistics to. Default: False
    :return: run analysis and plotting functions, create multiple outputs in the result folder

    """
    print("")
    print("------------------------------------------------------------")
    print("""           DNA FRAGMENT SIZE ANALYSIS           """)
    print("------------------------------------------------------------")
    print(f"""     
        Image input: {image_input}
        DNA file: {path_to_file}      
        Ladder file: {path_to_ladder}
        Meta file: {path_to_meta}
        Include marker: {include_marker}""")
    print("")

    logging.info(f"DNA file: {path_to_file}, Ladder file: {path_to_ladder},"
                 f"Meta file: {path_to_meta}")

    #####################################################################
    # 1. Create results dir and define inputs
    #####################################################################
    if not run_id:
        run_id = path_to_file.rsplit("/", 1)[1].rsplit(".", 1)[0]
    if not save_dir:
        save_dir = path_to_file.rsplit("/", 1)[0] + f"/{run_id}/"
    plot_dir = f"{save_dir}/plots/"
    qc_dir = f"{save_dir}/qc/"
    stats_dir =  f"{save_dir}/stats/"
    basepair_translation_file = f"{qc_dir}bp_translation.csv"
    source_file = f"{plot_dir}sourcedata.csv"
    logging.info(f"Saving results to: {save_dir}")
    print("         run_id:", run_id)
    print("         results to:", save_dir)
    print("------------------------------------------------------------")
    print("        Loading signal table")
    print("------------------------------------------------------------")
    #####################################################################
    # 2. Load the data & infer base pair (bp) positions from peaks
    #####################################################################
    df = check_file(path_to_file)

    # Only then make the effort to create folders
    for directory in [save_dir, plot_dir, qc_dir, stats_dir]:
        os.makedirs(directory, exist_ok=True)

    print("------------------------------------------------------------")
    print("        Calculating basepair positions based on ladder")
    print("------------------------------------------------------------")
    peak_dict = peak2basepairs(df, qc_dir, ladder_dir=path_to_ladder)
    df = pd.read_csv(basepair_translation_file, header=0, index_col=0)

    #####################################################################
    # 4. Height-normalize the data (default)
    #####################################################################

    print("------------------------------------------------------------")
    print("        Height-normalizing data and removing markers        ")
    print("------------------------------------------------------------")
    normalized_df = normalize(df, peak_dict=peak_dict, include_marker=
                              include_marker)
    # All downstream ana on height-norm data WITHOUT marker (unless
    # --include argument was set)
    df = normalized_df
    #####################################################################
    # 5. Add the metadata
    #####################################################################
    df = split_and_long_by_ladder(df)
    print(df)
    if path_to_meta:

        print("------------------------------------------------------------")
        print("        Parsing metadata ")
        print("------------------------------------------------------------")
        parse_meta_to_long(df, path_to_meta, source_file=source_file,
                                   image_input=image_input)
    else:
        print(f"--- No meta file, using column names.")
        df.to_csv(source_file)

    df = pd.read_csv(source_file, header=0, index_col=0)
    ######################################################################
    # 6. Add statistics
    ######################################################################
    print("------------------------------------------------------------")
    print("        Performing statistical analysis")
    print("------------------------------------------------------------")
    epg_stats(df, save_dir=stats_dir) #, peak_dict=peak_dict)

    #####################################################################
    # 5. Plot raw data (samples seperated)
    #####################################################################
    print("------------------------------------------------------------")
    print("        Plotting results")
    print("------------------------------------------------------------")
    gridplot(df, x=XCOL, y=YCOL, save_dir=plot_dir, title=f"all_samples",
             y_label=YLABEL, x_label=XLABEL)
    # END OF FUNCTION
# END OF SCRIPT