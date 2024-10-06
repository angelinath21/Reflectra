import os
import json
import pandas as pd

def format_json_to_hierarchical_csv_with_gaps(json_file, csv_file):
    """Converts a JSON file to a hierarchical CSV format with keys grouped under categories and row gaps."""
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)

        # Prepare the CSV data with grouped categories, indentation, and gaps
        csv_data = []

        for main_category, sub_dict in data.items():
            # Add the main category as a header row
            csv_data.append([main_category, ""])  # Empty second column for separation

            # If the value is a dictionary, add sub-level items with indentation
            if isinstance(sub_dict, dict):
                for sub_key, sub_value in sub_dict.items():
                    # Indent sub-keys for hierarchical visualization and add to CSV data
                    csv_data.append([f"    {sub_key}", sub_value])  # Indented sub-key

            # Add an empty row to separate categories visually
            csv_data.append(["", ""])  # Empty row

        # Convert to DataFrame and save to CSV
        df = pd.DataFrame(csv_data, columns=["Attribute", "Value"])
        df.to_csv(csv_file, index=False)
        print(f"Converted '{json_file}' to '{csv_file}' in hierarchical format successfully.")
    except Exception as e:
        print(f"Error converting '{json_file}' to hierarchical CSV: {e}")

def process_data_and_convert_to_csv(root_folder):
    """Processes all folders within the specified root folder, extracting data from MTL JSON files and converting to CSV."""
    raw_data_folder = os.path.join(root_folder, 'raw_data')

    if not os.path.exists(raw_data_folder):
        print(f"The specified folder '{raw_data_folder}' does not exist.")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Contents of the parent directory: {os.listdir(os.path.dirname(raw_data_folder))}")
        return

    # Create a 'downloadables' folder if it doesn't exist
    downloadables_folder = os.path.join(root_folder, 'results')
    os.makedirs(downloadables_folder, exist_ok=True)

    # Traverse through each folder in raw_data
    for folder_name in os.listdir(raw_data_folder):
        folder_path = os.path.join(raw_data_folder, folder_name)

        if os.path.isdir(folder_path):
            print(f"Processing folder: {folder_path}")
            output_file_name = f"{os.path.basename(folder_path)}_SUMMARY.json"
            json_file_path = os.path.join(folder_path, output_file_name)

            if os.path.exists(json_file_path):
                # Create a subfolder for the corresponding CSV file
                subfolder_path = os.path.join(downloadables_folder, os.path.basename(folder_path))
                os.makedirs(subfolder_path, exist_ok=True)

                # Prepare the CSV file path
                csv_file_path = os.path.join(subfolder_path, f"data_{os.path.basename(folder_path)}.csv")

                # Convert JSON to a hierarchical CSV format with row gaps
                format_json_to_hierarchical_csv_with_gaps(json_file_path, csv_file_path)
            else:
                print(f"No summary JSON file found in '{folder_name}'.")

# Example usage
current_directory = os.getcwd()  # Get the current working directory
root_directory = os.path.dirname(current_directory)  # Move up one directory
process_data_and_convert_to_csv(root_directory)