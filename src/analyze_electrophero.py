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
from constants import YLABEL, YCOL, XCOL, XLABEL
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
    Define the maxima in the ladder EPG.

    :param df:
    :param qc_save_dir:
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

        # Potential to customize the ladder specs manually (for developers)
        if "adjust" in ladder_type:
            peaks, _ = find_peaks(array, distance=20,  # 10 pos apart
                                  height=50)  # minimum height
        else:
            peaks, _ = find_peaks(array, distance=20,  # 10 pos apart
                                  height=min_peak_height)  # minimum height
        peak_list = peaks.tolist()
        print(f"{len(peak_list)} peaks detected.")
        logging.info(f"{len(peak_list)} peaks detected.")

        ##################################################################
        # 1.2 Detect ladder type
        ##################################################################
        check_ladder(ladder_dir)
        ladder_df = pd.read_csv(ladder_dir)
        ref = "custom"
        ladder_df["Basepairs"].astype(int).values.tolist()[::-1]
        peak_annos = ladder_df["Basepairs"].astype(int).values.tolist()[::-1]
        print(peak_annos)
        exit()
        try:
            if "marker" in ladder_df["Peak"]:
                print("--- MARKER DETECTED.")
                exit()
                logging.info("Markers detected")
            if "Basepairs" in ladder_df.columns:
                logging.info("Basepairs detected")
        except:
            print("Peak or Basepairs column in ladder file missing.")
            exit()
        peak_dict = {ref: peak_annos}

        # Now redo (basic if no ladder info is given)
        if len(peak_dict[ref]) != len(peak_list):
            error = ("Inconstistent number of peaks between ladder file "
                     "and data input")
            return None, error

        ladder2type.update({ladder: ref})

        #################################################################
        # 1.3 Plot
        #################################################################
        peakplot(array, peaks, ladder_id, ref, i, qc_save_dir,
                 y_label=y_label)

        #################################################################
        # 1.4 Integrate bp information into the df
        #################################################################
        peak_col = [0]
        peak_counter = 0
        for n, pos in enumerate(array):
            if n in peak_list:
                peak_col.append(peak_dict[ref][peak_counter])
                peak_counter += 1

            else:
                peak_col.append(np.nan)

        #################################################################
        # 1.5 Interpolate missing positions between the peaks
        #################################################################
        s = pd.Series(peak_col)
        df[ladder + "_interpol"] = s.interpolate()
        # Just update the df tb returned
        return_df[ladder] = s.interpolate()

        #################################################################
        # 1.3 Plot again with the inferred base pair scale
        #################################################################
        lineplot(df, x=f"{ladder}_interpol", y=ladder,
                 save_dir=qc_save_dir, title=f"{i}_{ref}_interpolated",
                 y_label=y_label,
                 x_label=x_label)

    #####################################################################
    # 2. Save the translation
    #####################################################################
    df.to_csv(qc_save_dir + "interpolated.csv")
    return_df.to_csv(qc_save_dir + "bp_translation.csv")

    #####################################################################
    # 3. Plot all ladders together
    #####################################################################
    ladderplot(df, ladder2type, qc_save_dir, y_label=y_label,
               x_label=x_label)

    #####################################################################
    # 4. Save the ladder infos
    #####################################################################
    d = pd.DataFrame.from_dict(ladder2type, orient="index")
    d.to_csv(f"{qc_save_dir}info.csv")
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


def parse_meta_to_long(df, metafile, sample_col="sample", source_file=""):
    """
    Parse metadata and transfer to long

    :param df:
    :param metafile:
    :return:
    """

    meta = pd.read_csv(metafile, header=0)
    try:
        meta["ID"] = meta["SAMPLE"]
    except:
        error = "Metafile misformatted."
        return error
    cols_not_to_add = ["SAMPLE","ID"]
    for col in meta.columns:
        if meta[col].isnull().values.any():
            error = ("Empty positions in meta file")
            return error
        if col not in cols_not_to_add:
            print(f"Adding metatadata: ", col)
            logging.info(f"Adding metatadata: ", col)
            dict_meta = dict(zip(meta.ID, meta[col]))
            df[col] = df[sample_col].map(dict_meta)
    df.to_csv(source_file)
    # END OF FUNCTION


def normalize(df, ladder="", peak_dict=""):
    """

    Function to normalize the RFU to a value between 0,1

    """
    ##https://stackoverflow.com/questions/26414913/normalize-columns-of-a-dataframe

    ################################################################################
    # 1. Remove the marker bands (lowest / top band)
    ################################################################################
    lower_marker = peak_dict[ladder[0]][0]
    upper_marker = peak_dict[ladder[0]][-1]
    ladder_field = [e for e in df.columns if "adder" in e][0]

    df = df[(df[ladder_field] > lower_marker) &
           (df[ladder_field] < upper_marker)]

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

def epg_stats(df, save_dir="", unit="normalized_fluorescent_units", size_unit="bp_pos",
              ladder="", peak_dict=None):
    """
    To compute basic statistics for DNA distr.
    :return:
    """

    if peak_dict:
        print(peak_dict)
        #################################################################
        # 1. Remove the marker bands (lowest / top band)
        #################################################################
        add_on = 0.1
        lower_marker = peak_dict[ladder[0]][0]
        lower_marker = lower_marker + (lower_marker*add_on)
        upper_marker = peak_dict[ladder[0]][-1]
        upper_marker = upper_marker - (upper_marker*add_on)
        print("--- Excluding marker peaks from analysis")
        logging.info("_ Excluding marker peaks from analysis")
        df = df[(df[size_unit] > lower_marker) &
                (df[size_unit] < upper_marker)]
    logging.info("Samples: ", df["sample"].value_counts())

    #####################################################################
    # 1. Basic stats
    #####################################################################
    # Make sure all sample names are type obj
    df["sample"].astype(object)
    basic_stats = df.describe(include='object')
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
        peaks, _ = find_peaks(array, distance=20,  # 10 pos apart
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


def epg_analysis(path_to_file, path_to_ladder, path_to_meta, run_id=None):
    """
    To plot the Tape Station electropherogram
    :param path_to_file: str
    :return:
    """
    print("")
    print("------------------------------------------------------------")
    print("""           DNA FRAGMENT SIZE ANALYSIS           """)
    print("------------------------------------------------------------")
    print(f"""     
        DNA file: {path_to_file}      
        Ladder file: {path_to_ladder}
        Meta file: {path_to_meta}""")
    print("")

    logging.info(f"DNA file: {path_to_file}, Ladder file: {path_to_ladder},"
                 f"Meta file: {path_to_meta}")

    #####################################################################
    # 1. Create results dir and define inputs
    #####################################################################
    if not run_id:
        run_id = path_to_file.rsplit("/", 1)[1].rsplit(".", 1)[0]
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
    # 3. Get source data, ladder type, transfer to long format
    #####################################################################
    ladder = pd.read_csv(qc_dir + "info.csv", index_col=0,
                         header=0).transpose().values[0]

    #####################################################################
    # 4. Height-normalize the data (default)
    #####################################################################
    print("------------------------------------------------------------")
    print("        Height-normalizing data")
    print("------------------------------------------------------------")
    normalized_df = normalize(df, ladder=ladder, peak_dict=peak_dict)
    df = normalized_df

    #####################################################################
    # 5. Add the metadata
    #####################################################################
    if not os.path.isfile(source_file):
        df = split_and_long_by_ladder(df, path_to_file)
        if path_to_meta:
            print("------------------------------------------------------------")
            print("        Parsing metadata ")
            print("------------------------------------------------------------")
            error = parse_meta_to_long(df, path_to_meta,
                                       source_file=source_file)
            if error:
                print(error)
                exit()
        else:
            print(f"--- No meta file, using column names.")
            df.to_csv(source_file)

    if os.path.isfile(source_file):
        df = pd.read_csv(source_file, header=0, index_col=0)
        ladder = pd.read_csv(qc_dir + "info.csv", index_col=0,
                             header=0).transpose().values[0]

    ######################################################################
    # 6. Add statistics
    ######################################################################
    print("------------------------------------------------------------")
    print("        Performing statistical analysis")
    print("------------------------------------------------------------")
    epg_stats(df, save_dir=plot_dir, ladder=ladder, peak_dict=peak_dict)

    #####################################################################
    # 5. Plot raw data (samples seperated)
    #####################################################################
    print("------------------------------------------------------------")
    print("        Plotting results")
    print("------------------------------------------------------------")
    gridplot(df, x=XCOL, y=YCOL, save_dir=plot_dir, title=f"all_samples",
             hue="sample", y_label=YLABEL, x_label=XLABEL,
             plot_lower=False, ladder=ladder, peak_dict=peak_dict,
             ladder_dir=path_to_ladder)
    return error
    # END OF FUNCTION
# END OF SCRIPT
