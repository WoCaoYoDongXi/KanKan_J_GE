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

st.set_page_config(layout="wide")
st.title("噴發前後土地覆蓋分類🌏")
# 定義 ROI 與視覺參數
my_point = ee.Geometry.Point([-175.2049470, -21.1988048])
vis_params = {'min':100, 'max': 3500, 'bands': ['B11',  'B8',  'B3']}
classVis = {
  'min': 0,
  'max': 10,
  'palette': ['006400' ,'ffbb22', 'ffff4c', 'f096ff', 'fa0000', 'b4b4b4',
              'f0f0f0', '0064c8', '0096a0', '00cf75', 'fae6a0']
}

# 訓練分類器（簡化：直接內建處理）
my_img = (
    ee.ImageCollection('COPERNICUS/S2_HARMONIZED')
    .filterBounds(my_point)
    .filterDate('2021-11-01', '2021-12-31')
    .sort('CLOUDY_PIXEL_PERCENTAGE')
    .first()
    .select('B.*')
)

my_lc = ee.Image('ESA/WorldCover/v200/2021')
classValues = [10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 100]
remapValues = ee.List.sequence(0, 10)
label = 'lc'
my_lc = my_lc.remap(classValues, remapValues, bandName='Map').rename(label).toByte()

sample = my_img.addBands(my_lc).stratifiedSample(**{
  'numPoints': 500,
  'classBand': label,
  'region': my_img.geometry(),
  'scale': 10,
  'geometries': True
})

sample = sample.randomColumn()
trainingSample = sample.filter('random <= 0.8')
validationSample = sample.filter('random > 0.8')
my_trainedClassifier = ee.Classifier.smileCart().train(**{
  'features': trainingSample,
  'classProperty': label,
  'inputProperties': my_img.bandNames()
})

# 噴發前後的影像與分類
my_newimg01 = (
    ee.ImageCollection('COPERNICUS/S2_HARMONIZED')
    .filterBounds(my_point)
    .filterDate('2021-11-01', '2021-12-31')
    .sort('CLOUDY_PIXEL_PERCENTAGE')
    .first()
    .select('B.*')
)
my_newimgClassified01 = my_newimg01.classify(my_trainedClassifier)

my_newimg02 = (
    ee.ImageCollection('COPERNICUS/S2_HARMONIZED')
    .filterBounds(my_point)
    .filterDate('2022-04-01', '2022-08-31')
    .sort('CLOUDY_PIXEL_PERCENTAGE')
    .first()
    .select('B.*')
)
my_newimgClassified02 = my_newimg02.classify(my_trainedClassifier)

# 地圖顯示
my_Map = geemap.Map()
left_layer = geemap.ee_tile_layer(my_newimgClassified01, classVis, 'Classified01')
right_layer = geemap.ee_tile_layer(my_newimgClassified02, classVis, 'Classified02')
my_Map.centerObject(my_point, 11)
my_Map.split_map(left_layer, right_layer)
my_Map.add_legend(title='ESA Land Cover Type', builtin_legend='ESA_WorldCover')
my_Map.to_streamlit(height=700)

from PIL import Image

# 讀取本地圖片
img = Image.open("eruption1.png")

# 顯示圖片
st.image(img, caption="噴發前大面積TreeCover地區",  use_container_width=True)

