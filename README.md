DNAvi: integration, analysis, and visualization of cell-free DNA fragment traces
===========


![DNA Image 1](static/workflow.png)


## 1. Description
DNAvi is an open-access software to integrate, analyze and visualize multiple cell-free DNA fragmentation profiles from liquid biopsies. It uses either gel images
or automated gel electrophoresis device output tables (electropherograms). The tool was tested on a 32 GB memory local PC on Ubuntu 24.04.2 LTS, as well as on Windows 10 and MAC-OS.

## 2. Installation

Please make sure you have installed **python => 3.12**. Next, download the required packages:

Python packages:

    pip install numpy pandas seaborn scipy matplotlib imageio scikit-image werkzeug scikit-posthocs

Conda:

    conda create --name dnavi numpy pandas seaborn scipy matplotlib imageio werkzeug scikit-image -y
    conda activate dnavi
    conda install conda-forge::scikit-posthocs -y

Next, download the repository.

Through *github CLI*:
    
    gh repo clone anjahess/DNAvi

Or through *wget*:

    wget https://github.com/anjahess/DNAvi/archive/refs/heads/main.zip

Unpack or move the DNAvi folder to your location of choice and you're ready to start.


## 3. Quick start

### 3.1 Open the termial

Linux: **Ctrl+Alt+T** \
MAC: **Launchpad -> Search Terminal -> Click on Terminal** \
Windows: **Windows Symbol -> search cmd.exe -> Click cmd.exe** 


### 3.2 Run DNAvi

In this example we will run DNAvi on a test electropherogram signal table provided in this package:

    cd DNAvi/
    python3 DNAvi.py -i tests/electropherogram.csv -l tests/ladder.csv -m tests/metadata.csv

This will result in the following output:
    
    Welcome to
      ____  _   _    _        _
     |  _ |  \ | |  / \__   _(_)
     | | | |  \| | / _ \ \ / / |
     | |_| | |\  |/ ___ \ V /| |
     |____/|_| \_/_/   \_\_/ |_| 
      
        DNA file: tests/electropherogram.csv      
        Ladder file: tests/ladder.csv
        Meta file: tests/metadata.csv

    ------------------------------------------------------------
               ELECTROPHEROGRAM DNA SIZE ANALYSIS
    ------------------------------------------------------------
         
            DNA file: tests/electropherogram.csv      
            Ladder file: tests/ladder.csv
            Meta file: None
    
    Saving results to: tests/results/
    
    ------------------------------------------------------------



... and additional infos depending on the analysis details. Once DNAvi is finished,
this message will appear:

You can now go to you results folder:
    
       ├── results
            ├── plots
            ├── stats
            └── qc

In the plots and stats folder, you will find various visualizations summarizing fragmentomic traces of your samples.


<p align="center">
<img src="static/example_cluster_condition.jpg" alt="Img_1" width="650">

<img src="static/plot_example_2.png" alt="Img_2" width="650">
</p>
In case you provided a metadata file, each category will result in its own plot. In the example below, the 27 samples stem from
two experiments, and we can see the integrated profile plot for each expeirment below:

<p align="center">
<img src="static/plot_example_1.png" alt="Img_3" width="450">
</p>

## 4. Multi-file input

If you have multiple gel images or csv files to process, just put them into a folder and point DNAvi to that folder: \
**! Attention:** Run together only files that have the **same DNA ladder**.

    python3 DNAvi.py -i /path/to/folder -l ladder.csv


## 5. Help and documentation


If you need help, simply run

    python3 DNAvi.py --help

Which will result in a display of command line arguments with additional explanaitons:


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


## 6. Citation

**Anja Hess<sup>1,2,3</sup>, Dominik Seelow<sup>1</sup>, and Helene Kretzmer<sup>2,4</sup>: 
DNAvi: Integration, statistics, and visualization of cell-free DNA fragment traces**
1. Center of Genomic Medicine, Berlin Institute of Health at Charité Universitätsmedizin Berlin, Berlin, Germany 
2. Max Planck Institute for Molecular Genetics, Berlin, Germany
3. Department of Biology, Chemistry and Pharmacy, Freie Universität Berlin, Berlin, Germany
4. Digital Health Cluster, Hasso Plattner Institute for Digital Engineering, Digital Engineering Faculty, University of Potsdam, Potsdam, Germany
