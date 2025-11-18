Normalization
===================


Per default, DNAvi performs min/max normalization. If you wish to run the anaylsis without this behavior, you can use other options:


Option 1: Running DNAvi without normalization
^^^^^^^^^^^^^^^^^^



.. code-block::

      -un, --unnormalized
      Do not perform min/max normalization. ATTENTION: will be DNA-concentration sensitive.


The example below gives you an idea what happens when normalization is removed (left) vs. applied (right) at the example of a *serial cfDNA dilution*.


        .. image:: _static/normalization.png
          :width: 800
          :alt: Normalizations


As you can see, the unnormalized version will reflect the reduction in DNA concentration as the cfDNA sample is diluted.
However, in clinical settings, we usually use all liquid available and do not normalize concentrations necessarily before running the DNA on a gel.
Hence, in such instances, normalization can help to visualize nucleosomal modes without being "distracted" by intensity-related differences between samples.
In the end, you will have to decide which mode is most appropriate to your research question.



Option 2: Running DNAvi while normalizing to a specific sample
^^^^^^^^^^^^^^^^^^

.. code-block::

      -nt [<sample_name>], --normalize_to [<sample_name>]
                            Name of the sample to normalize all values to. ATTENTION: will be DNA-concentration sensitive.

This will result in your sample of choice serving as the reference point for all other sample intensities.

Below is a comparison of all available modes on the *same* cfDNA samples

        .. image:: _static/normalization_comp.png
          :width: 800
          :alt: Norm-comp

**Image (from left to right): Unnormalized, normalized, normalized to a specific sample (Sample 1 in this case).**
