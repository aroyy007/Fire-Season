"""Read-only checks. Python stdlib only. Does not install/run downloaded code."""
import csv, datetime, hashlib, io, json, pathlib, urllib.request, urllib.error
OUT=pathlib.Path(__file__).resolve().parent
CHECKS={
'power_sample':'https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M_MAX,T2M_MIN,PRECTOTCORR,ALLSKY_SFC_SW_DWN,RH2M,WS2M&community=AG&longitude=89.55&latitude=24.85&start=20240101&end=20240107&format=JSON',
'hls_cmr_sample':'https://cmr.earthdata.nasa.gov/search/granules.json?short_name=HLSS30&version=2.0&bounding_box=89.50,24.80,89.60,24.90&temporal=2024-01-01T00:00:00Z,2024-01-31T23:59:59Z&page_size=2',
'soilgrids_sample':'https://rest.isric.org/soilgrids/v2.0/properties/query?lon=89.55&lat=24.85&property=clay&depth=0-5cm&value=mean',
'firms_modis_sample':'https://firms.modaps.eosdis.nasa.gov/data/active_fire/modis-c6.1/csv/MODIS_C6_1_SouthEast_Asia_24h.csv',
'firms_viirs_sample':'https://firms.modaps.eosdis.nasa.gov/data/active_fire/suomi-npp-viirs-c2/csv/SUOMI_VIIRS_C2_SouthEast_Asia_24h.csv',
}
REPOS=['ajwdewit/pcse','aquacropos/aquacrop','APSIMInitiative/ApsimX','DSSAT/dssat-csm-os','KUL-RSDA/AquaCrop','torchgeo/terratorch','NASA-IMPACT/Prithvi-EO-2.0','NASA-IMPACT/hls-foundation-os','nasa/earthaccess','isce-framework/isce3','insarlab/MintPy','NASA-IMPACT/hls-vi','ajwdewit/WOFOST_crop_parameters']
for repo in REPOS:
 CHECKS['repo_'+repo.replace('/','__')]='https://api.github.com/repos/'+repo
 CHECKS['license_'+repo.replace('/','__')]='https://api.github.com/repos/'+repo+'/license'
records=[]
for name,url in CHECKS.items():
 rec={'name':name,'url':url,'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'NASA-Space-Apps-research-readonly','Accept':'application/json' if 'api.github' in url else '*/*'})
  with urllib.request.urlopen(req,timeout=30) as r:
   body=r.read();rec.update(status=r.status,content_type=r.headers.get('Content-Type'),bytes=len(body),final_url=r.url,sha256=hashlib.sha256(body).hexdigest())
  ext='.json' if 'json' in rec['content_type'] or name.startswith(('repo_','license_')) else '.csv' if 'firms_' in name else '.txt'
  path=OUT/(name+ext);path.write_bytes(body);rec['response_file']=path.name
  if ext=='.json':
   obj=json.loads(body)
   if name=='power_sample':rec['validation']={'parameters':list(obj['properties']['parameter']),'day_counts':{k:len(v) for k,v in obj['properties']['parameter'].items()},'units':obj.get('parameters'),'missing_value':obj.get('header',{}).get('fill_value')}
   if name=='hls_cmr_sample':rec['validation']={'returned_granules':len(obj.get('feed',{}).get('entry',[]))}
   if name.startswith('repo_'):rec['validation']={'license':obj.get('license'),'default_branch':obj.get('default_branch'),'pushed_at':obj.get('pushed_at'),'archived':obj.get('archived')}
  if ext=='.csv':
   rows=list(csv.DictReader(io.StringIO(body.decode())));rec['validation']={'rows':len(rows),'columns':list(rows[0]) if rows else []}
 except Exception as e:rec['error']=str(e)
 records.append(rec);print(name,rec.get('status'),rec.get('bytes'),rec.get('error',''),flush=True)
 (OUT/'endpoint_evidence.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in records))
