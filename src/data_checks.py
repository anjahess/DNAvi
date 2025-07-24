"""

Functions to assure input files to DNAvi are correctly formatted

@author: Anja Hess
@date: 2025-JUL-23

"""

import argparse
import os
from csv import Sniffer
import pandas as pd
import werkzeug
from werkzeug.utils import secure_filename


def detect_delim(file, num_rows=1):
    """
    In case not tab delim
    #https://stackoverflow.com/questions/65909857/
    may-i-use-either-tab-or-comma-as-delimiter-
    when-reading-from-pandas-csv
    :param file:
    :param num_rows:
    :return:
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
    Function to check if a filename is okay
    :param filename: str
    :return: improved file name
    """

    filename = secure_filename(filename)
    return filename

def check_input(filename):
    """

    Function to check if the input is either a directory with csvs or images
    or a single file
    :param filename: str
    :return: raise error if file does not have correct format

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
    :param filename:
    :return:
    """
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
        error = ("Input file missing a ladder column. "
                 "Please add and try again.")
        print(error)
        exit()
    return df

def check_ladder(filename):
    """

    Function to check if the ladder is formatted correctly
    :param filename: str
    :return: raise error if file does not have correct format

    """
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

    if "Peak" not in df.columns or "Basepairs" not in df.columns:
        print("--- Ladder columns have to be named 'Peak' and 'Basepairs',"
              "please check and try again.")

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
    df["Basepairs"].astype(int).values.tolist()[::-1]
    peak_annos = df["Basepairs"].astype(int).values.tolist()[::-1]

    if not sorted(peak_annos) == peak_annos:
        error = ("Your markers in ladder file are not sorted by "
                 "basepair size. That's not allowed...sorry")
        print(error)
        exit()

    return filename



def check_meta(filename):
    """

    Function to check if the ladder is formatted correctly
    :param filename: str
    :return: raise error if file does not have correct format

    """
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
    # 3. Make sure it's really csv format
    ######################################################################
    if not filename.endswith('.csv'):
        raise argparse.ArgumentTypeError('File must have a csv extension')

    return filename


# END OF SCRIPT