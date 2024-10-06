import streamlit as st
import pandas as pd
import requests
from datetime import datetime

google_api_key = ""
observer_lat = 0
observer_lon = 0


# Function to get geocoded location from address
def get_geocoded_location(address):
    geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={google_api_key}"
    response = requests.get(geocode_url)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'OK':
            return data['results'][0]['geometry']['location']
        else:
            st.error(f"Geocoding failed: {data['status']}")
    else:
        st.error("Failed to get geolocation data")
    return None


st.title("Reflectra")

# User chooses between entering coordinates or address
location_choice = st.radio("Enter your location:", ("Enter Coordinates", "Enter Address"))

if location_choice == "Enter Coordinates":
    observer_lat = st.number_input("Enter your latitude", format="%.6f", value=-37.814007)
    observer_lon = st.number_input("Enter your longitude", format="%.6f", value=144.963171)
else:
    with st.form("address_form"):
        street = st.text_input("Street")
        city = st.text_input("City")
        state = st.text_input("State")
        postal_code = st.text_input("Postal Code")
        country = st.text_input("Country")
        submitted = st.form_submit_button("Geocode Address")

    if submitted and street and city and country:
        full_address = f"{street}, {city}, {state}, {postal_code}, {country}"
        location = get_geocoded_location(full_address)

        if location:
            observer_lat = location['lat']
            observer_lon = location['lng']
            st.write(f"Geocoded Location: Latitude: {observer_lat}, Longitude: {observer_lon}")
        else:
            st.error("Failed to retrieve latitude and longitude.")

# Display map of the location
if location_choice == "Enter Coordinates" or (location_choice == "Enter Address" and 'observer_lat' in locals()):
    st.write("### Location on Map")
    location_data = pd.DataFrame({'lat': [observer_lat], 'lon': [observer_lon]})
    st.map(location_data)

# Add a section for date selection and cloud coverage
st.write("### Select Date Range and Cloud Coverage")

# Choose between "Latest Acquisition" or specifying dates
date_choice = st.radio("Choose Date Option:", ("Latest Acquisition", "Specify Dates"))

if date_choice == "Specify Dates":
    # Date range input (start and end date)
    start_date = st.date_input("Start Date", datetime.now())
    end_date = st.date_input("End Date", datetime.now())

    # Display the selected dates
    st.write(f"Selected Date Range: {start_date} to {end_date}")
else:
    st.write("Latest acquisition will be used for date filtering.")

# Slider for cloud coverage
cloud_coverage = st.slider("Cloud Coverage (%)", min_value=0, max_value=100, value=50)

# Display the selected cloud coverage
st.write(f"Selected Cloud Coverage: {cloud_coverage}%")

if st.button("Get Data"):
    st.write("Fetching data for the selected location and parameters...")