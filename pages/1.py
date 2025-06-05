import streamlit as st
import ee
from google.oauth2 import service_account
import geemap.foliumap as geemap

# 1. GEE 認證：使用服務帳戶從 Streamlit Secrets 取得憑證
service_account_info = st.secrets["GEE_SERVICE_ACCOUNT"]

credentials = service_account.Credentials.from_service_account_info(
    service_account_info,
    scopes=["https://www.googleapis.com/auth/earthengine"]
)

ee.Initialize(credentials)

# 2. Streamlit 頁面設定與標題
st.set_page_config(layout="wide")
st.title("你看看這好東西啊🌏")

my_Map = geemap.Map()
roi = my_Map.user_roi
if roi is None:                                                     # If we have not defined any box region on the canvas,
    roi = ee.Geometry.BBox(-175.341105, -21.095057, -175.150307, -21.186537)    # then we define one that contains Pucallpa, Peru.
def get_ndvi(start_date, end_date):
    collection = ee.ImageCollection('COPERNICUS/S2_SR') \
        .filterBounds(roi) \
        .filterDate(start_date, end_date) \
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)) \
        .median() \
        .clip(roi)
    
    ndvi = collection.normalizedDifference(['B8', 'B4']).rename('NDVI')
    return ndvi

ndvi_before = get_ndvi('2021-11-01', '2021-12-31')
ndvi_after = get_ndvi('2022-04-01', '2022-08-31')

ndvi_vis = {
    'min': 0,
    'max': 0.8,
    'palette': ['white', 'yellow', 'green']
}
legend_colors_hex = ['#FFFFFF', '#FFFF00', '#008000'] 

left_layer = geemap.ee_tile_layer(ndvi_before, ndvi_vis, 'NDVI Before (2021)')
right_layer = geemap.ee_tile_layer(ndvi_after, ndvi_vis, 'NDVI After (2022)')

my_Map = geemap.Map()
my_Map.centerObject(roi, 12)
my_Map.split_map(left_layer, right_layer)
my_Map.add_legend(title='NDVI', labels=['Low', 'Medium', 'High'], colors=legend_colors_hex)
my_Map
my_Map.to_streamlit(height=600)
