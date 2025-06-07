import streamlit as st
import ee
from google.oauth2 import service_account
import geemap.foliumap as geemap
from PIL import Image
import datetime

# GEE 認證
service_account_info = st.secrets["GEE_SERVICE_ACCOUNT"]
credentials = service_account.Credentials.from_service_account_info(
    service_account_info,
    scopes=["https://www.googleapis.com/auth/earthengine"]
)
ee.Initialize(credentials)


st.title("噴發前後Sentinel-5P 氣溶膠指數變化")
st.markdown("""
為確定是否因氣體導致判讀及測量產生錯誤，因此使用氣溶膠指數去驗證。
""")
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
st.subheader("噴發前")
m1.to_streamlit(height=400)

# Map 2
m2 = geemap.Map(center=[lat, lon], zoom=10)
m2.addLayer(img2, vis_params, "噴發後")
st.subheader("噴發後")
m2.to_streamlit(height=400)

st.markdown("""
**觀察結果：**
根據上方圖資，
-所選之A區（陸地區）未有明顯氣溶膠累積。因此推斷樹林去受到火山灰覆蓋使樹木健康惡化是存在極高可能性的。可以根據土地覆蓋分類，針對特定改變區域，去改善其植被健康狀況。
-所選之C區（水體區）有明顯氣溶膠累積。因此推斷該開放水體的判讀測量，可能遭受氣溶膠影響，使反射出現差異，進而產生誤判。可能需要搭配其他圖資，才能增加判斷測量的準度。
""")



