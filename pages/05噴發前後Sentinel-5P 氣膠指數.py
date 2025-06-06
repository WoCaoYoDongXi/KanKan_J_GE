import streamlit as st
import ee
import geemap.foliumap as geemap


st.title("Sentinel-5P 氣膠指數 Split Map 比較")

# 區域設定
lon = st.number_input("輸入經度 (Longitude)", value=-175.2, format="%.4f")
lat = st.number_input("輸入緯度 (Latitude)", value=-21.1, format="%.4f")
radius_km = st.number_input("輸入半徑 (公里)", value=50, min_value=1, max_value=200)

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

# 建立 geemap SplitMap
split_map = geemap.SplitMap(left_layer=img1, right_layer=img2, vis_params=vis_params)
split_map.set_center(lon, lat, 8)
split_map.addLayer(region, {'color': 'red'}, '區域範圍')

# 顯示 split map
split_map.to_streamlit(height=600)
