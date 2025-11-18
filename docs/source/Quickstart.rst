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

    Linux: Ctrl+Alt+T
    MAC: Launchpad -> Search Terminal -> Click on Terminal
    Windows: Windows Symbol -> search cmd.exe -> Click cmd.exe


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
* **ladder.csv**: DNA size marker annotation :download:`example <_static/ladder.csv>` .
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
             results to: /.../DNAvi/tests/electropherogram/
    ------------------------------------------------------------
            Loading signal table
    ------------------------------------------------------------
    --- Performing input check
         Ladder  Sample_1  Sample_2  Sample_3  Sample_4  Sample_5  Sample_6  ...  Sample_18  Sample_19  Sample_20  Sample_21  Sample_25  Sample_26  Sample_27
    0  2.989603  2.427130  0.714618  6.358040  2.991041  1.130515  0.903835  ...   0.000000   2.076092   0.000427   0.832625   1.785758   5.907870  10.294200
    1  3.360477  2.020639  0.615121  6.315273  2.731391  0.929176  1.303182  ...   0.022654   2.227716   0.015034   0.920040   1.149061   8.089049   6.728103
    2  3.430417  1.893378  0.419766  5.906331  2.643009  0.395304  1.732408  ...   0.254736   2.125460   0.264249   1.067494   1.644679   7.602419   3.383577

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
            Height-normalizing data: True
            Keeping markers: False
    ------------------------------------------------------------
    --- Auto-detected marker cropping borders: 66.51515151515152 and 5256.410256410257
    ------------------------------------------------------------
            Parsing metadata
    ------------------------------------------------------------
    --- WARNING: 24 samples but 27 metafile IDs.
    --- Adding metatadata for CONDITION
    ------------------------------------------------------------
            Performing statistical analysis
    ------------------------------------------------------------
    --- Nucleosomal fractions & peak analysis
    --- Stats by CONDITION
    --- Entropy - Mann Whitney U - test (independent): p = 0.0,  (SIGNIFICANT)
    --- Skewness - Mann Whitney U - test (independent): p = 0.0,  (SIGNIFICANT)
    --- AUC (total) - Mann Whitney U - test (independent): p = 0.0,  (SIGNIFICANT)
    --- Mononucleosomal (100-200 bp) - Student's t - test (independent) unequal variance): p = 0.0,  (SIGNIFICANT)
    --- Dinucleosomal (201-400 bp) - Student's t - test (independent) assume equal variance): p = 0.0,  (SIGNIFICANT)
    --- Tetranucleosomal (601-800 bp) - Mann Whitney U - test (independent): p = 0.0,  (SIGNIFICANT)
    --- Pentanucleosomal (801-1000 bp) - Mann Whitney U - test (independent): p = 0.0,  (SIGNIFICANT)
    --- Hexanucleosomal (1001-1200 bp) - Mann Whitney U - test (independent): p = 0.0,  (SIGNIFICANT)
    --- Heptanucleosomal (1201-1400 bp) - Mann Whitney U - test (independent): p = 0.0,  (SIGNIFICANT)
    --- Octanucleosomal (1401-1600 bp) - Mann Whitney U - test (independent): p = 0.0,  (SIGNIFICANT)
    --- Nonanucleosomal (1601-1800 bp) - Mann Whitney U - test (independent): p = 0.0,  (SIGNIFICANT)
    --- Decanucleosomal (1801-2000 bp) - Mann Whitney U - test (independent): p = 0.0,  (SIGNIFICANT)
    --- Polynucleosomal (2001-7000 bp) - Mann Whitney U - test (independent): p = 0.0,  (SIGNIFICANT)
    --- Non-mono (> 250 bp) - Student's t - test (independent) unequal variance): p = 0.0,  (SIGNIFICANT)
    --- Oligo (> 1250 bp) - Mann Whitney U - test (independent): p = 0.0,  (SIGNIFICANT)
    --- Mitochondrial/TF - Mann Whitney U - test (independent): p = 0.0,  (SIGNIFICANT)
    --- Short (100-400 bp) - Student's t - test (independent) assume equal variance): p = 0.0,  (SIGNIFICANT)
    --- Long (> 401 bp) - Student's t - test (independent) unequal variance): p = 0.0,  (SIGNIFICANT)
    --- Tape %cfDNA (50-700 bp) - Student's t - test (independent) assume equal variance): p = 0.0,  (SIGNIFICANT)
    --- potential gDNA (1-5kB) - Mann Whitney U - test (independent): p = 0.0,  (SIGNIFICANT)
    --- average_size - Mann Whitney U - test (independent): p = 0.0,  (SIGNIFICANT)
    --- modal_size - Mann Whitney U - test (independent): p = 0.02,  (SIGNIFICANT)
    --- median_size - Mann Whitney U - test (independent): p = 0.0,  (SIGNIFICANT)
    --- max_peak - Mann Whitney U - test (independent): p = 0.0,  (SIGNIFICANT)
    Skipping Statistics since peak peak_2 only shows in one group of groups (['Cell type A'])with values: [[1542.25, 1456.52, 1369.57]]
    --- Plotting by sample
    --- Plotting by CONDITION
    ------------------------------------------------------------
     Finished basic analysis and statistics in 88.20970273017883
    ------------------------------------------------------------
    ------------------------------------------------------------
            Plotting results
    ------------------------------------------------------------
    --- Plotting by sample
    --- Plotting by CONDITION
    --- Sample grid plot
    ------------------------------------------------------------
     Finished plotting in 47.10104298591614
    ------------------------------------------------------------

    --- DONE. Results in same folder as input file.


As you can see in the very end, DNAvi has sucessfully finished the analysis.


Check results
^^^^^^^^^^^^^^^^^^

Lets make sure outputs are created, we will look for the folder:

.. code-block::

    cd tests
    ls
    >> electropherogram	 ...

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

... and contains the 3 result directories. You can explore them by yourself or consult :doc:`/Outputs` for more details.


Command line help
^^^^^^^^^^^^^^^^^^^^^^^^

To see all DNAvi commands run:

.. code-block::

    python3 DNAvi.py --help


This will result in a display of command line arguments with additional explanations:

.. code-block::

    Welcome to
      ____  _   _    _        _
     |  _ |  \ | |  / \__   _(_)
     | | | |  \| | / _ \ \ / / |
     | |_| | |\  |/ ___ \ V /| |
     |____/|_| \_/_/   \_\_/ |_|

    usage: DNAvi.py [-h] [-i [<input-file-or-folder>]] -l [<ladder-file>] [-m [<metadata-file>]] [-n [<run-name>]] [-incl] [-un] [-nt [<sample_name>]]
                    [-ml <int>] [-c [<config-file>]] [-iv [<(start,step)>]] [-p] [-cor] [--verbose] [-v]

    Analyse Electropherogram data e.g. for cell-free DNA from liquid biopsies

    options:
      -h, --help            show this help message and exit
      -i [<input-file-or-folder>], --input [<input-file-or-folder>]
                            Path to electropherogram table file or image file OR directory containing those files. Accepted formats: .csv/.png/.jpeg/.jpg or
                            directory containing those.
      -l [<ladder-file>], --ladder [<ladder-file>]
                            Path to ladder table file. Accepted format: .csv
      -m [<metadata-file>], --meta [<metadata-file>]
                            Path to metadata table file containing grouping information for input file (e.g. age, sex, disease). Accepted format: .csv
      -n [<run-name>], --name [<run-name>]
                            Name of your run/experiment. Will define output folder name
      -c [<config-file>], --config [<config-file>]
                            Define nucleosomal fractions with this path to a configuration file containing custom (nucleosome) intervals for statistics.
                            Accepted format: tab-separated text files (.txt)
      -iv [<(start,step)>], --interval [<(start,step)>]
                            Auto-generate nucleosomal size intervals by providing (start,step), e.g. start at 100 and increase by 200 bp
      -p, --paired          Perform paired statistical testing
      -un, --unnormalized   Do not perform min/max normalization. ATTENTION: will be DNA-concentration sensitive.
      -nt [<sample_name>], --normalize_to [<sample_name>]
                            Name of the sample to normalize all values to. ATTENTION: will be DNA-concentration sensitive.
      -ml <int>, --marker_lane <int>
                            Change the lane selected as the DNA marker/ladder, default is first lane (1). Using this will force to use the specified column
                            even if other columns are called Ladder already.
      -incl, --include      Include marker bands into analysis and plotting.
      -cor, --correct       Perform advanced automatic marker lane detection in samples with highly variant concentrations (e.g., dilution series), so that
                            the marker borders will be determined for each sample individually
      --verbose             increase output verbosity
      -v, --version         show program's version number and exit

    Version: 0.2, created by Anja Hess <github.com/anjahess>.


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
            DNA file: tests/gel/signal_table.csv
            Ladder file: tests/ladder.csv
            Meta file: tests/metadata_gel.csv
            Include marker: False

             run_id: signal_table
             results to: /.../DNAvi/tests/gel/
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
            Height-normalizing data: True
            Keeping markers: False
    ------------------------------------------------------------
    --- Auto-detected marker cropping borders: 16.02409638554217 and 4531.25
    ------------------------------------------------------------
            Parsing metadata
    ------------------------------------------------------------
    --- WARNING: Image - ONLY first 4 entries used (out of 4)
    --- Adding metatadata for CONDITION
    {'1': 'Group A', '2': 'Group B', '3': 'Group A', '4': 'Group B'}
    ------------------------------------------------------------
            Performing statistical analysis
    ------------------------------------------------------------
    --- Nucleosomal fractions & peak analysis
    --- Stats by CONDITION
    --- Mononucleosomal (100-200 bp) - Student's t - test (independent) unequal variance): p = 0.03,  (SIGNIFICANT)
    --- Dinucleosomal (201-400 bp) - Student's t - test (independent) assume equal variance): p = 0.02,  (SIGNIFICANT)
    --- Heptanucleosomal (1201-1400 bp) - Student's t - test (independent) assume equal variance): p = 0.01,  (SIGNIFICANT)
    --- Octanucleosomal (1401-1600 bp) - Student's t - test (independent) unequal variance): p = 0.02,  (SIGNIFICANT)
    --- Decanucleosomal (1801-2000 bp) - Student's t - test (independent) unequal variance): p = 0.03,  (SIGNIFICANT)
    --- Oligo (> 1250 bp) - Student's t - test (independent) unequal variance): p = 0.04,  (SIGNIFICANT)
    --- Long (> 401 bp) - Student's t - test (independent) unequal variance): p = 0.03,  (SIGNIFICANT)
    --- Tape %cfDNA (50-700 bp) - Student's t - test (independent) unequal variance): p = 0.04,  (SIGNIFICANT)
    --- potential gDNA (1-5kB) - Student's t - test (independent) unequal variance): p = 0.03,  (SIGNIFICANT)
    --- short-to-long fragment ratio - Student's t - test (independent) unequal variance): p = 0.03,  (SIGNIFICANT)
    --- average_size - Student's t - test (independent) unequal variance): p = 0.03,  (SIGNIFICANT)
    --- median_size - Student's t - test (independent) unequal variance): p = 0.02,  (SIGNIFICANT)
    --- Plotting by sample
    --- Plotting by CONDITION
    ------------------------------------------------------------
     Finished basic analysis and statistics in 21.949937105178833
    ------------------------------------------------------------
    ------------------------------------------------------------
            Plotting results
    ------------------------------------------------------------
    --- Plotting by sample
    --- Plotting by CONDITION
    --- Sample grid plot
    ------------------------------------------------------------
     Finished plotting in 26.767568111419678
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

    python3 DNAvi.py -i tests/multifolder -l tests/ladder.csv -m tests/metadata_multi.csv


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
