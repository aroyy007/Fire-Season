import earthaccess

# Aqua MODIS daily fire mask
modis_results = earthaccess.search_data(
    short_name="MYD14A1",
    version="061",
    temporal=("2023-03-01", "2023-03-08"),
    bounding_box=(93.0, 23.0, 96.0, 26.5),  # lon_min, lat_min, lon_max, lat_max — NE India–Myanmar pilot
)
print(f"MODIS granules found: {len(modis_results)}")
for g in modis_results[:3]:
    print(g)

# Suomi-NPP VIIRS daily fire mask
viirs_results = earthaccess.search_data(
    short_name="VNP14A1",
    version="002",
    temporal=("2023-03-01", "2023-03-08"),
    bounding_box=(93.0, 23.0, 96.0, 26.5),
)
print(f"VIIRS granules found: {len(viirs_results)}")
for g in viirs_results[:3]:
    print(g)