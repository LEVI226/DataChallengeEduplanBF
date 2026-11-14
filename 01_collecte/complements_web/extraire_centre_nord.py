"""Extraction traçable de la dernière colonne de quatre tableaux INSD.
Exécuter depuis ce dossier : python3 extraire_centre_nord.py
Prérequis : Python 3 et pdftotext (Poppler). Aucune clé ni API requise.
Les cellules publiées sont conservées ; les contrôles ne les corrigent pas.
"""
from pathlib import Path
import csv,json,subprocess,tempfile,xml.etree.ElementTree as ET
BASE=Path(__file__).resolve().parent
NS={'h':'http://www.w3.org/1999/xhtml'}
SOURCE='INSD_CentreNord_annuaire2024.pdf'
URL=next(r['url'] for r in json.loads((BASE/'registre_telechargements.json').read_text()) if r['fichier']==SOURCE)
TABLES={'ecoles':(83,84,85),'salles':(86,87,88),'eleves':(92,93,94),'enseignants':(101,102,103)}
PROVINCES={'Bam','Namentenga','Sanmatenga'}
rows=[]
with tempfile.TemporaryDirectory() as tmp:
    xml=Path(tmp)/'pages.html'
    subprocess.run(['pdftotext','-bbox-layout',str(BASE/SOURCE),str(xml)],check=True)
    pages=ET.parse(xml).findall('.//h:page',NS)
    for indicateur,numeros in TABLES.items():
        for num in numeros:
            words=pages[num-1].findall('.//h:word',NS)
            header=next(w for w in words if w.text=='23/24')
            previous=next(w for w in words if w.text=='22/23')
            limite=(float(previous.attrib['xMax'])+float(header.attrib['xMin']))/2
            debut=float(header.attrib['yMax'])+2
            left=[w for w in words if float(w.attrib['xMax'])<140 and float(w.attrib['yMin'])>debut]
            groups=[]
            for w in sorted(left,key=lambda w:(float(w.attrib['yMin']),float(w.attrib['xMin']))):
                y=float(w.attrib['yMin'])
                if groups and abs(y-groups[-1][0])<3:groups[-1][1].append(w)
                else:groups.append([y,[w]])
            pending=[];geo=None
            for y,ws in groups:
                text=' '.join(w.text or '' for w in ws)
                # Le PDF écrit « Pubic » pour Barsalogho, p. 94.
                if text.startswith('Pubic'):text=text.replace('Pubic','Public',1)
                statut=next((v for v in ['Public','Privé','Ensemble'] if text.startswith(v)),None)
                if statut is None:pending.append(text);continue
                if statut=='Public':geo=' '.join(pending);pending=[]
                else:pending=[]
                cells=sorted([w for w in words if (float(w.attrib['xMin'])+float(w.attrib['xMax']))/2>limite and abs(float(w.attrib['yMin'])-y)<3],key=lambda w:float(w.attrib['xMin']))
                raw=' '.join(w.text or '' for w in cells)
                assert raw.replace(' ','').isdigit(),(num,geo,statut,raw)
                rows.append(dict(region='Centre-Nord',territoire=geo,niveau='region' if geo=='Centre-Nord' else 'province' if geo in PROVINCES else 'commune',annee_scolaire='2023-2024',indicateur=indicateur,statut=statut,valeur=int(raw.replace(' ','')),cellule_source=raw,source=SOURCE,url=URL,page_pdf=num,verification='extraction_et_controles_arithmetiques; sans_confirmation_terrain'))
assert len(rows)==384,len(rows)
assert len({(r['indicateur'],r['territoire'],r['statut']) for r in rows})==384
checks=[]
for indicateur in TABLES:
    subset=[r for r in rows if r['indicateur']==indicateur]
    for geo in sorted({r['territoire'] for r in subset}):
        data={r['statut']:r['valeur'] for r in subset if r['territoire']==geo}
        checks.append(dict(indicateur=indicateur,controle='public_prive_ensemble',territoire=geo,calcule=data['Public']+data['Privé'],publie=data['Ensemble'],conforme=data['Public']+data['Privé']==data['Ensemble']))
    for statut in ['Public','Privé','Ensemble']:
        for niveau in ['commune','province']:
            total=sum(r['valeur'] for r in subset if r['niveau']==niveau and r['statut']==statut)
            regional=next(r['valeur'] for r in subset if r['niveau']=='region' and r['statut']==statut)
            checks.append(dict(indicateur=indicateur,controle=f'somme_{niveau}_{statut}',territoire='Centre-Nord',calcule=total,publie=regional,conforme=total==regional))
for name,data in [('INSD_CentreNord_primaire_2023_2024.csv',rows),('INSD_CentreNord_controles.csv',checks)]:
    with (BASE/'tables'/name).open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(data[0]));writer.writeheader();writer.writerows(data)
print(json.dumps({'cellules':len(rows),'territoires':len({r['territoire'] for r in rows}),'controles':len(checks),'conformes':sum(c['conforme'] for c in checks),'alertes':[c for c in checks if not c['conforme']]},ensure_ascii=False,indent=2))
