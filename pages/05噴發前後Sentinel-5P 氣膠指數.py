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


st.title("Sentinel-5P SO₂ 二氧化硫 Timelapse (兩週頻率)")

# 設定區域（以 Tongatapu 附近為例）
lon, lat = -175.2, -21.1
radius_km = 30
region = ee.Geometry.Point([lon, lat]).buffer(radius_km * 1000)

# 時間範圍
start_date = '2021-09-01'
end_date = '2022-04-30'

# 取得 Sentinel-5P SO2 影像集合
collection = (
    ee.ImageCollection('COPERNICUS/S5P/OFFL/L3_SO2')
    .filterDate(start_date, end_date)
    .filterBounds(region)
    .select('SO2_column_number_density')
)

# 兩週平均的影像集合
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
            .clip(region)
        )
        images.append(img)
        current = next_date
    return ee.ImageCollection(images)

biweekly_collection = add_biweekly_mean(collection, start_date, end_date)

# 取每張影像時間，轉成可讀字串
def get_dates(ic):
    dates = ic.aggregate_array('system:time_start').getInfo()
    readable_dates = [datetime.datetime.utcfromtimestamp(d / 1000).strftime('%Y-%m-%d') for d in dates]
    return readable_dates

dates = get_dates(biweekly_collection)

# 視覺化參數，opacity 在 Streamlit geemap Map 時用 addLayer() 參數控制
vis_params = {
    'min': 0.0,
    'max': 0.005,
    'palette': ['white', 'yellow', 'orange', 'red', 'purple', 'black']
}

# 建立 geemap Map 並逐張影像加入
m3 = geemap.Map(center=(lat, lon), zoom=7)

# 透明度設定 (Streamlit geemap Map 的 addLayer 有 opacity 參數)
opacity = 0.75

for i, img in enumerate(biweekly_collection.toList(biweekly_collection.size()).getInfo()):
    # 重新載入 Image (因 toList 會回傳 dict，不是 ee.Image)
    img_obj = ee.Image(img['id'])
    date_str = dates[i]
    m3.addLayer(img_obj, vis_params, f"SO2: {date_str}", opacity=opacity)

st.subheader("兩週頻率 Sentinel-5P SO₂ 影像圖層")
st.write("可切換左側圖層以查看不同時間點影像")
m3.to_streamlit(height=600)

