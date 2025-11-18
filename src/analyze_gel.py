"""

Add-on functions for electropherogram generation from an annotated gel image

Author: Anja Hess

Date: 2025-APR-15


"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import imageio.v3 as iio
import skimage as ski
import numpy as np
import logging
from skimage import measure, util
from skimage.filters import threshold_otsu
from skimage.measure import label, regionprops
from skimage.color import label2rgb
from skimage.transform import resize

def range_intersect(r1, r2):
    """

    Find intersection of two ranges

    :param r1: range
    :param r2: range
    :return: intersection

    """
    return range(max(r1.start, r2.start), min(r1.stop, r2.stop)) or None


def resize_img(image):
    """

    Resize each image (helpful for data storage)

    :param image_file: image array
    :return: resized image

    """

    height, width = image.shape[0], image.shape[1] #height, width

    # To target height
    TARGET_HEIGHT = 500
    coefficient = width / 500
    new_width = width / coefficient
    image_resized = resize(image, (TARGET_HEIGHT, new_width),
                           anti_aliasing=True)
    
    return image_resized


def remove_colors_from_img(image, max_range=0.3):
    """
    Remove colors from an image, especially colored arrows or marker annotations
    :param image: numpy array
    :param max_range: maximum color range to accept before making this black -> increasing = more tolerance
    :return: all colors now black.
    """
    RGBrange = np.ptp(image, axis=2)
    coloured = RGBrange > max_range
    image[coloured] = [0,0,0]
    return image


def analyze_gel(image_file, run_id=None, marker_lane=0):
    """

    Core function to generate a signal table from a DNA gel image.

    :param image_file: str, path to DNA gel image
    :return: multiple intermediate images to visualize the gel band detection are \
    generated and saved, finally the signal table is saved to disk and returned \
    along with the save_dir (str) and the error.
    """

    print("------------------------------------------------------------")
    print("        Loading image for signal table generation")
    print("------------------------------------------------------------")

    # Define output dir
    if not run_id:
        run_id = image_file.rsplit("/", 1)[1].rsplit(".", 1)[0]
    save_dir = image_file.rsplit("/", 1)[0] + f"/{run_id}/"
    save_table = f"{save_dir}signal_table.csv"
    gel_dir = f"{save_dir}images/"
    os.makedirs(save_dir, exist_ok=True)
    os.makedirs(gel_dir, exist_ok=True)

    ####################################################################################
    # 1. Load the image
    ####################################################################################
    input_image = image_file

    # load, resize, remove colors
    gel = iio.imread(uri=input_image)[:,:,:3]
    gel = resize_img(gel)
    gel = remove_colors_from_img(gel)

    fig, ax = plt.subplots()
    ax.imshow(gel, cmap="gray")
    plt.savefig(f"{gel_dir}colors-removed.png")
    plt.close()

    grey = ski.color.rgb2gray(gel)
    blurred_shapes = ski.filters.gaussian(grey, sigma=1.0)

    ####################################################################################
    # 2. Threshold
    ####################################################################################
    threshold = threshold_otsu(blurred_shapes)
    thresh_img = grey < threshold
    fig, ax = plt.subplots()
    ax.imshow(thresh_img, cmap="gray")
    plt.savefig(f"{gel_dir}thresholded.png")
    plt.close()

    ####################################################################################
    # 3. Partition into lanes
    ####################################################################################
    # Retrieve regions
    label_image = label(thresh_img)
    image_label_overlay = label2rgb(label_image, image=grey, bg_label=0)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.imshow(image_label_overlay)
    plt.savefig(f"{gel_dir}lanes.png")
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
            # GET X-COORDINATES (Y=Same)
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
                fill=False, edgecolor='red', linewidth=2)
            ax.add_patch(rect)
    plt.tight_layout()
    plt.savefig(f"{gel_dir}{counter}_lanes_borders.png")
    plt.close()

    ####################################################################################
    # Critical - lane coordinates are not sorted yet, do this here:
    ####################################################################################
    sorted_lane_coordinates = sorted(lane_coordinates.items(), key=lambda x: x[1])
    lane_coordinates = {}
    for i, ele in enumerate(sorted_lane_coordinates):
        lane_coordinates[i] = ele[1]

    ####################################################################################
    # 5. Retrieve intensity profile of each lane along Y-axis
    ####################################################################################
    profiles = []
    image_copy = blurred_shapes.copy()
    for region in lane_coordinates:
        # 1. The image is cropped to the lane only
        minc, maxc = lane_coordinates[region] # X-coordinates of each lane
        cropImg = image_copy[:, minc:maxc]
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
        plt.savefig(f"{gel_dir}{region}_profile.png")
        plt.close()
        profiles.append(profile)
    ####################################################################################
    # 5. Checkpoint - do we have enough lanes?
    ####################################################################################

    if len(profiles) <= 1:
        error = ("Insufficient gel lanes detected. "
                 "Make sure your image is a DNA gel image (must be white "
                 "background with black bands on it")
        print(error)
        logging.error(error)
        exit()

    ###################################################################################
    # 6. Transform to df + quick sanity check that ladder is available
    ###################################################################################
    df = pd.DataFrame.from_records(profiles).transpose()
    avail_lanes = df.shape[1]-1
    if avail_lanes < marker_lane:
        error = (f"--- Your marker lane ({marker_lane+1}) is outside the number of lanes "
              f"detected from your image (found {avail_lanes}). "
              f"Please check image outputs and try again.")
        print(error)
        logging.error(error)
        exit()
    ###################################################################################
    # 5. Save the inentsity profile
    ###################################################################################
    df.rename(columns={marker_lane: "Ladder"}, inplace=True)
    df.to_csv(save_table, index=False)

    return save_table, save_dir

# END OF SCRIPT