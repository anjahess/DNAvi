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

    #################################################################
    # Basic check for malformatted data
    #################################################################
    if df.isnull().values.any():
        print("--- Input signal table contains NaNs, that's implausible for "
              "DNA intensities. Please check input and try again.")
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


    ######################################################################

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