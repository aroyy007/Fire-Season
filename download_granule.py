import earthaccess

auth = earthaccess.login(strategy="netrc")
print("Authenticated:", auth.authenticated)

modis_results = earthaccess.search_data(
    short_name="MYD14A1",
    version="061",
    temporal=("2023-03-01", "2023-03-08"),
    bounding_box=(93.0, 23.0, 96.0, 26.5),
)
viirs_results = earthaccess.search_data(
    short_name="VNP14A1",
    version="002",
    temporal=("2023-03-01", "2023-03-08"),
    bounding_box=(93.0, 23.0, 96.0, 26.5),
)

modis_files = earthaccess.download(modis_results[:1], "./data/modis")
viirs_files = earthaccess.download(viirs_results[:1], "./data/viirs")

print("MODIS file:", modis_files)
print("VIIRS file:", viirs_files)