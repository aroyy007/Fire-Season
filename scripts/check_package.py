from pathlib import Path
import json,re,csv
ROOT=Path(__file__).resolve().parents[1]
errors=[];checks={}
api=json.loads((ROOT/'backend/openapi.json').read_text())
checks['api_operations']=sum(len(v) for v in api['paths'].values())
def walk(x):
 if isinstance(x,dict):
  if '$ref' in x:
   p=x['$ref'].split('/')[1:]; v=api
   try:
    for k in p:v=v[k]
   except KeyError:errors.append('Unresolved API reference: '+x['$ref'])
  for v in x.values():walk(v)
 elif isinstance(x,list):
  for v in x:walk(v)
walk(api)
checks['sql_tables']=len(re.findall(r'CREATE TABLE ',(ROOT/'backend/schema.sql').read_text()))
assert checks['sql_tables']==13
links=0
for p in [ROOT/'README.md',*sorted((ROOT/'docs').glob('*.md'))]:
 for _,url in re.findall(r'\[([^\]]+)\]\(([^)]+)\)',p.read_text()):
  if not url.startswith(('http:','https:','#')):
   links+=1
   if not (p.parent/url.split('#')[0]).exists():errors.append(f'Missing link in {p.name}: {url}')
checks['checked_local_links']=links
for name in ['sources','claims','evidence']:
 rows=[json.loads(l) for l in (ROOT/'research'/f'{name}.jsonl').read_text().splitlines()]
 checks[name+'_rows']=len(rows)
w=list(csv.DictReader((ROOT/'research/winners/global-winners-2023-2025.csv').open()))
checks['winner_rows']=len(w)
assert len(w)==30
assert len(set((r['competition_year'],r['global_award']) for r in w))==30
for p in (ROOT/'docs').glob('*.md'):
 if re.search(r'\b(?:TODO|TBD)\b',p.read_text()):errors.append('Unresolved placeholder: '+p.name)
checks['errors']=errors
checks['limits']=['SQL static inspection only; no PostgreSQL/PostGIS runtime migration test','No historical raster training or accuracy test','OpenAPI JSON/reference checks, not full external OpenAPI validator']
(ROOT/'output/qa/package-check.json').write_text(json.dumps(checks,indent=2))
print(json.dumps(checks,indent=2))
raise SystemExit(bool(errors))
