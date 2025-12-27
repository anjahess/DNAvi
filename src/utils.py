"""

Utilities and additional functions for electropherogram analysis. \n
Author: Anja Hess \n
Date: 2025-NOV-10 \n

"""

import pandas as pd
import numpy as np
import logging
import scipy.stats as stats


def vartest(stats_groups, alpha=0.05):
    """
    For validating that the ANOVA is used in normally ditr scenarios
    :param stats_groups:
    :param alpah:
    :return:
    """

    stat, p = stats.levene(*stats_groups)
    if p < alpha:
        return False
    return True

def normality(stats_groups, alpha=0.05):
    """

    While Shapiro's test does not confirm the sample
    stems from a normal distribution, we can at least reject
    this hypothesis and argue for the necessity to perform a
    non-parametric test.

    :param stats_groups:
    :param alpha: float
    :return:
    """
    for i, group in enumerate(stats_groups):
        s, p = stats.shapiro(group)
        logging.info(f"--- Shapiro-Wilk for group #{i} p-val: {round(p,ndigits=2)}")
        # reject null hypothesis that this is from normal distribution
        if p < alpha:
            return False
    return True
    # END OF FUNCTION

def mean_from_histogram(df, unit="", size_unit="", sample_unit="sample"):
    """

    Function to estimate the mean size of a patient/samples' DNA
    fragments (in base pairs) based on the fluorescence signal table.
    Strategy is to create a histogram and next infer the metrics.

    :param df: pandas.DataFrame
    :param unit: str, usually normalized fluorescence unit
    :param size_unit: str, fragment size unit (base pairs)
    :return: float, average fragment size

    """

    # Calculate mean bp from the histogram (frequency rescaled 0-100)
    df["counts"] = df[unit] * 100
    df["product"] = df[size_unit] * df["counts"]
    pivoted = df.pivot_table(index=sample_unit, values=["product", "counts"],
                             aggfunc="sum")
    pivoted["mean_bp"] = pivoted["product"] / pivoted["counts"].sum()
    mean_bp = df["product"].sum() / df["counts"].sum()

    # Estimate the Median & Mode from the count table
    # Decompress count table
    df = df['bp_pos'].repeat(df['counts']).to_frame()
    median = df.median().round(1)[0]
    mode = df.mode().round(1).values[0][0]
    return mean_bp, median, mode
    # END OF FUNCTION



def distribution_stats(df, save_dir="", unit="normalized_fluorescent_units", size_unit="bp_pos",
                       sample_unit="sample"):
    """
    Compute basic distribution statistics for each sample. \
    Includes: skewness, entropy, AUC

    :param df: pandas dataframe
    :param save_dir: str
    :param unit: str
    :param size_unit: str
    :param metric_unit: str
    :return: basic stats dataframe

    """
    pivoted = df.pivot(index=size_unit, columns=sample_unit, values=unit)
    #####################################################################
    # 1. Skewness, Entropy, AUC
    #####################################################################
    skewness = pivoted.skew()
    entropy = pivoted.apply(stats.entropy, axis=0)
    auc = pivoted.apply((lambda x: np.trapezoid(x, pivoted.index)))

    #####################################################################
    # 2. Mean, median, modal fragment size
    #####################################################################
    basic_stats = pd.DataFrame({"Skewness":skewness,"Entropy":entropy,
                                "AUC":auc})
    basic_stats.sort_index(inplace=True)
    basic_stats.to_csv(save_dir)
    return basic_stats
    # END OF FUNCTION

def merge_tables(signal_tables, save_dir="", meta_dict=False):
    """
    Function to create a composite from multiple image outputs \
    (Multi-image processing)
    :param signal_tables: list of directories to signal tables created from gel images
    :param save_dir: str
    :return: will save the composite to
    """

    merged_df = []

    for table in signal_tables:
        file_id = table.rsplit("/signal_table.csv")[0].rsplit("/")[-1]
        file = [e for e in meta_dict if file_id in e][0]
        meta = pd.read_csv(meta_dict[file])
        df = pd.read_csv(table)
        # Add sample names
        df.columns = ["Ladder"] + meta["SAMPLE"].values.tolist()
        if type(merged_df) == list:
            merged_df = df
        else:
            df.drop(columns="Ladder", inplace=True)
            merged_df = pd.concat([merged_df, df], axis=1)
    merged_df.to_csv(save_dir, index=False)
    return save_dir


def wide_to_long(df, id_var="pos", var_name="sample", value_name="value"):
    """

    Function to transfer wide dataframe to long format

    :param df: pandas.DataFrame in wide format
    :param id_var: str,  the column of the wide dataframe containing the id variable
    :param var_name: str, the new column in the long dataframe containing the variable name
    :param value_name: str, the new column in the long dataframe containing the value
    :return: pandas.DataFrame

    """

    df["id"] = df.index
    df_long = pd.melt(df,
                      id_vars=["id", id_var],
                      var_name=var_name,
                      value_name=value_name)
    del df_long["id"]
    return df_long


def integrate(df, ladders_present=""):
    """

    Beta: a function that in the future will allow help handling \
    resulting "gaps" when using multiple ladders within the same signal table.

    NOTE: Not implemented yet.

    :param df: pandas dataframe
    :param ladders_present: list of strings
    :return: a new pandas dataframe that does not have nan values despite multiple ladders

    """

    merged_df = []
    #####################################################################
    # 1. Slice dataframe by column, and unify the y-axis label
    #####################################################################
    for i, ladder in enumerate(ladders_present):
        current = df.columns.get_loc(ladder)
        try:
            next = df.columns.get_loc(ladders_present[i + 1])
        except IndexError:
            next = None

        if i == 0:
            sub_df = df.iloc[:, :next]
        else:
            sub_df = df.iloc[:, current:next]
        sub_df.rename(columns={ladder: "ladder"}, inplace=True)
        #################################################################
        # 2. Merge dataframes (on="ladder")
        #################################################################
        if type(merged_df) == list:
            merged_df = sub_df
        else:
            merged_df = pd.merge(merged_df, sub_df, on="ladder", how="outer")

    return merged_df