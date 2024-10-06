import os
import pandas as pd
import json
import matplotlib.pyplot as plt


def display_summary_data(json_file_path, results_folder):
    """Displays all attributes and their values from the SUMMARY JSON file."""
    # Read the JSON file
    try:
        with open(json_file_path, 'r') as json_file:
            summary_data = json.load(json_file)
    except FileNotFoundError:
        print(f"Error: The file '{json_file_path}' was not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: The file '{json_file_path}' is not a valid JSON file.")
        return

    # Extract image attributes
    image_attributes = [
        ("Spacecraft ID", summary_data.get('image_attributes', {}).get('spacecraft_id', None)),
        ("Sensor ID", summary_data.get('image_attributes', {}).get('sensor_id', None)),
        ("Station ID", summary_data.get('image_attributes', {}).get('station_id', None)),
        ("Date Acquired", summary_data.get('image_attributes', {}).get('date_acquired', None)),
        ("Time Acquired", summary_data.get('image_attributes', {}).get('time_acquired', None)),
        ("WRS Type", summary_data.get('image_attributes', {}).get('wrs_type', None)),
        ("WRS Path", summary_data.get('image_attributes', {}).get('wrs_path', None)),
        ("WRS Row", summary_data.get('image_attributes', {}).get('wrs_row', None)),
        ("Image Quality", summary_data.get('image_attributes', {}).get('image_quality', None)),
        ("Cloud Cover", summary_data.get('image_attributes', {}).get('cloud_cover', None)),
        ("Cloud Cover Land", summary_data.get('image_attributes', {}).get('cloud_cover_land', None)),
        ("Sun Azimuth", summary_data.get('image_attributes', {}).get('sun_azimuth', None)),
        ("Sun Elevation", summary_data.get('image_attributes', {}).get('sun_elevation', None)),
        ("Earth-Sun Distance", summary_data.get('image_attributes', {}).get('earth_sun_distance', None)),
    ]

    # Extract coordinates
    coordinates = [
        ("Upper Left Latitude", summary_data.get('coordinates', {}).get('UL_lat', None)),
        ("Upper Left Longitude", summary_data.get('coordinates', {}).get('UL_lon', None)),
        ("Upper Right Latitude", summary_data.get('coordinates', {}).get('UR_lat', None)),
        ("Upper Right Longitude", summary_data.get('coordinates', {}).get('UR_lon', None)),
        ("Lower Left Latitude", summary_data.get('coordinates', {}).get('LL_lat', None)),
        ("Lower Left Longitude", summary_data.get('coordinates', {}).get('LL_lon', None)),
        ("Lower Right Latitude", summary_data.get('coordinates', {}).get('LR_lat', None)),
        ("Lower Right Longitude", summary_data.get('coordinates', {}).get('LR_lon', None)),
    ]

    # Create DataFrames for the tables
    df_image_attributes = pd.DataFrame(image_attributes, columns=["Attribute", "Value"])
    df_coordinates = pd.DataFrame(coordinates, columns=["Attribute", "Value"])

    # Check if there are any attributes to display
    if df_image_attributes.empty and df_coordinates.empty:
        print("No attributes found in the JSON file.")
        return

    # Plot the tables
    plt.figure(figsize=(8, 10))

    # Display Image Attributes Table
    if not df_image_attributes.empty:
        plt.subplot(2, 1, 1)  # 2 rows, 1 column, 1st subplot
        plt.axis('tight')
        plt.axis('off')
        table_image_attributes = plt.table(cellText=df_image_attributes.values,
                                           colLabels=df_image_attributes.columns,
                                           loc='center', cellLoc='left')
        table_image_attributes.auto_set_font_size(False)
        table_image_attributes.set_fontsize(12)
        table_image_attributes.scale(1.5, 1.5)

    # Display Coordinates Table
    if not df_coordinates.empty:
        plt.subplot(2, 1, 2)  # 2 rows, 1 column, 2nd subplot
        plt.axis('tight')
        plt.axis('off')
        table_coordinates = plt.table(cellText=df_coordinates.values, colLabels=df_coordinates.columns,
                                      loc='center', cellLoc='left')
        table_coordinates.auto_set_font_size(False)
        table_coordinates.set_fontsize(12)
        table_coordinates.scale(1.5, 1.5)

    plt.tight_layout()

    # Save the plot as a JPG file in the specific folder
    plot_filename = os.path.join(results_folder, f'summary_{os.path.basename(os.path.dirname(json_file_path))}.jpg')
    plt.savefig(plot_filename, format='jpg', dpi=300, bbox_inches='tight')
    print(f"Plot saved as: {plot_filename}")  # Added confirmation message
    plt.close()  # Close the plot to avoid displaying it during batch processing


def run_data_visualisation_summary(root_directory):
    """Processes all folders within the specified root folder, extracting data from SUMMARY JSON files."""
    # Construct the full path to the raw_data folder
    raw_data_folder = os.path.join(root_directory, 'raw_data')

    # Check if the raw data folder exists
    if not os.path.exists(raw_data_folder):
        print(f"The specified folder '{raw_data_folder}' does not exist.")
        return

    # Traverse through each folder in raw_data
    for folder_name in os.listdir(raw_data_folder):
        folder_path = os.path.join(raw_data_folder, folder_name)

        # Check if the folder is a directory
        if os.path.isdir(folder_path):
            print(f"Processing folder: {folder_path}")

            # Construct the JSON file path
            json_file_name = f"{folder_name}_SUMMARY.json"
            json_file_path = os.path.join(folder_path, json_file_name)

            # Check if the JSON file exists
            if not os.path.exists(json_file_path):
                print(f"Warning: JSON file '{json_file_name}' does not exist in '{folder_path}'.")
                continue

            # Define the results directory based on the current folder name
            results_folder = os.path.join(root_directory, 'results', folder_name)

            # Create the results directory if it doesn't exist
            os.makedirs(results_folder, exist_ok=True)

            # Display the summary data from the JSON file
            display_summary_data(json_file_path, results_folder)


current_directory = os.getcwd()  # Get the current working directory
root_directory = os.path.dirname(current_directory)  # Move up one directory
run_data_visualisation_summary(root_directory)
