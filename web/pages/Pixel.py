import streamlit as st
import numpy as np
import zipfile
import io
import os
import pandas as pd  # For creating the CSV
from PIL import Image, ImageDraw
from streamlit_drawable_canvas import st_canvas


def find_csv_in_directory(directory):
    csv_file_path = None
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".csv"):
                csv_file_path = os.path.join(root, file)
                break  # Stop after finding the first CSV file
        if csv_file_path:
            break
    return csv_file_path

def create_zip_file(image_paths):
    # Create an in-memory zip file
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for image_path in image_paths:
            image_name = os.path.basename(image_path)  # Get the filename from the path
            zip_file.write(image_path, image_name)  # Add the image to the zip file

    # Seek to the beginning of the BytesIO object
    zip_buffer.seek(0)
    return zip_buffer

# Function to extract a 3x3 grid of RGB values around the target pixel
def extract_3x3_rgb_grid(img_array, center_x, center_y):
    """Extract a 3x3 RGB grid centered on (center_x, center_y) from the image array."""
    img_height, img_width, _ = img_array.shape
    grid = []

    # Fill the 3x3 grid with RGB values (handle edge cases)
    for i in range(-1, 2):
        row = []
        for j in range(-1, 2):
            x = center_x + j
            y = center_y + i
            if 0 <= x < img_width and 0 <= y < img_height:
                row.append(tuple(img_array[y, x]))  # Append the RGB values as a tuple
            else:
                row.append((0, 0, 0))  # Use black color for out-of-bounds pixels
        row = [f"({color[0]},{color[1]},{color[2]})" for color in row]  # Format as (R,G,B)
        grid.append(row)
    return grid


def get_scaled_pixel():
    # Retrieve scaled_x and scaled_y from session state
    scaled_x = st.session_state.get("scaled_x", None)  # Use None as a default value if not set
    scaled_y = st.session_state.get("scaled_y", None)
    return scaled_x, scaled_y


# Function to draw the 3x3 grid using PIL
def draw_3x3_grid_image(grid, highlight_center=True):
    """Create an image to represent the 3x3 grid with RGB values."""
    block_size = 50  # Size of each grid block
    grid_img_size = (block_size * 3, block_size * 3)
    grid_img = Image.new("RGB", grid_img_size, (255, 255, 255))  # Create a blank white image
    draw = ImageDraw.Draw(grid_img)

    # Draw each grid cell with the corresponding RGB value
    for i, row in enumerate(grid):
        for j, color in enumerate(row):
            top_left = (j * block_size, i * block_size)
            bottom_right = ((j + 1) * block_size, (i + 1) * block_size)
            rgb_tuple = tuple(map(int, color.strip("()").split(',')))
            draw.rectangle([top_left, bottom_right], fill=rgb_tuple, outline=(0, 0, 0))

            # Highlight the center cell if needed
            if highlight_center and i == 1 and j == 1:
                draw.rectangle([top_left, bottom_right], outline=(255, 255, 255), width=5)  # Highlight with white color

    return grid_img

def find_images(results_dir):
    image_path_1 = None
    image_path_2 = None

    # Loop through all folders in results_dir
    for folder_name in os.listdir(results_dir):
        folder_path = os.path.join(results_dir, folder_name)

        # Check if the folder is a directory
        if os.path.isdir(folder_path):
            print(f"Searching in folder: {folder_path}")

            # Look for image files in the current folder
            for file_name in os.listdir(folder_path):
                if file_name.startswith("summary") and file_name.endswith(".jpg"):
                    image_path_1 = os.path.join(folder_path, file_name)
                    print(f"Found summary image: {image_path_1}")
                elif file_name.startswith("surface_reflectance") and file_name.endswith(".jpg"):
                    image_path_2 = os.path.join(folder_path, file_name)
                    print(f"Found surface reflectance image: {image_path_2}")

                # Break the loop if both images are found
                if image_path_1 and image_path_2:
                    break

        # Stop searching further if both images are found
        if image_path_1 and image_path_2:
            break

    return image_path_1, image_path_2

def run_streamlit(root_directory):
    st.title("Reflectra DataBoard")

    results_dir = os.path.join(root_directory, "landsatTest/results")
    tif_file_path = None

    for folder_name in os.listdir(results_dir):
        folder_path = os.path.join(results_dir, folder_name)

        # Check if the folder is a directory
        if os.path.isdir(folder_path):
            print(f"Processing folder: {folder_path}")

            # Look for the .TIF file beginning with 'stacked_img'
            for file_name in os.listdir(folder_path):
                if file_name.startswith("stacked_img_") and file_name.endswith(".tif"):
                    tif_file_path = os.path.join(folder_path, file_name)
                    print(f"Found TIF file: {tif_file_path}")
                    break  # Stop after finding the first match

            # If the .TIF file is found, proceed with further processing
            if tif_file_path:
                #st.write(f"Found TIF file: {tif_file_path}")
                continue
            else:
                st.success(f"File '{tif_file_path}' found!")

    img = Image.open(tif_file_path)
    original_width, original_height = img.size
    img = img.convert("RGB")

    max_display_width = 600
    display_ratio = min(max_display_width / original_width, 0.5)
    display_width = int(original_width * display_ratio)
    display_height = int(original_height * display_ratio)

    # Initialize session state for storing all points
    if "points" not in st.session_state:
        st.session_state["points"] = []

    # Prepare the initial drawing based on all saved points
    initial_drawing = {"objects": []}
    for point in st.session_state["points"]:
        scaled_x, scaled_y, _, _ = point
        initial_drawing["objects"].append(
            {
                "type": "circle",
                "left": scaled_x,
                "top": scaled_y,
                "width": 10,
                "height": 10,
                "fill": "rgba(255, 165, 0, 0.8)",  # Highlight with orange
            }
        )

    # Display the image on a canvas for clickable interaction using the resized dimensions
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=2,
        background_image=img,
        update_streamlit=True,
        height=display_height,
        width=display_width,
        drawing_mode="point",
        initial_drawing=initial_drawing,
        key="canvas",
    )

    img_array = np.array(img)

    # Check if there is any click registered and store the most recent point
    if canvas_result.json_data is not None and len(canvas_result.json_data["objects"]) > 0:
        obj = canvas_result.json_data["objects"][-1]
        scaled_x = int(obj["left"])
        scaled_y = int(obj["top"])

        orig_x = int((scaled_x / display_width) * original_width)
        orig_y = int((scaled_y / display_height) * original_height)

        # Add the new point to the stack and update session state
        new_point = (scaled_x, scaled_y, orig_x, orig_y)
        if new_point not in st.session_state["points"]:
            st.session_state["points"].append(new_point)
    image_path_1, image_path_2 = find_images(results_dir)
    # Display the 3x3 grid and selected pixel information side by side
    if st.session_state["points"]:
        # Use the latest point from the stack for display
        scaled_x, scaled_y, orig_x, orig_y = st.session_state["points"][-1]
        if 0 <= orig_x < original_width and 0 <= orig_y < original_height:
            # Create two columns for side-by-side layout
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"### Selected Pixel Information:")
                st.write(f"**Scaled Coordinates** (Canvas Size): X = {scaled_x}, Y = {scaled_y}")
                st.write(f"**Original Coordinates** (Image Size): X = {orig_x}, Y = {orig_y}")

                rgb_grid = extract_3x3_rgb_grid(img_array, orig_x, orig_y)
                st.write("### 3x3 RGB Grid Around the Selected Pixel:")

                # Display the RGB values as a table
                for i, row in enumerate(rgb_grid):
                    st.write(f"Row {i + 1}: {row}")

            with col2:
                # Draw and display the 3x3 RGB grid image
                grid_img = draw_3x3_grid_image(rgb_grid)
                st.image(grid_img, caption="3x3 RGB Grid Map Around the Target Pixel", use_column_width=True)

            # Display SR graph and summary data


            # Check if images exist before displaying
            if os.path.exists(image_path_1) and os.path.exists(image_path_2):
                st.write("### Surface Reflectance and Surface Temperature Data + Scene Metadata")

                # Display images below the grid
                col3, col4 = st.columns(2)
                with col3:
                    img1 = Image.open(image_path_1)
                    st.image(img1, caption="Scene Metadata", use_column_width=True)

                with col4:
                    img2 = Image.open(image_path_2)
                    st.image(img2, caption="Surface Reflectance and Surface Temperature Data", use_column_width=True)
            else:
                st.warning("Image paths not found.")
    csv_file = find_csv_in_directory(results_dir)

    if image_path_1 and image_path_2 and tif_file_path and csv_file:
        image_paths = [tif_file_path, image_path_1, image_path_2, csv_file]  # Collect all image paths

        # Generate the zip file containing the images
        zip_buffer = create_zip_file(image_paths)

        # Display the download button for the zip file
        filename =os.path.basename(image_path_1).replace("summary_", "")
        filename = filename.replace(".jpg",".zip")
        print(filename)
        st.download_button(
            label="Download All files as ZIP",
            data=zip_buffer,
            file_name=filename,
            mime="application/zip"
        )
    else:
        st.warning("Cannot generate download. Make sure all images are available.")



current_directory = os.getcwd()  # Get the current working directory
root_directory = os.path.dirname(current_directory)  # Move up one directory
run_streamlit(root_directory)