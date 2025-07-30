Metadata
===================



1. The metadata format
^^^^^^^^^^^^^^^^^^

The metadata file in its simplest form is a two column table (**.csv format**). The first column has to be named **SAMPLE**
and contains in each row the sample id **matching exactly the name used for the input file columns**. In case of gel images
as input, the first *n* entries will be used, where *n* equals the number of lanes in the gel.



.. list-table:: Example of a DNAvi metadata file
   :widths: 25 25 50
   :header-rows: 1

   * - SAMPLE
     - YOUR_VARIABLE_1
     - YOUR_VARIABLE_2
   * - Sample_1
     - HEALTHY
     - FEMALE
   * - Sample_2
     - HEALTHY
     - FEMALE
   * - ...
     - ...
     - ...
   * - Sample_100
     - DISEASED
     - MALE

:download:`Metadata file example <_static/metadata.csv>`

2. Adding more metadata
^^^^^^^^^^^^^^^^^^


To add more metadata, simply add **additional columns** into the metadata file.

.. csv-table:: Example of an extended DNAvi metadata file
   :file: _static/metadata_ext.csv
   :widths: 30, 30, 30, 30, 30, 30
   :header-rows: 1


:download:`Extended metadata file example <_static/metadata_ext.csv>`

3. Adding metadata for gel images
^^^^^^^^^^^^^^^^^^

Since gel images do not contain lane names, the samples will be automatically named by lane number (e.g. 1,2,3...).
To add metadata for such samples, the **row number** in the metadata file will dictate the lane number the metadata is applied to.

