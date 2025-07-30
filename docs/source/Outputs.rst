Outputs
===================

After your analysis has been performed, your data will be automatically downloaded from your browser. 

1. Analysis folder
^^^^^^


The ZIP archive contains your unique working ID (c2e675.. in the example). Unzip the archive by double-clicking or using a software of your choice.


Once you have unzipped the folder, double click it to open it.
You will see the inputs you have submitted to DNAvi prior to the analysis. In the example that’s the DNA intensity table file called electropherogram.csv and a electropherogram_ladder.csv file. Only if you submitted a metafile, then a third file, in this case called electropherogram_meta.csv will be visible. Finally there is the results folder which we will open now.

For gel image inputs:
In case you have uploaded a gel image instead of a table file, the folder will additionally contain some outputs from the image analysis:

It is recommended to carefully check gel_lanes_border.png and gel_lanes.png to understand if all ladder and DNA bands have been sucessfully recongnized and in the lanes are correctly separated before proceeding. If that’s not the case, please carefully check the section on image inputs, because errors here may be likely caused by insufficient image quality. 
4.1.1 Results folder
The results folder contains two sub-directories, called QC and plots.
4.1.1.1 QC
The QC folder is all about the DNA marker and detecting its peaks. It makes sense to check it and make sure your DNA ladder has been recognized correctly, and that the base pairs assigned make sense. You will find the following files:
    • info.csv – a simple table giving information on your ladder type


    • interpolated.csv – your input data with missing intensity values interpolated 




    • bp_translation.csv – your input, but instead of ladder intensity values now with the assigned base pair position.

    • Peaks_N_ladder-name.pdf – A line plot that will show you the detected peaks as yellow crosses. Make sure all peaks that you consider important are correctly detected. The x-axis will only give you positional values at that stage.





      
      
      
      
      
      
    • peaks_all_interpolated.pdf & N_ladder-name_interpolated.pdf – Similar visualizations of ladder with base pairs already annotated.

If you have checked the QC outputs and found your ladder correctly annotated, you may proceed to the plots folder and check your samples.
4.1.1.2 Plots

In its simplest form, the output may consist of only three files, and expand with an additional plot yor each variable you specified in the metadata:
    • all_samples.pdf – a grid plot showing each DNA sample as an individual line plot














The y-axis shows normalized fluoresence signals to fit a value between 0 and 1. This way fragment profiles become comparable irrespective of sample concentration. The x-axis shows the basepair position based on the values submitted for your ladder. This is displayed in log scale. Each subplot is titled by the sample name you specified either in the table or meta file.
    • all_samples_nomarker_summary.pdf – a line plot summarizing all samples including the lower and upper marker signal















    • all_samples_by_YOURVARIABLE.pdf – for each variable specificd in the metafile, the summary line plot will stratify the samples into your groups, each group highlighted in another color.











    • sourcedata.csv – this table provides the source data used for generating above plots and is very helpful in case you want to process / visualize the data later in another program (R, pyhton, GraphPad) or if you need to upload them for a publication.

