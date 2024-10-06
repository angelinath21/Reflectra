import rasterio
import numpy as np
import os
import json

def dn_to_sr(dn):
    """Convert DN to Surface Reflectance."""
    return 2.75e-05 * dn - 0.2

def dn_to_temperature(dn):
    """Convert DN to Surface Temperature in Kelvin."""
    return 0.00341802 * dn + 149.0

def read_band_and_convert_to_sr(band_path, x, y):
    """Read a Landsat band TIFF file and convert the DN at (x, y) to Surface Reflectance."""
    with rasterio.open(band_path) as src:
        # Read the pixel value at (x, y)
        dn = src.read(1)[y, x]  # Note that y, x indexing is used
        sr = dn_to_sr(dn)
        return sr

def read_band_and_convert_to_temp(band_path, x, y):
    """Read the B10 TIFF file and convert the DN at (x, y) to Surface Temperature in Celsius."""
    with rasterio.open(band_path) as src:
        # Read the pixel value at (x, y)
        dn = src.read(1)[y, x]  # Note that y, x indexing is used
        temp_kelvin = dn_to_temperature(dn)
        temp_celsius = temp_kelvin - 273.15  # Convert Kelvin to Celsius
        return temp_kelvin, temp_celsius

def fetch_reflectance(root_directory, pixel_x, pixel_y):
    # Traverse all subdirectories in the root directory
    fetch_path = os.path.join(root_directory, "raw_data")
    # print(f"Root directory: {fetch_path}")

    # Check if the path exists and is a directory
    if not os.path.isdir(fetch_path):
        print(f"{fetch_path} is not a valid directory.")
        return

    # Traverse all subdirectories within "raw_data"
    for folder_name in os.listdir(fetch_path):
        folder_path = os.path.join(fetch_path, folder_name)
        # print(f"Folder path: {folder_path}")

        # Check if the folder_path is a directory (to avoid processing files)
        if os.path.isdir(folder_path):
            print(f'Processing folder: {folder_name}')
            reflectance_data = get_SR_ST(folder_path, folder_name, pixel_x, pixel_y)  # Pass folder_path here

            # Save the results to a JSON file inside the respective folder
            json_output_file = os.path.join(folder_path, f"{folder_name}_SR_ST_values.json")
            with open(json_output_file, 'w') as json_file:
                json.dump(reflectance_data, json_file, indent=4)

            print(f'Reflectance and temperature data saved to {json_output_file}')

def get_SR_ST(base_path, folder_name, pixel_x, pixel_y):
    # Construct the full path by appending the folder name once (correct directory structure)
    full_base_name = os.path.join(base_path, folder_name)

    # Input paths for B1 to B7 bands and B10
    # print(f"Full path: {full_base_name}")

    band_paths = {
        'B1': f'{full_base_name}_SR_B1.TIF',
        'B2': f'{full_base_name}_SR_B2.TIF',
        'B3': f'{full_base_name}_SR_B3.TIF',
        'B4': f'{full_base_name}_SR_B4.TIF',
        'B5': f'{full_base_name}_SR_B5.TIF',
        'B6': f'{full_base_name}_SR_B6.TIF',
        'B7': f'{full_base_name}_SR_B7.TIF',
        'B10': f'{full_base_name}_ST_B10.TIF'  # Path for the temperature band
    }

    # Initialize a dictionary to store SR and ST values for each band
    reflectance_data = {}

    # Loop through bands and store surface reflectance or temperature values
    for band_name, band_path in band_paths.items():
        try:
            if band_name == 'B10':
                temp_kelvin, temp_celsius = read_band_and_convert_to_temp(band_path, pixel_x, pixel_y)
                reflectance_data[band_name] = {
                    'Surface Temperature (K)': temp_kelvin,
                    'Surface Temperature (Celcius)': temp_celsius
                }
            else:
                sr_value = read_band_and_convert_to_sr(band_path, pixel_x, pixel_y)
                reflectance_data[band_name] = {'Surface Reflectance': sr_value}
        except Exception as e:
            reflectance_data[band_name] = f'Error: {e}'

    return reflectance_data

current_directory = os.getcwd()  # Get the current working directory
root_directory = os.path.dirname(current_directory)  # Move up one directory
fetch_reflectance(root_directory, 3000, 3000)