"""

Constants for electropherogram analysis.
@author: Anja Hess
@date: 2023-JUL-01

"""


ACCEPTED_FORMATS = ['.csv', '.png', '.jpeg', '.jpg']

# Peak detection ladder
DISTANCE = 20 # 20 pos apart min
CUSTOM_MIN_PEAK_HEIGHT=50 # if not auto-calc, requires ladder type to be set to "adjust"
PEAK_PROMINANCE=(0.2, None)

# Marker band cropping
HALO_FACTOR=0.4 # factor to calc bp to crop from markers

YCOL = "normalized_fluorescent_units"
XCOL = "bp_pos"
YLABEL = "Sample Intensity [Normalized FU]"
XLABEL = "Size [bp]"


palettediff3 = ["darkgrey", "black", "grey",
                "#d56763", "#85ada3", "#2d435b", "#eacdcb", "#fcd2a1",
                "#d56763", "darkred", "#477b80", 'grey', "#d56763", "#bfcfcd",
                "#fbc27b", "cadetblue", "#fbc27b","#477b80", "#2d435b",
                'lightslategrey',  "#eacdcb", "#bfcfcd", "#2d435b",
                "#986960", "#f1e8d7", "#d56763", "#fcd2a1", "#477b80", "#bfcfcd", "#d56763", "#fcd2a1", "#477b80",
                "#2d435b", "#477b80", "#2d435b", "#986960", "#f1e8d7", "#d56763", "#fcd2a1", "#477b80", 'lightgrey',
                "lightblue", "#fbc27b", "cadetblue", "#fbc27b", 'lightslategrey', "#85ada3", "#d56763", "#fcd2a1",
                "#477b80", "#eacdcb", "#bfcfcd", "#2d435b", "#986960", "#f1e8d7", "#d56763", "#fcd2a1", "#477b80", ]

palettediff2 = ["darkgrey", "#d56763", "#fcd2a1",
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

peak_dict = {"HSD5000": [15, 100, 250, 400, 600,
                         1000, 1500, 2500, 3500, 5000,
                         10000],
             "gDNA": [100, 250, 400, 600, 900,
                      1200, 1500, 2000, 2500, 3000,
                      4000, 7000, 15000, 48500],
             "cfDNA": [35, 50, 75, 100, 150,
                       200, 300, 400, 500, 600,
                       700, 1000]}
