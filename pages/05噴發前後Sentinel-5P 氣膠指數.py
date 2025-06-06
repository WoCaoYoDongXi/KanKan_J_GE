import streamlit as st
import ee
from google.oauth2 import service_account
import geemap.foliumap as geemap
import geemap

st.title("Sentinel-5P 氣膠指數 Split Map 比較")

# 區域設定
lon = -175.2
lat = -21.1
radius_km =30

region = ee.Geometry.Point([lon, lat]).buffer(radius_km * 1000)

# 時間段1
start_date_1 = '2022-04-21'
end_date_1 = '2022-04-25'

# 時間段2
start_date_2 = '2021-09-16'
end_date_2 = '2021-09-20'

# 讀取 Sentinel-5P 氣膠指數影像
def get_aerosol_image(start_date, end_date):
    img = (
        ee.ImageCollection('COPERNICUS/S5P/OFFL/L3_AER_AI')
        .filterDate(start_date, end_date)
        .filterBounds(region)
        .select('absorbing_aerosol_index')
        .mean()
        .clip(region)
    )
    return img

img1 = get_aerosol_image(start_date_1, end_date_1)
img2 = get_aerosol_image(start_date_2, end_date_2)

vis_params = {
    'min': 0,
    'max': 2,
    'palette': ['white', 'purple', 'blue', 'green', 'yellow', 'red']
}
m1 = geemap.Map()
m1.centerObject(center[lon, lat], 11)
m1.addLayer(img1, vis_params, "噴發前")
m1.to_streamlit(height=600)

m2 = geemap.Map()
m2.centerObject(center[lon, lat], 11)
m2.addLayer(img2, vis_params, "噴發前")
m2.to_streamlit(height=600)
