import streamlit as st
import ee
import geemap

# 初始化 Earth Engine
try:
    ee.Initialize()
except Exception:
    ee.Authenticate()
    ee.Initialize()

st.title("Sentinel-5P 氣膠指數 Split Map 比較")

# 區域設定
lon = -175.2
lat = -21.1
radius_km = 30

region = ee.Geometry.Point([lon, lat]).buffer(radius_km * 1000)

# 讀影像函式
def get_aerosol_image(start_date, end_date):
    return (
        ee.ImageCollection('COPERNICUS/S5P/OFFL/L3_AER_AI')
        .filterDate(start_date, end_date)
        .filterBounds(region)
        .select('absorbing_aerosol_index')
        .mean()
        .clip(region)
    )

# 取得兩時間段影像
img1 = get_aerosol_image('2022-04-21', '2022-04-25')
img2 = get_aerosol_image('2021-09-16', '2021-09-20')

vis_params = {
    'min': 0,
    'max': 2,
    'palette': ['white', 'purple', 'blue', 'green', 'yellow', 'red']
}

# 建立地圖 1
m = geemap.Map()
m.centerObject(region, 10)

with st.container():
    st.subheader("時間段 1: 2022-04-21 至 2022-04-25")
    m.clear_layers()
    m.addLayer(img1, vis_params, "氣膠指數")
    m.to_streamlit(height=400)

with st.container():
    st.subheader("時間段 2: 2021-09-16 至 2021-09-20")
    m.clear_layers()
    m.addLayer(img2, vis_params, "氣膠指數")
    m.to_streamlit(height=400)
