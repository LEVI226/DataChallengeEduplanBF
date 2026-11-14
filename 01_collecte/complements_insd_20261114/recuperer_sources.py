"""Récupérer les réponses publiques archivées, sans clé ni compte.
Depuis ce dossier : python3 recuperer_sources.py
Les originaux existants sont vérifiés ; un contenu distant modifié est refusé.
Les données individuelles EHCVM ne sont pas demandées par ce script.
"""
from pathlib import Path
import json,hashlib,urllib.request
BASE=Path(__file__).resolve().parent
for r in json.loads((BASE/'registre_sources.json').read_text()):
    if r['statut']!='recupere' or not r.get('fichier') or not r.get('sha256'):continue
    p=BASE/r['fichier']
    if p.exists():data=p.read_bytes()
    else:
        params=r.get('requete',r.get('parametres'))
        body=json.dumps(params).encode() if params is not None else None
        headers={'User-Agent':'Mozilla/5.0','Referer':'https://burkinafaso.opendataforafrica.org/'}
        if body is not None:headers['Content-Type']='application/json'
        data=urllib.request.urlopen(urllib.request.Request(r['url'],data=body,headers=headers),timeout=90).read()
    assert hashlib.sha256(data).hexdigest()==r['sha256'],f'Contenu modifié : {p.name}'
    if not p.exists():p.write_bytes(data)
    print('SHA-256 conforme :',p.name)
