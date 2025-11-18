"""

Command line interface tool for cell-free DNA fragment trace analysis with DNAvi.

Author: Anja Hess
Date: 2023-AUG-01

"""

logo=r"""Welcome to
  ____  _   _    _        _
 |  _ |  \ | |  / \__   _(_)
 | | | |  \| | / _ \ \ / / |
 | |_| | |\  |/ ___ \ V /| |
 |____/|_| \_/_/   \_\_/ |_| 
 """
print(logo)
import os
import glob
import argparse
import logging
import datetime
from src.data_checks import (check_input, check_ladder, check_meta, check_name,
                             check_marker_lane, check_config, check_interval,
                             generate_meta_dict)
from src.analyze_electrophero import epg_analysis, merge_tables
from src.constants import ACCEPTED_FORMATS, NUC_DICT, LOGFILE_NAME
from src.analyze_gel import analyze_gel

#########################################################################
# Initiate Logging (save to working dir)
#########################################################################
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename=f'{os.getcwd()}/{LOGFILE_NAME}',
                    filemode='w', force=True)
logging.info(f"--- RUN STARTED, {datetime.datetime.now()}")

#########################################################################
# Initiate Parser
#########################################################################
parser = argparse.ArgumentParser(description=
                                 'Analyse Electropherogram data '
                                 'e.g. for cell-free DNA from liquid biopsies',
                                 epilog=f"""Version: 0.2, created by 
                                 Anja Hess <github.com/anjahess>.""")

#########################################################################
# Add arguments
#########################################################################
parser.add_argument('-i', '--input',
                    type=check_input,
                    metavar='<input-file-or-folder>',
                    nargs='?', #single file
                    help='Path to electropherogram table file or image '
                         'file OR directory containing those files. '
                         'Accepted formats: .csv/.png/.jpeg/.jpg '
                         'or directory containing those.')

parser.add_argument('-l', '--ladder',
                    type=check_ladder,
                    metavar='<ladder-file>',
                    nargs='?', #single file
                    help='Path to ladder table file. Accepted format: '
                         '.csv',
                    required=True)

parser.add_argument('-m', '--meta',
                    type=check_meta,
                    metavar='<metadata-file>',
                    nargs='?', #single file
                    help='Path to metadata table file containing grouping '
                         'information for input file (e.g. age, sex, '
                         'disease). Accepted format: .csv',
                    required=False)

parser.add_argument('-n', '--name',
                    type=check_name,
                    metavar='<run-name>',
                    nargs='?', #single file
                    help='Name of your run/experiment. '
                         'Will define output folder name',
                    required=False)

parser.add_argument('-incl', '--include',
                    action="store_true",
                    default=False,
                    help='Include marker bands into analysis and plotting.',
                    required=False)

parser.add_argument('-un', '--unnormalized',
                    action="store_true",
                    default=False,
                    help='Do not perform min/max normalization. '
                         'ATTENTION: will be DNA-concentration sensitive.',
                    required=False)

parser.add_argument('-nt', '--normalize_to',
                    type=check_name,
                    metavar='<sample_name>',
                    nargs='?',
                    help='Name of the sample to normalize all values to.',
                    required=False)

parser.add_argument('-ml', '--marker_lane',
                    type=check_marker_lane,
                    metavar='<int>',
                    default=1,
                    help='Change the lane selected as the DNA marker/ladder, '
                         'default is first lane (1). Using this will force to use the '
                         'specified column even if other columns are called Ladder already.',
                    required=False)

parser.add_argument('-c', '--config',
                    type=check_config,
                    metavar='<config-file>',
                    nargs='?',  # single file
                    help='Path to configuration file containing custom '
                         '(nucleosome) intervals for statistics. '
                         'Accepted format: tab-separated text files (.txt)',
                    required=False)

parser.add_argument('-iv', '--interval',
                    type=check_interval,
                    metavar='<(start,step)>',
                    nargs='?',  # single file
                    help='Interval (start,step) for auto-generated nucleosomal '
                         'fractions',
                    required=False)

parser.add_argument('-p', '--paired',
                    action="store_true",
                    default=False,
                    help='Perform paired statistical testing')

parser.add_argument('-cor', '--correct',
                    action="store_true",
                    default=False,
                    help='Perform correction for samples with '
                         'highly variant concentrations (e.g., dilution series)')

parser.add_argument("--verbose", help="increase output verbosity",
                    action="store_true")

parser.add_argument('-v', '--version', action='version', version="v0.2")

#########################################################################
# Args to variables
#########################################################################
args = parser.parse_args()
save_dir = None
files_to_check = None
meta_dict = False
paired = False
normalize = True
normalize_to = False
correct = False
nuc_dict = NUC_DICT
csv_path, ladder_path, meta_path, run_id, marker_lane \
    = args.input, args.ladder, args.meta, args.name, args.marker_lane
marker_lane = marker_lane - 1 # transfer to 0-based format

if args.interval and args.config:
    print("Cannot use both interval and nuc_dict arguments.")
    exit(1)
if args.unnormalized and args.normalize_to:
    print("Cannot use both --unnormalized and --normalize_to.")
    exit(1)
if args.interval:
    nuc_dict = args.interval
if args.config:
    nuc_dict = args.config
if args.paired:
    paired = True
if args.unnormalized:
    normalize = False
if args.normalize_to:
    normalize_to = args.normalize_to
if args.correct:
    correct = args.correct
if args.correct and args.include:
    print("Cannot use both --include and --correct.")
    exit(1)
#########################################################################
# Decide: folder or single file processing
#########################################################################
if os.path.isdir(csv_path):
    if not csv_path.endswith("/"):
        csv_path = f"{csv_path}/"
    print(f"--- Checking folder {csv_path}")
    files_to_check = [f"{csv_path}{e}" for e in os.listdir(csv_path) if
                      e.endswith(tuple(ACCEPTED_FORMATS))]
    ######################################################################
    # Multi-file metadata handling
    ######################################################################
    meta_dict = generate_meta_dict(meta_path, files=files_to_check)

elif os.path.isfile(csv_path):
    files_to_check = [e for e in [csv_path] if
                      e.endswith(tuple(ACCEPTED_FORMATS))]
if not files_to_check:
    print(f"--- No valid file(s), only {ACCEPTED_FORMATS} accepted: "
          f"{csv_path}")
    exit(1)

#########################################################################
# Start the analysis
#########################################################################
for file in files_to_check:
    # Optional: transform from image
    if not file.endswith(".csv"):
        # IMAGES GO HERE, then defines save_dir
        signal_table, save_dir = analyze_gel(file, run_id=run_id,
                                            marker_lane=marker_lane)
        image_input = True
    else:
        # FILE ALREADY IN SIGNAL TABLE FORMAT
        signal_table = file
        image_input = False

    if meta_dict:
        meta_path = meta_dict[file]

    # Start analysis
    epg_analysis(signal_table, ladder_path, meta_path, run_id=run_id,
                 include_marker=args.include, image_input=image_input,
                 save_dir=save_dir, marker_lane=marker_lane,
                 nuc_dict=nuc_dict, paired=paired, normalize=normalize,
                 normalize_to=normalize_to, correct=correct)

#########################################################################
# Merge the results (for multi-file processing)
#########################################################################
if len(files_to_check) > 1:
    # Get the all signal tables
    signal_tables = [file for file in glob.glob(csv_path+"/*/signal_table.csv")]
    merge_file = merge_tables(signal_tables, save_dir=csv_path+"merged.csv", meta_dict=meta_dict)
    # And analyze all together
    print("--- Multiple files - collecting & merging all results")
    epg_analysis(merge_file, ladder_path, meta_path, run_id=run_id,
                 include_marker=args.include, image_input=False,
                 save_dir=save_dir, marker_lane=marker_lane,
                 nuc_dict=nuc_dict, paired=paired, normalize=normalize,
                 normalize_to=normalize_to, correct=correct)

# END OF SCRIPT