import streamlit as st
import ee
from google.oauth2 import service_account
import geemap.foliumap as geemap


st.write("## 噴發日期選擇以火山噴發前後Tongatapu島上空含雲量最少之時而定")
st.write("## 噴發前：21/09/16-20;噴發後：22/04/21-25")
my_point = ee.Geometry.Point([-175.2049470, -21.1988048])
st.write("## 火山噴發前")
my_img = (
    ee.ImageCollection('COPERNICUS/S2_HARMONIZED')
    .filterBounds(my_point)
    .filterDate('2021-09-16', '2021-09-20')
    .sort('CLOUDY_PIXEL_PERCENTAGE')#排序含雲量後取第一張含雲量最低的
    .first()
    .select('B.*')
)
vis_params = {'min':100, 'max': 3500, 'bands': ['B11',  'B8',  'B3']}
m1 = geemap.Map()
m1.centerObject(my_point, 11)
m1.addLayer(my_img, vis_params, "噴發前")
m1.to_streamlit(height=600)
st.write("## 火山噴發後")
my_img02 = (
    ee.ImageCollection('COPERNICUS/S2_HARMONIZED')
    .filterBounds(my_point)
    .filterDate('2022-04-21', '2022-04-25')
    .sort('CLOUDY_PIXEL_PERCENTAGE')#排序含雲量後取第一張含雲量最低的
    .first()
    .select('B.*')
)
vis_params = {'min':100, 'max': 3500, 'bands': ['B11',  'B8',  'B3']}
m2 = geemap.Map()
m2.centerObject(my_point, 11)
m2.addLayer(my_img02, vis_params, "噴發後")
m2.to_streamlit(height=600)
