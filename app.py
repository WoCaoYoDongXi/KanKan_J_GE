import streamlit as st

st.set_page_config(page_title="東加火山災後遙測分析", layout="wide")

st.title("🌋 東加火山災後地表變化分析")

st.markdown(
    """
    <video autoplay muted loop width="700">
        <source src="eruption.mp4" type="video/mp4">
    </video>
    """,
    unsafe_allow_html=True
st.video(video_bytes)
  ）
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
1. 預設研究範圍於東加地區最大島嶼 Tongatapu  
2. 採用 ESA WorldCover 10m v200 圖資，並使用 SmileCart 分類器進行分類訓練  
3. 訓練後製作噴發前後之土地覆蓋類別，並尋找較大面積之類別更動區域  
4. 在島嶼上指定研究觀察區域範圍  
5. 運用植生指數（NDVI）及水體指數（NDWI）去驗證地表變化  
""")

st.markdown("---")
st.info("👉 後續將展示分類圖、指數分析與觀察成果。")
