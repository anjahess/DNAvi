"""

Main functions for electropherogram analysis.
@author: Anja Hess
@date: 2023-JUL-01

"""

import os
import numpy as np
import pandas as pd
import sys
from scipy.signal import find_peaks
script_path = str(os.path.dirname(os.path.abspath(__file__)))
maindir = script_path.split("/src")[0]
sys.path.insert(0, script_path)
sys.path.insert(0, maindir)
sys.path.insert(0, f"{maindir}/src")
sys.path.insert(0, f"{maindir}/src")
from constants import YLABEL, YCOL, XCOL, XLABEL, DISTANCE, CUSTOM_MIN_PEAK_HEIGHT, HALO_FACTOR
from plotting import lineplot, ladderplot, peakplot, gridplot
from data_checks import check_file, check_ladder
import logging

def wide_to_long(df, id_var="pos", var_name="sample", value_name="value"):
    """
    Transfer pandas df to long format.

    :param df:
    :return:

    """

    df["id"] = df.index
    df_long = pd.melt(df,
                      id_vars=["id", id_var],
                      var_name=var_name,
                      value_name=value_name)
    del df_long["id"]
    return df_long


def peak2basepairs(df, qc_save_dir, y_label=YLABEL, x_label=XLABEL,
                   ladder_dir="", ladder_type="custom"):
    """
    Function to infer ladder peaks from the signal table and
    annotate those to base pair positions with the user-definded
    ladder-file.

    :param df: pandas dataframe
    :param qc_save_dir: directory to save qc results
    :param y_label: str
    :param x_label: str
    :param ladder_dir: str
    :param ladder_type: str
    :return:
    """
    ladder2type = {}
    return_df = df.copy()

    #####################################################################
    # 1. In the signal matrix: iterate through ladder columns
    #####################################################################
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
                                  height=min_peak_height)
        peak_list = peaks.tolist()
        print(f"{len(peak_list)} peaks detected.")

        ##################################################################
        # 1.2 Render ladder from user-provided file
        ##################################################################
        check_ladder(ladder_dir)
        ladder_df = pd.read_csv(ladder_dir)
        peak_annos = ladder_df["Basepairs"].astype(int).values.tolist()[::-1]

        ##################################################################
        # Find markers and store their bp values
        ##################################################################
        print("--- Checking for marker bands")
        markers = ladder_df[ladder_df['Peak'].str.contains(
            'marker')]["Basepairs"].tolist()
        if markers:
            print("--- Found markers: {}".format(markers), " (upper, lower)")

        peak_dict = {i: [peak_annos, markers]}
        ##################################################################
        # ---- SANITY CHECK ----- equals nr of detected peaks?
        ##################################################################
        if len(peak_dict[i][0]) != len(peak_list):
            error = ("Inconstistent number of peaks between ladder file "
                     "and data input")
            print(error)
            exit()
        ladder2type.update({ladder: i})

        #################################################################
        # 1.3 Plot intermed results
        #################################################################
        peakplot(array, peaks, ladder_id, i, i, qc_save_dir,
                 y_label=y_label)

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
    # 2. Save the translation and ladder info
    #####################################################################
    df.to_csv(qc_save_dir + "interpolated.csv")
    return_df.to_csv(qc_save_dir + "bp_translation.csv")
    d = pd.DataFrame.from_dict(ladder2type, orient="index")
    d.to_csv(f"{qc_save_dir}info.csv")

    #####################################################################
    # 3. Plot all ladders together (if multiple)
    #####################################################################
    ladderplot(df, ladder2type, qc_save_dir, y_label=y_label,
               x_label=x_label)

    return peak_dict, None
    # END OF FUNCTION


def split_and_long_by_ladder(df, path_to_file):
    """
    We transfer to long format giving each experiment the base pair
    position assigned by previous marker interpolation.

    :param df: pandas df
    :param path_to_file: str
    :return: pandas df (long)
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
    Parse metadata and transfer to long

    :param df:
    :param metafile:
    :return:
    """

    ################################################################################
    # 1. SANITY CHECK - COMPARE SAMPLE NUMBER AND AVAILABLE LANES
    ################################################################################
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
    ################################################################################
    # 2. Parse
    ################################################################################
    cols_not_to_add = ["SAMPLE","ID"]
    for col in [e for e in meta.columns if e not in cols_not_to_add]:

        print(f"--- Adding metatadata for", col)
        if image_input:
            # CURRENT RULE FOR IMAGES (NO GROUND TRUTH - TAKE FIRST N ROWS of META !
            conditions = meta[col].values.tolist()[:n_samples]
            dict_meta = dict(zip(samples,conditions))
            print(dict_meta)
        else:
            dict_meta = dict(zip(meta.ID, meta[col]))

        # Finally map
        df[col] = df[sample_col].map(dict_meta)
        ############################################################################
        # SANITY CHECK II -> Was there a successful mapping?
        ############################################################################
        if df[col].isna().all():
            print(f"--- WARNING: No metadata could be matched for {col} - are you sure"
                  f"SAMPLE names match signal table columns?")
    df.to_csv(source_file)
    # END OF FUNCTION


def remove_marker_from_df(df, peak_dict="", on=""):
    """
    Function to remove marker from dataframe incl halo

    :param df:
    :param peak_dict:
    :param on: str denoting column based on which dataframe will be cut
    :return: pd.DataFrame

    """

    ################################################################################
    # 1. Define the markers
    ################################################################################
    upper_marker = peak_dict[0][1][0]
    lower_marker = peak_dict[0][1][1]

    ################################################################################
    # 2. Calculate the halo to crop left/right from the marker band
    # (relative so this will work with different ladders)
    # Max crop: you cannot crop too much above or beyond marker to not
    # cause the df to be too small/empty
    ################################################################################
    # low bp higher multiplicator
    lower_marker = lower_marker + (lower_marker * (HALO_FACTOR*3))
    upper_marker = upper_marker - (upper_marker * HALO_FACTOR)
    print(f"--- Excluding marker peaks from analysis (factor: {HALO_FACTOR})")
    logging.info("_ Excluding marker peaks from analysis")
    df = df[(df[on] > lower_marker) & (df[on] < upper_marker)]
    return df


def normalize(df, peak_dict="", include_marker=False):
    """
    Function to normalize the RFU to a value between 0,1
    https://stackoverflow.com/questions/26414913/normalize-columns-of-a-dataframe
    :param df:
    :param ladder:
    :param peak_dict:
    :return:
    """
    ladder_field = [e for e in df.columns if "adder" in e][0]

    if not include_marker:
        df = remove_marker_from_df(df, peak_dict=peak_dict, on=ladder_field)

    ################################################################################
    # 2. Normalize to a value between 0-1 Remove the marker
    ################################################################################
    result = df.copy()
    for feature_name in df.columns:
        if "Ladder" in feature_name:
            continue
        max_value = df[feature_name].max()
        min_value = df[feature_name].min()
        result[feature_name] = (df[feature_name] - min_value) / (max_value - min_value)
    return result
    # END OF FUNCTION

def epg_stats(df, save_dir="", unit="normalized_fluorescent_units", size_unit="bp_pos",
              peak_dict=None):
    """
    To compute basic statistics for DNA size distritbutions
    :param df:
    :param save_dir:
    :param unit:
    :param size_unit:
    :param peak_dict:
    :return:
    """
    #####################################################################
    # 1. Basic stats
    #####################################################################
    # Make sure all sample names are type obj
    df["sample"].astype(object)
    basic_stats = df.describe() #include='object'
    basic_stats.to_csv(f"{save_dir}basic_statistics.csv")

    #####################################################################
    # 2. Peak positions per sample
    #####################################################################
    peak_info = []

    for sample in df["sample"].unique():
        # Select the fluorescence values from this sample
        sub_df = df[df["sample"] == sample]
        # Add to array
        array = np.array(sub_df[unit].values.tolist())
        max_peak = array.max()

        # Define min peak height
        min_peak_height = max_peak * 0.2
        peaks, _ = find_peaks(array, distance=DISTANCE,  # n pos apart
                                  height=min_peak_height)  # minimum height

        # Get the fluorescence val for each peak
        peak_list = [array[e] for e in peaks.tolist()]

        # Assign the basepair position
        for i, peak in enumerate(peak_list):
            bp = df.loc[df[unit] == peak, size_unit].iloc[0]
            peak_info.append([sample, i, peak, bp])

    peak_df = pd.DataFrame(peak_info, columns=["sample", "peak_id",
                                               "peak_fluorescence", "bp"])
    peak_df.to_csv(f"{save_dir}peak_statistics.csv")

    ######################################################################
    # 3. Optional: Grouped stats (Mean sizes per group)
    ######################################################################
    cols_not_to_plot = [size_unit, "sample", unit]
    mean_info = []

    for col in [c for c in df.columns if c not in cols_not_to_plot]:
        print(f"--- Stats by {col}")
        logging.info(f"--- Stats by {col}")
        df["sample"].value_counts()
        for cond in df[col].unique():
            # Estimate the mean bp from the histogram
            sub_df = df[df[col] == cond]
            # size = val   # frequency recaled 0-100
            sub_df["counts"] = sub_df[unit]*100
            sub_df["product"] =  sub_df[size_unit]*sub_df["counts"]
            mean_bp = sub_df["product"].sum() / sub_df["counts"].sum()
            mean_info.append([col, cond, mean_bp])

    mean_df = pd.DataFrame(mean_info, columns=["variable", "condition",
                                               "mean_size_bp"])
    mean_df.to_csv(f"{save_dir}group_statistics.csv")
    # END OF FUNCTION


def epg_analysis(path_to_file, path_to_ladder, path_to_meta, run_id=None,
                 include_marker=False, image_input=False, save_dir=False):
    """
    Function to analyze DNA distribution from a signal table.
    :param path_to_file: str
    :param path_to_ladder: str
    :param path_to_meta: str
    :param run_id: str
    :param include_marker: bool
    :return:
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
    for directory in [save_dir, plot_dir, qc_dir]:
        os.makedirs(directory, exist_ok=True)

    print("------------------------------------------------------------")
    print("        Calculating basepair positions based on ladder")
    print("------------------------------------------------------------")
    peak_dict, error = peak2basepairs(df, qc_dir,ladder_dir=path_to_ladder)
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
    # --include argument was set
    df = normalized_df

    #####################################################################
    # 5. Add the metadata
    #####################################################################
    df = split_and_long_by_ladder(df, path_to_file)
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
    epg_stats(df, save_dir=plot_dir, peak_dict=peak_dict)

    #####################################################################
    # 5. Plot raw data (samples seperated)
    #####################################################################
    print("------------------------------------------------------------")
    print("        Plotting results")
    print("------------------------------------------------------------")
    gridplot(df, x=XCOL, y=YCOL, save_dir=plot_dir, title=f"all_samples",
             y_label=YLABEL, x_label=XLABEL)
    return error
    # END OF FUNCTION
# END OF SCRIPT
