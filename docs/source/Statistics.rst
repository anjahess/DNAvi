Statistics
===================

This section describes DNAvi's statistical analyses and outputs.

Basic statistics
^^^^^^^^^^^^^^^^^^

This table is a broad description of your dataset, specifically all numerical data provided.

.. csv-table:: Example of basic statistics output
   :file: _static/basic_statistics.csv
   :widths: 30, 30, 30, 30
   :header-rows: 1


The following metrics are provided and exemplified based on the "bp_pos" column:
    • **Skewness** - skew of the size distribution, ~ 0 for normally distributed data
    • **Entropy** - Shannon entropy of the distribution
    • **AUC** - total area under the signal intensity curve


Peak statistics
^^^^^^^^^^^^^^^^^^

This table contains information on average sizes and individual peaks. Let's have a look at the line plots for two samples to understand the corresponding statistics:

.. image:: _static/example_stats.png
  :width: 500
  :alt: Example stats


.. csv-table:: Example of peak statistics output
   :file: _static/peak_statistics.csv
   :widths: 30, 30, 30, 30, 30, 30, 30, 30
   :header-rows: 1


For each sample, peak metrics are provided:
    • **average_size** : the average fragment size in bp, estimated from the signal table (histogram)
    • **median_size** : the median in bp, estimated from the signal table (histogram)
    • **mode** : the mode value in bp, estimated from the signal table (histogram)
    • **max_peak**: the most intense peak (peak with highest fluorescent signal) of this sample
    • **metadata**: additional columns assigning categories if :doc:`/Metadata` were provided
    • **peak_id**: the detected peaks (0-based) for each sample, numbered from low to high fragment size, and their metrics. In the example, 6 peaks are detected in Sample_1 while 7 peaks detected in Sample_2.
    • **a variety of nucleosomal fractions** : the percentage of cfDNA in specific size intervals. Customizable!
    • **estimated genomic DNA content** : the percentage of estimated gDNA (based on high molecular weight DNA thresholds). Customizable!


Group statistics
^^^^^^^^^^^^^^^^^^

For each variable specified in the :doc:`/Metadata` a table containing statistical testing results is provided.
Let's have a look at an example where cell-free DNA from two groups (Control vs. Treatment) were compared.
The metadata-based evaluation allows to answer biological questions (see also next section).


**Note**: DNAvi will choose the statistical test based on your group data distribution (normal/non-normal), variance (equal variance),
group size (2 or more).


.. image:: _static/example_stats_condition.jpg
  :width: 300
  :alt: Example stats


.. csv-table:: Example of group statistics output I
   :file: _static/group_statistics_by_CONDITION.csv
   :widths: 30, 30, 30, 30, 30, 30, 30, 30, 30, 30
   :header-rows: 1

**Result:** In this example, the **average_size**, **max_peak**, and also the **first peak** size do show a statistical difference
between the two groups, as the Kruskal Wallis test computed a *p* value **< 0.05**. **Unique peaks** refer to peaks that only occur in one group,
but not in the other. Because they are unique to a group, no statistical comparison is performed for those peaks.
