import streamlit as st
import ee
from google.oauth2 import service_account
import geemap.foliumap as geemap

my_Map = geemap.Map()

my_point = ee.Geometry.Point([-175.2049470, -21.1988048])

my_img = (
    ee.ImageCollection('COPERNICUS/S2_HARMONIZED')
    .filterBounds(my_point)
    .filterDate('2021-09-16', '2021-09-20')
    .sort('CLOUDY_PIXEL_PERCENTAGE')#排序含雲量後取第一張含雲量最低的
    .first()
    .select('B.*')
)
my_img02 = (
    ee.ImageCollection('COPERNICUS/S2_HARMONIZED')
    .filterBounds(my_point)
    .filterDate('2022-04-21', '2022-04-25')
    .sort('CLOUDY_PIXEL_PERCENTAGE')#排序含雲量後取第一張含雲量最低的
    .first()
    .select('B.*')
)
vis_params = {'min':100, 'max': 3500, 'bands': ['B11',  'B8',  'B3']}

my_Map.centerObject(my_point, 11)
my_Map.addLayer(my_img, vis_params, "噴發前")
my_Map.addLayer(my_img02, vis_params, "噴發後")
my_Map.to_streamlit(height=600)
