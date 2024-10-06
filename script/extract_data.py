import os
import tarfile
import shutil



# Function to extract .tar files and store them in separate directories
def extract_tar_files(directory):
    # List all the files in the directory
    for item in os.listdir(directory):
        if item.endswith(".tar"):  # Only process .tar files
            file_path = os.path.join(directory, item)
            # Create a directory based on the .tar file name (without extension)
            tar_folder = os.path.join(directory, os.path.splitext(item)[0])
            if not os.path.exists(tar_folder):
                os.makedirs(tar_folder)  # Create the folder if it doesn't exist

            try:
                # Extract the .tar file contents into the new folder
                with tarfile.open(file_path, "r") as tar:
                    print(f"Extracting {item} into {tar_folder}...")
                    tar.extractall(path=tar_folder)  # Extract contents into the new folder
                    print(f"{item} extracted successfully into {tar_folder}.")

                # Move the .tar file into the folder after extraction
                new_tar_path = os.path.join(tar_folder, item)
                shutil.move(file_path, new_tar_path)
                print(f"Moved {item} to {tar_folder}.")

            except Exception as e:
                print(f"Error extracting {item}: {e}")

def extract_data(root_directory):
    output_directory = os.path.join(root_directory, 'raw_data')
    extract_tar_files(output_directory)
    print("Extraction process complete.")
