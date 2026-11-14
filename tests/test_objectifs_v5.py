"""Vérifications indépendantes des objectifs V5 : cas manuels et énumération."""
from pathlib import Path
import itertools
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'code'))


class ObjectifsV5(unittest.TestCase):
    def module(self):
        import allocation_objectifs
        return allocation_objectifs

    def test_completer_puis_utiliser_reliquat(self):
        # Coûts de franchissement : 1, 3, 0. On complète A,
        # puis le poste restant va à B qui reste au-dessus du seuil.
        r = self.module().repartir_seuil([100, 200, 20], [1, 1, 1], 2, 50)
        self.assertEqual(r['ajout_seuil'], [1, 0, 0])
        self.assertEqual(r['ajout_reliquat'], [0, 1, 0])
        self.assertEqual(r['ajout'], [1, 1, 0])
        self.assertEqual(r['cout_franchissement'], 1)
        self.assertEqual(r['reliquat'], 1)
        self.assertEqual(r['cout_province_supplementaire'], 4)

    def test_meilleur_nombre_par_enumeration(self):
        m = self.module()
        for e in ([100, 200, 20], [170, 90, 45], [51, 51, 180]):
            for b in range(7):
                a = m.repartir_seuil(e, [1, 1, 1], b, 50)['ajout']
                obtenu = sum(v/(1+x) > 50 for v, x in zip(e, a))
                possibles = [sum(v/(1+x) > 50 for v, x in zip(e, xs))
                             for xs in itertools.product(range(b+1), repeat=3) if sum(xs) <= b]
                self.assertEqual(obtenu, min(possibles))
                self.assertEqual(sum(a), b)

    def test_egalites_zero_et_invalides(self):
        m = self.module()
        self.assertEqual(m.repartir_seuil([51, 51], [1, 1], 1)['ajout'], [1, 0])
        self.assertEqual(m.repartir_seuil([0, 0], [1, 1], 0)['ajout'], [0, 0])
        for b in [-1, 1.2, True]:
            with self.assertRaises(ValueError): m.repartir_seuil([50], [1], b)
        for e, s, seuil in [([], [], 50), ([50], [0], 50), ([50], [1], 0), ([float('nan')], [1], 50)]:
            with self.assertRaises(ValueError): m.repartir_seuil(e, s, 1, seuil)

    def test_courbe_moyens(self):
        m = self.module()
        self.assertEqual(m.unites_plafond([120, 60], [1, 1], 60), 1)
        self.assertEqual(m.unites_plafond([120, 60], [1, 1], 50), 3)

    def test_seuil_decimal_sans_poste_fantome(self):
        m = self.module()
        self.assertEqual(m.unites_plafond([39420], [891], 43.8), 9)
        self.assertEqual(m.unites_plafond([63], [89], .7), 1)
        r = m.repartir_seuil([39420], [891], 9, 43.8)
        self.assertEqual(r['ajout_seuil'], [9])
        self.assertEqual(r['reliquat'], 0)

    def test_rapport_demographique_et_couverture(self):
        import pandas as pd
        m = self.module()
        d = pd.DataFrame({'province': ['A', 'B'], 'eleves_public': [40, 80],
                          'eleves_prive': [10, 40], 'maitres_public': [1, 2]})
        p = pd.DataFrame({'province': ['A', 'B'], 'population_6_11_2025': [100, 100]})
        r = m.lecture_demographique(d, p)
        self.assertEqual(r.inscrits_pour_100_enfants.tolist(), [50, 120])
        self.assertEqual(r.eleves_public.sum(), 120)
        with self.assertRaises(ValueError): m.lecture_demographique(d, p.iloc[:1])
        with self.assertRaises(ValueError): m.lecture_demographique(d, pd.concat([p, p]))

    def test_donnees_reelles(self):
        import pandas as pd
        root = Path(__file__).resolve().parents[1]
        d = pd.read_csv(root/'03_transformation/EXX_03-transformation_D3_architect_indicateurs-provinces-public_v1.csv')
        d = d[d.annee_scolaire == '2024-2025'].sort_values(['region', 'province'])
        r = self.module().repartir_seuil(d.eleves.tolist(), d.maitres.tolist(), 2000)
        self.assertEqual(r['provinces_ramenees'], 23)
        self.assertEqual(r['cout_franchissement'], 1856)
        self.assertEqual(r['reliquat'], 144)
        self.assertEqual(r['cout_province_supplementaire'], 2057)
        loroum = d.province.tolist().index('LOROUM')
        self.assertEqual(r['ajout_seuil'][loroum], 161)
        decimal = self.module().repartir_seuil(d.eleves.tolist(), d.maitres.tolist(), 9, 43.8)
        zondoma = d.province.tolist().index('ZONDOMA')
        self.assertEqual(decimal['ajout_seuil'][zondoma], 9)
        self.assertEqual(decimal['provinces_ramenees'], 1)
        self.assertEqual(decimal['reliquat'], 0)


if __name__ == '__main__':
    unittest.main()
