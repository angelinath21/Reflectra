import os
import json
from datetime import datetime


def find_mtl_json(folder_path):
    """Finds a file containing 'MTL' in its name in the given folder path."""
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if 'MTL' in file and file.endswith('.json'):
                return os.path.join(root, file)  # Return the first matching file
    return None


def read_json_file(file_path):
    """Reads a JSON file and returns its content."""
    with open(file_path, 'r') as file:
        return json.load(file)


def extract_image_attributes(data):
    """Extracts image attributes from the JSON data."""
    image_attributes = data["LANDSAT_METADATA_FILE"].get("IMAGE_ATTRIBUTES", {})

    return {
        "spacecraft_id": image_attributes.get("SPACECRAFT_ID"),
        "sensor_id": image_attributes.get("SENSOR_ID"),
        "station_id": image_attributes.get("STATION_ID"),
        "date_acquired": image_attributes.get("DATE_ACQUIRED"),
        "time_acquired": image_attributes.get("SCENE_CENTER_TIME"),
        "wrs_type": image_attributes.get("WRS_TYPE"),
        "wrs_path": image_attributes.get("WRS_PATH"),
        "wrs_row": image_attributes.get("WRS_ROW"),
        "image_quality": image_attributes.get("IMAGE_QUALITY"),
        "cloud_cover": image_attributes.get("CLOUD_COVER"),
        "cloud_cover_land": image_attributes.get("CLOUD_COVER_LAND"),
        "sun_azimuth": image_attributes.get("SUN_AZIMUTH"),
        "sun_elevation": image_attributes.get("SUN_ELEVATION"),
        "earth_sun_distance": image_attributes.get("EARTH_SUN_DISTANCE")
    }


def extract_coordinates(data):
    """Extracts corner coordinates from the JSON data."""
    coordinates = {}

    # Accessing the correct path for corner coordinates
    projection_attributes = data["LANDSAT_METADATA_FILE"].get("PROJECTION_ATTRIBUTES", {})

    if projection_attributes:
        for corner in ['UL', 'UR', 'LL', 'LR']:
            lat_key = f'CORNER_{corner}_LAT_PRODUCT'
            lon_key = f'CORNER_{corner}_LON_PRODUCT'

            lat_value = projection_attributes.get(lat_key)
            lon_value = projection_attributes.get(lon_key)

            # Check if values exist before converting
            if lat_value is not None and lon_value is not None:
                coordinates[f"{corner}_lat"] = float(lat_value)
                coordinates[f"{corner}_lon"] = float(lon_value)
            else:
                print(f"Warning: {lat_key} or {lon_key} is missing.")

    return coordinates


def write_extracted_data_to_json(extracted_data, output_file):
    """Writes the extracted data to a JSON file."""
    with open(output_file, 'w') as json_file:
        json.dump(extracted_data, json_file, indent=4)
    print(f"Extracted data has been written to {output_file}")


def run_process_data(folder_path):
    mtl_file_path = find_mtl_json(folder_path)

    if mtl_file_path:
        print(f"Found JSON file containing 'MTL' at: {mtl_file_path}")

        # Read the JSON file
        data = read_json_file(mtl_file_path)

        # Extract relevant data
        image_attributes = extract_image_attributes(data)
        coordinates = extract_coordinates(data)

        # Create a dictionary to store all data
        extracted_data = {
            "image_attributes": image_attributes,
            "coordinates": coordinates,
        }

        # Print extracted data (optional)
        print("\nIMAGE ATTRIBUTES")
        for key, value in image_attributes.items():
            print(f"{key.replace('_', ' ').title()}: {value}")

        print("\nCOORDINATES")
        for key, value in coordinates.items():
            print(f"{key}: {value}")

        # Create output file name by appending '_SUMMARY' to the folder name
        output_file_name = f"{os.path.basename(folder_path)}_SUMMARY.json"
        output_file_path = os.path.join(folder_path, output_file_name)

        # Write the extracted data to a JSON file
        write_extracted_data_to_json(extracted_data, output_file_path)

        # Return the extracted data
        return extracted_data
    else:
        print("No JSON file containing 'MTL' found in the specified folder.")
        return None


def process_data(root_folder):
    """Processes all folders within the specified root folder, extracting data from MTL JSON files."""
    # Construct the full path to the raw_data folder
    raw_data_folder = os.path.join(root_folder, 'raw_data')

    # Check if the raw data folder exists
    if not os.path.exists(raw_data_folder):
        print(f"The specified folder '{raw_data_folder}' does not exist.")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Contents of the parent directory: {os.listdir(os.path.dirname(raw_data_folder))}")
        return

    # Traverse through each folder in raw_data
    for folder_name in os.listdir(raw_data_folder):
        folder_path = os.path.join(raw_data_folder, folder_name)

        # Check if the folder is a directory
        if os.path.isdir(folder_path):
            print(f"Processing folder: {folder_path}")
            extracted_data = run_process_data(folder_path)

            if extracted_data:
                print(f"Data extracted successfully from {folder_name}.\n")
            else:
                print(f"No MTL JSON found in {folder_name}.\n")


# Call the process_data function with the absolute path to the script's parent directory
def process_landsat_data(root_directory):
    process_data(root_directory)

current_directory = os.getcwd()  # Get the current working directory
root_directory = os.path.dirname(current_directory)  # Move up one directory
process_landsat_data(root_directory)