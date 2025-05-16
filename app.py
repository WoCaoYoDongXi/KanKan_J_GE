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
st.title("🌍 使用服務帳戶連接 GEE 的 Streamlit App")

# 3. 定義地理區域 (點)
my_point = ee.Geometry.Point([120.5583462887228, 24.081653403304525])

# 4. 取得 Landsat NDVI 並顯示 (示範用)
landsat = ee.ImageCollection("LANDSAT/LC09/C02/T1_L2") \
    .filterBounds(my_point) \
    .filterDate("2022-01-01", "2022-12-31") \
    .median()

ndvi = landsat.normalizedDifference(["SR_B5", "SR_B4"]).rename("NDVI")

# 5. Sentinel-2 影像取樣與分類分析
my_image = (
    ee.ImageCollection('COPERNICUS/S2_HARMONIZED')
    .filterBounds(my_point)
    .filterDate('2021-01-01', '2022-01-01')
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10))
    .sort('CLOUDY_PIXEL_PERCENTAGE')
    .first()
    .select('B.*')
)

vis_params = {'min': 100, 'max': 3500, 'bands': ['B4', 'B3', 'B2']}

training_samples = my_image.sample(
    region=my_image.geometry(),
    scale=10,
    numPixels=10000,
    seed=0,
    geometries=True,
)

clusterer = ee.Clusterer.wekaKMeans(10).train(training_samples)
result_clusters = my_image.cluster(clusterer)

legend_dict = {
    'zero'  : '#e6194b',
    'one'   : '#3cb44b',
    'two'   : '#ffe119',
    'three' : '#4363d8',
    'four'  : '#f58231',
    'five'  : '#911eb4',
    'six'   : '#46f0f0',
    'seven' : '#f032e6',
    'eight' : '#bcf60c',
    'nine'  : '#fabebe',
}

palette = list(legend_dict.values())
vis_params_clusters = {'min': 0, 'max': 9, 'palette': palette}

# 6. 建立 geemap 地圖，加入 NDVI 與 Sentinel-2 分類圖層並啟動雙視窗比較
Map = geemap.Map(center=[24.081653403304525, 120.5583462887228], zoom=9)  # 注意緯度經度順序

# 加入 Landsat NDVI
Map.addLayer(ndvi, {"min": 0, "max": 1, "palette": ["white", "green"]}, "Landsat NDVI")

# 左圖: Sentinel-2 真彩色
left_layer = geemap.ee_tile_layer(my_image, vis_params, 'Sentinel-2 true color')

# 右圖: Weka KMeans 分類結果
right_layer = geemap.ee_tile_layer(result_clusters, vis_params_clusters, 'Weka KMeans classified')

Map.split_map(left_layer, right_layer)

# 加入分類圖例
Map.add_legend(title='Land Cover Type', legend_dict=legend_dict, position='bottomright')

# 7. 將地圖輸出到 Streamlit
Map.to_streamlit(height=600)
