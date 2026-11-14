"""Extraction locale des colonnes 2023-2024, sans IA ni accès réseau.
Python 3, Poppler/pdftotext. Les valeurs publiées ne sont pas corrigées.
Les variantes typographiques des noms sont séparées des cellules numériques.
"""
from pathlib import Path
import csv,json,re,subprocess,xml.etree.ElementTree as ET,collections,unicodedata
BASE=Path(__file__).resolve().parent
SOURCES=BASE.parent/'complements_web'
NS={'h':'http://www.w3.org/1999/xhtml'}
CONFIG={
 'CentreEst':dict(region='Centre-Est',provinces=['Boulgou','Koulpélogo','Kourittenga'],communes=30,tables={
  'ecoles':[(8,'Boulgou'),(9,'Koulpélogo'),(10,'Kourittenga'),(11,None)],
  'salles':[(12,'Boulgou'),(13,'Koulpélogo'),(14,'Kourittenga'),(15,None)],
  'eleves':[(20,'Boulgou'),(21,'Koulpélogo'),(22,'Kourittenga'),(23,None)],
  'enseignants':[(32,'Boulgou'),(33,'Koulpélogo'),(34,'Kourittenga'),(35,None)],
  'ecoles_fermees_insecurite':[(41,'Boulgou'),(42,'Koulpélogo'),(43,'Kourittenga'),(44,None)]}),
 'Est':dict(region='Est',provinces=['Gnagna','Gourma','Komondjoari','Kompienga','Tapoa'],communes=27,tables={
  'ecoles':[(8,'Gnagna'),(9,'Gourma'),(10,'Komondjoari'),(11,'Kompienga'),(12,'Tapoa'),(13,None)],
  'salles':[(14,'Gnagna'),(16,'Gourma'),(18,'Komondjoari'),(20,'Kompienga'),(22,'Tapoa'),(24,None)],
  'eleves':[(26,'Gnagna'),(27,'Gourma'),(28,'Komondjoari'),(29,'Kompienga'),(30,'Tapoa'),(31,None)],
  'enseignants':[(44,'Gnagna'),(45,'Gourma'),(46,'Komondjoari'),(47,'Kompienga'),(48,'Tapoa'),(49,None)],
  'ecoles_fermees_insecurite':[(55,'Gnagna'),(56,'Gourma'),(57,'Komondjoari'),(58,'Kompienga'),(59,'Tapoa'),(60,None)]})}
def plain(s):return ''.join(c for c in unicodedata.normalize('NFD',s.lower()) if not unicodedata.combining(c)).replace(' ','').replace('-','')
def group_words(words,tolerance=2.7):
 groups=[]
 for w in sorted(words,key=lambda w:(float(w.attrib['yMin']),float(w.attrib['xMin']))):
  y=float(w.attrib['yMin'])
  if groups and abs(y-groups[-1][0])<tolerance:groups[-1][1].append(w)
  else:groups.append([y,[w]])
 return groups
def text(ws):return ' '.join(w.text or '' for w in sorted(ws,key=lambda w:float(w.attrib['xMin'])))
def geo_normalise(raw,province,conf):
 s=raw.strip()
 if plain(s).startswith('total'):
  if 'region' in plain(s):return conf['region'],'region'
  if province:return province,'province'
 if plain(s) in ['centreest','est']:return conf['region'],'region'
 for p in conf['provinces'] if province is None else []:
  if plain(s)==plain(p) or plain(s)=='koulpelogo' and p=='Koulpélogo':return p,'province'
 return s,'commune'
def save(name,records):
 with (BASE/name).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
allrows=[];warnings=[]
for key,conf in CONFIG.items():
 source=f'INSD_{key}_annuaire2024.pdf';url=next(r['url'] for r in json.loads((SOURCES/'registre_telechargements.json').read_text()) if r['fichier']==source)
 xml=BASE/f'{key}_coordonnees.html'
 subprocess.run(['pdftotext','-bbox-layout',str(SOURCES/source),str(xml)],check=True)
 pages=ET.parse(xml).findall('.//h:page',NS)
 tablemap={num:(ind,prov) for ind,items in conf['tables'].items() for num,prov in items}
 current=None;lastgeo={}
 for pn,page in enumerate(pages,1):
  if not 80<=pn<=130:continue
  words=page.findall('.//h:word',NS)
  headings=[]
  for line in page.findall('.//h:line',NS):
   t=text(line.findall('h:word',NS));m=re.search(r'^Tableau\s*([\d\s.]+)\s*:',t)
   if m:
    parts=re.findall(r'\d+',m[1]);headings.append((float(line.attrib['yMin']),int(parts[-1]) if len(parts)>=3 and parts[-2]=='04' else -1))
  headers=[w for w in words if w.text=='23/24']
  events=sorted([(y,'table',id) for y,id in headings]+[(float(w.attrib['yMin']),'header',w) for w in headers],key=lambda x:x[0])
  for ei,(y,kind,value) in enumerate(events):
   if kind=='table':current=value;continue
   if current not in tablemap:continue
   ind,province=tablemap[current];h=value
   stop=min([ey for ey,_,_ in events[ei+1:] if ey>y+2]+[float(page.attrib['height'])-45])
   y0=float(h.attrib['yMin'])+5
   prev=[w for w in words if w.text in ['22/23','22/123'] and abs(float(w.attrib['yMin'])-y)<3]
   if not prev:raise ValueError(('Avant-dernière colonne introuvable',key,pn,current))
   lastx=(float(h.attrib['xMin'])+float(prev[-1].attrib['xMax']))/2
   firsthead=[float(w.attrib['xMin']) for w in words if re.fullmatch(r'\d\d/\d\d',w.text or '') and abs(float(w.attrib['yMin'])-y)<3]
   leftlimit=min(firsthead)-5
   left=[w for w in words if float(w.attrib['xMax'])<leftlimit and y0<float(w.attrib['yMin'])<stop]
   pending=[];geo=lastgeo.get(current)
   for ry,ws in group_words(left):
    t=text(ws);clean=plain(t)
    status=next((s for k,s in [('public','Public'),('prive','Privé'),('ensemble','Ensemble'),('pubic','Public')] if clean==k),None)
    if status is None:
     if re.match(r'^\d+\s',t) or 'Annuaire' in t or re.match(r'^\d+\s*\|',t) or t.startswith(('Source','STATISTIQUES','ORGANISATION','___')):continue
     pending.append(t);continue
    if status=='Public':
     if pending:geo=' '.join(pending)
     if geo is None:raise ValueError(('Territoire manquant',key,pn,current,ry))
     lastgeo[current]=geo;pending=[]
    elif pending:
     warnings.append((key,pn,current,'nom_non_public',pending));pending=[]
    cells=sorted([w for w in words if (float(w.attrib['xMin'])+float(w.attrib['xMax']))/2>lastx and abs(float(w.attrib['yMin'])-ry)<3],key=lambda w:float(w.attrib['xMin']))
    raw=text(cells);numeric=raw.replace(' ','').replace('\u00a0','')
    if numeric and numeric.lower() not in ['nd','-','...'] and not numeric.isdigit():raise ValueError(('Cellule non entière',key,pn,current,geo,status,raw))
    territory,level=geo_normalise(geo,province,conf)
    allrows.append(dict(region=conf['region'],province=province or (territory if level=='province' else ''),territoire=territory,territoire_source=geo,niveau=level,annee_scolaire='2023-2024',indicateur=ind,statut=status,valeur=int(numeric) if numeric.isdigit() else '',statut_cellule='publiee' if numeric.isdigit() else 'manquante',cellule_source=raw,tableau=f'02.04.{current:03d}',portee_table='communes' if province else 'provinces',page_pdf=pn,source=source,url=url,validation='extraction_documentaire; controle_arithmetique_separe; pas_confirmation_terrain'))
   if pending:lastgeo[current]=' '.join(pending)
# Harmoniser les seules variantes d’accentuation et de tirets, à partir des noms des écoles.
canon={(r['region'],r['province'],plain(r['territoire'])):r['territoire'] for r in allrows if r['indicateur']=='ecoles' and r['niveau']=='commune'}
for r in allrows:
 if r['niveau']=='commune':r['territoire']=canon.get((r['region'],r['province'],plain(r['territoire'])),r['territoire'])
save('cellules_publiees.csv',allrows)
print('Cellules brutes',len(allrows),'avertissements',warnings[:10])
for key,c in CONFIG.items():
 rs=[r for r in allrows if r['region']==c['region']]
 print(c['region'],dict(collections.Counter(r['indicateur'] for r in rs)))
 for ind in c['tables']:
  ss=[r for r in rs if r['indicateur']==ind]
  communes={r['territoire'] for r in ss if r['niveau']=='commune'}
  print(ind,len(communes),'attendu',c['communes'])
