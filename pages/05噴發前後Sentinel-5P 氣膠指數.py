import streamlit as st
import ee
from google.oauth2 import service_account
import geemap.foliumap as geemap
from PIL import Image
# GEE 認證
service_account_info = st.secrets["GEE_SERVICE_ACCOUNT"]
credentials = service_account.Credentials.from_service_account_info(
    service_account_info,
    scopes=["https://www.googleapis.com/auth/earthengine"]
)
ee.Initialize(credentials)


st.title("噴發前後Sentinel-5P 數據變化")

# 區域設定
lon = -175.2
lat = -21.1
radius_km = 20

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

img1 = get_aerosol_image('2021-09-16', '2021-09-20')
img2 = get_aerosol_image('2022-04-21', '2022-04-25')

vis_params = {
    'min': 0,
    'max': 2,
    'palette': ['white', 'purple', 'blue', 'green', 'yellow', 'red'],
    'opacity': 0.6 
}

# Map 1
m1 = geemap.Map(center=[lat, lon], zoom=10)
m1.addLayer(img1, vis_params, "噴發前")
st.subheader("噴發前氣膠指數")
m1.to_streamlit(height=400)

# Map 2
m2 = geemap.Map(center=[lat, lon], zoom=10)
m2.addLayer(img2, vis_params, "噴發後")
st.subheader("噴發前氣膠指數")
m2.to_streamlit(height=400)

def get_so2_image(start_date, end_date):
    return (
        ee.ImageCollection('COPERNICUS/S5P/OFFL/L3_SO2')
        .filterDate(start_date, end_date)
        .filterBounds(region)
        .select('SO2_column_number_density')  # 注意變數名稱不同
        .mean()
        .clip(region)
    )

# 兩個時間段影像
img3 = get_so2_image('2021-09-16', '2021-09-20')  # 噴發前
img4 = get_so2_image('2022-04-21', '2022-04-25')  # 噴發後

# 顯示參數
vis_params = {
    'min': 0.0,
    'max': 0.005,
    'palette': ['white', 'yellow', 'orange', 'red', 'purple', 'black'],
    'opacity': 0.6 
}

# Map 1：噴發前
m3 = geemap.Map(center=[lat, lon], zoom=10)
m3.addLayer(img3, vis_params, "SO₂：2021-09-16 至 2021-09-20")
st.subheader("噴發前二氧化硫柱密度")
m3.to_streamlit(height=400)
# Map 2：噴發後
m3 = geemap.Map(center=[lat, lon], zoom=10)
m3.addLayer(img4, vis_params, "SO₂：2022-04-21 至 2022-04-25")
st.subheader("噴發後二氧化硫柱密度")
m3.to_streamlit(height=400)

