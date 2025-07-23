"""

Add on functions for electropherogram generation from an annotated gel image
@author: Anja Hess
@date: 2025-APR-15

"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import imageio.v3 as iio
import skimage as ski
from skimage import data, measure, util
from skimage.filters import threshold_otsu
from skimage.measure import label, regionprops
from skimage.color import label2rgb


def range_intersect(r1, r2):
    return range(max(r1.start, r2.start), min(r1.stop, r2.stop)) or None


def analyze_gel(image_file):
    """

    :param image_file:
    :return:
    """
    ####################################################################################
    # 1. Load the image
    ####################################################################################
    input_image = image_file
    gel = iio.imread(uri=input_image)[:,:,:3]
    grey = ski.color.rgb2gray(gel)
    blurred_shapes = ski.filters.gaussian(grey, sigma=1.0)

    ####################################################################################
    # 2. Threshold
    ####################################################################################
    threshold = threshold_otsu(blurred_shapes)
    thresh_img = grey < threshold
    fig, ax = plt.subplots()
    ax.imshow(thresh_img, cmap="gray")
    plt.savefig(input_image.rsplit('.',1)[0]+"_thresholded.png")
    plt.close()

    ####################################################################################
    # 3. Partition into lanes
    ####################################################################################
    # Retrieve regions
    label_image = label(thresh_img)
    image_label_overlay = label2rgb(label_image, image=grey, bg_label=0)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.imshow(image_label_overlay)
    plt.savefig(input_image.rsplit('.',1)[0]+"_lanes.png")
    plt.close()
    height_max = label_image.shape[0]

    ####################################################################################
    # 4. Retrieve lane X-coordinates
    ####################################################################################
    lane_coordinates = {}
    counter = 0
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.imshow(label_image, cmap="gray")
    for i, region in enumerate(regionprops(label_image)):
        if region.area >= 100: # Minimum size
            ovlp = None
            minr, minc, maxr, maxc = region.bbox

            #############################################################################
            # # GET X-COORDINATES (Y=Same)
            # Exclude overlapping coordinates that are already in the dict
            #############################################################################
            if (minc, maxc) not in lane_coordinates.values():
                r1 = range(minc, maxc)
                for x,y in lane_coordinates.values():
                    r2 = range(x,y)
                    ovlp = range_intersect(r1, r2)
                    if ovlp:
                        break
                if ovlp:
                    continue
                counter += 1
                lane_coordinates[counter] = (minc, maxc)
            rect = mpatches.Rectangle(
                (minc, 0), maxc - minc, height_max,
                fill=False,
                edgecolor='red',
                linewidth=2)
            ax.add_patch(rect)
    plt.tight_layout()
    plt.savefig(input_image.rsplit('.',1)[0]+f"_{counter}_lanes_borders.png")
    plt.close()

    ####################################################################################
    # 5. Retrieve intensity profile of each lane along Y-axis
    ####################################################################################
    profiles = []
    image_copy = blurred_shapes.copy()
    for region in lane_coordinates:
        # 1. The image is cropped to the lane only
        minc, maxc = lane_coordinates[region] # X-coordinates of each lane
        cropImg = image_copy[0:502, minc:maxc]   #Todo: Y- Coordinates for crop flexible!!

        # 2. Invert the colors (so black ergo DNA is the highest signal)
        cropImginvert = util.invert(cropImg, signed_float=False)
        start = (0,cropImg.shape[1]/2)  # Start of the profile line row=100, col=0
        end = (cropImg.shape[0],cropImg.shape[1]/2)  # End of the profile line row=100, col=last

        # Invert the scale so the most far DNA is the lowest basebairs
        inverted_scale = cropImginvert[::-1]
        profile = measure.profile_line(inverted_scale, start, end)
        fig, ax = plt.subplots(1, 2)
        ax[0].set_title('Image')
        ax[0].imshow(cropImg, cmap="gray")
        ax[0].plot([start[1], end[1]], [start[0], end[0]], 'r')
        ax[1].set_title('Profile')
        ax[1].plot(profile)
        plt.savefig(input_image.rsplit('.',1)[0]+f"{region}_profile.png")
        plt.close()
        profiles.append(profile)

    ####################################################################################
    # 5. Checkpoint - do we have enough lanes?
    ####################################################################################
    if len(profiles) <= 1:
        error = ("Insufficient gel lanes detected. "
                 "Make sure your image is a DNA gel image (must be white "
                 "background with black bands on it)")
        return "", error
    ###################################################################################
    # 6. Save the inentsity profile
    ####################################################################################
    df = pd.DataFrame.from_records(profiles).transpose()
    df.rename(columns={0: "Ladder"}, inplace=True)
    df.to_csv(input_image.rsplit('.',1)[0]+".csv", sep='\t', index=False)

    return input_image.rsplit('.',1)[0]+".csv", None

# END OF SCRIPT