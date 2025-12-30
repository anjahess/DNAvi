"""

Plotting functions for electropherogram analysis


Author: Anja Hess


Date: 2025-AUG-06

"""
import logging
import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
from src.constants import PALETTE, ALTERNATE_FORMAT
from matplotlib.patches import Patch
import warnings; warnings.filterwarnings("ignore")

def gridplot(df, x, y, save_dir="", title="", y_label="", x_label="",
             cols_not_to_plot=["bp_pos", "normalized_fluorescent_units"],
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
    plt.savefig(f"{save_dir}{title}_summary.{ALTERNATE_FORMAT}", bbox_inches='tight')
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
        if col == "sample":
            # Allows to plot clustermap even when no group data is provided
            wide_df = prep_df.pivot(index=col, columns=x,
                                    values=y).reset_index()
        else:
            wide_df = prep_df.pivot(index=["sample", col], columns=x,
                               values=y).reset_index()
        required_colors = round(int(len(wide_df[col].unique())/5))
        if required_colors <= 5:
            required_colors = 2
        lut = dict(zip(wide_df[col].unique(), PALETTE)) #sns.color_palette(palette='colorblind')*required_colors
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
        plt.savefig(f"{save_dir}cluster_by_{col}.{ALTERNATE_FORMAT}", bbox_inches="tight")
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
        #plt.axvline(x=100)
        #plt.axvline(x=50000)
        plt.ylabel(y_label)
        plt.xlabel(x_label)
        plt.title(f"{title} by {col}")
        plt.xscale('log')
        plt.savefig(f"{save_dir}{title}_by_{col}.pdf",
                    bbox_inches='tight')
        plt.savefig(f"{save_dir}{title}_by_{col}.{ALTERNATE_FORMAT}",
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
    plt.savefig(f"{save_dir}{title}.{ALTERNATE_FORMAT}")
    plt.close()
    # END OF FUNCTION


def p2stars(p):
    """
    Add asterisk based on p-value
    :param p: float, the p-value
    :return: str
    """
    if p > 0.05:
        return "ns"
    if p < 0.001:
        return '***'
    elif p < 0.01:
        return '**'
    elif p < 0.05:
        return '*'
    # END OF FUNCTION


def stats_plot(path_to_df, cols_not_to_plot=None, region_id="region_id",
               y="value", cut=False):
    """
    Plot statistical results
    :param path_to_df: str
    :param cols_not_to_plot: list of columns to exclude from plot
    :return: plots statistics in same directory as input dataframe
    """
    df = pd.read_csv(path_to_df, index_col=0)
    sns.set_context("paper")
    #####################################################################
    # Remove peaks where all values are 0
    #####################################################################
    cat_counts = df.groupby([region_id])[y].sum()

    peaks_without_vals = cat_counts[cat_counts == 0].index.tolist()
    if peaks_without_vals:
        logging.info(f"--- Not plotting {peaks_without_vals}")
    df = df[~df[region_id].isin(peaks_without_vals)]
    #####################################################################
    # 1. Plot grid based on every available metric in peak_id
    #####################################################################
    for categorical_var in (["sample"] +  [e for e in df.columns if
                             e not in cols_not_to_plot]):
        plot_df = df.copy()
        print(f"--- Plotting by {categorical_var}")
        #################################################################
        # If possible, get the p value, anno stars
        #################################################################
        possible_stats_dir = (path_to_df.rsplit("/", 1)[0] +
                              f"/group_statistics_by_{categorical_var}.csv")

        if os.path.exists(possible_stats_dir):
            stats_info = pd.read_csv(possible_stats_dir, index_col=0
                                     ).round({'p_value': 3})
            stats_dict = pd.Series(stats_info.p_value.values,
                                   index=stats_info.peak_name).to_dict()
            plot_df["p_val"] = plot_df[region_id].map(stats_dict)
            plot_df["stars"] = plot_df["p_val"].apply(p2stars)
            plot_df[region_id] = (plot_df[region_id].astype(str) + " \n p=" +
                             plot_df["p_val"].astype(str)) + " (" + plot_df["stars"] + ")"
        # Check all peaks are there
        peak_ids = plot_df[region_id].value_counts().index.tolist()
        if not peak_ids:
            print(f"No peaks {categorical_var}")
            continue
        #################################################################
        # Create the grid plot
        #################################################################
        g = sns.FacetGrid(plot_df, col=region_id, col_wrap=4, hue=categorical_var,
                          sharex=True, sharey=False, palette=PALETTE)

        if categorical_var == "sample":
            g = sns.FacetGrid(plot_df, col=region_id, col_wrap=4, hue=categorical_var,
                              sharex=True, sharey=False, palette=PALETTE,
                              aspect=1.5)
            g.map(sns.barplot, categorical_var, y, palette=PALETTE,
                  )
        else:
            if cut:
                g.map(sns.violinplot, categorical_var, y, inner_kws=dict(box_width=5, whis_width=2, color="black"),
                      edgecolor="black", alpha=.7, cut=0)
            else:
                g.map(sns.violinplot, categorical_var, y, inner_kws=dict(box_width=5, whis_width=2, color="black"),
                      edgecolor="black", alpha=.7)
            g.map(sns.stripplot, categorical_var, y, color="white", linewidth=1, edgecolor="black")

        # Rotate x-axis labels
        [plt.setp(ax.get_xticklabels(), rotation=90) for ax in g.axes.flat]
        plt.savefig(path_to_df.replace(".csv", f"_{categorical_var}.pdf"), bbox_inches="tight")
        plt.savefig(path_to_df.replace(".csv", f"_{categorical_var}.{ALTERNATE_FORMAT}"), bbox_inches="tight")
        plt.close()
    plt.close()
    # END OF FUNCTION




def peakplot(array, peaks, ladder_id, ref, i, qc_save_dir, y_label="",x_label="",
             size_values=""):
    """

    Plot the peaks detected in a DNA size profile

    :param array: np.ndarray
    :param peaks: list of int
    :param ladder_id: str or int, name of the ladder
    :param ref: dtr, type of reference
    :param i: int, index of the ladder (potentially multiple)
    :param qc_save_dir: str, path to folder to save the figure to
    :param y_label: str, y label name
    :param x_label: str, x label name
    :return: plots are generated and saved to disk.
    """

    sample_id = i
    plt.plot(array)
    plt.plot(peaks, array[peaks], "x")

    # Add the annotated base-pair values if possible
    max_x = len(array) # relative val for label
    center_factor = max_x * 0.035 # labels look prettier when up
    if size_values:
        for i, (x, y) in enumerate(zip(peaks, array[peaks])):
            if len(size_values) == len(peaks):
                # The size values are already translated
                real_pos = round(size_values[i])
            else:
                # Still need to infer the correct peak bp
                real_pos = round(size_values[x])
            plt.annotate(f"{round(real_pos,1)} bp", xy=(x-center_factor, y+0.04),
                         size=7)
    plt.plot(np.zeros_like(array), "--", color="gray")
    plt.title(f"{ladder_id}")
    plt.xlim(10 ^ 0, None)
    plt.ylabel(y_label)
    plt.xlabel(x_label)
    plt.savefig(f"{qc_save_dir}peaks_{sample_id}_{ref}.pdf")
    plt.savefig(f"{qc_save_dir}peaks_{sample_id}_{ref}.{ALTERNATE_FORMAT}")
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
    plt.savefig(f"{save_dir}{title}.{ALTERNATE_FORMAT}")
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
    plt.savefig(f"{qc_save_dir}peaks_all_interpolated.{ALTERNATE_FORMAT}")
    plt.close()
    # END OF FUNCTION
