from pathlib import Path
import json, re, hashlib

ROOT=Path(__file__).resolve().parents[1]
sources=[]; seen=set()
for name in ['challenges','winners']:
 for line in (ROOT/'research'/name/'sources.jsonl').read_text().splitlines():
  s=json.loads(line)
  if s['url'] not in seen:sources.append(s);seen.add(s['url'])
for p in sorted((ROOT/'docs').glob('*.md')):
 for title,url in re.findall(r'\[([^\]]+)\]\((https?://[^\s)]+)\)',p.read_text()):
  if url not in seen:
   sources.append({'source_id':'R'+hashlib.sha256(url.encode()).hexdigest()[:10], 'title':title,'url':url,'retrieved_at':'2026-09-18/19','source_type':'linked_primary_reference','verification':'See module and endpoint ledgers; not all references have automated HTTP validation.'});seen.add(url)
(ROOT/'research/sources.jsonl').write_text('\n'.join(json.dumps(s,ensure_ascii=False) for s in sources)+'\n')
for name in ['evidence','claims']:
 rows=[]
 for folder in ['challenges','winners']:
  for line in (ROOT/'research'/folder/(name+'.jsonl')).read_text().splitlines():
   d=json.loads(line);d['module']=folder;rows.append(d)
 if name=='evidence':
  for f in ['endpoint_evidence.jsonl','fire_endpoint_evidence.jsonl']:
   for line in (ROOT/'research/models'/f).read_text().splitlines():
    d=json.loads(line);d['module']='models';d['evidence_type']='request_log';rows.append(d)
 if name=='claims':
  rows += [{'claim_id':'P01','claim':'Fire Season is the recommended team-specific concept.','status':'analyst_judgment','support':'challenge-comparison.md'},
           {'claim_id':'P02','claim':'The proposed transfer model improves on baselines.','status':'not_tested_do_not_assert','support':'docs/03-MODEL-AND-DATA-PROTOCOL.md'},
           {'claim_id':'P03','claim':'The backend migration works in PostgreSQL.','status':'not_runtime_tested_do_not_assert','support':'backend/schema.sql'}]
 (ROOT/'research'/(name+'.jsonl')).write_text('\n'.join(json.dumps(s,ensure_ascii=False) for s in rows)+'\n')
text='# Source index\n\nResearch dates: 18–19 September 2026. Each entry is a source, not an independent validation of product performance. See the module-level evidence and endpoint logs for retrieval limits.\n\n'
for s in sources:text+=f"- **{s['source_id']}** — [{s['title']}]({s['url']})\n"
(ROOT/'research/SOURCES.md').write_text(text)

S={
 'Error':{'type':'object','required':['error'],'properties':{'error':{'type':'object','required':['code','message'],'properties':{'code':{'type':'string'},'message':{'type':'string'},'details':{'type':'array','items':{'type':'object'}}}}}},
 'Dataset':{'type':'object','required':['id','short_name','version','platform','access_status'],'properties':{'id':{'type':'integer'},'short_name':{'type':'string'},'version':{'type':'string'},'platform':{'type':'string'},'access_status':{'enum':['documented','discovered','downloaded','decoded']},'quality_notice':{'type':['string','null']}}},
 'RegionInput':{'type':'object','additionalProperties':False,'required':['name','geometry'],'properties':{'name':{'type':'string','minLength':1,'maxLength':200},'geometry':{'type':'object','required':['type','coordinates'],'properties':{'type':{'enum':['Polygon','MultiPolygon']},'coordinates':{'type':'array','minItems':1,'items':{'type':'array'}}},'description':'GeoJSON WGS84; server validates nesting, ranges, area, topology and <=10000 vertices.'}}},
 'Region':{'type':'object','required':['id','name','revision'],'properties':{'id':{'type':'string','format':'uuid'},'name':{'type':'string'},'revision':{'type':'integer','minimum':1},'is_public':{'type':'boolean'}}},
 'AnalysisInput':{'type':'object','additionalProperties':False,'required':['region_id','snapshot_id','start_date','end_date','baseline_years','qa_policy_version'],'properties':{'region_id':{'type':'string','format':'uuid'},'snapshot_id':{'type':'string','format':'uuid'},'calibration_id':{'type':['string','null'],'format':'uuid'},'start_date':{'type':'string','format':'date'},'end_date':{'type':'string','format':'date'},'baseline_years':{'type':'array','items':{'type':'integer','minimum':2000,'maximum':2100},'uniqueItems':True},'qa_policy_version':{'type':'string'}}},
 'Analysis':{'type':'object','required':['id','status'],'properties':{'id':{'type':'string','format':'uuid'},'status':{'enum':['queued','running','succeeded','failed','cancelled']},'comparison_status':{'enum':['available','experimental','insufficient_support','unsupported',None]},'error_code':{'type':['string','null']}}},
 'CalendarBin':{'type':'object','required':['month','value_kind','estimate','unit'],'properties':{'month':{'type':'string','format':'date'},'value_kind':{'enum':['observed','modeled','unavailable']},'estimate':{'type':['number','null'],'minimum':0,'maximum':1000},'lower_bound':{'type':['number','null']},'upper_bound':{'type':['number','null']},'unit':{'const':'active_cell_days_per_1000_valid_cell_days'},'valid_cell_days':{'type':['integer','null'],'minimum':0},'fire_cell_days':{'type':['integer','null'],'minimum':0},'unavailable_reason':{'type':['string','null']},'calibration_id':{'type':['string','null'],'format':'uuid'}}},
 'Receipt':{'type':'object','required':['analysis_id','input_sha256','source_manifest','method'],'properties':{'analysis_id':{'type':'string','format':'uuid'},'input_sha256':{'type':'string','pattern':'^[0-9a-f]{64}$'},'source_manifest':{'type':'array','items':{'type':'object','required':['source_url','sha256'],'properties':{'source_url':{'type':'string','format':'uri'},'sha256':{'type':'string'}}}},'method':{'type':'object'},'limitations':{'type':'array','items':{'type':'string'}}}},
 'BriefInput':{'type':'object','additionalProperties':False,'properties':{'generator':{'enum':['template','llm'],'default':'template'},'question':{'type':'string','maxLength':1000}}},
 'Brief':{'type':'object','required':['id','status','generator'],'properties':{'id':{'type':'string','format':'uuid'},'status':{'enum':['queued','running','succeeded','failed']},'generator':{'enum':['template','llm']},'body_markdown':{'type':['string','null']},'claims':{'type':'array','items':{'type':'object'}},'validation_result':{'type':['object','null']}}},
 'Detection':{'type':'object','required':['latitude','longitude','acquired_at','platform','product'],'properties':{'latitude':{'type':'number'},'longitude':{'type':'number'},'acquired_at':{'type':'string','format':'date-time'},'platform':{'type':'string'},'product':{'type':'string'},'processing_status':{'enum':['NRT','standard']}}}
}
def ref(name):return {'$ref':'#/components/schemas/'+name}
def response(name,many=False):
 schema={'type':'array','items':ref(name)} if many else ref(name)
 return {'description':'Successful response','content':{'application/json':{'schema':schema}}}
paths={}
def add(path,method,summary,output,status='200',request=None,many=False,auth=False):
 op={'summary':summary,'security':[{'bearerAuth':[]}] if auth else [{},{'bearerAuth':[]}],'responses':{status:response(output,many),'422':response('Error'),'429':response('Error'),'503':response('Error')}}
 if '{id}' in path:op['parameters']=[{'name':'id','in':'path','required':True,'schema':{'type':'string','format':'uuid'}}];op['responses']['404']=response('Error')
 if request:op['requestBody']={'required':True,'content':{'application/json':{'schema':ref(request)}}}
 if status in ['201','202']:op['responses'][status]['headers']={'Location':{'schema':{'type':'string'},'description':'Resource status URL'}}
 paths.setdefault('/api/v1'+path,{})[method]=op
add('/datasets','get','List supported datasets','Dataset',many=True)
add('/regions','get','List accessible regions','Region',many=True)
add('/regions','post','Create a private region revision','Region','201','RegionInput',auth=True)
add('/analyses','post','Request immutable analysis','Analysis','202','AnalysisInput',auth=True)
paths['/api/v1/analyses']['post']['parameters']=[{'name':'Idempotency-Key','in':'header','required':True,'schema':{'type':'string','minLength':1,'maxLength':200}}]
paths['/api/v1/analyses']['post']['responses']['409']=response('Error')
add('/analyses/{id}','get','Get analysis status','Analysis')
add('/analyses/{id}/calendar','get','Get monthly results','CalendarBin',many=True)
add('/analyses/{id}/receipt','get','Get reproduction receipt','Receipt')
add('/analyses/{id}/detections','get','Get recent context detections, not harmonization numerator','Detection',many=True)
add('/analyses/{id}/briefs','post','Create explanation with evidence validation','Brief','202','BriefInput',auth=True)
add('/briefs/{id}','get','Get explanation','Brief')
add('/analyses/{id}/cancel','post','Idempotently cancel owned active analysis','Analysis',auth=True)
for route in ['/api/v1/regions','/api/v1/analyses/{id}/detections']:
 op=paths[route]['get'];op.setdefault('parameters',[]).extend([{'name':'cursor','in':'query','schema':{'type':'string'}},{'name':'limit','in':'query','schema':{'type':'integer','minimum':1,'maximum':500,'default':100}}]);op['responses']['200']['headers']={'X-Next-Cursor':{'schema':{'type':'string'},'description':'Opaque next cursor, absent on final page'}}
api={'openapi':'3.1.0','info':{'title':'Fire Season proposed API','version':'0.1.0','description':'Design contract; not an implemented service. Cross-field scientific and access-control invariants are in docs/06-BACKEND-SCHEMA.md.'},'paths':paths,'components':{'schemas':S,'securitySchemes':{'bearerAuth':{'type':'http','scheme':'bearer'}}}}
(ROOT/'backend/openapi.json').write_text(json.dumps(api,indent=2)+'\n')
print(f'{len(sources)} unique linked sources; {sum(len(v) for v in paths.values())} API operations')
