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
my_Map

my_point = ee.Geometry.Point([-175.2049470, -21.1988048])

my_img = (
    ee.ImageCollection('COPERNICUS/S2_HARMONIZED')
    .filterBounds(my_point)
    .filterDate('2021-11-01', '2021-12-31')
    .sort('CLOUDY_PIXEL_PERCENTAGE')#排序含雲量後取第一張含雲量最低的
    .first()
    .select('B.*')
)

vis_params = {'min':100, 'max': 3500, 'bands': ['B11',  'B8',  'B3']}

my_lc = ee.Image('ESA/WorldCover/v200/2021')
classValues = [10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 100]
remapValues = ee.List.sequence(0, 10)
label = 'lc'
my_lc = my_lc.remap(classValues, remapValues, bandName='Map').rename(label).toByte()

classVis = {
  'min': 0,
  'max': 10,
  'palette': ['006400' ,'ffbb22', 'ffff4c', 'f096ff', 'fa0000', 'b4b4b4',
            'f0f0f0', '0064c8', '0096a0', '00cf75', 'fae6a0']
}

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
validationSample = validationSample.classify(my_trainedClassifier)
validationAccuracy = validationSample.errorMatrix(label, 'classification')

my_newpoint01 = ee.Geometry.Point([-175.2049470, -21.1988048])

my_newimg01 = (
    ee.ImageCollection('COPERNICUS/S2_HARMONIZED')
    .filterBounds(my_newpoint01)
    .filterDate('2021-11-01', '2021-12-31')
    .sort('CLOUDY_PIXEL_PERCENTAGE')
    .first()
    .select('B.*')
)

vis_params = {'min':100, 'max': 3500, 'bands': ['B11',  'B8',  'B3']}
my_newimgClassified01 = my_newimg01.classify(my_trainedClassifier)

classVis = {
  'min': 0,
  'max': 10,
  'palette': ['006400' ,'ffbb22', 'ffff4c', 'f096ff', 'fa0000', 'b4b4b4',
            'f0f0f0', '0064c8', '0096a0', '00cf75', 'fae6a0']
}

my_newpoint02 = ee.Geometry.Point([-175.2049470, -21.1988048])

my_newimg02 = (
    ee.ImageCollection('COPERNICUS/S2_HARMONIZED')
    .filterBounds(my_newpoint02)
    .filterDate('2022-04-01', '2022-08-31')
    .sort('CLOUDY_PIXEL_PERCENTAGE')
    .first()
    .select('B.*')
)

vis_params = {'min':100, 'max': 3500, 'bands': ['B11',  'B8',  'B3']}
my_newimgClassified02 = my_newimg02.classify(my_trainedClassifier)

classVis = {
  'min': 0,
  'max': 10,
  'palette': ['006400' ,'ffbb22', 'ffff4c', 'f096ff', 'fa0000', 'b4b4b4',
            'f0f0f0', '0064c8', '0096a0', '00cf75', 'fae6a0']
}

my_Map = geemap.Map()

left_layer = geemap.ee_tile_layer(my_newimgClassified01, classVis, 'Classified01')
right_layer = geemap.ee_tile_layer(my_newimgClassified02, classVis, 'Classified02')

my_Map.centerObject(my_point, 11)
my_Map.split_map(left_layer, right_layer)
my_Map.add_legend(title='ESA Land Cover Type', builtin_legend='ESA_WorldCover')
my_Map

my_Map.to_streamlit(height=500)

