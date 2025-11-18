Nucleosomal fractions
===================


Per default, DNAvi computes cfDNA content based on fixed size ranges.


Default fractions
^^^^^^^^^^^^^^^^^^

Default fractions are fixated in a **python dictionary instance** in the **constants.py** file (see API).

.. code-block::

    NUC_DICT = {"Mononucleosomal (100-200 bp)": (100,200),
                "Dinucleosomal (201-400 bp)": (201,400),
                "Trinucleosomal (401-600 bp)": (401,600),
                "Tetranucleosomal (601-800 bp)": (601,800),
                "Pentanucleosomal (801-1000 bp)": (801,1000),
                "Hexanucleosomal (1001-1200 bp)": (1001, 1200),
                "Heptanucleosomal (1201-1400 bp)": (1201, 1400),
                "Octanucleosomal (1401-1600 bp)": (1401, 1600),
                "Nonanucleosomal (1601-1800 bp)": (1601, 1800),
                "Decanucleosomal (1801-2000 bp)": (1801, 2000),
                "Polynucleosomal (2001-7000 bp)": (2001, 7000),
                "Non-mono (> 250 bp)": (251, None),
                "Oligo (> 1250 bp)": (1250, None),
                "Mitochondrial/TF":(None,100),
                "Short (100-400 bp)":(100,400),
                "Long (> 401 bp)":(401,None),
                "Short ~cfDNA (50-700 bp)":(50, 700),
                "potential gDNA (1-5kB)":(1001, 5000),
                "likely gDNA (>3.5kB)": (3501, None),
                "very likely gDNA (>5kB)":(5001, None),
                "very very likely gDNA (>8kB)":(8001, None),
                }


Customizing fractions
^^^^^^^^^^^^^^^^^^

If you wish to customize these ranges, you have two options:




Option 1: Config file
""""""""""""""""""""""""""

You will just need to specify the path to the config file when submitting an analysis with **- - config**

.. code-block::

      -c [<config-file>], --config [<config-file>]
                            Define nucleosomal fractions with this path to a configuration file containing custom (nucleosome) intervals for statistics.
                            Accepted format: tab-separated text files (.txt)



Here's an example for a config file:


.. csv-table:: Example of a custom file for nucleosomal fractions
   :file: _static/nucleosomal_fractions.csv
   :widths: 30, 30, 30
   :header-rows: 1


:download:`Config file example <_static/nucleosomal_fractions.txt>`





Option 2: Setting an interval
""""""""""""""""""""""""""


If you want to quickly test intervals (and avoid typing in small changes into the config file), you can tell DNAvi to compute the ranges for you.
They will be *saved to the log file* and *displayed in the terminal*.


.. code-block::

      -iv [<(start,step)>], --interval [<(start,step)>]
      Auto-generate nucleosomal size intervals by providing (start,step), e.g. start at 100 and increase by 200 bp


As an example we chose a random paradigm of starting at 300 bp and increasing in (unreasonably large) step sizes of 2kB.

.. code-block::

    python3 DNAvi.py -i tests/gel.png -l tests/ladder.csv -m tests/metadata_gel.csv -iv 300,2000


This will trigger DNAvi to output new intervals:

.. code-block::

    Welcome to
      ____  _   _    _        _
     |  _ |  \ | |  / \__   _(_)
     | | | |  \| | / _ \ \ / / |
     | |_| | |\  |/ ___ \ V /| |
     |____/|_| \_/_/   \_\_/ |_|

    --- Performing ladder check
    --- Performing metadata check
    --- Performing interval check
    --- Computing nucleosomal intervals from 300 bp in steps of 2000 bp.
    Mono 301 2300
    Di 2301 4300
    Tri 4301 6300
    Tetra 6301 8300
    Penta 8301 10300
    Hexa 10301 12300
    Hepta 12301 14300
    Octa 14301 16300
    Nona 16301 18300
    Deca 18301 20300



Please note that the names are not necessarily matching biological meaning - this option is really rather for quickly determining the interval sizes you need. We recommend to fixate them into a proper config file (see above), once you found ranges that work for you.
