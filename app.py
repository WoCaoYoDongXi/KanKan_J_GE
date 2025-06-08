import streamlit as st

st.set_page_config(page_title="東加火山災後遙測分析", layout="wide")

st.title("🌋 東加火山噴發前後地表變化分析")

st.markdown(
    """
    <iframe width="700" height="394"
    src="https://www.youtube.com/embed/GLBy3_1tijM?autoplay=1&mute=1&loop=1&playlist=GLBy3_1tijM"
    frameborder="0"
    allow="autoplay; encrypted-media"
    allowfullscreen>
    </iframe>
    """,
    unsafe_allow_html=True
)
st.write("""
東加火山噴發影像
""")

st.markdown("#### 研究動機")
st.write("""
當初在新聞上看見東加火山噴發的一瞬間，蕈狀雲將空照圖整個填滿，令我印象深刻。
在課程中，也學習到如何運用圖資訓練及觀察土地覆蓋類別。
因此本報告以東加火山噴發前後的衛星影像與土地覆蓋分類為基礎，
結合 NDVI 與 NDWI 指數，分析災後地表的變化，
作為遙測災後監測的實證案例。
""")

st.markdown("#### 背景說明")
st.write("""
2022年1月15日，位於南太平洋的東加海底火山（Hunga Tonga–Hunga Haʻapai）
發生了近百年來最劇烈的一次火山噴發。
此次爆發引發海嘯與大量火山灰，
不僅對當地基礎建設與居民生活造成破壞，
也對周遭陸地與海洋生態系統產生重大影響。
""")

st.markdown("#### 研究問題")
st.write("""
1. 火山噴發前後，當地的土地覆蓋類型是否產生明顯改變？
2. 土地覆蓋類別與植生（NDVI）/水體（NDWI）指數能否彼此驗證，證明災後地表環境變化？
""")

st.markdown("#### 方法與流程")
st.write("""
1.預設研究範圍於東加地區最大島嶼Tongatapu
2.採用ESA WorldCover 10m v200圖資，
  並使用smileRandomForest分類器進行分類訓練。
  隨機選取80%作為訓練資料，其餘20%作為測試資料。
3.訓練後生成噴發前後之土地覆蓋類別，
  並尋找較大面積覆蓋類別更動區域。
4.於選定區域運用植生指數(NDVI)及水體指數(NDWI)去驗證地表變化
5.用氣溶膠指數(AI)去排除因氣溶膠所使地表反射改變所產生的判讀及測量錯誤

註：採用哨兵2號（Sentinel-2）影像；日期選擇以噴發前後之研究範圍上空含雲量最少的期間。
""")

st.markdown("---")
st.info("採用哨兵2號（Sentinel-2）影像；日期選擇以噴發前後之研究範圍上空含雲量最少的期間。")
