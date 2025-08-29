"""

Constants for electropherogram analysis

Author: Anja Hess

Date: 2023-AUG-06

"""

########################################################################################################################
# BAND DETECTION SETTINGS
########################################################################################################################
# Peak detection ladder
DISTANCE = 20 # 20 pos apart min
"""Minimum required distance of two peaks to be discriminated."""

MIN_PEAK_HEIGHT_FACTOR=0.2
"""Factor by which to multiply the maximum peak height to set the minimum peak height to be detected. """

MAX_PEAK_WIDTH_FACTOR=1
"""Fraction of entire gel length to set the maximum accepted peak width - ONLY FOR THE LADDER, not for sample peaks"""

PEAK_PROMINENCE=(0.2, None)
"""Tuple, minimum peak prominence """

# Constants for basepair annotation
INTERPOLATE_FUNCTION="quadratic"
"""Function to interpolate missing base pair values based on user-annotated values """

BACKGROUND_SUBSTRACTION_STATS=0.1
"""Int, fraction of max peak to be removed from dataset for statistical testing \
higher -> lower sens but pot better discrimination, lower -> sens up, more noise """

# Marker band cropping
HALO_FACTOR=0.35 # factor to calc bp to crop from markers
"""Float [0-1] factor by which the marker will be multiplied to define cropping range when removing marker peaks"""


########################################################################################################################
# OTHER SETTINGS
########################################################################################################################

ACCEPTED_FORMATS = ['.csv', '.png', '.jpeg', '.jpg']
"""Possible input formats"""

YCOL = "normalized_fluorescent_units"
"""Standardized y axis name"""
XCOL = "bp_pos"
"""Standardized x axis name"""
YLABEL = "Sample Intensity [Normalized FU]"
"""Standardized y labe name"""
XLABEL = "Size [bp]"
"""Standardized x label name"""

PALETTE = ["cadetblue","#fbc27b", "#d56763", "darkgrey", "#85ada3", "#eacdcb", "#a7c6c9", "#2d435b",
           "#d56763", "darkred", "#477b80", 'grey', "#d56763", "#bfcfcd", "#fbc27b", "#fbc27b", "#477b80",
           "#2d435b", 'lightslategrey',  "#eacdcb", "#bfcfcd", "#2d435b", "#986960", "#f1e8d7", "#d56763",
           "#fcd2a1", "#477b80", "#bfcfcd", "#d56763", "#fcd2a1", "#477b80", "#2d435b", "#477b80", "#2d435b",
           "#986960", "#f1e8d7", "#d56763", "#fcd2a1", "#477b80", 'lightgrey', "lightblue", "#fbc27b",
           "#fbc27b", 'lightslategrey', "#85ada3", "#d56763", "#fcd2a1", "#477b80", "#eacdcb", "#bfcfcd",
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

# Step size = 250 bp
NUC_DICT = {"Mononucleosomal (100-250 bp)": (100,250),
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
            }
"""Dictionary with standardized peak size options (beta)"""
