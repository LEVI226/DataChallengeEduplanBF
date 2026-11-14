"""La V2 doit rester versionnée, compacte et reproductible sans données externes."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
class LivraisonV2Test(unittest.TestCase):
    def builder(self):
        spec=importlib.util.spec_from_file_location('livraison',ROOT/'code/11_preparer_livraison.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

    def test_version_refuse_ecrasement_v1(self):
        m=self.builder()
        with tempfile.TemporaryDirectory() as td:
            old=Path(td)/'old';old.mkdir();(old/'MANIFESTE.json').write_text('{"version":1}')
            with self.assertRaisesRegex(ValueError,'version'):
                m.construire(root=Path(td),sortie='old',version=2)
            self.assertEqual((old/'MANIFESTE.json').read_text(),'{"version":1}')

    def test_version_inconnue_refusee_avant_ecriture(self):
        m=self.builder()
        with tempfile.TemporaryDirectory() as td:
            for version in [0,4,-1,'2',True]:
                with self.assertRaises(ValueError):m.construire(root=Path(td),sortie='output',version=version)
            self.assertFalse((Path(td)/'output').exists())

    def test_archive_refuse_noms_dupliques(self):
        import zipfile
        import warnings
        m=self.builder()
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'duplicate.zip'
            with warnings.catch_warnings():
                warnings.simplefilter('ignore',UserWarning)
                with zipfile.ZipFile(p,'w') as z:
                    z.writestr('code/a.py','version 1')
                    z.writestr('code/a.py','version 2')
            with self.assertRaisesRegex(ValueError,'dupliqu'):
                m.verifier_archive(p)

    def test_selection_etape_preserve_version_anterieure(self):
        m=self.builder()
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            for n in ['resultat_v1.csv','audit_v2.md','cache.pyc']:(root/n).write_text('x')
            self.assertEqual([p.name for p in m.produits_etape(root,1)],['resultat_v1.csv'])
            self.assertEqual({p.name for p in m.produits_etape(root,2)},{'resultat_v1.csv','audit_v2.md'})

    def test_documentation_exclut_fiche_humaine_future(self):
        m=self.builder()
        self.assertFalse(m.version_fichier_autorisee(Path('FICHE_CONTROLE_HUMAIN_v3.csv'),2))
        self.assertFalse(m.version_fichier_autorisee(Path('VERIFICATION_LIVRAISON_V3.md'),2))
        self.assertTrue(m.version_fichier_autorisee(Path('FICHE_CONTROLE_HUMAIN_v3.csv'),3))

    def test_selection_complements_exclut_catalogues_et_caches(self):
        import sys
        sys.path.insert(0,str(ROOT/'code'))
        from complements_livraison import fichiers_complements
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            # Toute entrée est explicite : ajouter un cache ne doit pas le publier.
            (root/'01_collecte/complements_insd_20261114').mkdir(parents=True)
            secret=root/'01_collecte/complements_insd_20261114/ODFA_catalogue_metadonnees.json'
            secret.write_text('catalogue volumineux non utilisé')
            selected=fichiers_complements(root,exiger=False)
            self.assertNotIn(secret,{p for paths in selected.values() for p in paths})
            self.assertEqual(set(selected),{'sources','code','01_collecte','02_nettoyage','03_transformation','04_analyse','05_interpretation'})

if __name__=='__main__':unittest.main()
