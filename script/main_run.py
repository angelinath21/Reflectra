import os
from download_data import download_landsat_data
from extract_data import extract_data
from process_data import process_landsat_data
from script.fetch_reflectance import fetch_reflectance
from script.process_data import process_data
from script.visualise_data import visualize_data
from stack_img import stack_image
from visualise_data import run_data_visualisation_sr_st
from visualise_img_attributes import run_data_visualisation_summary
from create_downloadable import process_data_and_convert_to_csv
from web_dev_pixel import get_scaled_pixel
# import API details

def main():
    # API KEY - change to your own API key.
    username = 'YOUR_API_USERNAME'
    password = 'YOUR_API_KEY'

    # LANDSAT DATA PARAMETERS
    landsat_product_id = 'landsat_ot_c2_l2'
    latitude = -38.1477
    longitude = 145.3764
    start_date = '2023-01-01'  #YYYY-MM-DD
    end_date = '2023-10-01'
    cloud_cover = 5

    # OUTPUT & CURRENT DIRECTORY
    current_directory = os.getcwd()  # Get the current working directory
    root_directory = os.path.dirname(current_directory)  # Move up one directory
    print(root_directory)

    # 1. Download Landsat Data with given parameters
    # most_recent = False  # Bool to determine if we need most recent data
    # download_landsat_data(username, password, landsat_product_id, latitude, longitude, start_date, end_date, cloud_cover, root_directory, most_recent)

    # 2. Extract Data
    # extract_data(root_directory)

    # 3. Processs Data
    # process_data(root_directory)

    # 4. Fetch reflectance data
    pixel_x, pixel_y = get_scaled_pixel()
    fetch_reflectance(root_directory, pixel_x, pixel_y)

    # 5. Stack image
    stack_image(root_directory)

    # 6. Visualise data
    run_data_visualisation_sr_st(root_directory)

    # 7. Process Data (get SR, radioisometric scaling factors, image attributes, lat & long)
    process_landsat_data(root_directory)

    # 8. Visualise Data and store them in /results
    run_data_visualisation_sr_st(root_directory)
    run_data_visualisation_summary(root_directory)

    # 9. Create downloadables
    process_data_and_convert_to_csv(root_directory)

    print("All processes completed.")

if __name__ == "__main__":
    main()