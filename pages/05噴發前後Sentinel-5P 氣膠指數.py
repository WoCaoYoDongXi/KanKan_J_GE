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



start_date2 = '2021-09-01'
end_date2 = '2022-04-30'

collection = (
    ee.ImageCollection('COPERNICUS/S5P/OFFL/L3_SO2')
    .filterDate(start_date2, end_date2)
    .filterBounds(region)
    .select('SO2_column_number_density')
)

def add_biweekly_mean(collection, start, end):
    current = ee.Date(start)
    stop = ee.Date(end)
    images = []
    while current.millis().lt(stop.millis()).getInfo():
        next_date = current.advance(14, 'day')
        img = (
            collection
            .filterDate(current, next_date)
            .mean()
            .set('system:time_start', current.millis())
            .set('system:index', current.format('YYYYMMdd'))  # 這行很重要，補上index
            .clip(region)
        )
        images.append(img)
        current = next_date
    return ee.ImageCollection(images)

biweekly_collection = add_biweekly_mean(collection, start_date2, end_date2)

dates_millis = biweekly_collection.aggregate_array('system:time_start').getInfo()
dates = [ee.Date(d).format('YYYY-MM-dd').getInfo() for d in dates_millis]

images_list = biweekly_collection.toList(biweekly_collection.size())

vis_params = {
    'min': 0.0,
    'max': 0.005,
    'palette': ['white', 'yellow', 'orange', 'red', 'purple', 'black']
}

st.title("兩週頻率 Sentinel-5P SO₂ 影像比較 (透明度 0.75)")

m = geemap.Map(center=[lat, lon], zoom=8)

for i in range(len(dates)):
    img = ee.Image(images_list.get(i))  # 轉 ee.Image
    img_id = img.get('system:index').getInfo()
    date_str = dates[i]
    m.addLayer(img, vis_params, f"SO₂: {date_str}", opacity=0.75)

st.subheader("圖層列表可於左側切換")
m.to_streamlit(height=600)



