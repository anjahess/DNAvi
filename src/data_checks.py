"""

Functions to assure input files for DNAvi are correctly formatted

Author: Anja Hess

Date: 2025-JUL-23

"""

import argparse
import os
from csv import Sniffer
import pandas as pd
from werkzeug.utils import secure_filename
import logging

def check_marker_lane(input_nr):
    """
    Quickly check if the number for marker lane is pos
    :param input_nr: int
    :return: int if check passed
    """
    try:
        int(input_nr)
    except Exception as exception:
        logging.exception(exception)
        print(f'Marker lane number must be an integer (full number) not ({input_nr})')
        exit()

    if int(input_nr) > 0:
        return int(input_nr)
    else:
        print(f"--- Negative numbers are not allowed for marker lane positions ({input_nr})")
        exit(1)

def detect_delim(file, num_rows=1):
    """

    Detect delimiter from input table with Sniffer

    :param file: str, path to input file
    :param num_rows: int, number of rows in file
    :return: str, detected delimiter

    """
    sniffer = Sniffer()
    with open(file, 'r') as f:
        for row in range(num_rows):
            line = next(f).strip()
            delim = sniffer.sniff(line)
    return delim.delimiter
    # END OF FUNCTION

def check_name(filename):
    """

    Function to generate secure filename from filename

    :param filename: str
    :return: improved file name

    """

    filename = secure_filename(filename)
    return filename

def check_input(filename):
    """

    Function to check if the input exists

    :param filename: str

    :return: raise error if file does not exist

    """

    ######################################################################
    # 1. Make sure all arguments exist
    ######################################################################
    if not(os.path.exists(filename)):
        print(f"{filename} doesn't exist")
        exit()
    return filename



def check_file(filename):
    """

    Function to check if file is correctly formatted

    :param filename: str
    :return: raise error if file is incorrectly formatted

    """

    print("--- Performing input check")
    ######################################################################
    # 2. Path vs File
    ######################################################################
    try:
        delim = detect_delim(filename, num_rows=4)
    except Exception as exception:
        logging.exception(exception)
        print(f"--- {filename} seems to have less than 4 rows. "
              f"Not plausible. Please check your input file.")
        exit()
    try:
        df = pd.read_csv(filename, header=0, delimiter=delim)
    except Exception as exception:
        logging.exception(exception)
        print("--- Error reading your (generated) CSV file,"
              "please check your input file.")
        exit()
    print(df.head(3))

    #####################################################################
    # Basic check for malformatted data
    #####################################################################
    if df.isnull().values.any():
        print("--- Input signal table contains NaNs, that's not "
              "plausible for DNA intensities. "
              "Please check input and try again.")
        exit()
    for col in df.columns:
        if "Unnamed" in col:
            print(f"--- Warning, column without name detected: {col}")
        dtype = df[col].dtype
        if dtype != float:
            error = (f"Invalid data type in {col}: not a number (float). "
                     f"Please check your input and try again.")
            print(error)
            exit()

    #####################################################################
    # Check that there is a ladder column
    #####################################################################
    detected_ladders = [e for e in df.columns if "Ladder" in e]
    if not detected_ladders:
        error = ("--- Warning: Input file missing a ladder column, "
                 "defaulting to first column as DNA marker.")
        print(error)
    return df

def check_ladder(filename):
    """

    Function to check if the ladder is formatted correctly

    :param filename: str
    :return: raise error if file does not have correct format

    """

    print("--- Performing ladder check")
    ######################################################################
    # 1. Make sure all arguments exist
    ######################################################################
    if not(os.path.exists(filename)):
        print(f"{filename} doesn't exist")
        exit()

    ######################################################################
    # 2. Make sure you have a proper dataframe
    ######################################################################
    try:
        delim = detect_delim(filename, num_rows=3)
    except Exception as exception:
        logging.exception(exception)
        print(f"--- {filename} seems to have less than 4 rows. "
              f"Not plausible. Please check your input file.")
        exit()
    try:
        df = pd.read_csv(filename, header=0, delimiter=delim)
    except Exception as exception:
        logging.exception(exception)
        print("--- Error reading your ladder file,"
              "please check it and try again.")
        exit()
    if "Peak" not in df.columns or "Basepairs" not in df.columns or "Name" not in df.columns:
        print("--- Ladder columns have to be named 'Peak', 'Basepairs' and 'Name'."
              " Please check and try again.")
        exit()
    ######################################################################
    # 3. Make sure ladder content is plausible
    ######################################################################
    if (df['Peak'].isnull().values.any() or
            df['Basepairs'].isnull().values.any()):
        error = ("Empty positions in ladder file detected. "
                 "Make sure Peak/Basepairs column have the same length.")
        print(error)
        exit()

    if (df["Basepairs"].dtypes != float and
            (df["Basepairs"].dtypes != int)):
        error = ("Peak column in ladder file contains "
                 "invalid data (not int or float).")
        print(error)
        exit()

    zero_count = df['Basepairs'].value_counts().get(0, 0)
    if zero_count > 0:
        error = ("Detected Zeros in Basepairs column. "
                 "That's not allowed...sorry")
        print(error)
        exit()


    ######################################################################
    # Check individual ladders (in case of multiple ladders passed)
    ######################################################################
    for ladder in df["Name"].unique():
        sub_df = df[df["Name"] == ladder].reset_index(drop=True)
        peak_annos = sub_df["Basepairs"].astype(int).values.tolist()[::-1]

        if not sorted(peak_annos) == peak_annos:
            error = ("Your markers in ladder file are not sorted by "
                     "DESCENDING basepair size. That's not allowed...sorry."
                     "Please order like so: 1000,500,300... and try again.")
            print(error)
            exit()

        ######################################################################
        # Find markers and check them
        ######################################################################
        markers = sub_df[sub_df['Peak'].str.contains('marker')]["Basepairs"].tolist()

        if markers:
            # Check that there are only 2 markers, and that they are
            # not in the middle of the peaks
            marker_pos = sub_df.loc[sub_df['Peak'].str.contains(
                'marker')]["Basepairs"].index.tolist()

            last_row_index = len(sub_df.values) - 1  # 0-based
            if len(markers) > 2:
                print("--- Ladder Error: more than two markers. That's implausible,"
                      " please correct the ladder file and retry.")
                exit()
            if len(markers) == 2 and ((0 not in marker_pos) or (last_row_index not in marker_pos)):
                print("--- Ladder Error: DNA markers should be first and last entry")
                exit()
            if len(markers) == 1 and ((0 not in marker_pos) and (last_row_index not in marker_pos)):
                print("--- Ladder Error: DNA marker should be either first or last entry")
                exit()
    return filename



def check_meta(filename):
    """

    Check if the metadata file is formatted correctly

    :param filename: str, path to metadata file

    :return: raise error if file does not have correct format

    """
    print("--- Performing metadata check")
    ######################################################################
    # 1. Make sure all arguments exist
    ######################################################################
    if not(os.path.exists(filename)):
        print(f"{filename} doesn't exist")
        exit()

    ######################################################################
    # 2. Make sure the extension is right
    ######################################################################
    if not filename.endswith('.csv'):
        raise argparse.ArgumentTypeError('File must have a csv extension')

    ######################################################################
    # 3. Check nomenclature, NANs and duplicates in the index
    ######################################################################
    try:
        delim = detect_delim(filename, num_rows=4)
    except Exception as exception:
        logging.exception(exception)
        print(f"--- {filename} seems to have less than 4 rows. "
              f"Not plausible. Please check your input file.")
        exit()
    try:
        df = pd.read_csv(filename, delimiter=delim, header=0)
    except Exception as e:
        logging.exception(e)
        print("Metafile misformatted. Make sure your fields do not contain commata.")
        exit()

    try:
        df["ID"] = df["SAMPLE"]
    except Exception as exception:
        logging.exception(exception)
        print("Metafile misformatted. Make sure first column is 'SAMPLE'")
        exit()

    if df["SAMPLE"].isnull().values.any():
        print("--- Meta table contains NaNs in SAMPLE column,"
              "Make sure every sample has a name and try again.")
        exit()

    if df.duplicated(subset=["SAMPLE"]).any():
        print("--- Duplicate sample names in metadata. Please give each "
              "sample a unique ID and try again.")
        exit()

    return filename


def check_config(filename):
    """

    Check if the config file is formatted correctly

    :param filename: str, path to config file

    :return: raise error if file does not have correct format

    """
    print("--- Performing custom config file check")
    ######################################################################
    # 1. Make sure all arguments exist
    ######################################################################
    if not(os.path.exists(filename)):
        print(f"{filename} doesn't exist")
        exit()
    ######################################################################
    # 2. Detect delimiter
    ######################################################################
    try:
        delim = detect_delim(filename, num_rows=2)
    except Exception as exception:
        logging.exception(exception)
        print(f"--- {filename} seems to have less than 2 rows. "
              f"Not plausible. Please check your input file.")
        exit()
    try:
        df = pd.read_csv(filename, header=0, delimiter=delim)
    except Exception as exception:
        logging.exception(exception)
        print("--- Error reading your ladder file,"
              "please check it and try again.")
        exit()
    ######################################################################
    # 3. Check nomenclature in names column
    ######################################################################
    try:
        print(df)
    except Exception as exception:
        logging.exception(exception)
        print("Metafile misformatted. Make sure first column is called"
              "'name', the second is 'start', and the third is 'end'")
        exit()
    if df["name"].isnull().values.any():
        print("--- Config file table contains NaNs in 'name' column."
              "Make sure every range has a name, and try again.")
        exit()

    ######################################################################
    # 4. Replace NaN with 0 for int check, check dups
    ######################################################################
    df["start"].fillna( 0, inplace=True)
    df["end"].fillna( 0, inplace=True)
    try:
        df["start"] = df["start"].astype(int)
        df["end"] = df["end"].astype(int)
    except Exception as exception:
        logging.exception(exception)
        print("--- Non-integers in start/end. Make sure only integers are there.")
        exit()
    if df.duplicated(subset=["name"]).any():
        print("--- Duplicate sample names in config. Please give each "
              "sample a unique ID and try again.")
        exit()

    ######################################################################
    # 5. Check for common errors
    ######################################################################

    # Convert back
    df["end"].replace(0, None, inplace=True)
    df["start"].replace(0, None, inplace=True)
    ######################################################################
    # 5. Check for common errors
    ######################################################################
    # Start > End
    len_too_small = len(df[df["end"] < df["start"]])
    if len_too_small > 0:
        print("--- Positions in end are < start, please correct the config file:",
              df[df["end"] < df["start"]]
              )
        exit()
    # Interval <2bp
    len_too_narrow = len(df[(df["end"] - df["start"]) < 2])
    if len_too_narrow > 0:
        print("--- The interval is < 2bp. Please make it larger.",
              df[(df["end"] - df["start"]) < 2]
              )
        exit()
    isnull_len = df.isnull().sum(axis=1).max()
    # Two NaNs
    if isnull_len > 1:
        print("--- Two Empty interval detected, please change or remove it.")
        exit()
    ######################################################################
    # 6. Finally parse to the normal nuc dict format and return
    ######################################################################
    nuc_dict = {row[0]: (row[1], row[2]) for row in df.values}
    return nuc_dict




def compute_nuc_intervals(start, step=200, total_steps=10,
                          prefixes=["Mono", "Di", "Tri", "Tetra", "Penta", "Hexa",
                                    "Hepta", "Octa", "Nona", "Deca"]):
    """

    Compute interpretable nucleosomaal intervals in format them
    into a common DNAvi nuc dict.

    :param start:
    :param step:
    :param total_steps:
    :param prefixes:
    :return: new nuc_dict (pyhton dictionary)
    """

    #####################################################################
    # 1. Define list range and add the name for each
    #####################################################################
    max_list = (total_steps * step)
    nuc_dict = {}
    for i, size in enumerate(range(start, max_list, step)):
        interval_name = prefixes[i]
        start_1based = size + 1
        end = size + step
        print(interval_name, start_1based, end)
        nuc_dict[f"{interval_name}({start_1based}-{end}bp)"] = (start_1based, end)

    #####################################################################
    # Everything larger goes up
    #####################################################################
    nuc_dict[f"Deca({start_1based}-{end}bp)"] = \
        (nuc_dict[f"Deca({start_1based}-{end}bp)"][1]+1, None)

    return nuc_dict
    # END OF FUNCTION


def check_interval(interval_string, max_val=100000):
    """

    Check if the config file is formatted correctly

    :param filename: str, path to config file

    :return: raise error if file does not have correct format

    """
    print("--- Performing interval check")

    ######################################################################
    # 1. Detect delimiter
    ######################################################################
    if "," not in interval_string:
        print("Missing interval delimiter. Please provide interval "
              "as Start,Step (e.g. 100,200 for starting at 100bp and increasing "
              "in 200 bp steps).")
        exit(1)
    if interval_string.count(",") > 1:
        print("Too many delimiters. Please provide interval "
              "as Start,Step (e.g. 100,200 for starting at 100bp and increasing "
              "in 200 bp steps).")
        exit(1)
    ######################################################################
    # 2. Split and convert to int
    ######################################################################
    start, step = interval_string.replace(" ","").split(",")
    try:
        start = int(start)
    except ValueError:
        print(f"--- Invalid start value for interval: {start}. Please provide integer.")
        exit(1)
    try:
        step = int(step)
    except ValueError:
        print(f"--- Invalid start value for interval: {step}. Please provide integer.")
        exit(1)
    print(f"--- Computing nucleosomal intervals from {start} bp in steps of {step} bp.")

    if step < 5 or start < 5:
        print(f"--- Start/Step too small. Please increase value.")
        exit(1)
    if start > max_val or step > max_val:
        print(f"--- Start or step value too large. Please lower value.")
        exit(1)
    ######################################################################
    # 3. Convert to nucleosomal dict
    ######################################################################
    nuc_dict = compute_nuc_intervals(start=start, step=step)
    return nuc_dict


def generate_meta_dict(meta_path, files=[]):
    """
    A function to conveniently parse metadata for multiple files
    when handling multi-file inputs

    :param meta_path: path to metadata file
    :param files: list
    :return: dictionary parsing the new split metadata file for each input file
    """

    meta_df = pd.read_csv(meta_path)
    meta_dict = {}
    toplevel_dir = f"{os.path.dirname(meta_path)}/"

    for file in files:
        file_name = file.split("/")[-1]
        print(f"--- Getting metadata for {file_name} ---")
        meta_df_file = meta_df[meta_df["FILE"] == file_name]
        if meta_df_file.empty:
            meta_dict[file] = False
        else:
            file_meta = file.rsplit('.',1)[0]+"_meta.csv"
            file_id = file_meta.rsplit('/',1)[1]
            file_meta_name = f"{toplevel_dir}{file_id}"
            meta_df_file.to_csv(file_meta_name, index=False)
            meta_dict[file] = file_meta_name
    return meta_dict
    # END OF FUNCTION
# END OF SCRIPT