import os
import rasterio
import numpy as np
import json
import matplotlib.pyplot as plt  # Import matplotlib for displaying images

# Function to extract bounding box from STAC JSON
def extract_metadata(stac_file):
    with open(stac_file, 'r') as f:
        data = json.load(f)

    # Extracting the bounding box coordinates
    bbox = data['bbox']
    ul_lon, ul_lat = bbox[0], bbox[3]  # Upper Left Longitude and Latitude
    lr_lon, lr_lat = bbox[2], bbox[1]  # Lower Right Longitude and Latitude

    # Default CRS for WRS-2
    crs = 'EPSG:4326'  # WGS 84

    return (ul_lon, ul_lat, lr_lon, lr_lat, crs)

# Function to process each folder in the raw data directory
def run_process_data(folder_path, folder_name, root_directory):
    stac_file = None
    file_list = []

    # Look for STAC JSON and band files in the specified folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith('_SR_stac.json'):
            stac_file = os.path.join(folder_path, file_name)
        elif file_name.endswith('SR_B4.TIF'):
            file_list.append(os.path.join(folder_path, file_name))  # Red band
        elif file_name.endswith('SR_B3.TIF'):
            file_list.append(os.path.join(folder_path, file_name))  # Green band
        elif file_name.endswith('SR_B2.TIF'):
            file_list.append(os.path.join(folder_path, file_name))  # Blue band

    if stac_file and len(file_list) == 3:  # Ensure we found the STAC file and all three bands
        # Extract metadata
        ul_lon, ul_lat, lr_lon, lr_lat, crs = extract_metadata(stac_file)

        # Read each band and stack them into an RGB image
        bands = {}
        for i, path in enumerate(file_list):
            with rasterio.open(path) as src:
                bands[i] = src.read(1)  # Read the first band (2D array)

        # Stack the bands into an RGB image
        rgb_image = np.dstack((bands[2], bands[1], bands[0]))  # Assuming [R, G, B] order

        # Normalize the values to 0-255 for visualization
        rgb_image = (rgb_image / rgb_image.max() * 255).astype(np.uint8)

        # Show the RGB image using matplotlib
        plt.imshow(rgb_image)
        plt.title('Stacked RGB Image')
        plt.axis('off')  # Hide axis
        # plt.show()  # Display the image

        # Define the transform based on the bounding box
        transform = rasterio.transform.from_bounds(ul_lon, lr_lat, lr_lon, ul_lat, rgb_image.shape[1], rgb_image.shape[0])

        # Create results directory if it doesn't exist
        results_directory = os.path.join(root_directory, "results")
        os.makedirs(results_directory, exist_ok=True)
        output_subdirectory = os.path.join(results_directory, folder_name)
        # print(f"output: {output_subdirectory}")

        # Write the RGB image as a GeoTIFF in the new subdirectory
        output_file = os.path.join(output_subdirectory, f"stacked_img_{folder_name}.tif")
        with rasterio.open(
                output_file,
                'w',
                driver='GTiff',
                height=rgb_image.shape[0],
                width=rgb_image.shape[1],
                count=3,
                dtype='uint8',
                crs=crs,
                transform=transform
        ) as dst:
            dst.write(rgb_image[:, :, 0], 1)  # Red channel
            dst.write(rgb_image[:, :, 1], 2)  # Green channel
            dst.write(rgb_image[:, :, 2], 3)  # Blue channel

        return True  # Data processed successfully
    return False  # Data not processed due to missing files


# Function to traverse and process folders in raw_data
def stack_image(raw_data_folder):
    # Traverse through each folder in raw_data
    raw_data_folder = os.path.join(raw_data_folder, "raw_data")

    for folder_name in os.listdir(raw_data_folder):
        folder_path = os.path.join(raw_data_folder, folder_name)
        print(folder_path)

        # Check if the folder is a directory
        if os.path.isdir(folder_path):
            print(f"Processing folder: {folder_path}")
            extracted_data = run_process_data(folder_path, folder_name, root_directory)

            if extracted_data:
                print(f"Data extracted successfully from {folder_name}.\n")
            else:
                print(f"No valid STAC JSON or bands found in {folder_name}.\n")

# Main execution
current_directory = os.getcwd()  # Get the current working directory
root_directory = os.path.dirname(current_directory)  # Move up one directory
stack_image(root_directory)
