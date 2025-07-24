"""

CMD interface for electropherogram analysis.

Input: raw electropherogram csv file. In the same directory
you can add a meta file (name_of_csv + "_meta.csv") explaining the conditions.

Usage: python3 DNAvi.py /path/to/csv
# Alias dnaint: dnaint /home/anja/Documents/projects/mpi/5_lab/3_project/
liquid_bio/x_results/2_manuscript/nextcloud/v5/00_Electros/Electropherogram.csv
@author: Anja Hess
@date: 2023-JUL-01

"""

print(r"""Welcome to
  ____  _   _    _        _
 |  _ |  \ | |  / \__   _(_)
 | | | |  \| | / _ \ \ / / |
 | |_| | |\  |/ ___ \ V /| |
 |____/|_| \_/_/   \_\_/ |_| 
 """)

import os
import argparse
from src.data_checks import check_input, check_ladder, check_meta, check_name
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
                                 Anja Hess <anja.hess@mail.de>, 
                                 Max Planck Institute for Molecular Genetics, 
                                 Berlin, GERMANY""")

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

parser.add_argument("--verbose", help="increase output verbosity",
                    action="store_true")

args = parser.parse_args()

#########################################################################
# Args to variables
#########################################################################
csv_path, ladder_path, meta_path = args.input, args.ladder, args.meta

#########################################################################
# Decide for folder or single file processing
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
    if file.endswith(".csv"):
        epg_analysis(file, ladder_path, meta_path, run_id=args.name)
    else:
        dna_file_from_image, error = analyze_gel(file, run_id=args.name)
        if not error:
            error = epg_analysis(dna_file_from_image, ladder_path, meta_path
                                 , run_id=args.name)
        else:
            print(error)
print("")
print("--- DNA fragmentation analysis DONE. Results in same folder as your input file.")
# END OF SCRIPT
