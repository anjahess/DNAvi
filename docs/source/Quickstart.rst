.. DNAvi documentation master file, created by
   sphinx-quickstart on Thu Jul 24 15:51:52 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Quickstart
===================


Go to the DNAvi directory
^^^^^^^^^^^^^^^^^^

Open your terminal:

.. code-block::

    Linux: **Ctrl+Alt+T**
    MAC: **Launchpad -> Search Terminal -> Click on Terminal**
    Windows: **Windows Symbol -> search cmd.exe -> Click cmd.exe**


Make sure you are within DNAvi - typing 'ls' should show you the package contents, e.g. **DNAvi.py**

.. code-block::

    cd path/to/DNAvi/
    ls
    >> DNAvi.py  docs  LICENSE  README.md  src  static  tests


Run DNAvi
^^^^^^^^^^^^^^^^^^

If you are in the right directory, you can run an example provided with the package (no downloads required).
Just type:

.. code-block::

    python3 DNAvi.py -i tests/electropherogram.csv -l tests/ladder.csv -m tests/metadata.csv

Alternatively, you can find all input files are provided here for download as well:

* **electropherogram.csv**: the DNA signal table :download:`example <_static/electropherogram.csv>` .
* **ladder.csv**: DNA ladder annotation :download:`example <_static/ladder.csv>` .
* **meta.csv**: Metadata file DNA ladder annotation :download:`example <_static/metadata.csv>` .



Watch DNAvi work
^^^^^^^^^^^^^^^^^^

Now you should receive the full DNAvi output providing details on the ongoing analysis. Wait for DNAvi to finish:




.. code-block::

    Welcome to
      ____  _   _    _        _
     |  _ |  \ | |  / \__   _(_)
     | | | |  \| | / _ \ \ / / |
     | |_| | |\  |/ ___ \ V /| |
     |____/|_| \_/_/   \_\_/ |_|

    --- Performing ladder check
    --- Performing metadata check

    ------------------------------------------------------------
               DNA FRAGMENT SIZE ANALYSIS
    ------------------------------------------------------------

            Image input: False
            DNA file: tests/electropherogram.csv
            Ladder file: tests/ladder.csv
            Meta file: tests/metadata.csv
            Include marker: False

             run_id: electropherogram
             results to: tests/electropherogram/
    ------------------------------------------------------------
            Loading signal table
    ------------------------------------------------------------
    --- Performing input check
         Ladder  Sample_1  Sample_2  Sample_3  Sample_4  Sample_5  ...  Sample_19  Sample_20  Sample_21  Sample_25  Sample_26  Sample_27
    0  2.989603  2.427130  0.714618  6.358040  2.991041  1.130515  ...   2.076092   0.000427   0.832625   1.785758   5.907870  10.294200
    1  3.360477  2.020639  0.615121  6.315273  2.731391  0.929176  ...   2.227716   0.015034   0.920040   1.149061   8.089049   6.728103
    2  3.430417  1.893378  0.419766  5.906331  2.643009  0.395304  ...   2.125460   0.264249   1.067494   1.644679   7.602419   3.383577

    [3 rows x 25 columns]
    ------------------------------------------------------------
            Calculating basepair positions based on ladder
    ------------------------------------------------------------
    --- Ladder columns in data: 1 ---
    --- Ladder translations found: 1 : ['HSD5000'] ---
    --- Ladder #0: 11 peaks detected.
    ... Selecting HSD5000
    --- Checking for marker bands
    --- Found markers: [10000, 15]
    ------------------------------------------------------------
            Height-normalizing data and removing markers
    ------------------------------------------------------------
    --- Excluding marker peaks from analysis (factor: 0.35)
                bp_pos     sample  normalized_fluorescent_units
    0        31.313131   Sample_1                      0.452592
    1        32.171717   Sample_1                      0.398056
    2        33.030303   Sample_1                      0.351162
    3        33.888889   Sample_1                      0.311716
    4        34.747475   Sample_1                      0.280791
    ...            ...        ...                           ...
    11899  5897.435897  Sample_27                      0.000218
    11900  6025.641026  Sample_27                      0.000123
    11901  6153.846154  Sample_27                      0.000000
    11902  6282.051282  Sample_27                      0.000033
    11903  6410.256410  Sample_27                      0.000176

    [11904 rows x 3 columns]
    ------------------------------------------------------------
            Parsing metadata
    ------------------------------------------------------------
    --- WARNING: 24 samples but 27 metafile IDs.
    --- Adding metatadata for CONDITION
    ------------------------------------------------------------
            Performing statistical analysis
    ------------------------------------------------------------
    No peaks found for sample Sample_13.
    Ignoring this sample.
    --- Stats by CONDITION
    Skipping Kruskal stats since peak 8 only shows in one group of groups (['Cell type B'])with values: [[2373.2394366197186]]
    --- Not plotting [] (bp/frac = 0 for all samples)
    --- Plotting by sample
    --- Plotting by CONDITION
    ------------------------------------------------------------
            Plotting results
    ------------------------------------------------------------
    --- Plotting by CONDITION
    --- Sample grid plot

    --- DONE. Results in same folder as input file.


As you can see in the very end, DNAvi has sucessfully finished the analysis.


Check results
^^^^^^^^^^^^^^^^^^

Lets make sure outputs are created, we will look for the folder:

.. code-block::

    cd tests
    ls
    >> Lin_2018_cropped.jpg  Trinidad_2023.jpg  electropherogram.csv  ladder.csv		    metadata.csv      metadata_suzawa.csv
    >> Suzawa_2017.png       electropherogram	 gel.png	       ladder_lin_and_trinidad.csv  metadata_lin.csv  metadata_trinidad.csv

We can see the new folder *electropherogram* was created ...

.. code-block::

    cd electropherogram
    ls
    plots  qc  stats
    tree
    >> ├── plots
    >> │   ├── all_samples.pdf
    >> │   ├── all_samples_by_CONDITION.pdf
    >> │   ├── all_samples_summary.pdf
    >> │   ├── cluster_by_CONDITION.pdf
    >> │   └── sourcedata.csv
    >> ├── qc
    >> │   ├── 0_interpolated.pdf
    >> │   ├── bp_translation.csv
    >> │   ├── info.csv
    >> │   ├── interpolated.csv
    >> │   ├── peaks_0_0.pdf
    >> │   └── peaks_all_interpolated.pdf
    >> └── stats
    >>     ├── basic_statistics.csv
    >>     ├── group_statistics_by_CONDITION.csv
    >>     ├── peak_statistics.csv
    >>     ├── peak_statistics_CONDITION.pdf
    >>     └── peak_statistics_sample.pdf


... and contains the 3 result directories. You can explore them by yourself or consultate :doc:`/Outputs` for more details.


Command line help
^^^^^^^^^^^^^^^^^^^^^^^^

To see all DNAvi commands run:

.. code-block::

    python3 DNAvi.py --help


This will result in a display of command line arguments with additional explanaitons:

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


Use a gel image as input
^^^^^^^^^^^^^^^^^^^^^^^^

You can start the analysis from a gel image as well. We provide an example in the tests/ directory that
comes with downloading DNAvi. Simply type:

.. code-block::

    python3 DNAvi.py -i tests/gel.png -l tests/ladder.csv -m tests/metadata_gel.csv


Watch DNAvi work:

.. code-block::

        Welcome to
      ____  _   _    _        _
     |  _ |  \ | |  / \__   _(_)
     | | | |  \| | / _ \ \ / / |
     | |_| | |\  |/ ___ \ V /| |
     |____/|_| \_/_/   \_\_/ |_|

    --- Performing ladder check
    --- Performing metadata check
    ------------------------------------------------------------
            Loading image for signal table generation
    ------------------------------------------------------------

    ------------------------------------------------------------
               DNA FRAGMENT SIZE ANALYSIS
    ------------------------------------------------------------

            Image input: True
            DNA file: tests/hlo-gel/signal_table.csv
            Ladder file: tests/ladder.csv
            Meta file: tests/metadata_gel.csv
            Include marker: False

             run_id: signal_table
             results to: /./DNAvi/tests/hlo-gel/
    ------------------------------------------------------------
            Loading signal table
    ------------------------------------------------------------
    --- Performing input check
         Ladder         1         2         3         4
    0  0.231248  0.077621  0.054479  0.066294  0.066193
    1  0.252772  0.089723  0.063269  0.075393  0.074656
    2  0.289584  0.110746  0.079725  0.092882  0.089840
    ------------------------------------------------------------
            Calculating basepair positions based on ladder
    ------------------------------------------------------------
    --- Ladder columns in data: 1 ---
    --- Ladder translations found: 1 : ['HSD5000'] ---
    --- Ladder #0: 11 peaks detected.
    ... Selecting HSD5000
    --- Checking for marker bands
    --- Found markers: [10000, 15]
    ------------------------------------------------------------
            Height-normalizing data and removing markers
    ------------------------------------------------------------
    --- Excluding marker peaks from analysis (factor: 0.35)
               bp_pos sample  normalized_fluorescent_units
    0       31.117611      1                      0.216739
    1       31.556239      1                      0.209807
    2       31.993652      1                      0.201972
    3       32.429849      1                      0.192685
    4       32.864831      1                      0.183947
    ...           ...    ...                           ...
    1591  5878.676510      4                      0.011366
    1592  6005.916862      4                      0.016435
    1593  6137.025167      4                      0.020189
    1594  6272.001426      4                      0.021767
    1595  6410.845637      4                      0.023694

    [1596 rows x 3 columns]
    ------------------------------------------------------------
            Parsing metadata
    ------------------------------------------------------------
    --- WARNING: Image - ONLY first 4 entries used (out of 4)
    --- Adding metatadata for CONDITION
    {'1': 'Group A', '2': 'Group B', '3': 'Group A', '4': 'Group B'}
    ------------------------------------------------------------
            Performing statistical analysis
    ------------------------------------------------------------
    --- Stats by CONDITION
    --- Not plotting [] (bp/frac = 0 for all samples)
    --- Plotting by sample
    --- Plotting by CONDITION
    ------------------------------------------------------------
     Finished basic analysis and statistics in 12.800647258758545
    ------------------------------------------------------------
    ------------------------------------------------------------
            Plotting results
    ------------------------------------------------------------
    --- Plotting by sample
    --- Plotting by CONDITION
    --- Sample grid plot
    ------------------------------------------------------------
     Finished plotting in 22.0695583820343
    ------------------------------------------------------------

    --- DONE. Results in same folder as input file.


And check the results (here are a few examples of the output):


           .. image:: _static/GELEXAMPLE_profile.png

           .. image:: _static/GELEXAMPLE_samples.png

           .. image:: _static/GELEXAMPLE_cluster.png


Use a directory with multiple files as input
^^^^^^^^^^^^^^^^^^^^^^^^

Sometimes you may wish to run DNAvi on multiple images / signal tables without restarting
the analysis every single time. You do so by pointing DNAvi to the folder where your files are.
We provide an example, you can simply type:

.. code-block::

    python3 DNAvi.py -i tests/mutltifolder -l tests/ladder.csv -m tests/metadata_multi.csv


**Note**: If processing multiple files, your metadata file needs to specify the file name in a separate column.

:download:`Multi metadata example <_static/metadata_multi_full.csv>`

.. csv-table:: Example of a multi-file input DNAvi metadata file
   :file: _static/metadata_multi.csv
   :widths: 30, 30, 30
   :header-rows: 1


**Note**: To enjoy a smooth analysis, only put signal tables or images into the multi-input folder.


DNAvi will then go through your files and create the usual outputs for each file inside the multi-input folder.
On top of the interface there will be a short short message, indicating that your metafiles are parsed:

.. code-block::


    Welcome to
      ____  _   _    _        _
     |  _ |  \ | |  / \__   _(_)
     | | | |  \| | / _ \ \ / / |
     | |_| | |\  |/ ___ \ V /| |
     |____/|_| \_/_/   \_\_/ |_|

    --- Performing ladder check
    --- Performing metadata check
    --- Checking folder tests/multifolder/
    --- Getting metadata for gel3.jpg ---
    --- Getting metadata for gel1.png ---
    --- Getting metadata for gel2.png ---
