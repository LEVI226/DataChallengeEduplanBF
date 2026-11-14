"""Signaler, par commune, les contrôles locaux et ceux de sa province.
La qualification reste documentaire et n'est jamais un statut de sécurité.
"""
from pathlib import Path
import csv,collections,json
BASE=Path(__file__).resolve().parent
rows=list(csv.DictReader((BASE/'primaire_communes_provinces_2023_2024.csv').open()))
checks=list(csv.DictReader((BASE/'controles_annuaires.csv').open()))
out=[]
for region,province,commune in sorted({(r['region'],r['province'],r['territoire']) for r in rows if r['niveau']=='commune'}):
 for ind in ['ecoles','salles','eleves','enseignants','ecoles_fermees_insecurite']:
  cells=[r for r in rows if (r['region'],r['province'],r['territoire'],r['niveau'],r['indicateur'])==(region,province,commune,'commune',ind)]
  assert len(cells)==3
  local=[c for c in checks if (c['region'],c['indicateur'],c['territoire'],c['controle'])==(region,ind,commune,'public_prive_ensemble')]
  provincial=[c for c in checks if (c['region'],c['indicateur'],c['territoire'],c['controle'])==(region,ind,province,'somme_communes')]
  regional=[c for c in checks if (c['region'],c['indicateur'],c['controle'])==(region,ind,'somme_provinces')]
  out.append(dict(region=region,province=province,commune=commune,annee_scolaire='2023-2024',indicateur=ind,cellules_publiees=sum(c['valeur']!='' for c in cells),triplet_local='non_verifiable' if any(c['resultat']=='non_verifiable' for c in local) else 'alerte' if any(c['resultat']=='alerte' for c in local) else 'conforme',somme_communes_province='alerte' if any(c['resultat']=='alerte' for c in provincial) else 'non_verifiable' if any(c['resultat']=='non_verifiable' for c in provincial) else 'conforme',somme_provinces_region='alerte' if any(c['resultat']=='alerte' for c in regional) else 'conforme',usage='contexte historique uniquement' if ind=='ecoles_fermees_insecurite' else 'analyse documentaire ; ne remplace pas les observations 2024-2025',source=cells[0]['source'],pages_pdf=','.join(sorted({r['page_pdf'] for r in cells},key=int))))
assert len(out)==285
with (BASE/'qualite_communes.csv').open('w',encoding='utf-8',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
print('285 qualifications documentaires ; aucun statut de sécurité déduit.')
