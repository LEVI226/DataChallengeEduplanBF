"""Cas calculables à la main : absences, zéros, scissions et erreurs de lecture."""
import importlib.util
from pathlib import Path
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "code/06_contexte_esu.py"


def ligne(numero, *cellules):
    return {"document": "rapport.pdf", "page": "16", "ligne": str(numero),
            "nb_cellules": str(len(cellules)),
            **{f"c{i}": valeur for i, valeur in enumerate(cellules, 1)}}


REFERENTIEL = {
    "LOROUM": {"code": "BF5401", "province": "Loroum", "region": "Yaadga", "province_annuaire": "LOROUM"},
    "DJELGODJI": {"code": "BF5901", "province": "Djelgodji", "region": "Soum", "province_annuaire": "SOUM"},
    "KARO PELI": {"code": "BF5902", "province": "Karo-Peli", "region": "Soum", "province_annuaire": "SOUM"},
}


class ContexteESUTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if SCRIPT.exists():
            spec = importlib.util.spec_from_file_location("contexte_esu", SCRIPT)
            cls.module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cls.module)
        else:
            cls.module = None

    def module_present(self):
        self.assertIsNotNone(self.module, "Le traitement ESU reste à implémenter")
        return self.module

    def test_lignes_de_region_et_totaux_ne_deviennent_pas_des_provinces(self):
        m = self.module_present()
        rows = [ligne(1, "Annexe 2: Structures délocalisées"),
                ligne(2, "YAADGA", "LOROUM", "1", "0", "10", "11"),
                ligne(3, "Total YAADGA", "1", "0", "10", "11"),
                ligne(4, "Total général", "1", "0", "10", "11"),
                ligne(5, "Annexe 3: Préscolaire"),
                ligne(6, "LOROUM", "396", "357", "753")]
        obs, totaux, _ = m.extraire_annexes(rows, REFERENTIEL)
        self.assertEqual(len(obs), 1)
        self.assertEqual(obs[0]["valeur"], 10)
        self.assertEqual(obs[0]["indicateur"], "ecoles_delocalisees")
        self.assertEqual(len(totaux), 2)

    def test_zero_explicite_reste_zero_absence_reste_inconnue(self):
        m = self.module_present()
        rows = [ligne(1, "Annexe 1: Structures rouvertes"),
                ligne(2, "LOROUM", "0", "0", "0", "0")]
        obs, _, _ = m.extraire_annexes(rows, REFERENTIEL)
        natif, anciens = m.construire_contexte(obs, REFERENTIEL)
        valeurs = {(r["province_annuaire"], r["indicateur"]): r for r in anciens}
        self.assertEqual(valeurs[("LOROUM", "ecoles_rouvertes")]["valeur"], 0)
        self.assertEqual(valeurs[("LOROUM", "ecoles_rouvertes")]["statut_renseignement"], "renseigne")
        self.assertIsNone(valeurs[("LOROUM", "ecoles_delocalisees")]["valeur"])
        self.assertEqual(len(natif), 9)

    def test_scission_somme_seulement_si_tous_les_territoires_sont_renseignes(self):
        m = self.module_present()
        rows = [ligne(1, "Annexe 4: EDI du primaire"),
                ligne(2, "DJELGODJI", "2 699", "2 792", "5 491"),
                ligne(3, "KARO-PELI", "535", "509", "1 044")]
        obs, _, _ = m.extraire_annexes(rows, REFERENTIEL)
        _, anciens = m.construire_contexte(obs, REFERENTIEL)
        soum = next(r for r in anciens if r["province_annuaire"] == "SOUM" and r["indicateur"] == "eleves_deplaces")
        self.assertEqual(soum["valeur"], 6535)
        self.assertEqual(soum["date_observation"], "2026-02-28")
        self.assertEqual(soum["statut_etablissement"], "non distingue dans le tableau")
        _, anciens_partiels = m.construire_contexte(obs[:1], REFERENTIEL)
        partiel = next(r for r in anciens_partiels if r["province_annuaire"] == "SOUM" and r["indicateur"] == "eleves_deplaces")
        self.assertIsNone(partiel["valeur"])
        self.assertEqual(partiel["statut_renseignement"], "partiel")

    def test_total_incoherent_et_province_inconnue_sont_refuses(self):
        m = self.module_present()
        for row in [ligne(2, "LOROUM", "6 228", "6 112", "12 341"),
                    ligne(2, "PROVINCE INCONNUE", "1", "2", "3"),
                    ligne(2, "LOROUM", "illisible", "2", "3")]:
            with self.subTest(row=row), self.assertRaises(ValueError):
                m.extraire_annexes([ligne(1, "Annexe 4: EDI du primaire"), row], REFERENTIEL)

    def test_doublon_ne_peut_pas_doubler_les_effectifs(self):
        m = self.module_present()
        rows = [ligne(1, "Annexe 4: EDI du primaire"),
                ligne(2, "LOROUM", "6 228", "6 112", "12 340"),
                ligne(3, "LOROUM", "6 228", "6 112", "12 340")]
        with self.assertRaises(ValueError):
            m.extraire_annexes(rows, REFERENTIEL)

    def test_ligne_provinciale_mal_extraite_ne_devient_pas_une_absence(self):
        m = self.module_present()
        rows = [ligne(1, "Annexe 4: EDI du primaire"),
                ligne(2, "LOROUM", "0", "0", "0", "cellule en trop", "autre cellule")]
        with self.assertRaises(ValueError):
            m.extraire_annexes(rows, REFERENTIEL)


if __name__ == "__main__":
    unittest.main()
