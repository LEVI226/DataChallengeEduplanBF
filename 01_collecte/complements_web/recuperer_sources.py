"""Retélécharger les sources publiques du registre, sans compte ni clé.
Depuis ce dossier : python3 recuperer_sources.py
Les fichiers existants sont contrôlés ; aucun original différent n'est écrasé.
"""
from pathlib import Path
import hashlib,json,urllib.request
BASE=Path(__file__).resolve().parent
for item in json.loads((BASE/'registre_telechargements.json').read_text()):
    if item['statut']!='telecharge':continue
    path=BASE/item['fichier']
    data=path.read_bytes() if path.exists() else urllib.request.urlopen(item['url'],timeout=90).read()
    assert data.startswith(b'%PDF'),f"Réponse non PDF : {path.name}"
    assert hashlib.sha256(data).hexdigest()==item['sha256'],f"Contenu différent du registre : {path.name}"
    if not path.exists():path.write_bytes(data)
    print('SHA-256 conforme :',path.name)
