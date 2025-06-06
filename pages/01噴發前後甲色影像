my_Map = geemap.Map()
my_Map

my_point = ee.Geometry.Point([-175.2049470, -21.1988048])

my_img = (
    ee.ImageCollection('COPERNICUS/S2_HARMONIZED')
    .filterBounds(my_point)
    .filterDate('2021-10-26', '2021-10-31')
    .sort('CLOUDY_PIXEL_PERCENTAGE')#排序含雲量後取第一張含雲量最低的
    .first()
    .select('B.*')
)


vis_params = {'min':100, 'max': 3500, 'bands': ['B11',  'B8',  'B3']}

my_Map.centerObject(my_point, 11)
my_Map.addLayer(my_img, vis_params, "Sentinel-2")

my_Map.to_streamlit(height=600)
