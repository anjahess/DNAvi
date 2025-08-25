Advanced Settings
===================

Due to standardized DNAvi :doc:`/Inputs`, in most times our default values will work.
However, customized changes to **constants.py** allow to you to modify these parameters.

**Warning: ALWAYS SAVE A COPY OF constants.py BEFORE YOU MAKE ANY CHANGES.**

Customizations can help should you experience that your expected bands are not detected, or you still have too much marker band
inside your plot.

Where to find Advanced Settings
^^^^^^

Your band detection settings are in **DNAvi/src/constants.py**
Simply open the file in a Text Editor:



Format of the constats.py file
^^^^^^

.. code-block::

    ########################################################################################################################
    # BAND DETECTION SETTINGS
    ########################################################################################################################
    # Peak detection ladder
    DISTANCE = 20 # 20 pos apart min
    """Minimum required distance of two peaks to be discriminated."""

    MIN_PEAK_HEIGHT_FACTOR=0.2
    """Factor by which to multiply the maximum peak height to set the minimum peak height to be detected. """

    MAX_PEAK_WIDTH_FACTOR=0.1
    """Fraction of entire gel length to set the maximum accepted peak width - ONLY FOR THE LADDER, not for sample peaks"""

    PEAK_PROMINENCE=(0.3, None)
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


Example: Adjusting Peak (Band) calling parameters
^^^^^^

For example, let's assume your **two left** ladder band peaks were **not detected**:

        .. image:: _static/peak_not_detected.png
          :width: 400
          :alt: Missing peaks


A quick look into constants.py shows us, that the **MIN_PEAK_HEIGHT_FACTOR** is set indeed quite high (to 0.9),
meaning the peak must be **higher than 90%** of the max intensity to be detected:

.. code-block::

        MIN_PEAK_HEIGHT_FACTOR=0.9
        """Factor by which to multiply the maximum peak height to set the minimum peak height to be detected. """

So let's **change that to 0.2** to be more liberal allowing smaller peaks to be detected (>20% of the max intensity):

.. code-block::

        MIN_PEAK_HEIGHT_FACTOR=0.2
        """Factor by which to multiply the maximum peak height to set the minimum peak height to be detected. """

Now our two left markers are detected, as indicated by the orange cross:

        .. image:: _static/peak_detected.png
          :width: 400
          :alt: Peaks

Other parameters
""""""""""""""""""""""""""
Other parameters include the peak prominence, the minimum distance between peaks, background substraction for statistics
and the interpolation function to retrieve missing base pair positions based on the ladder. They are described in the
**API reference** and can be adjusted by advanced users/developers as needed.