"""

Plotting functions for electropherogram analysis


Author: Anja Hess


Date: 2025-AUG-06

"""
import os
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
from src.constants import PALETTE
from matplotlib.patches import Patch

def gridplot(df, x, y, save_dir="", title="", y_label="", x_label="",
             cols_not_to_plot=["bp_pos", "sample", "normalized_fluorescent_units"],
             ):
    """

    Generate line plot for DNA fragment sizes with masking option for marker peaks

    :param df: pandas.DataFrame
    :param x: str, the plot's x variable
    :param y: str, the plot's y variable
    :param save_dir: str, path to save the figure
    :param title: str, title of the figure
    :param y_label: str, y label of the figure
    :param x_label: str, x label of the figure
    :param cols_not_to_plot: list of columns to exclude from plot to get categorical vars
    :return: plot is generated and saved to disk.
    """

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

    #####################################################################
    # By category
    #####################################################################
    cat_vars = [c for c in df.columns if c not in cols_not_to_plot]
    for col in cat_vars:

        #################################################################
        # Clustermap
        #################################################################

        # In case marker is in reduce to one entry per sample
        df["sample-bp"] = df[x].astype(str) + "_" + df["sample"].astype(str)
        prep_df = df.drop_duplicates(subset=["sample-bp"])
        del prep_df["sample-bp"]

        # Now ready to be transformed to wide
        wide_df = prep_df.pivot(index=["sample", col], columns=x,
                           values=y).reset_index()
        lut = dict(zip(wide_df[col].unique(), sns.color_palette(
            palette='colorblind')))
        row_colors = wide_df[col].map(lut)
        sns.clustermap(wide_df.drop(columns=["sample", col]),
                       rasterized=True, row_cluster=True,
                       cmap="YlGnBu",yticklabels=False,xticklabels=False,
                       col_cluster=False, row_colors=row_colors)
        handles = [Patch(facecolor=lut[name]) for name in lut]
        plt.legend(handles, lut, title=col,
                   bbox_to_anchor=(1, 1),
                   bbox_transform=plt.gcf().transFigure, loc='upper right')
        plt.savefig(f"{save_dir}cluster_by_{col}.pdf", bbox_inches="tight")
        plt.close()

        #################################################################
        # Overview by condition
        #################################################################
        print(f"--- Plotting by {col}")
        hue = col
        sns.lineplot(data=df, x=x, y=y, alpha=.7,
                     palette=PALETTE[:len(df[hue].unique())],
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
    g = sns.FacetGrid(df, col=hue, hue=hue, col_wrap=3, palette=PALETTE)
    g.map(sns.lineplot, x, y, alpha=.7)
    g.add_legend()

    # Add labels
    plt.ylabel(y_label)
    plt.xlabel(x_label)
    plt.suptitle(f"{title}")
    plt.xscale('log')
    plt.savefig(f"{save_dir}{title}.pdf")
    plt.close()

    # END OF FUNCTION

def peakplot(array, peaks, ladder_id, ref, i, qc_save_dir, y_label=""):
    """

    Plot the peaks detected in a DNA size profile

    :param array: np.ndarray
    :param peaks: list of int
    :param ladder_id: str or int, name of the ladder
    :param ref: dtr, type of reference
    :param i: int, index of the ladder (potentially multiple)
    :param qc_save_dir: str, path to folder to save the figure to
    :param y_label: str, y label name
    :return: plots are generated and saved to disk.

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

    Core line plot function for DNA fragment sizes

    :param df: pandas.DataFrame
    :param x: x variable
    :param y: y variable
    :param save_dir: str, path to save the figure
    :param title: str, title of the figure
    :param y_label: str, y label of the figure
    :param x_label: str, x label of the figure
    :param hue: str, optional to set hue parameter
    :param units: bool
    :param plot_lower: bool
    :param estimator: str, which estimator to use
    :param style: str, style of line plot
    :param window: bool or tuple for x axis limits
    :return: plots are generated and saved to disk.
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
                     palette=PALETTE[:n_cats], units=units,
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

    :param df: pandas.DataFrame
    :param ladder2type: dict
    :param qc_save_dir: str
    :param y_label: str, y label of the figure
    :param x_label: str, x label of the figure
    :return: plot generated and saved to the QC directory

    """

    fig, ax = plt.subplots()
    for i, ladder in enumerate([e for e in df.columns if "Ladder" in e and
                                                         "interpol" not in e]):
        sns.lineplot(data=df, x=f"{ladder}_interpol", y=ladder,
                     color=PALETTE[i], label=ladder2type[ladder])
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
