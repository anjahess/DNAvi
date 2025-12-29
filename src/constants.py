"""

Constants for electropherogram analysis

Author: Anja Hess

Date: 2023-AUG-06

"""

import logging

########################################################################################################################
# BAND DETECTION SETTINGS
########################################################################################################################
# Peak detection ladder
DISTANCE = 20 #pos apart min
"""Minimum required distance of two peaks to be discriminated."""
logging.info("--- DNAvi constants:", DISTANCE)

MIN_PEAK_HEIGHT_FACTOR=0.2
"""Factor by which to multiply the maximum peak height to set the minimum peak height to be detected. """
logging.info(MIN_PEAK_HEIGHT_FACTOR)

MAX_PEAK_WIDTH_FACTOR=1
"""Fraction of entire gel length to set the maximum accepted peak width - ONLY FOR THE LADDER, not for sample peaks"""
logging.info(MAX_PEAK_WIDTH_FACTOR)

PEAK_PROMINENCE=(0.2, None)
"""Tuple, minimum peak prominence """
logging.info(PEAK_PROMINENCE)

# Constants for basepair annotation
INTERPOLATE_FUNCTION="linear"
"""Function to interpolate missing base pair values based on user-annotated values """
logging.info(INTERPOLATE_FUNCTION)

BACKGROUND_SUBSTRACTION_STATS=0.1
logging.info(BACKGROUND_SUBSTRACTION_STATS)
"""Int, fraction of max peak to be removed from dataset for statistical testing \
higher -> lower sens but pot better discrimination, lower -> sens up, more noise """

HALO_FACTOR=0
logging.info(HALO_FACTOR)
"""Int, an optional addition to remove more base-pair positions if automatic marker cropping is either \
insufficient or if a smaller window of the DNA data shall be analysed. \
Default value is 0 (= no additional cropping, only auto-detection). \ 
It is suggested to start with values of 0.1 (will add 10% on top of the marker position)."""

ARTIFICIAL_MAX=100000
logging.info(ARTIFICIAL_MAX)
"""Int, artificial maximum base-pair position to interpolate positions beyond upper marker \
 or in cases where there is no upper marker."""

########################################################################################################################
# OTHER SETTINGS
########################################################################################################################

ACCEPTED_FORMATS = ['.csv', '.png', '.jpeg', '.jpg']
"""Possible input formats"""

LOGFILE_NAME = "dnavi.log"

YCOL = "normalized_fluorescent_units"
"""Standardized y axis name"""
XCOL = "bp_pos"
"""Standardized x axis name"""
YLABEL = "Sample Intensity [Normalized FU]"
"""Standardized y labe name"""
XLABEL = "Size [bp]"
"""Standardized x label name"""
XLABEL_PRIOR_SIZE= "Size"
"""Standardized x label name before interpolation"""
ALTERNATE_FORMAT = "svg"
"""The second format apart from .pdf to save images to"""

PALETTE = ["cadetblue","#fbc27b", "#d56763", "darkgrey","#a7c6c9", "#2d435b",
           "#d56763", "darkred", "#477b80", 'grey', "#d56763", "#bfcfcd", "#fbc27b", "#fbc27b", "#477b80",
           "#2d435b", 'lightslategrey',"#bfcfcd", "#2d435b", "#986960", "#f1e8d7", "#d56763",
           "#fcd2a1", "#477b80", "#bfcfcd", "#d56763", "#fcd2a1", "#477b80", "#2d435b", "#477b80", "#2d435b",
           "#986960", "#f1e8d7", "#d56763", "#fcd2a1", "#477b80", 'lightgrey', "lightblue", "#fbc27b",
           "#fbc27b", 'lightslategrey', "#85ada3", "#d56763", "#fcd2a1", "#477b80", "#bfcfcd",
           "#2d435b", "#986960", "#f1e8d7", "#d56763", "#fcd2a1", "#477b80"]
"""Standardized color palette"""

LADDER_DICT = {"HSD5000": [15, 100, 250, 400, 600,
                         1000, 1500, 2500, 3500, 5000,
                         10000],
               "gDNA": [100, 250, 400, 600, 900,
                      1200, 1500, 2000, 2500, 3000,
                      4000, 7000, 15000, 48500],
               "cfDNA": [35, 50, 75, 100, 150,
                       200, 300, 400, 500, 600,
                       700, 1000]}

"""Dictionary with standardized peak size options (beta)"""
# Step size = 200 bp (default) (excl < 100bp)
NUC_DICT = {"Mononucleosomal (100-200 bp)": (100,200),
            "Dinucleosomal (201-400 bp)":(201,400),
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
            "Short I (50-700 bp)":(50, 700),
            "Short II (100-400 bp)":(100, 400),
            "Long (> 401 bp)":(401,None),
            "potential gDNA (1-5kB)":(1001, 5000),
            "likely gDNA (>3.5kB)": (3501, None),
            "very likely gDNA (>5kB)":(5001, None),
            "very very likely gDNA (>8kB)":(8001, None),
            }

# Step size = 250 bp
NUC_DICT_250 = {"Mononucleosomal (100-250 bp)": (100,250),
            "Dinucleosomal (251-500 bp)":(251,500),
            "Trinucleosomal (501-750 bp)": (501,750),
            "Tetranucleosomal (751-1000 bp)": (751,1000),
            "Pentanucleosomal (1000-1250 bp)": (1001,1250),
            "Hexanucleosomal (1251-1500 bp)": (1251, 1500),
            "Heptanucleosomal (1501-1750 bp)": (1501, 1750),
            "Octanucleosomal (1751-2000 bp)": (1751, 2000),
            "Nonanucleosomal (2001-2250 bp)": (2001, 2250),
            "Decanucleosomal (=> 2250 bp)": (2250, None),
            "Polynucleosomal (=> 750 bp)": (751, None),
            "Non-mono (> 250 bp)": (251, None),
            "Oligo (> 1250 bp)": (1250, None),
            "Mitochondrial/TF":(None,100)
            }
"""Dictionary with standardized peak size options (beta)"""
