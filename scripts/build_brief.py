from pathlib import Path
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/pdf'
OUT.mkdir(parents=True, exist_ok=True)
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='TitleCustom', fontName='Helvetica-Bold', fontSize=31, leading=35, textColor=colors.HexColor('#20343D'), spaceAfter=20))
styles.add(ParagraphStyle(name='SectionCustom', fontName='Helvetica-Bold', fontSize=19, leading=23, spaceAfter=14, textColor=colors.HexColor('#20343D')))
styles.add(ParagraphStyle(name='BodyCustom', fontName='Helvetica', fontSize=10.5, leading=16, spaceAfter=12, textColor=colors.HexColor('#20343D')))
styles.add(ParagraphStyle(name='SmallCustom', fontName='Helvetica', fontSize=8.5, leading=12, spaceAfter=8))
story=[]
def p(s,style='BodyCustom'):story.append(Paragraph(s,styles[style]))
def heading(s):p(s,'SectionCustom')
def page():story.append(PageBreak())
def link(label,url):return f'<link href="{url}" color="#245D78">{label}</link>'
def table(rows,widths):
 t=Table([[Paragraph(str(c),styles['SmallCustom']) for c in row] for row in rows],colWidths=widths,repeatRows=1,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E4ECF0')),('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,0),(-1,-1),.4,colors.HexColor('#CDD8DE'))]))
 story.append(t)

p('NASA Space Apps 2026 / Team decision brief','SmallCustom')
p('Fire Season','TitleCustom')
p('Did burning change, or did the observing system change?','SectionCustom')
p('Recommended challenge: <b>Harmonization of MODIS and VIIRS Hot Spots.</b> Build a reproducible burning-activity calendar that reveals seasonality, unusual observations and the limits of cross-satellite comparisons.')
p('This recommendation fits your confirmed strength in Python, data science and remote sensing, and your preference for practical Earth impact. It is a reasoned selection, not a prediction of winning odds.')
p('The product serves a regional environmental analyst preparing a monitoring brief. Its signature interaction compares native sensor records with an evaluated common-reference estimate, then opens the source receipt and uncertainty behind the result.')
p('<b>Choose provisionally.</b> Before committing the team, download and decode one real paired historical fire-mask sample. Catalog discovery and recent public CSV access succeeded; historical mask extraction and model validation remain uncompleted.')
p('Prepared 19 September 2026. Research began 18 September. This is a planning package, not a deployed application or validated forecasting service.','SmallCustom')
p(link('Official challenge', 'https://www.spaceappschallenge.org/2026/challenges/harmonization-of-modis-and-viirs-hot-spots/'),'SmallCustom')
page()
heading('Why this challenge')
p('The following ordering is analyst judgment using practical impact, data readiness, distinctiveness, demonstration quality, feasibility and validation tractability. The full memo records the weights and limitations. Ten options received brief-level review; four Earth-focused choices received deeper data checks.')
table([['Challenge','Score / 5','Decision'],['Fire harmonization','4.75','Best match to your team'],['Field Shift','4.30','Strong with an agronomist'],['Earth System Trend Detective','4.20','Best fallback'],['Dancing with the SARs','4.00','Requires verified repeat imagery'],['Earth Information Jukebox','3.85','Accessibility-led alternative'],['Junior Astronaut Trainer','3.80','Education/game focus'],['Space Mission Design Game','3.65','Scope risk'],['CLPS Lunar Mission Browser','3.50','Geometry expertise needed'],['Abandoned but not Forgotten','3.50','Storytelling focus'],['Flame in Freefall','3.35','Experimental comparability risk'],['Earth analog locations','3.30','Similarity-validation risk'],['Martian Map','3.25','Integration/safety-claim risk'],['Astronaut health monitoring','3.10','Clinical-validation burden'],['Planet X and SPHEREx','3.00','Astronomy/data gate']], [302,62,135])
page()
heading('What makes it different')
p('G.R.O.W., a 2024 Local Impact winner, already has a public implementation combining FIRMS, maps, weather and a voice assistant. Another conversational fire map would be weak differentiation. Fire Season focuses on whether historical comparisons remain credible when the observation system changes.')
p('<b>The minimum product:</b> one regional calendar, native sensor comparison, visible coverage gaps, a validated transfer where available, an inspectable month, and a downloadable method receipt. A second region provides a geographical hold-out test.')
p('<b>The user flow:</b> select a region; inspect the seasonal calendar; open an unusual month; compare native and reference-scale values; inspect uncertainty; export a monitoring brief. Missing support produces an explicit unavailable result.')
p('<b>The visual direction:</b> a continuous year-by-month calendar, restrained slate/blue surfaces and an orange activity scale. Hatching means missing observations. Modeled values and observed values have different marks. The map provides context instead of dominating the product.')
p('The MVP does not predict spread, assign ignition cause, estimate burned hectares from hotspot counts or issue evacuation instructions. A language model may explain a saved result; it cannot invent measurements or override scientific gates.')
p(link('NASA 2024 winners','https://www.nasa.gov/learning-resources/stem-engagement-at-nasa/nasa-international-space-apps-challenge-announces-2024-global-winners/')+' / '+link('GROW implementation','https://github.com/Florianopolis-NASA-Space-Apps/wildfires_chat_dashboard'),'SmallCustom')
page()
heading('The scientific contract')
p('Use compatible daily 1 km masks from Aqua MODIS and Suomi-NPP VIIRS for the historical study. Preserve the platform, collection, acquisition interval and QA policy. Recent FIRMS 375 m points are a separate context layer; their counts must not be divided by the daily-mask support.')
p('<b>Metric:</b> detected active land-cell-days per 1,000 valid observed land-cell-days. Cloud, missing and unknown observations are not zero fire activity. Daily composites support a valid-cell-day metric, not a complete correction for clear overpass effort.')
p('<b>Model:</b> start with native and simple seasonal baselines, then test a grouped binomial GLM that maps VIIRS activity onto an Aqua reference scale. Fit on paired valid support. Evaluate on withheld years and a separate region. Quantify bias, rate error, seasonal timing and interval coverage.')
p('<b>Release gate:</b> demonstrate improvement over simple baselines and inspect residual failures. Keep poor-support or out-of-domain results unavailable. Thresholds in the protocol are proposed acceptance targets, not achieved results.')
p('NASA currently announces Suomi-NPP science-product delivery ending on 1 November 2026. Historical NPP observations remain useful, but a contemporary NOAA-20/21 extension requires separate calibration. The event is listed for 14-15 November 2026.')
p(link('MODIS product guide','https://www.earthdata.nasa.gov/s3fs-public/2023-09/MODIS_C6_C6.1_Fire_User_Guide_1.0.pdf')+' / '+link('VIIRS product and transition notice','https://www.earthdata.nasa.gov/data/catalog/lpcloud-vnp14a1-002'),'SmallCustom')
page()
heading('Build and recruit around the core')
p('<b>Architecture:</b> React/TypeScript calendar and MapLibre context map; FastAPI; PostgreSQL/PostGIS for metadata and ownership; a Python worker with Parquet/DuckDB for analytical data; immutable object storage for granules, models and receipts. No GPU is required for the proposed GLM.')
p('The supplied SQL defines 13 tables covering users, datasets, granules, snapshots, regions, calibrations, analyses, jobs, monthly results, artifacts, briefs and idempotency. It has not been applied to a database. Runtime roles, grants, worker access and scientific invariants still need implementation and integration tests.')
table([['Responsibility','Deliverable'],['Remote-sensing/statistics lead','Metric, transfer, held-out evaluation'],['Data engineer','Paired masks, QA and provenance'],['Backend engineer','Analysis API, immutable export'],['Visualization/frontend engineer','Calendar and evidence inspection'],['Product/research lead','User testing, reference checks, story']], [205,294])
story.append(Spacer(1,15))
p('During the event, spend the first quarter on real data and native calendars, the next quarter on transfer and evaluation, and the remainder on integration, user tests and presentation. Cut the optional assistant before cutting validity or the reliable demo.')
p('Confirm the current 2026 rules for pre-event work, team size, AI disclosure and submission format. The discovered detailed guide still carries a 2025 label; historical rules are not silently treated as current.','SmallCustom')
page()
heading('Evidence, limits and next decision')
p('<b>Checked:</b> all 14 challenge briefs; 2023-2025 winner identities and relevant prior art; NASA fire-product manuals; public FIRMS and POWER samples; historical fire/HLS/NISAR catalog discovery; crop-model and EO-model repositories; selected license texts; and the requested skill resources.')
p('<b>Not yet checked end to end:</b> authenticated historical raster extraction, fitted harmonization, model accuracy, region-specific ground truth, real user benefit, production deployment and database migration. No social-impact number or model benchmark has been fabricated.')
p('Three ECC skills were installed: API design, PostgreSQL patterns and verification loop. Other skill repositories were reviewed selectively. Their availability is not evidence that a scientific method has been validated.')
p('<b>Next decision:</b> recruit the science/data pair first and run the paired-mask feasibility gate. If it passes, form the team around Fire Season. If it fails, use the prepared Trend Detective fallback. Field Shift becomes more attractive with a reachable agronomist and local farming partner.')
p('The complete workspace contains the challenge comparison, winner registry, source/evidence ledgers, PRD, TRD, model/data protocol, app-flow design, team plan, backend schema and repository/skill audits. Read README.md or the generated research-report.html to navigate it.')
p(link('Official event','https://www.spaceappschallenge.org/')+' / '+link('2026 terms','https://www.spaceappschallenge.org/legal/')+' / '+link('Submission guide - verify year','https://www.spaceappschallenge.org/resources/project-submission-guide/'),'SmallCustom')

def footer(canvas,doc):
 canvas.setStrokeColor(colors.HexColor('#CDD8DE'));canvas.line(48,44,547,44)
 canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#4E626C'))
 canvas.drawString(48,30,'Fire Season / Research and planning / 19 September 2026')
 canvas.drawRightString(547,30,str(doc.page))

doc=SimpleDocTemplate(str(OUT/'fire-season-decision-brief.pdf'),pagesize=(595,842),rightMargin=48,leftMargin=48,topMargin=47,bottomMargin=60,title='Fire Season - NASA Space Apps 2026 decision brief',author='Research and planning')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(OUT/'fire-season-decision-brief.pdf')
