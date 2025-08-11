"""

Constants for electropherogram analysis

Author: Anja Hess

Date: 2023-AUG-06

"""


ACCEPTED_FORMATS = ['.csv', '.png', '.jpeg', '.jpg']
"""Possible input formats"""

# Peak detection ladder
DISTANCE = 20 # 20 pos apart min
"""Minimum required distance of two peaks to be discriminated."""

CUSTOM_MIN_PEAK_HEIGHT=50 # if not auto-calc, requires ladder type to be set to "adjust"
"""Minimum required height for a peak to be detected. """

PEAK_PROMINANCE=(0.2, None)
"""Tuple, minimum peak prominence """


# Marker band cropping
HALO_FACTOR=0.3 # factor to calc bp to crop from markers
"""Float [0-1] factor by which the marker will be multiplied to define cropping range when removing marker peaks"""

YCOL = "normalized_fluorescent_units"
"""Standardized y axis name"""
XCOL = "bp_pos"
"""Standardized x axis name"""
YLABEL = "Sample Intensity [Normalized FU]"
"""Standardized y labe name"""
XLABEL = "Size [bp]"
"""Standardized x label name"""

PALETTE = ["darkgrey", "#d56763", "#fcd2a1",
                "#85ada3", "#eacdcb", "#a7c6c9", "#2d435b",
                "#d56763", "darkred", "#477b80", 'grey', "#d56763", "#bfcfcd",
                "#fbc27b", "cadetblue", "#fbc27b","#477b80", "#2d435b",
                'lightslategrey',  "#eacdcb", "#bfcfcd", "#2d435b",
                "#986960", "#f1e8d7", "#d56763", "#fcd2a1", "#477b80", "#bfcfcd", "#d56763", "#fcd2a1", "#477b80",
                "#2d435b", "#477b80", "#2d435b", "#986960", "#f1e8d7", "#d56763", "#fcd2a1", "#477b80", 'lightgrey',
                "lightblue", "#fbc27b", "cadetblue", "#fbc27b", 'lightslategrey', "#85ada3", "#d56763", "#fcd2a1",
                "#477b80", "#eacdcb", "#bfcfcd", "#2d435b", "#986960", "#f1e8d7", "#d56763", "#fcd2a1", "#477b80",
                "#986960", "#f1e8d7", "#d56763", "#fcd2a1", "#477b80", "#bfcfcd", "#d56763", "#fcd2a1", "#477b80",
                "#2d435b", "#477b80", "#2d435b", "#986960", "#f1e8d7", "#d56763", "#fcd2a1", "#477b80", 'lightgrey',
                "lightblue", "#fbc27b", "cadetblue", "#fbc27b", 'lightslategrey', "#85ada3", "#d56763", "#fcd2a1",
                "#477b80", "#eacdcb", "#bfcfcd", "#2d435b", "#986960", "#f1e8d7", "#d56763", "#fcd2a1", "#477b80",
                ]
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
NUC_DICT = {"Mononucleosomal (1)": (100,250),
            "Dinucleosomal (2)":(251,500),
            "Trinucleosomal (3)": (501,750),
            "Quatronucleosomal (4)": (751,1000),
            "Pentanucleosomal (5)": (1001,1250),
            "Hexanucleosomal (6)": (1251, 1500),
            "Heptanucleosomal (7)": (1501, 1750),
            "Octanucleosomal (8)": (1751, 2000),
            "Nonanucleosomal (9)": (2001, 2250),
            "=> Hexanucleosomal (10)": (2250, None),
            "Polynucleosomal (=> 3)": (751, None),
            }
"""Dictionary with standardized peak size options (beta)"""
