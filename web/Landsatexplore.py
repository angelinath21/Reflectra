import streamlit as st
import time
import requests
from geopy.distance import geodesic
from datetime import datetime
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# Define the base URL and your API key
api_key = ""
google_api_key = ""
base_url = "https://api.n2yo.com/rest/v1/satellite/radiopasses/"
observer_lat=0
observer_lon=0

# Geocoding function to get latitude and longitude from an address
def get_geocoded_location(address):
    geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={google_api_key}"
    response = requests.get(geocode_url)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'OK':
            # Return only the location data
            return data['results'][0]['geometry']['location']
        else:
            st.error(f"Geocoding failed: {data['status']}")
    else:
        st.error("Failed to get geolocation data")
    return None

# Convert UTC seconds to a human-readable date-time format
def utc_to_local_time(utc_seconds):
    return datetime.utcfromtimestamp(utc_seconds).strftime('%Y-%m-%d %H:%M:%S')

# Get the satellite pass data
def get_satellite_passes(norad_id, observer_lat, observer_lon, observer_alt, number_of_days):
    request_url = f"{base_url}{norad_id}/{observer_lat}/{observer_lon}/{observer_alt}/{number_of_days}/40/&apiKey={api_key}"
    response = requests.get(request_url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        st.error("Error fetching satellite data")
        return None

# Notify user if satellite pass is within the time window
def is_within_time_window(current_time, pass_time, window_minutes):
    time_difference = (pass_time - current_time).total_seconds() / 60
    return 0 <= time_difference <= window_minutes

# Function to send email notification
def send_email(subject, body, user_email):
    sender_email = "dummydummytestest@gmail.com"
    password = "dbgh xqqw bjjc vqci"  # Use app password for Gmail if 2FA is enabled

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = user_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, user_email, msg.as_string())
        st.success("Email sent successfully")
    except Exception as e:
        st.error(f"Error sending email: {e}")


st.set_page_config(layout="wide")

# Streamlit app structure
st.title("Reflectra")

# Select the satellite
message_placeholder = st.empty()

st.write("Select the satellite:")
landsat_8 = st.checkbox("Landsat 8 (NORAD ID: 39084)")
landsat_9 = st.checkbox("Landsat 9 (NORAD ID: 49260)")

# Determine which NORAD ID to use based on checkbox
norad_id = None
if landsat_8 and landsat_9:
    message_placeholder.error("Please select only one satellite.")
elif landsat_8:
    norad_id = 39084
elif landsat_9:
    norad_id = 49260

container = st.container()

col1, col2, col3 = st.columns(3)

with col2:
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

with col3:
    observer_alt = st.number_input("Enter your altitude (meters above sea level)", value=1)
    number_of_days = st.number_input("Enter number of days to track passes", min_value=1, max_value=10, value=2)
    time_window = st.number_input("Enter time window for notification (in minutes)", min_value=1, value=10)

    # Input user email
    user_email = st.text_input("Enter your email address")
    if norad_id and st.button("Calculate Next Pass"):

        if landsat_8 and landsat_9:
            message_placeholder.error("Please select only one satellite.")

        # Fetch satellite pass data
        passes_data = get_satellite_passes(norad_id, observer_lat, observer_lon, observer_alt, number_of_days)

        if passes_data:
            st.write(f"Satellite Name: {passes_data['info']['satname']}")
            st.write(f"Transaction Count: {passes_data['info']['transactionscount']}")
            st.write(f"Number of Passes: {passes_data['info']['passescount']}")
            p1 = passes_data['passes'][0]

            # Start the loop
            st.session_state.is_running = True
            email_sent = False

            while st.session_state.is_running:
                p1 = passes_data['passes'][0]
                container.write("### Next Pass")
                container.write(f"Start Time (UTC): {utc_to_local_time(p1['startUTC'])}")
                container.write(f"Start Azimuth: {p1['startAz']}&deg; ({p1['startAzCompass']})")
                container.write(f"Max Elevation: {p1['maxEl']}&deg; at {utc_to_local_time(p1['maxUTC'])} (Azimuth: {p1['maxAz']}&deg; - {p1['maxAzCompass']})")
                container.write(f"End Time (UTC): {utc_to_local_time(p1['endUTC'])}")
                container.write(f"End Azimuth: {p1['endAz']}&deg; ({p1['endAzCompass']})")

                # Current time to compare with pass times
                current_time = datetime.utcnow()
                max_elevation_time = datetime.utcfromtimestamp(p1['maxUTC'])

                # Notify user if the pass is within the user-defined time window
                if is_within_time_window(current_time, max_elevation_time, time_window):
                    if not email_sent:  # Check if email has already been sent
                        container.success(f"Satellite pass will occur within {time_window} minutes!")
                        email_subject = "Satellite Pass Notification"
                        email_body = f"The satellite pass will occur within {time_window} minutes!\n\nDetails:\nStart Time (UTC): {utc_to_local_time(p1['startUTC'])}"
                        send_email(email_subject, email_body, user_email)
                        email_sent = True  # Set flag to true to prevent resending
                else:
                    email_sent = False
                    time_until_pass = (max_elevation_time - current_time).total_seconds() / 60
                    container.write(f"Satellite pass will occur in {time_until_pass:.2f} minutes. Not within the {time_window} minute window yet.")

                time.sleep(60)  # Wait for a minute before checking again
        else:
            st.error("No data available or an error occurred.")

with col1:
    if location_choice == "Enter Coordinates" or (location_choice == "Enter Address" and 'observer_lat' in locals()):
        location_data = pd.DataFrame({'lat': [observer_lat], 'lon': [observer_lon]})
        st.map(location_data)

st.markdown("""
<style>
   h1 {
      text-align: left;
      text-transform: uppercase;
   }
</style>
""", unsafe_allow_html=True)
