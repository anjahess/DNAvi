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
import argparse
from src.data_checks import check_input, check_ladder, check_meta, check_name, check_marker_lane, check_config
from src.analyze_electrophero import epg_analysis
from src.constants import ACCEPTED_FORMATS
from src.analyze_gel import analyze_gel
#########################################################################
# Initiate Parser
#########################################################################
parser = argparse.ArgumentParser(description=
                                 'Analyse Electropherogram data '
                                 'e.g. for cell-free DNA from liquid biopsies',
                                 epilog=f"""Version: 0.1, created by 
                                 Anja Hess <anja.hess@mail.de>, MPIMG""")

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

parser.add_argument('-ml', '--marker_lane',
                    type=check_marker_lane,
                    metavar='<int>',
                    default=1,
                    help='Change the lane selected as the DNA marker/ladder, '
                         'default is first lane (1). Using this will force to use the '
                         'specified column even if other columns are called Ladder already.',
                    required=False)

parser.add_argument("--verbose", help="increase output verbosity",
                    action="store_true")

parser.add_argument('-v', '--version', action='version', version="v0.1")

#########################################################################
# Args to variables
#########################################################################
args = parser.parse_args()
save_dir = None
csv_path, ladder_path, meta_path, run_id, marker_lane = args.input, args.ladder, args.meta, args.name, args.marker_lane
marker_lane = marker_lane - 1 #transfer to 0-based format

#########################################################################
# Decide: folder or single file processing
#########################################################################
if os.path.isdir(csv_path):
    print(f"--- Checking folder {csv_path}")
    files_to_check = [f"{csv_path}{e}" for e in os.listdir(csv_path) if
                      e.endswith(tuple(ACCEPTED_FORMATS))]
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
        signal_table, save_dir, error = analyze_gel(file, run_id=run_id,
                                                    marker_lane=marker_lane)
        image_input = True
        if error:
            print(error)
            exit(1)
    else:
        # FILE ALREADY IN SIGNAL TABLE FORMAT
        signal_table = file
        image_input = False

    # Start analysis
    epg_analysis(signal_table, ladder_path, meta_path, run_id=run_id,
                 include_marker=args.include, image_input=image_input,
                 save_dir=save_dir, marker_lane=marker_lane,
                 nuc_dict=nuc_dict)

print("")
print("--- DONE. Results in same folder as input file.")
# END OF SCRIPT
