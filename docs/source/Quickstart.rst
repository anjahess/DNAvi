.. DNAvi documentation master file, created by
   sphinx-quickstart on Thu Jul 24 15:51:52 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Quickstart
===================



1. Open the termial
^^^^^^^^^^^^^^^^^^

Linux: **Ctrl+Alt+T**

MAC: **Launchpad -> Search Terminal -> Click on Terminal**

Windows: **Windows Symbol -> search cmd.exe -> Click cmd.exe**


2. Run DNAvi
^^^^^^^^^^^^^^^^^^

In this example we will run DNAvi on a test electropherogram signal table provided in this package:

.. code-block::

    python3 DNAvi.py -i electropherogram.csv -l ladder.csv -m meta.csv

* **electropherogram.csv**: the DNA signal table :download:`example <_static/electropherogram.csv>` .
* **ladder.csv**: DNA ladder annotation :download:`example <_static/ladder.csv>` .
* **meta.csv**: Metadata file DNA ladder annotation :download:`example <_static/metadata.csv>` .

To see all input options run:

.. code-block::

    python3 DNAvi.py --help


Which will result in a display of command line arguments with additional explanaitons:

.. code-block::

    Welcome to
      ____  _   _    _        _
     |  _ |  \ | |  / \__   _(_)
     | | | |  \| | / _ \ \ / / |
     | |_| | |\  |/ ___ \ V /| |
     |____/|_| \_/_/   \_\_/ |_|

    usage: DNAvi.py [-h] [-i [<input-file-or-folder>]] -l [<ladder-file>] [-m [<metadata-file>]] [-n [<run-name>]] [-incl]
                    [-ml <int>] [--verbose] [-v]

    Analyse Electropherogram data e.g. for cell-free DNA from liquid biopsies

    options:
      -h, --help            show this help message and exit
      -i [<input-file-or-folder>], --input [<input-file-or-folder>]
                            Path to electropherogram table file or image file OR directory containing those files. Accepted formats:
                            .csv/.png/.jpeg/.jpg or directory containing those.
      -l [<ladder-file>], --ladder [<ladder-file>]
                            Path to ladder table file. Accepted format: .csv
      -m [<metadata-file>], --meta [<metadata-file>]
                            Path to metadata table file containing grouping information for input file (e.g. age, sex, disease).
                            Accepted format: .csv
      -n [<run-name>], --name [<run-name>]
                            Name of your run/experiment. Will define output folder name
      -incl, --include      Include marker bands into analysis and plotting.
      -ml <int>, --marker_lane <int>
                            Change the lane selected as the DNA marker/ladder, default is first lane (1)
      --verbose             increase output verbosity
      -v, --version         show program's version number and exit

    Version: 0.1, created by Anja Hess <anja.hess@mail.de>, MPIMG