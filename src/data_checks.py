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

def check_marker_lane(input_nr):
    """
    Quickly check if the number for marker lane is pos
    :param input_nr: int
    :return: int if check passed
    """
    try:
        int(input_nr)
    except:
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
    except:
        print(f"--- {filename} seems to have less than 4 rows. "
              f"Not plausible. Please check your input file.")
        exit()
    try:
        df = pd.read_csv(filename, header=0, delimiter=delim)
    except:
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
    except:
        print(f"--- {filename} seems to have less than 4 rows. "
              f"Not plausible. Please check your input file.")
        exit()
    try:
        df = pd.read_csv(filename, header=0, delimiter=delim)
    except:
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
        sub_df["Basepairs"].astype(int).values.tolist()[::-1]
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
    df = pd.read_csv(filename, header=0)
    try:
        df["ID"] = df["SAMPLE"]
    except:
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
# END OF SCRIPT