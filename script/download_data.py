import json
import os

from landsatxplore.api import API
from landsatxplore.earthexplorer import EarthExplorer
import landsatxplore.errors
from datetime import datetime


def download_landsat_data(username, password, landsat_product_id, latitude, longitude, start_date, end_date,
                          cloud_cover, root_directory, most_recent):
    # Scene footprints
    output_directory = os.path.join(root_directory, 'raw_data')
    scene_footprints_directory = os.path.join(root_directory, 'scene_footprints')

    # Initialize API and EarthExplorer instances
    api = API(username, password)
    ee = EarthExplorer(username, password)

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    if most_recent:
        start_date = '2024-01-01'
        today_date = datetime.today().date()
        end_date = today_date.strftime('%Y-%m-%d')  # Format it as YYYY-MM-DD

    # Search for the specified Landsat scene
    scenes = api.search(
        dataset=landsat_product_id,
        latitude=latitude,
        longitude=longitude,
        start_date=start_date,
        end_date=end_date,
        max_cloud_cover=cloud_cover
    )

    print(f"{len(scenes)} scenes found.")

    if most_recent:
        if scenes:
            most_recent_scene = scenes[0]  # Get the first (most recent) scene
            print(f"Most recent scene found: {most_recent_scene}")

            # Process the most recent scene
            acquisition_date = most_recent_scene['acquisition_date'].strftime('%Y-%m-%d')
            product_id = most_recent_scene['landsat_product_id']

            print(f"Acquisition Date: {acquisition_date}, Product ID: {product_id}")

            # Write scene footprints to disk in the output directory
            geojson_filename = os.path.join(scene_footprints_directory,
                                            f"{product_id}.geojson")  # Save in scene footprints directory
            with open(geojson_filename, "w") as f:
                json.dump(most_recent_scene['spatial_coverage'].__geo_interface__, f)

            # Download surface reflectance data
            try:
                print(f"Downloading surface reflectance data for scene {product_id}...")
                ee.download(most_recent_scene['entity_id'], output_dir=output_directory)
                print(f"Surface reflectance data for {product_id} downloaded successfully.")

                # Extract LEVEL1_MIN_MAX_REFLECTANCE from the downloaded JSON file
                reflectance_file_path = os.path.join(output_directory,
                                                     f"{product_id}.json")  # Adjust the filename accordingly
                if os.path.exists(reflectance_file_path):  # Ensure the file exists
                    with open(reflectance_file_path, 'r') as reflectance_file:
                        reflectance_data = json.load(reflectance_file)
                        min_max_reflectance = reflectance_data.get("LEVEL1_MIN_MAX_REFLECTANCE", {})
                        return min_max_reflectance  # Return the extracted reflectance data
                else:
                    print(f"Warning: Reflectance file '{reflectance_file_path}' not found after download.")

            except landsatxplore.errors.EarthExplorerError as e:
                print(f"Error downloading scene {product_id}: {e}")

        else:
            print("No scenes found for the most recent query.")

    else:
        # Normal processing for all scenes
        for scene in scenes:
            acquisition_date = scene['acquisition_date'].strftime('%Y-%m-%d')
            product_id = scene['landsat_product_id']

            if product_id == scene['landsat_product_id']:
                print(f"Acquisition Date: {acquisition_date}, Product ID: {product_id}")

                # Write scene footprints to disk in the output directory
                geojson_filename = os.path.join(scene_footprints_directory,
                                                f"{product_id}.geojson")  # Save in scene footprints directory
                with open(geojson_filename, "w") as f:
                    json.dump(scene['spatial_coverage'].__geo_interface__, f)

                # Download surface reflectance data
                try:
                    print(f"Downloading surface reflectance data for scene {product_id}...")
                    ee.download(scene['entity_id'], output_dir=output_directory)
                    print(f"Surface reflectance data for {product_id} downloaded successfully.")

                    # Extract LEVEL1_MIN_MAX_REFLECTANCE from the downloaded JSON file
                    reflectance_file_path = os.path.join(output_directory,
                                                         f"{product_id}.json")  # Adjust the filename accordingly
                    if os.path.exists(reflectance_file_path):  # Ensure the file exists
                        with open(reflectance_file_path, 'r') as reflectance_file:
                            reflectance_data = json.load(reflectance_file)
                            min_max_reflectance = reflectance_data.get("LEVEL1_MIN_MAX_REFLECTANCE", {})
                            return min_max_reflectance  # Return the extracted reflectance data
                    else:
                        print(f"Warning: Reflectance file '{reflectance_file_path}' not found after download.")

                except landsatxplore.errors.EarthExplorerError as e:
                    print(f"Error downloading scene {product_id}: {e}")

    # Logout from both API and EarthExplorer
    api.logout()
    ee.logout()

    return "No data was found for the given Landsat parameters"  # Return None if no data was found for the given Landsat ID
