"""Régénérer les compléments documentaires V2, sans réseau ni API.
Ne modifie pas les calculs ni les données du simulateur.
Python 3, Poppler/pdftotext ; extraire les sept ZIP V2 à une même racine.
"""
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=[
 '01_collecte/complements_web/extraire_centre_nord.py',
 '01_collecte/complements_insd_20261114/extraire_odfa.py',
 '01_collecte/complements_insd_20261114/controler_odfa.py',
 '01_collecte/rapprochement_20261114/extraire_annuaires.py',
 '01_collecte/rapprochement_20261114/controler_annuaires.py',
 '01_collecte/rapprochement_20261114/rapprocher_sources.py',
 '01_collecte/rapprochement_20261114/qualifier_communes.py']
def main():
    for script in SCRIPTS:
        p=ROOT/script
        if not p.is_file():raise FileNotFoundError(f'Complément absent : {script}. Extraire aussi l’archive de code et les deux archives de collecte V2.')
        subprocess.run([sys.executable,str(p)],cwd=ROOT,check=True)
if __name__=='__main__':main()
