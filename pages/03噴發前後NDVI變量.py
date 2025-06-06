
import streamlit as st
import ee
from google.oauth2 import service_account
import geemap.foliumap as geemap

# GEE 認證
service_account_info = st.secrets["GEE_SERVICE_ACCOUNT"]
credentials = service_account.Credentials.from_service_account_info(
    service_account_info,
    scopes=["https://www.googleapis.com/auth/earthengine"]
)
ee.Initialize(credentials)

# 頁面設定
st.set_page_config(layout="wide")
st.title("噴發前後NDVI變化🌏")

# 移除 Streamlit 預設標頭與選單
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# 地圖初始化與 ROI
my_Map = geemap.Map()
roi = my_Map.user_roi
if roi is None:
    roi = ee.Geometry.BBox(-175.324150, -21.108753, -175.235046, -21.183011)

# 計算 NDVI
def get_ndvi(start_date, end_date):
    collection = ee.ImageCollection('COPERNICUS/S2_SR') \
        .filterBounds(roi) \
        .filterDate(start_date, end_date) \
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)) \
        .median() \
        .clip(roi)
    ndvi = collection.normalizedDifference(['B8', 'B4']).rename('NDVI')
    return ndvi

ndvi_before = get_ndvi('2021-09-16', '2021-09-20')
ndvi_after = get_ndvi('2022-04-21', '2022-04-25')

# 可視化參數與圖層
ndvi_vis = {
    'min': 0,
    'max': 0.8,
    'palette': ['white', 'yellow', 'green']
}
legend_colors_hex = ['#FFFFFF', '#FFFF00', '#008000'] 

left_layer = geemap.ee_tile_layer(ndvi_before, ndvi_vis, 'NDVI Before (2021)')
right_layer = geemap.ee_tile_layer(ndvi_after, ndvi_vis, 'NDVI After (2022)')

# 顯示地圖
my_Map = geemap.Map()
my_Map.centerObject(roi, 12)
my_Map.split_map(left_layer, right_layer)
my_Map.add_legend(title='NDVI', labels=['Low', 'Medium', 'High'], colors=legend_colors_hex)
my_Map.to_streamlit(height=600)

def get_ndvi_stats(ndvi_image, region):
    stats = ndvi_image.reduceRegion(
        reducer=ee.Reducer.mean().combine(ee.Reducer.min(), '', True).combine(ee.Reducer.max(), '', True),
        geometry=region,
        scale=10,
        maxPixels=1e9
    )
    return stats

# 計算 NDVI 統計
stats_before = get_ndvi_stats(ndvi_before, roi)
stats_after = get_ndvi_stats(ndvi_after, roi)

# 將統計結果轉為 Python 字典
ndvi_stats_before = stats_before.getInfo()
ndvi_stats_after = stats_after.getInfo()

# 使用 Streamlit 顯示統計數值
st.subheader("NDVI 統計比較")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**2021 年（火山前）**")
    st.metric("平均 NDVI", f"{ndvi_stats_before['NDVI_mean']:.3f}")
    st.metric("最小 NDVI", f"{ndvi_stats_before['NDVI_min']:.3f}")
    st.metric("最大 NDVI", f"{ndvi_stats_before['NDVI_max']:.3f}")

with col2:
    st.markdown("**2022 年（火山後）**")
    st.metric("平均 NDVI", f"{ndvi_stats_after['NDVI_mean']:.3f}")
    st.metric("最小 NDVI", f"{ndvi_stats_after['NDVI_min']:.3f}")
    st.metric("最大 NDVI", f"{ndvi_stats_after['NDVI_max']:.3f}")

st.markdown("""從NDVI數值來看，其平均值大幅下降0.192。且最大值也大幅下降0.241""")
