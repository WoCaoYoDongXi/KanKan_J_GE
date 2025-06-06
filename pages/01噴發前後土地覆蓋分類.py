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

# Streamlit 介面設定
st.set_page_config(layout="wide")
st.title("分類圖資變化比較 🌋")

# 參數與位置設定
my_point = ee.Geometry.Point([-175.2049470, -21.1988048])
classVis = {
    'min': 0,
    'max': 10,
    'palette': ['006400' ,'ffbb22', 'ffff4c', 'f096ff', 'fa0000', 'b4b4b4',
                'f0f0f0', '0064c8', '0096a0', '00cf75', 'fae6a0']
}

# 訓練資料與分類器
my_img = ee.ImageCollection('COPERNICUS/S2_HARMONIZED') \
    .filterBounds(my_point) \
    .filterDate('2021-11-01', '2021-12-31') \
    .sort('CLOUDY_PIXEL_PERCENTAGE') \
    .first() \
    .select('B.*')

my_lc = ee.Image('ESA/WorldCover/v200/2021')
classValues = [10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 100]
remapValues = ee.List.sequence(0, 10)
my_lc = my_lc.remap(classValues, remapValues, bandName='Map').rename('lc').toByte()

sample = my_img.addBands(my_lc).stratifiedSample(
    numPoints=500,
    classBand='lc',
    region=my_img.geometry(),
    scale=10,
    geometries=True
).randomColumn()

my_trainedClassifier = ee.Classifier.smileRandomForest(numberOfTrees=100).train(
    features=sample.filter('random <= 0.8'),
    classProperty='lc',
    inputProperties=my_img.bandNames()
)

# 火山前後影像與分類
my_newimg01 = ee.ImageCollection('COPERNICUS/S2_HARMONIZED') \
    .filterBounds(my_point) \
    .filterDate('2021-12-25', '2021-12-31') \
    .sort('CLOUDY_PIXEL_PERCENTAGE') \
    .first() \
    .select('B.*')
my_newimgClassified01 = my_newimg01.classify(my_trainedClassifier)

my_newimg02 = ee.ImageCollection('COPERNICUS/S2_HARMONIZED') \
    .filterBounds(my_point) \
    .filterDate('2022-03-06', '2022-03-10') \
    .sort('CLOUDY_PIXEL_PERCENTAGE') \
    .first() \
    .select('B.*')
my_newimgClassified02 = my_newimg02.classify(my_trainedClassifier)

# 地圖顯示
my_Map = geemap.Map()
my_Map.centerObject(my_point, 11)
my_Map.split_map(
    geemap.ee_tile_layer(my_newimgClassified01, classVis, 'Classified01'),
    geemap.ee_tile_layer(my_newimgClassified02, classVis, 'Classified02')
)
my_Map.add_legend(title='ESA Land Cover Type', builtin_legend='ESA_WorldCover')
my_Map.to_streamlit(height=600)

# 讀取本地圖片
img = Image.open("eruption1.png")

# 顯示圖片
st.image(img, caption="噴發前土地覆蓋分類",  use_container_width=True)
# 讀取本地圖片
img02 = Image.open("eruption2.png")

# 顯示圖片
st.image(img02, caption="噴發後土地覆蓋分類",  use_container_width=True)
