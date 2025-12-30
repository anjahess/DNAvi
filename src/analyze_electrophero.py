"""

Main functions for electropherogram analysis. \n
Author: Anja Hess \n
Date: 2025-AUG-06 \n

"""
import os
import sys
import time
import shutil
import statistics
import datetime
import logging
import numpy as np
import scikit_posthocs as sp
from scipy.signal import find_peaks
script_path = os.path.dirname(os.path.abspath(__file__))
"""Local directory of DNAvi analyze_electrophero module"""
maindir = script_path.split("/src")[0]
"""Local directory of DNAvi (MAIN)"""
sys.path.insert(0, script_path)
sys.path.insert(0, maindir)
sys.path.insert(0, f"{maindir}/src")
sys.path.insert(0, f"{maindir}/src")
from constants import (YLABEL, YCOL, XCOL, XLABEL, DISTANCE, MIN_PEAK_HEIGHT_FACTOR, MAX_PEAK_WIDTH_FACTOR,
                       PEAK_PROMINENCE, NUC_DICT, BACKGROUND_SUBSTRACTION_STATS, ARTIFICIAL_MAX,
                       INTERPOLATE_FUNCTION, LOGFILE_NAME, HALO_FACTOR, XLABEL_PRIOR_SIZE)
from plotting import lineplot, ladderplot, peakplot, gridplot, stats_plot
from data_checks import check_file
from utils import *


def peak2basepairs(df, qc_save_dir, y_label=YLABEL, x_label=XLABEL,
                   ladder_dir="", ladder_type="custom", marker_lane=0):
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

    #####################################################################
    # 0. Check for ladders
    #####################################################################
    ladders_present = [e for e in df.columns if "Ladder" in e]
    print(f"--- Ladder columns in data: {len(ladders_present)} ---")
    if not ladders_present:
        #################################################################
        # If it's a simple upper lower error let's forgive it
        #################################################################
        if [e for e in df.columns if "ladder" in e]:
            df.rename(columns={"ladder": "Ladder"}, inplace=True)
        else:
            ##################################################################
            # In case of missing ladder, rename the first or specified col
            ##################################################################
            col_to_rename = df.columns[marker_lane]
            print(f"--- WARNING: No 'Ladder' present in the signal table - "
                  f"defaulting to {marker_lane-1}th ({col_to_rename}) as DNA marker.")
            df.rename(columns={col_to_rename: "Ladder"}, inplace=True)
        ladders_present = ["Ladder"]
    ladder_df = pd.read_csv(ladder_dir)
    parsed_ladders = ladder_df["Name"].unique()
    print(f"--- Ladder translations found: {len(parsed_ladders)} : "
          f"{parsed_ladders} ---")
    return_df = df.copy()
    #####################################################################
    # 1. In the signal matrix: iterate through ladder columns
    #####################################################################
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
        min_peak_height = max_peak*MIN_PEAK_HEIGHT_FACTOR
        max_width = len(df)
        max_peak_width = max_width*MAX_PEAK_WIDTH_FACTOR
        peaks, _ = find_peaks(array, distance=DISTANCE,
                              prominence=PEAK_PROMINENCE,
                              height=min_peak_height,
                              width=(None,max_peak_width)
                              )
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
        ##################################################################
        # ---- SANITY CHECK ----- equals nr of detected peaks?
        ##################################################################
        if len(peak_dict[i][0]) != len(peak_list):
            error = (f"Inconsistent number of peaks between "
                     f"ladder file ({len(peak_dict[i][0])} bands) "
                     f"and the actual data in gel image/table ladder "
                     f"({len(peak_list)} bands). "
                     f"Please check {qc_save_dir} to see what peaks are "
                     f"missing or whether your ladder is in the "
                     f"wrong position or if this is NOT a gel image.")
            print(error)
            exit()

        #################################################################
        # 1.3 Plot intermed results
        #################################################################
        peakplot(array, peaks, parsed_ladders[i], i, i, qc_save_dir,
                 y_label=y_label, x_label=f"{XLABEL_PRIOR_SIZE} (before annotation)",
                 size_values=peak_annos)

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
                # Add an artificial last position
                if n == len(array)-1:
                    peak_col.append(ARTIFICIAL_MAX)
                else:
                    peak_col.append(np.nan)

        #################################################################
        # 1.5 Interpolate missing positions between the peaks
        #################################################################
        s = pd.Series(peak_col)
        # inside: don't add values beyond the max marker lane (since we dont have a size ref there)
        interpolated = s.interpolate(method=INTERPOLATE_FUNCTION,
                                     limit_area="inside")
        df[ladder + "_interpol"] = interpolated
        return_df[ladder] = interpolated

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
    except Exception as exception:
        logging.exception(exception)
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


def remove_marker_from_df(df, peak_dict="", on="", correct_for_variant_samples=False):
    """

    Function to remove marker from dataframe including a halo, meaning \
    a defined number of base pairs around the marker band specified in the \
    constants module

    :param df: pandas.DataFrame
    :param peak_dict: dict, previously generated with peak2basepairs
    :param on: str denoting column based on which dataframe will be cut
    :param correct_for_variant_samples: bool - if this option is chosen, each sample will
    be checked individually for end of the marker peaks and cropped based on this information.
    Defaults to False, meaning that the marker halo is estimated from the first sample.
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
            ###############################################################
            # 0. Define first valley
            ###############################################################
            valley_lists = []
            for sample in [e for e in df.columns if e != on]:
                array = df[sample] * -1
                max_peak = array.min()
                min_peak_height = max_peak * MIN_PEAK_HEIGHT_FACTOR  # Define min peak height
                mins, _ = find_peaks(df[sample] * -1, distance=DISTANCE,
                                     height=min_peak_height)
                valley_list = [df[on][e] for e in mins.tolist() if df[on][e] > lower_marker]
                valley_lists.append(valley_list)
                first_relevant_valley = valley_list[0]
                if correct_for_variant_samples:  # crop for each sample individually
                    df[sample][df[on] < first_relevant_valley] = np.nan
                else:
                    break
            for val in valley_list:
                if val > lower_marker:
                    break
            lower_marker = val
            df = df[(df[on] > lower_marker)]
            return df
        else:
            print(f"Only higher marker {peak_dict[0][1][0]} bp."
                  f"(Not plausible but may be okay to crop view)")
            upper_marker = peak_dict[0][1][0]
            df = df[(df[on] < upper_marker)]
            return df
    else:
        upper_marker = peak_dict[0][1][0]
        lower_marker = peak_dict[0][1][1]
        ######################################################################
        # 0. Define first and last valley (dynamically remove markers)
        ######################################################################
        first_valleys = []
        last_valleys = []
        for sample in [e for e in df.columns if e != on]:
            array=df[sample] * -1
            max_peak = array.min()
            min_peak_height = max_peak * MIN_PEAK_HEIGHT_FACTOR  # Define min peak height
            mins, _ = find_peaks(df[sample] * -1, distance=DISTANCE,
                                 height=min_peak_height)
            valley_list = [df[on][e] for e in mins.tolist()
                           if lower_marker < df[on][e] < upper_marker]
            first_valleys.append(valley_list[0])
            last_valleys.append(valley_list[-1])
            if correct_for_variant_samples:
                df[sample][df[on] < valley_list[0]] = np.nan
                df[sample][df[on] > valley_list[-1]] = np.nan
            else:
                break
        ###################################################################
        # 2. Remove
        ###################################################################
        lower_marker = max(first_valleys)
        upper_marker = min(last_valleys)
        print("--- Auto-detected marker cropping borders:", lower_marker,
              "and" , upper_marker)
        logging.info(f"--- Auto-detected marker cropping borders: {lower_marker} and {upper_marker}")
        ###################################################################
        # (HALO: prev mode - left for recap purpose)
        ###################################################################
        if HALO_FACTOR != 0:
            # Prev more
            lower_marker = lower_marker + (lower_marker * (HALO_FACTOR*2))
            upper_marker = upper_marker - (upper_marker * (HALO_FACTOR))
            logging.info(f"_ HALO FACTOR ADDED {HALO_FACTOR}"
                         f"- Excluding marker peaks from {lower_marker}"
                         f"- to {upper_marker}.")
        if not correct_for_variant_samples:
            df = df[(df[on] > lower_marker) &(df[on] < upper_marker)]
        if correct_for_variant_samples:
            df.dropna(inplace=True)
    return df
    # END OF FUNCTION

def nuc_fractions(df, unit="", size_unit="", nuc_dict=NUC_DICT):
    """

    Estimate nucleosomal fractions (percentages) of \
    a sample's cfDNA based on pre-defined base pair ranges.

    :param df: pandas.DataFrame
    :param unit: str, usually normalized fluorescence unit
    :param size_unit: str, fragment size unit (base pairs)
    :return: pd.Dataframe of nucleosomal fractions

    """

    fraction_df = []

    ######################################################################
    # 0. Perform background substraction
    ######################################################################
    df = df[df[unit] > (df[unit].max()*BACKGROUND_SUBSTRACTION_STATS)]

    ######################################################################
    # 1.  Sum of all intensities
    ######################################################################
    sum_all = df[unit].sum()

    ######################################################################
    # 2. Define the fraction inside each basepair range (~nucleosomal
    # fraction)
    ######################################################################
    for range in nuc_dict:
        start = nuc_dict[range][0]
        end = nuc_dict[range][1]
        if not end:
            sub_df = df[df[size_unit] >= start]
        if not start:
            sub_df = df[df[size_unit] < end]
        # Crop df to nuc range
        if start and end:
            sub_df = df[(df[size_unit] > start) & (df[size_unit] <= end)]

        # Calculate area under each nucleosomal mode
        auc = np.trapezoid(y=sub_df[unit], x=sub_df[size_unit])

        # Calculate fraction of signal
        fraction_signal_range = sub_df[unit].sum() / sum_all
        fraction_df.append([range, start, end, auc, fraction_signal_range,
                            round(fraction_signal_range * 100,1)])

    fraction_df = pd.DataFrame(fraction_df, columns=["name", "start", "end",
                                                     "auc", "fraction_dna",
                                                     "percent"]).set_index("name")
    return fraction_df
    # END OF FUNCTION


def run_stats(df, variable="", category="", paired=False, alpha=0.05,
              region_id="region_id"):
    """

    Function to perform statistical tests (parametric or
    non-parametric) infer significance for the difference \
    in mean base pair fragment size for patients/samples from different groups

    :param df: pandas.DataFrame
    :param variable: continuous variable
    :param category: categorical variable
    :param paired: boolean
    :return: statistics per group in a dataframe

    """

    stats_data = []
    n_groups = len(df[category].unique())

    ######################################################################
    # 1. Collect values for each identified peak (or av/max)
    ######################################################################
    for peak in df[region_id].unique():
        sub_df = df[df[region_id] == peak]
        stats_groups = []
        stats_dict = {}
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
                print(f"No data found for group {group}.")
                continue
            stats_groups.append(group_data)
            stats_dict.update({str(group): group_data})
            average_dict.update({str(group): float(statistics.mean(group_data))})
            mode_dict.update({str(group): float(statistics.mode(group_data))})
            median_dict.update({str(group): float(statistics.median(group_data))})
            names.append(str(group))

        ######################################################################
        # Check in enough groups
        ######################################################################
        if len(stats_groups) == 1:
            print("Skipping Statistics since "
                  f"peak {peak} only shows in one group of groups ({names})"
                  f"with values:", stats_groups)
            s = p_value = 1
            unique_peak = True
            test_performed = "None (peak unique to group)"
            stats_data.append([peak, test_performed, p_value, signi, results,
                               unique_peak, average_dict, mode_dict,
                               median_dict, stats_dict])
            continue


        ######################################################################
        # 2. Test normality
        ######################################################################
        assume_normal = normality(stats_groups)
        logging.info(f"--- Normality distribution assumed: {assume_normal}")
        assume_equal_var = vartest(stats_groups)
        logging.info(f"--- Equal variances assumed: {assume_equal_var}")
        ######################################################################
        # 3. Quick pre-test if you have qual sample sizes (paired)
        ######################################################################
        if paired:
            group_sizes = [len(e) for e in stats_groups]
            all_same = group_sizes.count(group_sizes[0]) == len(group_sizes)
            if not all_same:
                print(f"--- Chose paired, but unequal sample sizes: {group_sizes}. "
                      f"Please assure equal sample sizes in each group and try again.")
                logging.warning(f"--- Chose paired, but unequal sample sizes: {group_sizes}. "
                      f"Please assure equal sample sizes in each group and try again.")
                continue

        if len(names) == 2 and n_groups == 2: # only if that's the max
            ###################################################################
            # 2.1 Less than 3 groups
            ###################################################################
            if assume_normal and not paired:
                test_performed = "Student's t - test (independent) "
                if assume_equal_var:
                    s, p_value = stats.ttest_ind(stats_groups[0], stats_groups[1],
                                                 equal_var=True)
                    test_performed += "assume equal variance)"
                else:
                    s, p_value = stats.ttest_ind(stats_groups[0], stats_groups[1],
                                                 equal_var=False)
                    test_performed += "unequal variance)"
                if p_value < alpha:
                    signi = True
                else:
                    signi = False

            if assume_normal and paired:
                test_performed = "Student's t - test (paired)"
                s, p_value = stats.ttest_rel(stats_groups[0], stats_groups[1])
                if p_value < alpha:
                    signi = True
                else:
                    signi = False

            if not assume_normal and not paired:
                test_performed = "Mann Whitney U - test (independent)"
                s, p_value = stats.mannwhitneyu(stats_groups[0], stats_groups[1])
                if p_value < alpha:
                    signi = True
                else:
                    signi = False

            if not assume_normal and paired:
                test_performed = "Wilcoxon signed-rank test (paired)"
                s, p_value = stats.wilcoxon(stats_groups[0], stats_groups[1])
                if p_value < alpha:
                    signi = True
                else:
                    signi = False

        else:
            ##################################################################
            # 2. Run Kruskal Wallis Test for multiple groups (non-parametric)
            ##################################################################
            if not assume_normal or not assume_equal_var:
                test_performed = "Kruskal-Wallis"
                try:
                    s, p_value = stats.kruskal(*stats_groups)
                except ValueError:
                    print("Skipping Kruskal stats since "
                          f"peak {peak} only shows in one group of groups ({names})"
                          f"with values:", stats_groups)
                    s = p_value = 1
                    unique_peak = True
                    test_performed = "None (peak unique to group)"

            if assume_normal and assume_equal_var:
                test_performed = "one-way ANOVA"
                try:
                    s, p_value = stats.f_oneway(*stats_groups)
                except ValueError:
                    print("Skipping Anova",
                          f"peak {peak} only shows in one group of groups ({names})"
                          f"with values:", stats_groups)
                    s = p_value = 1
                    unique_peak = True
                    test_performed = "None (peak unique to group)"

            # 2. If the Kruskal/ANOVA says groups are different do a posthoc
            if p_value < 0.05:
                signi = True
                p_adjust_test = 'bonferroni'
                if len(stats_groups) < 3:
                    results = sp.posthoc_conover([stats_groups[0],
                                                  stats_groups[1]],
                                                 p_adjust=p_adjust_test)
                else:
                    # As array - to avoid errors w/ n>2 and unequal numbers
                    stats_groups_for_posthoc = np.asarray(stats_groups, dtype="object")
                    results = sp.posthoc_conover(stats_groups_for_posthoc,
                                                 p_adjust=p_adjust_test)
                results.columns = names
                results["condition"] = names
                results.set_index("condition", inplace=True)
                test_performed += f" with {p_adjust_test} correction"
            else:
                signi = False

        info=(f"--- {peak} - {test_performed}: p = {round(p_value,2)}, "
              f" ({'SIGNIFICANT' if signi else 'NOT significant'})")
        if signi:
            print(info)
        logging.info(info)

        # Add to data storage
        stats_data.append([peak, test_performed, p_value, signi, results,
                             unique_peak, average_dict, mode_dict,
                           median_dict, stats_dict])

    #####################################################################
    # 2. Generate df from storage
    #####################################################################
    stats_df = pd.DataFrame(stats_data,
                              columns=["peak_name",
                                       "test_performed", "p_value",
                                       "p<0.05", "posthoc_p_values",
                                       "unique_peak",
                                       "average", "modal", "median",
                                       "groups"])
    return stats_df

def marker_and_normalize(df, peak_dict="", include_marker=False, normalize=True,
                         normalize_to=False, correct=False):
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
        df = remove_marker_from_df(df, peak_dict=peak_dict, on=ladder_field,
                                   correct_for_variant_samples=correct)
        if not normalize:
            return df

    ######################################################################
    # 2. Optional: Normalize to a reference sample
    ######################################################################
    if normalize_to:
        result = df.copy()
        if normalize_to not in df.columns:
            print(f"--- Warning: '{normalize_to}' is not a valid sample name.")
            print(f"--- Please choose one of these: {df.columns.tolist()}")
            logging.warning(f"--- {normalize_to} is not a valid sample name.")
            exit()
        for feature_name in df.columns:
            if "Ladder" in feature_name:
                continue
            result[feature_name] = df[feature_name]/ df[normalize_to]
        return result
    ######################################################################
    # 3. Optional: Normalize to a value between 0-1
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


def epg_stats(df, save_dir="", unit="normalized_fluorescent_units", size_unit="bp_pos",
              metric_unit="value", nuc_dict=NUC_DICT, paired=False, region_id="region_id",
              cut=False):
    """

    Compute and output basic statistics for DNA size distributions

    :param df: pandas.DataFrame
    :param save_dir: string, where to save the statistics to
    :param unit: string (y-variable)
    :param size_unit: string (x-variable)
    :param paired: bool, whether measurements were paired
    :return: will save three dataframes as .csv files in stats \
    directory: basic_statistics.csv, peak_statistics.csv, \
    group_statistics_by_CATEGORICAL-VAR.csv)

    """
    #####################################################################
    # 1. Basic stats
    #####################################################################
    df["sample"].astype(object) # Make sure all sample names are type obj
    distr_stats = distribution_stats(df, save_dir=f"{save_dir}basic_statistics.csv",
                       unit=unit, size_unit=size_unit)
    full_stats_dir = f"{save_dir}peak_statistics.csv"

    #####################################################################
    # 2. Average bp size, peak positions, and peak size per sample
    #####################################################################
    print("--- Nucleosomal fractions & peak analysis")

    # Initiate the dataframe (will be used for statistics)
    peak_info = []
    peak_columns = ["sample", region_id, "From [bp]", "To [bp]", "AUC", metric_unit, "unit"]

    for sample in df["sample"].unique():
        # Select data for only this sample
        sub_df = df[df["sample"] == sample]

        ##################################################################
        # 2.1 Skew, AUC, Entropy
        ##################################################################
        entropy = distr_stats.loc[sample]["Entropy"]
        peak_info.append([sample, "Entropy", np.nan, np.nan, np.nan,
                          entropy, "nats"])
        skew = distr_stats.loc[sample]["Skewness"]
        peak_info.append([sample, "Skewness", np.nan, np.nan, np.nan,
                          skew, "Skewness"])
        auc_total = distr_stats.loc[sample]["AUC"]
        peak_info.append([sample, "AUC (total)", np.nan, np.nan, np.nan,
                          auc_total, "NFU x position"])
        ##################################################################
        # 2.2 Nucleosomal fractions with AUC
        ##################################################################
        nuc_df = nuc_fractions(sub_df, unit=unit, size_unit=size_unit,
                               nuc_dict=nuc_dict)
        for nuc_feature in nuc_df.index:
            auc = nuc_df.loc[nuc_feature, "auc"]
            percentage = nuc_df.loc[nuc_feature, "percent"]
            start = nuc_df.loc[nuc_feature, "start"]
            end = nuc_df.loc[nuc_feature, "end"]
            peak_info.append([sample, nuc_feature, start, end, auc,
                              percentage, "percent total DNA (%)"])
        ##################################################################
        # 2.3 Short-to-long fragment ratio
        ##################################################################
        nuc_fractions_avail = nuc_df.index.tolist()
        if "Short II (100-400 bp)" in nuc_fractions_avail and "Long (> 401 bp)" in nuc_fractions_avail:
            short = nuc_df.loc["Short II (100-400 bp)"]["percent"]
            long = nuc_df.loc["Long (> 401 bp)"]["percent"]
            s2l_ratio = short/long
            peak_info.append([sample, "short-to-long fragment ratio", np.nan, np.nan, np.nan,
                              s2l_ratio, "ratio (short/long fragments)"])
        ##################################################################
        # 2.4 Mean, median, mode bp
        ##################################################################
        mean_bp, median_bp, mode_bp = mean_from_histogram(
            sub_df, unit=unit, size_unit=size_unit)
        peak_info.append([sample, "average_size", np.nan, np.nan, np.nan,
                          round(mean_bp,2), "bp"])
        peak_info.append([sample, "modal_size", np.nan, np.nan, np.nan,
                          mode_bp, "bp"])
        peak_info.append([sample, "median_size", np.nan, np.nan, np.nan,
                          median_bp, "bp"])

        ##################################################################
        # 2.5 Peaks
        ##################################################################
        array = np.array(sub_df[unit].values.tolist())
        max_peak = array.max()
        min_peak_height = max_peak * MIN_PEAK_HEIGHT_FACTOR  # Define min peak height
        peaks, _ = find_peaks(array, distance=DISTANCE,  # n pos apart
                              height=min_peak_height, # minimum height
                              prominence=PEAK_PROMINENCE)
        bp_positions = sub_df[size_unit].values.tolist()

        # Plot the peaks for each sample
        peakplot(array, peaks, str(sample), "sample", str(sample), save_dir,
                 y_label=YLABEL, x_label=XLABEL_PRIOR_SIZE, size_values=bp_positions)

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
            peak_info.append([sample, f"peak_{i}", np.nan, np.nan, np.nan,
                              round(bp,2), "bp"])
            if peak == max_peak:
                peak_info.append([sample, "max_peak", np.nan, np.nan,np.nan,
                                  round(bp,2), "bp"])

    #####################################################################
    # Create the nucleosome & peak dataframe
    #####################################################################
    peak_df = pd.DataFrame(peak_info, columns=peak_columns)

    ######################################################################
    # 3. Optional: Grouped stats (Mean sizes)
    ######################################################################
    cols_no_stats = [size_unit, "sample", unit]

    for categorical_variable in [c for c in df.columns if c not in
                                                          cols_no_stats]:
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
        stats_df = run_stats(peak_df, variable=metric_unit,
                             category=categorical_variable, paired=paired)
        stats_df.to_csv(f"{save_dir}group_statistics_by_{categorical_variable}.csv")
        # END LOOP

    ######################################################################
    # 4. Save the group-annotated statistics & plot
    ######################################################################
    peak_df.to_csv(full_stats_dir)
    stats_plot(full_stats_dir, cols_not_to_plot=peak_columns, region_id=region_id,
               y=metric_unit, cut=cut)
    # END OF FUNCTION


def epg_analysis(path_to_file, path_to_ladder, path_to_meta, run_id=None,
                 include_marker=False, image_input=False, save_dir=False, marker_lane=0,
                 nuc_dict=NUC_DICT, paired=False, normalize=True, normalize_to=False,
                 correct=False, cut=False):
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
    :param paired: bool, whether to perform a paired statistical analysis
    :param normalize: bool, whether to perform min-max normalization
    :param normalize_to: str of False, name of sample to which all other samples are normalized to
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
    logging.info(f"Min-Max Normalization: {normalize}")
    logging.info(f"Include marker: {include_marker}")
    logging.info(f"Correct for concentration-variances: {correct}")
    logging.info(f"Paired analysis: {paired}")
    #####################################################################
    # 1. Create results dir and define inputs
    #####################################################################
    if not run_id:
        run_id = path_to_file.rsplit("/", 1)[1].rsplit(".", 1)[0]
    if not save_dir:
        save_dir = path_to_file.rsplit("/", 1)[0] + f"/{run_id}/"
    if not save_dir.startswith("/"):
        save_dir = maindir + "/" + save_dir
    plot_dir = f"{save_dir}/plots/"
    qc_dir = f"{save_dir}qc/"
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
    ######################################################################
    # Save the metrics to log file
    ######################################################################
    t1 = time.time()
    logging.info(f"--- DNAvi RUN LOG {datetime.UTC} ---\n")
    logging.info(f"DNAvi Start time\t{t1}\n")
    logging.info(f"DNAvi Nuc Fractions: \t{nuc_dict}\n")

    print("------------------------------------------------------------")
    print("        Calculating basepair positions based on ladder")
    print("------------------------------------------------------------")
    peak_dict = peak2basepairs(df, qc_dir, ladder_dir=path_to_ladder,
                               marker_lane=marker_lane)
    df = pd.read_csv(basepair_translation_file, header=0, index_col=0)
    # Only use data within maximum marker size
    df.dropna(inplace=True)
    #####################################################################
    # 4. Height-normalize the data (default)
    #####################################################################
    print("------------------------------------------------------------")
    print(f"        Height-normalizing data: {normalize} \n"
          f"        Keeping markers: {include_marker}")
    print("------------------------------------------------------------")
    df = marker_and_normalize(df, peak_dict=peak_dict, include_marker=include_marker,
                      normalize=normalize, normalize_to=normalize_to, correct=correct)

    #####################################################################
    # 5. Add the metadata
    #####################################################################
    df = split_and_long_by_ladder(df)

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
    epg_stats(df, save_dir=stats_dir, nuc_dict=nuc_dict, paired=paired,
              cut=cut)

    # Time the basic modules
    t_mod2 = time.time()

    print("------------------------------------------------------------")
    print(f" Finished basic analysis and statistics in {t_mod2-t1} ")
    print("------------------------------------------------------------")
    logging.info(f"Basic module ends\t{t_mod2}\n")
    logging.info(f"Basic module total time\t{t_mod2-t1}\n")
    #####################################################################
    # 5. Plot raw data (samples seperated)
    #####################################################################
    t_plot1 = time.time()
    print("------------------------------------------------------------")
    print("        Plotting results")
    print("------------------------------------------------------------")
    gridplot(df, x=XCOL, y=YCOL, save_dir=plot_dir, title=f"all_samples",
             y_label=YLABEL, x_label=XLABEL)
    t_plot2 = time.time()
    print("------------------------------------------------------------")
    print(f" Finished plotting in {t_plot2-t_plot1} ")
    print("------------------------------------------------------------")
    logging.info(f"Plot module total time\t{t_plot2 - t_plot1}\n")
    logging.info(f"DNAVI TOTAL TIME\t{t_plot2 - t1}\n")

    #########################################################################
    # Copy the log file for the user..
    #########################################################################
    print("")
    print("--- DONE. Results in same folder as input file.")
    logging.info(f"--- RUN  FINISHED SUCCESSFULLY, {datetime.datetime.now()}")
    #########################################################################
    # Copy the log file for the user..
    #########################################################################
    shutil.copy(f'{os.getcwd()}/{LOGFILE_NAME}', f'{save_dir}/{LOGFILE_NAME}')
    # END OF FUNCTION
# END OF SCRIPT