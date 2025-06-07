
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
st.title("噴發前後NDWI變化💧")

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
    roi = ee.Geometry.BBox(-175.229805, -21.143209, -175.196110, -21.183709)

def get_ndwi(start_date, end_date):
    collection = ee.ImageCollection('COPERNICUS/S2_SR') \
        .filterBounds(roi) \
        .filterDate(start_date, end_date) \
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)) \
        .median() \
        .clip(roi)
    
    ndwi = collection.normalizedDifference(['B3', 'B8']).rename('NDWI')
    return ndwi

ndwi_before = get_ndwi('2021-09-16', '2021-09-20')
ndwi_after = get_ndwi('2022-04-21', '2022-04-25')

# 可視化參數與圖層
ndwi_vis = {
    'min': -1,
    'max': 1,
    'palette': ['brown', 'white', 'blue']
}
legend_colors_hex = ['#8B4513', '#FFFFFF', '#0000FF'] 

left_layer = geemap.ee_tile_layer(ndwi_before, ndwi_vis, 'NDWI Before (2021)')
right_layer = geemap.ee_tile_layer(ndwi_after, ndwi_vis, 'NDWI After (2022)')

# 顯示地圖
my_Map = geemap.Map()
my_Map.centerObject(roi, 14)
my_Map.split_map(left_layer, right_layer)
my_Map.add_legend(title='NDWI', labels=['Low', 'Medium', 'High'], colors=legend_colors_hex)
my_Map.to_streamlit(height=600)

def get_ndwi_stats(ndwi_image, region):
    stats02 = ndwi_image.reduceRegion(
        reducer=ee.Reducer.mean().combine(ee.Reducer.min(), '', True).combine(ee.Reducer.max(), '', True),
        geometry=region,
        scale=10,
        maxPixels=1e9
    )
    return stats02

stats02_before = get_ndwi_stats(ndwi_before, roi)
stats02_after = get_ndwi_stats(ndwi_after, roi)

# 將統計結果轉為 Python 字典
ndwi_stats_before = stats02_before.getInfo()
ndwi_stats_after = stats02_after.getInfo()

# 使用 Streamlit 顯示統計數值
st.subheader("NDWI 統計比較")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**2021 年（火山前）**")
    st.metric("平均 NDWI", f"{ndwi_stats_before['NDWI_mean']:.3f}")
    st.metric("最小 NDWI", f"{ndwi_stats_before['NDWI_min']:.3f}")
    st.metric("最大 NDWI", f"{ndwi_stats_before['NDWI_max']:.3f}")

with col2:
    st.markdown("**2022 年（火山後）**")
    st.metric("平均 NDWI", f"{ndwi_stats_after['NDWI_mean']:.3f}")
    st.metric("最小 NDWI", f"{ndwi_stats_after['NDWI_min']:.3f}")
    st.metric("最大 NDWI", f"{ndwi_stats_after['NDWI_max']:.3f}")

st.markdown("""
**觀察結果：**

- 從NDWI數值來看，其平均值顯著下降了0.090，且最大值也大幅下降了0.586。
- 平均值下降：表示全區水體面積或水體反射性明顯降低。
- 最大值下降:即使是在最濕潤的區域，水體指標也大幅減弱，
- 根據上方觀察結果，初步推測開放水體可能因火山噴發後所產生的火山灰，使水體出現大幅改變（如淤積）。不排除是因為火山噴發產生之氣溶膠使地表反射出現變化，導致判讀及測量錯誤。
""")
