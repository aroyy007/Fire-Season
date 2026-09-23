"""Public historical metadata and documentation checks; no downloads of executable code."""
import datetime,hashlib,json,pathlib,urllib.request
OUT=pathlib.Path(__file__).resolve().parent
q='&bounding_box=92,20,100,28&temporal=2023-03-01T00:00:00Z,2023-03-08T23:59:59Z&page_size=2'
checks={
'fire_cmr_myd14a1':'https://cmr.earthdata.nasa.gov/search/granules.json?short_name=MYD14A1&version=061'+q,
'fire_cmr_vnp14a1':'https://cmr.earthdata.nasa.gov/search/granules.json?short_name=VNP14A1&version=002'+q,
'fire_cmr_vj114a1':'https://cmr.earthdata.nasa.gov/search/granules.json?short_name=VJ114A1&version=002'+q,
'fire_cmr_vnp14img':'https://cmr.earthdata.nasa.gov/search/granules.json?short_name=VNP14IMG&version=002'+q,
'fire_cmr_myd14':'https://cmr.earthdata.nasa.gov/search/granules.json?short_name=MYD14&version=061'+q,
'fireatlas_license':'https://raw.githubusercontent.com/Earth-Information-System/fireatlas/main/LICENSE',
'fireapp_license':'https://raw.githubusercontent.com/NASA-IMPACT/us-fire-events-tool/main/LICENSE',
'viirs_guide':'https://viirsland.gsfc.nasa.gov/PDF/VIIRS_activefire_User_Guide.pdf',
'modis_guide':'https://www.earthdata.nasa.gov/s3fs-public/2023-09/MODIS_C6_C6.1_Fire_User_Guide_1.0.pdf',
}
rows=[]
for name,url in checks.items():
 rec={'name':name,'url':url,'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'NASA-Space-Apps-research-readonly'}),timeout=30) as r:
   b=r.read();rec.update(status=r.status,bytes=len(b),content_type=r.headers.get('Content-Type'),sha256=hashlib.sha256(b).hexdigest())
  ext='.json' if 'cmr_' in name else '.pdf' if 'guide' in name else '.txt';path=OUT/(name+ext);path.write_bytes(b);rec['response_file']=path.name
  if ext=='.json':
   entries=json.loads(b).get('feed',{}).get('entry',[]);rec['validation']={'returned_granules':len(entries),'ids':[x['id'] for x in entries],'titles':[x.get('title') for x in entries]}
 except Exception as e:rec['error']=str(e)
 rows.append(rec);print(name,rec.get('status'),rec.get('validation',rec.get('error','')),flush=True)
 (OUT/'fire_endpoint_evidence.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in rows))
