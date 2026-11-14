"""L'audit doit détecter les décalages, même si les sommes restent égales."""
import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "code/08_verifier_pdf_esu.py"


class AuditPDFTest(unittest.TestCase):
    def charger(self):
        self.assertTrue(SCRIPT.exists(), "Audit direct du PDF à implémenter")
        spec = importlib.util.spec_from_file_location("audit_pdf", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_primaire_distingue_des_autres_ordres_et_des_totaux(self):
        m = self.charger()
        texte = "Annexe 1: Structures rouvertes\n  LOROUM    0    1    40    41\nTotal général    0    1    40    41\nAnnexe 3: EDI préscolaire\nLOROUM    396    357    753\fAnnexe 4: EDI primaire\nLOROUM    6 228    6 112    12 340"
        lignes = m.lire_pdf(texte)
        self.assertEqual([(r['annexe'], r['page'], r['valeur']) for r in lignes], [(1, 1, 40), (4, 2, 12340)])

    def test_inversion_de_valeurs_est_detectee_meme_si_total_identique(self):
        m = self.charger()
        pdf = [{'annexe': 1, 'page': 15, 'province': 'LOROUM', 'valeur': 40},
               {'annexe': 1, 'page': 15, 'province': 'PASSORE', 'valeur': 26}]
        table = [{'source_annexe': '1', 'source_page': '15', 'libelle_province_source': 'LOROUM', 'valeur': '26'},
                 {'source_annexe': '1', 'source_page': '15', 'libelle_province_source': 'PASSORE', 'valeur': '40'}]
        audit = m.comparer(pdf, table)
        self.assertEqual([r['conforme'] for r in audit], [False, False])

    def test_omission_et_doublon_sont_bloquants(self):
        m = self.charger()
        pdf = [{'annexe': 1, 'page': 15, 'province': 'LOROUM', 'valeur': 40}]
        with self.assertRaises(ValueError):
            m.comparer(pdf, [])
        texte = "Annexe 1: Structures rouvertes\nLOROUM    0    1    40    41\nLOROUM    0    1    40    41"
        with self.assertRaises(ValueError):
            m.lire_pdf(texte)
