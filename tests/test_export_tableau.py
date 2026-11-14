import importlib.util
from pathlib import Path
import unittest
import pandas as pd

SCRIPT = Path(__file__).resolve().parents[1] / "code/10_tableau_de_bord.py"


class ExportTableauTest(unittest.TestCase):
    def charger(self):
        self.assertTrue(SCRIPT.exists(), "Export du tableau de bord à implémenter")
        spec = importlib.util.spec_from_file_location("export_tableau", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_inconnues_esu_preservees_et_scenarios_rattaches_a_la_province(self):
        m = self.charger()
        ind = pd.DataFrame([dict(province="BAM", region="CENTRE NORD", eleves=100,
                                maitres=2, salles=3, groupes_pedagogiques=2,
                                inscriptions_region="proches du maximum")])
        besoins = pd.DataFrame([dict(province="BAM", scenario="demographie_insd", eleves_projetes=110)])
        esu = pd.DataFrame([dict(province="BAM", esu_ecoles_rouvertes=None,
                                esu_ecoles_rouvertes_statut="non_renseigne", esu_ecoles_delocalisees=0,
                                esu_ecoles_delocalisees_statut="renseigne", esu_eleves_deplaces=7,
                                esu_eleves_deplaces_statut="renseigne")])
        result = m.construire_donnees(ind, besoins, esu, {"BAM": []})
        province = result["provinces"][0]
        self.assertIsNone(province["esu"]["ecoles_rouvertes"])
        self.assertEqual(province["esu"]["ecoles_delocalisees"], 0)
        self.assertEqual(province["demandes"], {"actuel": 100, "demographie_insd": 110})

    def test_scenario_incomplet_ou_doublon_refuse(self):
        m = self.charger()
        ind = pd.DataFrame([dict(province=p, region="R", eleves=100, maitres=2,
                                salles=2, groupes_pedagogiques=2, inscriptions_region="") for p in ["A", "B"]])
        besoins = pd.DataFrame([dict(province="A", scenario="demographie_insd", eleves_projetes=110)])
        esu = pd.DataFrame([dict(province="A"), dict(province="B")])
        with self.assertRaises(ValueError):
            m.construire_donnees(ind, besoins, esu, {"A": [], "B": []})
