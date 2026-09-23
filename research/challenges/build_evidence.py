from pathlib import Path
import json
p=Path(__file__).parent
rows=[
('C01','2026 challenge briefs supplied by user','https://www.spaceappschallenge.org/2026/challenges/','User-provided text, 14 challenge entries','Choose from 14 challenges for you and your team','user_supplied'),
('C02','NASA POWER API tutorial','https://power.larc.nasa.gov/docs/tutorials/service-data-request/api/','Guidance on Multiprocessing Download','0.5 x 0.625 degree resolution for meteorology and 1 x 1 for solar parameters.','official_documentation'),
('C03','NASA POWER Daily API','https://power.larc.nasa.gov/docs/services/api/temporal/daily/','Time Standards, lines 82-83','Daily API (Application Programming Interface) defaults to providing LST (Local Solar Time)','official_documentation'),
('C04','Harmonized Landsat and Sentinel-2','https://hls.gsfc.nasa.gov/','Improving Land Monitoring Capabilities','30-meter spatial resolution','official_documentation'),
('C05','SMAP SPL4SMGP Version 8','https://nsidc.org/data/spl4smgp/versions/8','Data Access & Tools, line 195','A free NASA Earthdata Login account is required to access these data.','official_data_centre'),
('C06','SoilGrids global gridded soil information','https://isric.org/explore/soilgrids','Service notice, line 53','have decided to temporarily pause the service','official_data_provider'),
('C07','SoilGrids layers','https://docs.isric.org/globaldata/soilgrids/SoilGrids_faqs_01.html','What do the filename codes mean, lines 40-42','a folder with GeoTIFF tiles.','official_documentation'),
('C08','FIRMS archive download','https://firms.modaps.eosdis.nasa.gov/download/','Temporal Coverage, lines 30-31','MODIS Collection 6.1: Temporal Coverage: 1 November 2000 - present','official_documentation'),
('C09','FIRMS Area API','https://firms.modaps.eosdis.nasa.gov/api/area/','DAY_RANGE, line 54','1 .. 5 - number of days to query at one time','official_documentation'),
('C10','NASA FIRMS WMS','https://firms.modaps.eosdis.nasa.gov/mapserver/wms-info/','WMS Examples','VIIRS 375m','official_documentation'),
('C11','FIRMS US/Canada FAQ','https://forum.earthdata.nasa.gov/viewtopic.php?t=5200','Properties of fire activity and active fire detection data resolution','small, very hot fires and larger, smoldering fires, can both trigger fire detection algorithms.','official_support'),
('C12','NISAR L-Band Data Now Publicly Available','https://asf.alaska.edu/notices/nisar-l-band-data-now-publicly-available/','Release notice, line 14','The initial public release began on July 20, 2026','official_data_centre'),
('C13','NISAR GCOV Data User Guide','https://nisar-docs.asf.alaska.edu/gcov/','Product Overview, line 54','pixel spacing of 10 or 20 meters','official_documentation'),
('C14','NASA Giovanni','https://giovanni.earthdata.nasa.gov/','Login Required','Please log in to your NASA Earthdata account to create plots and access data.','official_application'),
('C15','MERRA-2 data access','https://gmao.gsfc.nasa.gov/gmao-products/merra-2/wmo-data-access_merra-2/','Recommended products - map visualization','The Giovanni MERRA-2 portal provides access to data visualization, statistical analysis, and download.','official_documentation'),
('C16','IMERG technical documentation','https://gpm.nasa.gov/sites/default/files/2023-07/IMERG_TechnicalDocumentation_final_230713.pdf','Product resolution paragraph','All three Runs create half-hourly 0.1°×0.1° products','official_documentation'),
('C17','IMERG latency','https://gpm.nasa.gov/resources/faq/what-determines-latency-imerg','Final Run paragraph','usually giving a latency of about 3.5 months.','official_documentation'),
('C18','MOD14A1.061 Earth Engine catalog','https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MOD14A1','Description, line 69','The product distinguishes between fire, no fire and no observation.','platform_documentation'),
('C19','VNP14A1 NASA product record','https://ladsweb.modaps.eosdis.nasa.gov/missions-and-measurements/products/VNP14A1','Title, line 0','VIIRS/NPP Level 3 Daily Gridded Active Fire 1 km','official_product_record'),
('C20','NASA VIIRS burned area product validation and MODIS comparison','https://doi.org/10.1016/j.rse.2025.115006','Abstract','using 561 interpreted Landsat image pairs','primary_research'),
('C21','Detection rates and biases of MODIS and agency reports','https://www.sciencedirect.com/science/article/pii/S0034425718304826','Abstract','nearly 250,000 agency reported wildfires as reference data','primary_research'),
('C22','NISAR CMR catalog query, live response','https://cmr.earthdata.nasa.gov/search/collections.json?keyword=NISAR%20GCOV&page_size=5','feed.entry[0].summary','These data are partially validated','live_api'),
('C23','FIRMS VIIRS South Asia 24-hour sample','https://firms.modaps.eosdis.nasa.gov/data/active_fire/viirs/csv/SUOMI_VIIRS_C2_South_Asia_24h.csv','Downloaded CSV header','latitude,longitude,bright_ti4,scan,track,acq_date,acq_time,satellite,confidence,version,bright_ti5,frp,daynight','live_api'),
('C24','POWER Dhaka-area 3-day sample','https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M,PRECTOTCORR&community=AG&longitude=90.4&latitude=23.8&start=20240101&end=20240103&format=JSON','properties.parameter.T2M.20240101','17.93','live_api'),
('C25','Trend generation documentation','https://gis.earthdata.nasa.gov/portal/help/en/11.5/analyze/generate-trend.htm','Notes','The Mann-Kendall test does not consider serial correlation or seasonal effects.','platform_documentation')
]
with (p/'sources.jsonl').open('w') as f, (p/'evidence.jsonl').open('w') as e:
 for sid,title,url,locator,quote,typ in rows:
  f.write(json.dumps(dict(source_id=sid,title=title,url=url,retrieved_at='2026-09-18',source_type=typ),ensure_ascii=False)+'\n')
  e.write(json.dumps(dict(evidence_id='E'+sid[1:],source_id=sid,quote=quote,locator=locator,support_status='verified_source_text' if typ!='user_supplied' else 'user_provided_brief',limitations='Single-source documentation establishes provider-specific facts, not independent validation of user outcomes.'),ensure_ascii=False)+'\n')
claims=[
('fire_access','FIRMS live regional CSV retrieved with 787 records.', ['C23'],'verified_live_sample'),
('power_access','POWER daily sample returned 3 daily values for each of two parameters.', ['C24'],'verified_live_sample'),
('nisar_access','CMR lists provisional GCOV collection C2854338529-ASF; binary granule was not downloaded.', ['C22'],'verified_metadata_only'),
('soil_api','SoilGrids official page reports temporarily paused REST service.', ['C06'],'verified_documentation'),
('effort','Effort-adjusted detection rates need observed-clear/no-fire information beyond positive-only FIRMS records.', ['C18','C23'],'inference_from_product_schemas'),
('recommendation','Fire harmonization is best fit for strong Python/remote-sensing team focused on practical Earth impact.', ['C01','C08','C18','C20'],'analyst_recommendation'),
('field_limits','Coarse climate/soil moisture grids cannot establish measured field-specific agronomic outcomes.', ['C02','C05'],'scale-based_inference'),
('nisar_quality','Provisional GCOV is suitable for exploratory analysis with explicit validation limitations.', ['C22'],'verified_metadata'),
]
with (p/'claims.jsonl').open('w') as f:
 for cid,claim,ids,status in claims:f.write(json.dumps(dict(claim_id=cid,claim=claim,source_ids=ids,status=status))+'\n')
(p/'run_manifest.json').write_text(json.dumps(dict(date='2026-09-18',task='Compare 14 NASA Space Apps 2026 challenges; deep-dive fire, farms, trends and NISAR',mode='deep',assumptions=['4-6 people','Strong Python/data science or remote sensing confirmed via parent','Practical Earth impact preferred','Hackathon MVP, not operational decision system'],providers=['web search/open','direct HTTPS small public samples'],limitations=['Main challenge web pages unavailable through web open; supplied brief used','Full historical fire archive not downloaded','No Earthdata authentication or remote-sensing binary granule download','Rankings are analyst judgments, not competition outcome probabilities']),indent=2))
print('Wrote',len(rows),'sources and evidence records')
