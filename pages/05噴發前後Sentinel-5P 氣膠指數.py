import streamlit as st
import ee
import geemap


st.title("Sentinel-5P 氣膠指數 Split Map 比較")

# 區域設定
lon = -175.2
lat = -21.1
radius_km = 30

region = ee.Geometry.Point([lon, lat]).buffer(radius_km * 1000)

def get_aerosol_image(start_date, end_date):
    return (
        ee.ImageCollection('COPERNICUS/S5P/OFFL/L3_AER_AI')
        .filterDate(start_date, end_date)
        .filterBounds(region)
        .select('absorbing_aerosol_index')
        .mean()
        .clip(region)
    )

img1 = get_aerosol_image('2022-04-21', '2022-04-25')
img2 = get_aerosol_image('2021-09-16', '2021-09-20')

vis_params = {
    'min': 0,
    'max': 2,
    'palette': ['white', 'purple', 'blue', 'green', 'yellow', 'red']
}

# Map 1
m1 = geemap.Map(center=[lat, lon], zoom=10)
m1.addLayer(img1, vis_params, "氣膠指數 時間段1")
st.subheader("時間段 1: 2022-04-21 至 2022-04-25")
m1.to_streamlit(height=400)

# Map 2
m2 = geemap.Map(center=[lat, lon], zoom=10)
m2.addLayer(img2, vis_params, "氣膠指數 時間段2")
st.subheader("時間段 2: 2021-09-16 至 2021-09-20")
m2.to_streamlit(height=400)

