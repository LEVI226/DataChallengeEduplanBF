"""Concordance entre deux implémentations indépendantes des répartitions."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import unittest

RACINE = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("node"), "Node est nécessaire pour le contrôle Python/JS, pas pour utiliser l'interface")
class ConcordanceMoteurTest(unittest.TestCase):
    def test_allocations_identiques_sur_les_situations_exportees(self):
        fichier = RACINE / "tableau_de_bord/donnees.js"
        self.assertTrue(fichier.is_file(), "Relancer la chaîne avant le contrôle d'export")
        source = fichier.read_text(encoding="utf-8")
        data = json.loads(source.removeprefix("window.DCB_DATA=").removesuffix(";\n"))
        spec = importlib.util.spec_from_file_location("repartition_reference", RACINE / "code/05_repartition.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        cases = []
        for scenario in data["scenarios"]:
            for ressource in ["maitres", "salles"]:
                for budget in [0, 1, 500, 2000]:
                    for regle in ["proportionnelle", "deficit_d_abord", "egalisation"]:
                        eleves = [p["demandes"][scenario["id"]] for p in data["provinces"]]
                        stocks = [p[ressource] for p in data["provinces"]]
                        cases.append({"scenario": scenario["id"], "ressource": ressource,
                                      "budget": budget, "regle": regle, "eleves": eleves, "stocks": stocks,
                                      "attendu": module.repartir(eleves, stocks, budget, regle).tolist()})
        script = "const fs=require('fs'),m=require(process.argv[1]);const cs=JSON.parse(fs.readFileSync(0,'utf8'));process.stdout.write(JSON.stringify(cs.map(c=>m.repartir(c.eleves,c.stocks,c.budget,c.regle,50))));"
        r = subprocess.run(["node", "-e", script, str(RACINE / "tableau_de_bord/moteur.js")],
                           input=json.dumps(cases), capture_output=True, text=True, check=True)
        obtenus = json.loads(r.stdout)
        self.assertEqual(len(obtenus), len(cases))
        for case, obtenu in zip(cases, obtenus):
            with self.subTest(scenario=case["scenario"], ressource=case["ressource"], budget=case["budget"], regle=case["regle"]):
                self.assertEqual(obtenu, case["attendu"])

    def test_franchissement_scenarios_seuils_et_phases(self):
        import sys
        sys.path.insert(0, str(RACINE/'code'))
        from allocation_objectifs import repartir_seuil
        data = json.loads((RACINE/'tableau_de_bord/donnees.js').read_text().removeprefix('window.DCB_DATA=').removesuffix(';\n'))
        cases = []
        for scenario in data['scenarios']:
            for res in ['maitres', 'salles']:
                for seuil in [40, 43.8, 50, 55.5, 60]:
                    for budget in [0, 1, 2000, 6000]:
                        e = [p['demandes'][scenario['id']] for p in data['provinces']]
                        s = [p[res] for p in data['provinces']]
                        cases.append(dict(e=e, s=s, seuil=seuil, budget=budget, attendu=repartir_seuil(e,s,budget,seuil)))
        script = "const m=require(process.argv[1]); const cs=JSON.parse(require('fs').readFileSync(0,'utf8')); process.stdout.write(JSON.stringify(cs.map(c=>m.repartirSeuil(c.e,c.s,c.budget,c.seuil))));"
        out = subprocess.run(['node','-e',script,str(RACINE/'tableau_de_bord/moteur.js')],input=json.dumps(cases),text=True,capture_output=True,check=True)
        for case, got in zip(cases, json.loads(out.stdout)):
            self.assertEqual(got, case['attendu'])
