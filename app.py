import streamlit as st
import ee
from google.oauth2 import service_account
import geemap.foliumap as geemap

# 從 Streamlit Secrets 讀取 GEE 服務帳戶金鑰 JSON
service_account_info = st.secrets["GEE_SERVICE_ACCOUNT"]

# 使用 google-auth 進行 GEE 授權
credentials = service_account.Credentials.from_service_account_info(
    service_account_info,
    scopes=["https://www.googleapis.com/auth/earthengine"]
)

# 初始化 GEE
ee.Initialize(credentials)


###############################################
st.set_page_config(layout="wide")
st.title("🌍 使用服務帳戶連接 GEE 的 Streamlit App")

# 參數設定
my_point = ee.Geometry.Point([120.5583462887228, 24.081653403304525])

# 1. 讀取 Sentinel-2 影像並選取波段
my_image = (
    ee.ImageCollection('COPERNICUS/S2_HARMONIZED')
    .filterBounds(my_point)
    .filterDate('2021-01-01', '2022-01-01')
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10))
    .sort('CLOUDY_PIXEL_PERCENTAGE')
    .first()
    .select('B.*')
)

# 真彩色視覺化參數 (B4, B3, B2)
vis_params = {'min': 100, 'max': 3500, 'bands': ['B4', 'B3', 'B2']}

# 建立地圖物件
my_Map = geemap.Map()

# 中心定位與顯示真彩色圖層
my_Map.centerObject(my_image, 8)
my_Map.addLayer(my_image, vis_params, 'Sentinel-2 true color')

# 2. 從影像取樣建立訓練資料
training001 = my_image.sample(
    region=my_image.geometry(),
    scale=10,
    numPixels=10000,
    seed=0,
    geometries=True,
)

my_Map.addLayer(training001, {}, 'Training samples')

# 3. 訓練 Weka KMeans 分群器 (10 類)
clusterer_KMeans = ee.Clusterer.wekaKMeans(10).train(training001)

# 4. 分群影像
result002 = my_image.cluster(clusterer_KMeans)

# 5. 分類結果視覺化調色盤與參數
legend_dict = {
    'zero'  : '#e6194b',  # 紅
    'one'   : '#3cb44b',  # 綠
    'two'   : '#ffe119',  # 黃
    'three' : '#4363d8',  # 藍
    'four'  : '#f58231',  # 橘
    'five'  : '#911eb4',  # 紫
    'six'   : '#46f0f0',  # 青
    'seven' : '#f032e6',  # 粉紅紫
    'eight' : '#bcf60c',  # 淺綠黃（醒目）
    'nine'  : '#fabebe',  # 淡粉紅（柔和）
}
palette = list(legend_dict.values())
vis_params_002 = {'min': 0, 'max': 9, 'palette': palette}

# 6. 用雙視窗對比顯示真彩色與分類結果
left_layer = geemap.ee_tile_layer(my_image, vis_params, 'Sentinel-2 true color')
right_layer = geemap.ee_tile_layer(result002, vis_params_002, 'Weka KMeans classified land cover')

my_Map = geemap.Map()
my_Map.centerObject(my_image.geometry(), 9)
my_Map.split_map(left_layer, right_layer)

# 加入分類圖例
my_Map.add_legend(title='Land Cover Type', legend_dict=legend_dict, position='bottomright')

# 顯示地圖
my_Map

my_Map.to_streamlit(height=700)

