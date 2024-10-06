import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import json

def visualize_data(json_file_path, root_directory, results_folder):
    """Visualizes the data from the given JSON file."""
    # Read the JSON file
    try:
        with open(json_file_path, 'r') as json_file:
            band_data = json.load(json_file)
    except FileNotFoundError:
        print(f"Error: The file '{json_file_path}' was not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: The file '{json_file_path}' is not a valid JSON file.")
        return

    # Midpoint wavelengths for each band (in micrometers)
    wavelengths = [
        (0.43, 0.45), (0.45, 0.51), (0.53, 0.59),
        (0.64, 0.67), (0.85, 0.88), (1.57, 1.65), (2.11, 2.29)
    ]

    # Define band names
    bands = ['B1 - Coastal aerosol', 'B2 - Blue', 'B3 - Green',
             'B4 - Red', 'B5 - NIR', 'B6 - SWIR 1', 'B7 - SWIR 2']

    # Extract SR values for bands 1-7
    sr_values = [
        band_data.get('B1', {}).get('Surface Reflectance', None),
        band_data.get('B2', {}).get('Surface Reflectance', None),
        band_data.get('B3', {}).get('Surface Reflectance', None),
        band_data.get('B4', {}).get('Surface Reflectance', None),
        band_data.get('B5', {}).get('Surface Reflectance', None),
        band_data.get('B6', {}).get('Surface Reflectance', None),
        band_data.get('B7', {}).get('Surface Reflectance', None)
    ]

    # Extract surface temperature for Band 10
    band_10_temperature_K = band_data.get('B10', {}).get('Surface Temperature (K)', None)
    band_10_temperature_C = band_data.get('B10', {}).get('Surface Temperature (Celcius)', None)

    # Create DataFrame for plotting
    df = pd.DataFrame({
        'Band': bands,
        'Wavelength': wavelengths,
        'Surface Reflectance': sr_values
    })

    # Plotting
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x=[(low + high) / 2 for low, high in wavelengths], y='Surface Reflectance',
                 marker='o')

    plt.title('Surface Reflectance (Bands 1 - 7)')
    plt.ylabel('Reflectance Value')
    plt.xlabel('Wavelength (micrometers)')
    plt.tight_layout()  # Automatically adjust space

    # Table for Surface Reflectance
    surface_reflectance_data = [[band, f"{wavelength[0]} - {wavelength[1]}", f"{sr_value:.4f}" if sr_value is not None else "N/A"]
                                for band, wavelength, sr_value in zip(bands, wavelengths, sr_values)]

    # Table for Surface Temperature
    surface_temperature_data = [
        ["B10 - Thermal Infrared 1", "10.60 - 11.19", f"{band_10_temperature_K:.2f} K / {band_10_temperature_C:.2f} °C" if band_10_temperature_K is not None and band_10_temperature_C is not None else "N/A"]
    ]

    # Combine both tables
    table_data = [["Surface Reflectance", "", ""], ["Band", "Wavelength (μm)", "Value"]] + surface_reflectance_data
    table_data += [["", "", ""]]  # Spacer row between two tables
    table_data += [["Surface Temperature", "", ""], ["Band", "Wavelength (μm)", "Value"]] + surface_temperature_data

    # Display the table below the graph
    table = plt.table(cellText=table_data, colWidths=[0.3, 0.3, 0.3], loc="bottom", cellLoc="center", bbox=[0.0, -0.6, 1, 0.5])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.2)

    # Hide the borders of the table
    for key, cell in table.get_celld().items():
        cell.set_edgecolor('none')  # Set the edge color to none to hide borders

    # Adjust layout to fit the table
    plt.subplots_adjust(bottom=0.3)  # Reduced bottom margin to bring the table closer

    # Save the plot as a JPG file
    plot_filename = os.path.join(results_folder, f'surface_reflectance_{os.path.basename(os.path.dirname(json_file_path))}.jpg')
    plt.savefig(plot_filename, format='jpg', dpi=300, bbox_inches='tight')
    plt.close()  # Close the plot to avoid displaying it during batch processing

def run_data_visualisation_sr_st(root_directory):
    """Processes all folders within the specified root folder, extracting data from MTL JSON files."""
    # Construct the full path to the raw_data folder
    raw_data_folder = os.path.join(root_directory, 'raw_data')

    # Print the constructed path for debugging
    print(f"Looking for raw_data folder at: {raw_data_folder}")

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

            # Construct the JSON file path
            json_file_name = f"{folder_name}_SR_ST_values.json"
            json_file_path = os.path.join(folder_path, json_file_name)

            # Check if the JSON file exists
            if not os.path.exists(json_file_path):
                print(f"Warning: JSON file '{json_file_name}' does not exist in '{folder_path}'.")
                continue

            # Define the results directory based on the current folder name
            results_folder = os.path.join(root_directory, 'results', folder_name)

            # Create the results directory if it doesn't exist
            os.makedirs(results_folder, exist_ok=True)

            # Visualize the data from the JSON file
            visualize_data(json_file_path, root_directory, results_folder)

            print(f"Visualization completed for {folder_name}.\n")

# Execute the script
current_directory = os.getcwd()  # Get the current working directory
root_directory = os.path.dirname(current_directory)  # Move up one directory
run_data_visualisation_sr_st(root_directory)
