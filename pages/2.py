import streamlit as st
import ee
from google.oauth2 import service_account
import geemap.foliumap as geemap

# 初始化 Earth Engine
service_account_info = st.secrets["GEE_SERVICE_ACCOUNT"]
credentials = service_account.Credentials.from_service_account_info(
    service_account_info,
    scopes=["https://www.googleapis.com/auth/earthengine"]
)
ee.Initialize(credentials)

# 設定地點與分類視覺參數
point = ee.Geometry.Point([-175.2049, -21.1988])
vis_params = {'min': 0, 'max': 10, 'palette': ['006400' ,'ffbb22', 'ffff4c',
 'f096ff', 'fa0000', 'b4b4b4', 'f0f0f0', '0064c8', '0096a0', '00cf75', 'fae6a0']}

# 已經事先訓練好的分類器（範例用 smileCart，可在 GEE 中重新訓練）
img = ee.ImageCollection('COPERNICUS/S2_HARMONIZED') \
    .filterBounds(point).filterDate('2021-11-01', '2021-12-31') \
    .sort('CLOUDY_PIXEL_PERCENTAGE').first().select('B.*')

# 建立與訓練樣本分類器
lc = ee.Image('ESA/WorldCover/v200/2021')
label = 'lc'
lc_remapped = lc.remap(
    [10,20,30,40,50,60,70,80,90,95,100], 
    ee.List.sequence(0,10), 
    bandName='Map'
).rename(label).toByte()
sample = img.addBands(lc_remapped).stratifiedSample(
    numPoints=500, classBand=label, region=img.geometry(), scale=10, geometries=True
)
classifier = ee.Classifier.smileCart().train(
    features=sample, classProperty=label, inputProperties=img.bandNames()
)

# 讀取噴發前後影像並分類
def classify_image(start, end):
    image = ee.ImageCollection('COPERNICUS/S2_HARMONIZED') \
        .filterBounds(point).filterDate(start, end) \
        .sort('CLOUDY_PIXEL_PERCENTAGE').first().select('B.*')
    return image.classify(classifier)

classified_before = classify_image('2021-11-01', '2021-12-31')
classified_after = classify_image('2022-04-01', '2022-08-31')

# 建立地圖並加上分割圖層
Map = geemap.Map()
Map.centerObject(point, 11)
Map.split_map(
    geemap.ee_tile_layer(classified_before, vis_params, 'Before'),
    geemap.ee_tile_layer(classified_after, vis_params, 'After')
)
Map.add_legend(title='ESA WorldCover', builtin_legend='ESA_WorldCover')
Map.to_streamlit(height=600)

