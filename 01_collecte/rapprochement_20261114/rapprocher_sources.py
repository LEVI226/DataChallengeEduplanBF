"""Comparer sans modifier les sources : ODFA 2024, annuaires 2023-2024.
Les libellés de période et les champs sont conservés distincts.
"""
from pathlib import Path
import csv,json,collections,xml.etree.ElementTree as ET,subprocess,re,unicodedata,hashlib
BASE=Path(__file__).resolve().parent;PROJECT=BASE.parents[1]
NS={'h':'http://www.w3.org/1999/xhtml'}
def normal(s):return ''.join(c for c in unicodedata.normalize('NFD',s.upper()) if not unicodedata.combining(c)).replace('-',' ').strip()
def lire(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def save(name,records):
 with (BASE/name).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
prov=[r for r in lire(PROJECT/'02_nettoyage/EXX_02-nettoyage_D3_engineer_primaire-provinces-statut_v1.csv') if r['annee_scolaire']=='2023-2024' and r['niveau']=='province']
names={normal(r['province']):r['region'] for r in prov}
source=next((PROJECT/'01_collecte/datapack_extrait/DataPack_DCB_2026').rglob('CNS529*.pdf'))
xml=BASE/'CNS529_enseignants_coordonnees.html'
subprocess.run(['pdftotext','-f','206','-l','212','-bbox-layout',str(source),str(xml)],check=True)
current=None;teachers=[]
for pn,page in enumerate(ET.parse(xml).findall('.//h:page',NS),206):
 words=page.findall('.//h:word',NS);groups=[]
 for w in sorted([w for w in words if float(w.attrib['xMin'])<80 and float(w.attrib['yMin'])>150],key=lambda w:(float(w.attrib['yMin']),float(w.attrib['xMin']))):
  y=float(w.attrib['yMin'])
  if groups and abs(y-groups[-1][0])<1.4:groups[-1][1].append(w)
  else:groups.append([y,[w]])
 for y,ws in groups:
  t=' '.join(w.text or '' for w in ws);n=normal(t)
  if n in names:current=n;continue
  if current and n in ['FEMMES','HOMMES','TOTAL']:
   cells=sorted([w for w in words if 282<float(w.attrib['xMin'])<307 and abs(float(w.attrib['yMin'])-y)<1.4],key=lambda w:float(w.attrib['xMin']))
   raw=' '.join(w.text or '' for w in cells)
   assert raw.replace(' ','').isdigit(),(pn,current,t,raw)
   teachers.append(dict(region=names[current],province=current,sexe=n,valeur=int(raw.replace(' ','')),cellule_source=raw,source=source.name,tableau='IV.1.3 Public+Privé, total de tous les enseignants',page_pdf=pn,annee_scolaire='2023-2024',sha256_source=hashlib.sha256(source.read_bytes()).hexdigest()))
   if n=='TOTAL':current=None
assert len(teachers)==135 and len({r['province'] for r in teachers})==45,(len(teachers),len({r['province'] for r in teachers}))
assert len({(r['province'],r['sexe']) for r in teachers})==135
for p in names:
 vals={r['sexe']:r['valeur'] for r in teachers if r['province']==p}
 assert vals['FEMMES']+vals['HOMMES']==vals['TOTAL'],(p,vals)
save('CNS529_tous_enseignants_2023_2024.csv',teachers)
odfa={}
for id in ['tyliupe','cvbkpse']:
 for r in lire(PROJECT/f'01_collecte/complements_insd_20261114/tables/ODFA_{id}.csv'):
  if r['annee_libelle']!='2024':continue
  dims=json.loads(r['dimensions_json']);reg=normal(dims.get('régions',dims.get('region','')))
  if id=='tyliupe' and dims['sexe']=='Ensemble':odfa[(reg,'enseignants')]=float(r['valeur'])
  elif id=='cvbkpse':odfa[(reg,'salles' if dims['rubrique']=='Classes' else 'ecoles')]=float(r['valeur'])
comparison=[]
for reg in sorted({r['region'] for r in prov}):
 for ind in ['enseignants','ecoles','salles']:
  if ind=='enseignants':rs=[r for r in teachers if r['region']==reg and r['sexe']=='TOTAL'];number=sum(r['valeur'] for r in rs);field='tous enseignants, public+privé';pages=','.join(sorted({str(r['page_pdf']) for r in rs},key=int))
  else:rs=[r for r in prov if r['region']==reg and r['statut']=='Total'];number=sum(int(r[ind]) for r in rs);field=ind+', public+privé';pages=','.join(sorted({r['source_page'] for r in rs},key=int))
  value=odfa.get((normal(reg),ind));comparison.append(dict(region=reg,indicateur=ind,champ_cns=field,valeur_cns=number,valeur_odfa=value,ecart_odfa_moins_cns=value-number if value is not None else '',resultat='absent' if value is None else 'conforme' if value==number else 'ecart',periode_cns='2023-2024',periode_odfa='libellé annuel 2024 ; rapprochement documentaire, pas conversion automatique',source_cns=source.name,pages_pdf_cns=pages))
save('rapprochement_ODFA_CNS529_2024.csv',comparison)
# Les tableaux régionaux extraits sont comparés aux références DGESS à même millésime scolaire.
regional=lire(BASE/'primaire_communes_provinces_2023_2024.csv')+lire(PROJECT/'01_collecte/complements_web/tables/INSD_CentreNord_primaire_2023_2024.csv')
comparison_reg=[]
for r in regional:
 if r['niveau']!='region' or r['statut']!='Ensemble' or r['indicateur']=='ecoles_fermees_insecurite':continue
 key=(normal(r['region']),r['indicateur'])
 if r['indicateur']=='eleves':number=sum(int(x['eleves']) for x in prov if normal(x['region'])==key[0] and x['statut']=='Total');field='élèves, public+privé'
 else:
  match=next(x for x in comparison if (normal(x['region']),x['indicateur'])==key);number=match['valeur_cns'];field=match['champ_cns']
 value=int(r['valeur']);comparison_reg.append(dict(region=r['region'],indicateur=r['indicateur'],champ_cns=field,valeur_annuaire_regional=value,valeur_cns=number,ecart_regional_moins_cns=value-number,resultat='conforme' if value==number else 'ecart_a_expliquer',source_regional=r['source'],page_pdf_regional=r['page_pdf'],source_cns=source.name,annee_scolaire='2023-2024'))
save('rapprochement_annuaires_regionaux_CNS529.csv',comparison_reg)
print(json.dumps({'cns_enseignants_cellules':len(teachers),'controle_sexe_provinces':'45 conformes sur 45','national_tous_enseignants':sum(r['valeur'] for r in teachers if r['sexe']=='TOTAL'),'odfa_cns':dict(collections.Counter(r['resultat'] for r in comparison)),'regionaux_cns':dict(collections.Counter(r['resultat'] for r in comparison_reg)),'ecarts_regionaux':[r for r in comparison_reg if r['resultat']!='conforme']},ensure_ascii=False,indent=2))
