## Reflectra
**NASA Space Apps 2024 Challenge - Landsat Reflectance Data**  
View our slide deck here -> [Slide Deck](https://www.canva.com/design/DAGSyfC0AVY/IIK1vEh_jwR-97L4ge-y7Q/view?utm_content=DAGSyfC0AVY&utm_campaign=designshare&utm_medium=link&utm_source=editor)

A web app tool that allows users to compare ground-based spectral measurements against satellite imagery of Landsat 8 and Landsat 9.

### Features:
1. User enters desired location by either latitude and longitude or address.
2. User can specify Landsat scene parameters, such as cloud cover and acquisition time. Acquisition time can be the most recent scene or the scenes spanning a custom time range.
3. User can view the RGB composite stack image.
4. User can get surface reflectance and surface temperature values by the pixel (30m x 30m resolution).
5. Surface reflectance and surface temperature are plotted on a graph for easy visualization.
6. User can view the scene metadata such as image attributes (World Reference System Path and Row, Satellite ID, Sensor ID, and more).
7. User can save a data bundle comprising:
   - 1 x RGB Composite Stack Image (.TIF)
   - 1 x Surface Reflectance and Surface Temperature Graph (.PNG)
   - 1 x Scene Metadata (.PNG)
   - 1 x Scene Metadata (.CSV)
8. User can track how much time it will take until the next pass for Landsat 8 and Landsat 9, given a location.
9. User can set up an email notification to serve as a reminder with a custom time window (e.g., reminder 10 minutes prior to satellite pass).

### Tools
1. Python 3.11
2. [LandsatExplore](https://pypi.org/project/landsatxplore/)
3. Google Maps and Geocoding API
4. Streamlit

### Dependencies
1. numpy
2. pandas
3. matplotlib
4. rasterio
5. GDAL
6. scikit-image
7. geopandas
8. seaborn

**By:**  
Angelina The  
Brishlav Kayastha  
Fardin Islam  
Jibin Gnanadhas  

Melbourne, Australia  
October 2024

