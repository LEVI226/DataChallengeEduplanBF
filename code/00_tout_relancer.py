"""
Relance tout le travail, dans l'ordre, à partir des fichiers sources.

Lancer depuis le dossier DataChallenge :  python code/00_tout_relancer.py
Le script s'arrête au premier contrôle non conforme.
"""
from pathlib import Path
import subprocess
import sys

ETAPES = ["01_provinces_tableau_I1.py", "02_regions_series_10_ans.py", "03_indicateurs_provinces.py",
          "04_projection_2030.py", "05_repartition.py", "06_contexte_esu.py", "07_cartes_et_graphiques.py",
          "10_tableau_de_bord.py"]
DOSSIER = Path(__file__).resolve().parent

for etape in ETAPES:
    print(f"\n{'=' * 20} {etape} {'=' * 20}")
    resultat = subprocess.run([sys.executable, str(DOSSIER / etape)], cwd=DOSSIER.parent)
    if resultat.returncode != 0:
        sys.exit(f"Arrêt : {etape} a échoué.")
print("\nTout a été relancé sans erreur.")
