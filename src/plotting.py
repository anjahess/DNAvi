"""

Plotting functions for electropherogram analysis.
@author: Anja Hess
@date: 2023-JUL-01

"""
import os
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
from src.constants import palettediff2

def set_style_for_paper():
    factor = 5
    ticks = 2
    lines = 0.5
    font = 0.6

    rc = {"boxplot.flierprops.markersize": 1,
          "boxplot.flierprops.markeredgewidth": font,
          "lines.linewidth": lines,
          "axes.linewidth": lines,
          "xtick.major.width": lines,
          "xtick.major.size": ticks,
          "xtick.minor.size": ticks,
          "ytick.major.width": lines,
          "ytick.major.size": ticks,
          "legend.frameon": False,
          "boxplot.meanprops.markersize": font,
          "legend.fontsize": font,
          "legend.title_fontsize": font,
          "legend.markerscale": 0.1,
          'figure.figsize': (11.7/factor, 8.27/factor)}
    sns.set(style="ticks", font_scale=font, rc=rc)
    return rc
    # END OF FUNCTION

def gridplot(df, x, y, save_dir="", title="", y_label="", x_label=""):
    """
    DNA size line plot with masking option for marker peaks

    :param df:
    :param x:
    :param y:
    :param save_dir:
    :param title:
    :param y_label:
    :param x_label:
    :return:
    """

    df[x] = df[x].astype(int)

    #####################################################################
    # All in one plot
    #####################################################################
    sns.lineplot(data=df, x=x, y=y, alpha=.7)
    plt.ylabel(y_label)
    plt.xlabel(x_label)
    plt.title(f"{title}")


    # Log scale
    plt.xscale('log')
    plt.savefig(f"{save_dir}{title}_summary.pdf", bbox_inches='tight')
    plt.close()
    cols_not_to_plot = ["bp_pos", "sample", "normalized_fluorescent_units"]

    for col in [c for c in df.columns if c not in cols_not_to_plot]:
        # Overview by condition
        print(f"--- Plotting by {col}")
        hue = col
        sns.lineplot(data=df, x=x, y=y, alpha=.7,
                     palette=palettediff2[:len(df[hue].unique())],
                     hue=hue)
        # Add labels
        plt.ylabel(y_label)
        plt.xlabel(x_label)
        plt.title(f"{title} by {col}")
        plt.xscale('log')
        plt.savefig(f"{save_dir}{title}_by_{col}.pdf",
                    bbox_inches='tight')
        plt.close()

    #####################################################################
    # 2. Plot
    #####################################################################
    print("--- Sample grid plot")
    hue="sample"
    g = sns.FacetGrid(df, col=hue, hue=hue, col_wrap=3, palette=palettediff2)
    g.map(sns.lineplot, x, y, alpha=.7)
    g.add_legend()

    # flatten axes into a 1-d array
    axes = g.axes.flatten()
    # iterate through the axes
    #for i, ax in enumerate(axes):
    #    ax.axvline(lower_marker, ls='--', c='black')
    #    ax.axvline(upper_marker, ls='--', c='black')
    # Add marker line
   # plt.xlim(lower_marker, upper_marker)

    # Add labels
    plt.ylabel(y_label)
    plt.xlabel(x_label)
    plt.suptitle(f"{title}")
    #if upper_marker > 1000:
    plt.xscale('log')
    plt.savefig(f"{save_dir}{title}.pdf")
    plt.close()
    # END OF FUNCTION

def peakplot(array, peaks, ladder_id, ref, i, qc_save_dir, y_label=""):
    """

    :param array:
    :param peaks:
    :param ladder_id:
    :param ref:
    :param i:
    :param qc_save_dir:
    :param y_label:
    :return:
    """
    plt.plot(array)
    plt.plot(peaks, array[peaks], "x")
    plt.plot(np.zeros_like(array), "--", color="gray")
    plt.title(ladder_id + f" {ref}")
    plt.xlim(10 ^ 0, None)
    plt.ylabel(y_label)
    plt.savefig(f"{qc_save_dir}peaks_{i}_{ref}.pdf")
    plt.close()
    # END OF FUNCTION


def lineplot(df, x, y, save_dir="", title="", y_label="", x_label="",
             hue=None, units=None, plot_lower=False, estimator="mean",
             style=None, window=False):
    """
    DNA size line plot

    :param df:
    :param x:
    :param y:
    :param save_dir:
    :param title:
    :param y_label:
    :param x_label:
    :param window: x lims
    :return:
    """

    #####################################################################
    # 1. Special settings
    #####################################################################
    if window:
        save_dir = save_dir + f"/window_{window[0]}-{window[1]}_bp/"
        os.makedirs(save_dir, exist_ok=True)
    if plot_lower:
        lower_xlim = 10 ^ 0
    else:
        lower_xlim = 40  # markers are < 40 bps exc. gDNA
    if units:
        estimator = None

    #####################################################################
    # 2. Plot
    #####################################################################
    fig, ax = plt.subplots()

    if hue is not None:
        n_cats = len(df[hue].unique())
        sns.lineplot(data=df, x=x, y=y, hue=hue,
                     palette=palettediff2[:n_cats], units=units,
                     estimator=estimator,
                     style=style)
    else:
        sns.lineplot(data=df, x=x, y=y, units=units,
                     estimator=estimator,
                     style=style)
    plt.title(f"{title}")
    plt.xscale('log')
    for axis in [ax.xaxis, ax.yaxis]:
        axis.set_major_formatter(ScalarFormatter())
    plt.ylabel(y_label)
    plt.xlabel(x_label)
    plt.xlim(lower_xlim, None)
    if window:
        plt.xlim(window[0], window[1])
    plt.savefig(f"{save_dir}{title}.pdf")
    plt.close()
    # END OF FUNCTION


def ladderplot(df, ladder2type, qc_save_dir, y_label="", x_label=""):
    """

    Plot multiple ladders into one plot

    :param df: panas DataFrame
    :param ladder2type: dict
    :param qc_save_dir: str
    :param y_label: str
    :param x_label: ste
    :return: plot appears in QC directory

    """

    fig, ax = plt.subplots()
    for i, ladder in enumerate([e for e in df.columns if "Ladder" in e and
                                                         "interpol" not in e]):
        sns.lineplot(data=df, x=f"{ladder}_interpol", y=ladder,
                     color=palettediff2[i], label=ladder2type[ladder])
        plt.title(f"All ladders, interpolated")
        plt.xscale('log')
        for axis in [ax.xaxis, ax.yaxis]:
            axis.set_major_formatter(ScalarFormatter())
    plt.xlim(10 ^ 0, None)
    plt.ylabel(y_label)
    plt.xlabel(x_label)
    plt.savefig(f"{qc_save_dir}peaks_all_interpolated.pdf")
    plt.close()
    # END OF FUNCTION
