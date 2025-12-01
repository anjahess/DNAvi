[![DOI](https://zenodo.org/badge/1025068693.svg)](https://doi.org/10.5281/zenodo.17642352)

DNAvi: integration, analysis, and visualization of cell-free DNA fragment traces
===========


![DNA Image 1](static/workflow.png)


## 1. Description
DNAvi is an open-source software to integrate, analyze and visualize multiple cell-free DNA fragmentation profiles from liquid biopsies. It uses either gel images
or automated gel electrophoresis device output tables (electropherograms). The tool was tested on a 32 GB memory local PC on Ubuntu 24.04.2 LTS, as well as on Windows 10 and macOS.

## 2. Installation

### With pip (recommended)

    pip install dnavi

Done! You can move to Quick start.

### From github (alternative)

Please make sure you have installed **python ≥ 3.12**. Next, download the required packages:

Python packages:

    pip install numpy pandas seaborn scipy matplotlib imageio scikit-image werkzeug scikit-posthocs

Conda:

    conda create --name dnavi numpy pandas seaborn scipy matplotlib imageio werkzeug scikit-image -y
    conda activate dnavi
    conda install conda-forge::scikit-posthocs -y

Next, download the repository.

Through *https*:

    git clone https://github.com/anjahess/DNAvi.git

Through *github CLI*:
    
    gh repo clone anjahess/DNAvi

Or through *zip download*:

    Go to <Code> (top right), then click 'Download ZIP'.

Unpack or move the DNAvi folder to your location of choice and you're ready to start.
        

## 3. Quick start

### 3.1 Open the termial

Linux: **Ctrl+Alt+T** \
macOS: **Launchpad -> Search Terminal -> Click on Terminal** \
Windows: **Windows Symbol -> search cmd.exe -> Click cmd.exe** 


### 3.2 Run DNAvi

In this example we will run DNAvi on a test electropherogram signal table provided in this package:

    cd path/to/DNAvi/

Hint: to find where DNAvi is installed type "pip show dnavi".
    
    dnavi -i tests/electropherogram.csv -l tests/ladder.csv -m tests/metadata.csv

Or, if you installed from github:

    

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

    dnavi -i /path/to/folder -l ladder.csv


## 5. Help and documentation


If you need help, simply run

    dnavi --help


Which will result in a display of command line arguments with additional explanaitons:


    Welcome to
      ____  _   _    _        _
     |  _ |  \ | |  / \__   _(_)
     | | | |  \| | / _ \ \ / / |
     | |_| | |\  |/ ___ \ V /| |
     |____/|_| \_/_/   \_\_/ |_| 
     
    usage: DNAvi.py [-h] [-i [<input-file-or-folder>]] -l [<ladder-file>] [-m [<metadata-file>]] [-n [<run-name>]] [-c [<config-file>]] [-iv [<(start,step)>]]
                    [-p] [-un] [-nt [<sample_name>]] [-ml <int>] [-incl] [-cor] [--verbose] [-v]
    
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



## 6. Acknowledgements

Special thanks to [Yara Matani](https://github.com/yaramt) and [Philine Guckelberger](https://github.com/philinegu) for testing DNAvi!

## 7. Citation

**Anja Hess<sup>1,2,3</sup>, Dominik Seelow<sup>1</sup>, and Helene Kretzmer<sup>2,4</sup>: 
DNAvi: Integration, statistics, and visualization of cell-free DNA fragment traces (2025).**
1. Center of Genomic Medicine, Berlin Institute of Health at Charité Universitätsmedizin Berlin, Berlin, Germany 
2. Max Planck Institute for Molecular Genetics, Berlin, Germany
3. Department of Biology, Chemistry and Pharmacy, Freie Universität Berlin, Berlin, Germany
4. Digital Health Cluster, Hasso Plattner Institute for Digital Engineering, Digital Engineering Faculty, University of Potsdam, Potsdam, Germany
