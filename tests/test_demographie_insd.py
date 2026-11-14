"""Contrôles manuels et source originale des populations 6–11 ans."""
import csv
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'code/demographie_insd.py'

def ligne(n, *cells, page=219):
    return dict(document='source.pdf', page=str(page), ligne=str(n),
                **{f'c{i}': str(c) for i, c in enumerate(cells, 1)})

def exemple():
    return [ligne(1, 'PROVINCE DES BALES'),
            ligne(2, "Groupes d'âges", 2024, 2025, 2026),
            ligne(3, '6 -11 ans', 1, 2, 3, 40, 60, 100, 1, 2, 3),
            ligne(4, 2029, 2030, 2031),
            ligne(5, '6 - 11 ans', 1, 2, 3, 50, 70, 120, 1, 1, 999)]

class DemographieTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = None
        if SCRIPT.exists():
            spec = importlib.util.spec_from_file_location('demographie_insd', SCRIPT)
            cls.module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cls.module)

    def module_present(self):
        self.assertIsNotNone(self.module, 'Extraction INSD à implémenter')
        return self.module

    def test_entetes_variables_sexes_provenance_et_annees_non_selectionnees(self):
        obs = self.module_present().extraire(exemple(), ['LES BALE'])
        self.assertEqual([(r['annee'], r['ensemble']) for r in obs], [(2025, 100), (2030, 120)])
        self.assertEqual((obs[0]['document'], obs[0]['page'], obs[0]['ligne']), ('source.pdf', 219, 3))
        f = self.module.facteurs(obs)
        self.assertEqual(f.loc[0, 'facteur_demographique'], 1.2)

    def test_entete_groupes_et_ages_sur_deux_lignes(self):
        rows = exemple()
        rows[1]['c1'] = 'Groupes'
        self.assertEqual(len(self.module_present().extraire(rows, ['LES BALE'])), 2)

    def test_alias_des_provinces(self):
        m = self.module_present()
        for source, cible in [('PROVINCE DES BALES', 'LES BALE'), ('PROVINCE DU KOMONDJOARI', 'KOMONDJARI'),
                              ('PROVINCE DU KOMANDJARI', 'KOMONDJARI'), ('PROVINCE DU KOURITENGA', 'KOURITTENGA'),
                              ("PROVINCE DE L’OUDALAN", 'OUDALAN')]:
            self.assertEqual(m.normaliser_province(source), cible)

    def test_refus_doublon_trou_inconnue_sexes_et_zero(self):
        m = self.module_present()
        cases = [exemple() + [ligne(6, '6-11 ans', 1, 2, 3, 50, 70, 120)],
                 exemple()[:3], [ligne(1, 'PROVINCE DU MYSTERE')] + exemple()[1:]]
        for column, value in [('c7', '101'), ('c5', '0'), ('c5', '-1'), ('c5', 'illisible')]:
            rows = exemple(); rows[2][column] = value; cases.append(rows)
        for rows in cases:
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                m.extraire(rows, ['LES BALE'])

    def test_projection_arrondi_final_et_seuils_distincts(self):
        m = self.module_present()
        import pandas as pd
        ind = pd.DataFrame([dict(region='R', province='LES BALE', eleves=101, maitres=1, salles=2)])
        f = m.facteurs(m.extraire(exemple(), ['LES BALE']))
        p = m.projeter_provinces(ind, f, 'demographie_insd_moins10', 0.9, '2029-2030', 50, 30)
        self.assertEqual(p.iloc[0]['eleves_projetes'], 109)
        self.assertEqual((p.iloc[0]['besoin_maitres'], p.iloc[0]['besoin_salles']), (3, 4))
        self.assertEqual((p.iloc[0]['maitres_a_ajouter'], p.iloc[0]['salles_a_ajouter']), (2, 2))
        obs = m.extraire(exemple(), ['LES BALE']); obs[0]['ensemble'] = 0
        with self.assertRaises(ValueError): m.facteurs(obs)

    def test_script04_produit_six_scenarios_et_tables(self):
        import subprocess
        import sys
        import pandas as pd
        resultat = subprocess.run([sys.executable, str(ROOT / 'code/04_projection_2030.py')], capture_output=True, text=True)
        self.assertEqual(resultat.returncode, 0, resultat.stderr)
        besoins = pd.read_csv(ROOT / '04_analyse/EXX_04-analyse_D3_scientist_besoins-provinces-2030_v1.csv')
        self.assertEqual(len(besoins), 270)
        self.assertEqual(set(besoins.scenario), {'tendance_longue', 'croissance_nationale', 'retour_au_pic',
                                               'demographie_insd', 'demographie_insd_moins10', 'demographie_insd_plus10'})
        m = self.module_present()
        self.assertEqual(len(pd.read_csv(m.F_POPULATION)), 90)
        self.assertEqual(len(pd.read_csv(m.F_FACTEURS)), 45)
        self.assertTrue((pd.read_csv(m.F_CONTROLES).ecart == 0).all())

    def test_source_originale_90_observations_45_provinces_et_agregats(self):
        m = self.module_present()
        import pandas as pd
        provinces = pd.read_csv(ROOT / '03_transformation/EXX_03-transformation_D3_architect_indicateurs-provinces-public_v1.csv').province.unique()
        with m.SOURCE.open(encoding='utf-8-sig', newline='') as stream:
            obs = m.extraire(csv.DictReader(stream, delimiter=';'), provinces)
        self.assertEqual(len(obs), 90)
        self.assertEqual(len({r['province'] for r in obs}), 45)
        self.assertTrue(all(r['hommes'] + r['femmes'] == r['ensemble'] for r in obs))
        self.assertEqual({year:sum(r['ensemble'] for r in obs if r['annee'] == year) for year in (2025,2030)}, {2025:4328008,2030:4664547})
        self.assertEqual(len(m.facteurs(obs)), 45)

if __name__ == '__main__': unittest.main()
