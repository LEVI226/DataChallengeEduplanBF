"""Contrat de dépôt : limites strictes et archives sans chemins dangereux."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

RACINE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('livraison', RACINE/'code/11_preparer_livraison.py')

class LivraisonTests(unittest.TestCase):
    def module(self):
        self.assertTrue(Path(SPEC.origin).exists(), 'Le constructeur de livraison doit exister')
        module = importlib.util.module_from_spec(SPEC)
        SPEC.loader.exec_module(module)
        return module

    def test_code_equipe_refuse_identite_et_chemin(self):
        m = self.module()
        for value in ['Jean Dupont', '../E07', 'E07/abc', 'E1', 'E007', 'e07']:
            with self.assertRaises(ValueError): m.valider_equipe(value)
        self.assertEqual(m.valider_equipe('E07'), 'E07')
        self.assertEqual(m.valider_equipe('EXX'), 'EXX')

    def test_adapter_preserve_bom_et_remplace_code(self):
        m = self.module()
        source = b'\xef\xbb\xbfprovince,equipe\nBANWA,EXX\n'
        self.assertEqual(m.adapter(source, 'E07'),
                         b'\xef\xbb\xbfprovince,equipe\nBANWA,E07\n')
        self.assertEqual(m.adapter(source, 'EXX'), source)
        self.assertEqual(m.adapter(b'equipe\nEXX\n', 'E07'), b'equipe\nE07\n')

    def test_nom_equipe_et_livraison_preparee_sans_sources(self):
        m = self.module()
        self.assertEqual(m.valider_equipe('EduplanBf'), 'EduplanBf')
        with tempfile.TemporaryDirectory() as td:
            manifeste = m.construire(equipe='EduplanBf', sortie=td, version=5,
                                     sans_sources_brutes=True)
            self.assertEqual(len(manifeste['fichiers_a_deposer']), 9)
            self.assertTrue(manifeste['sans_sources_brutes'])
            noms = []
            for p in Path(td).glob('*.zip'):
                with zipfile.ZipFile(p) as z:
                    noms.extend(z.namelist())
            self.assertIn('tableau_de_bord/donnees.js', noms)
            self.assertFalse(any(n.startswith('00_sources/') or
                                 'lignes-brutes' in n or
                                 n.endswith(('.pdf', '.xlsx')) for n in noms))
            self.assertFalse(any(n.endswith('cellules_publiees.csv') for n in noms))
            with zipfile.ZipFile(next(Path(td).glob('*01-collecte*.zip'))) as z:
                self.assertTrue(all(n.endswith(('LISEZ-MOI.md', 'registre_sources.json'))
                                    for n in z.namelist()))
            self.assertTrue(any(n.endswith('primaire_communes_provinces_2023_2024.csv')
                                for n in noms))
            notice = next(Path(td).glob('*notice*.md')).read_text()
            self.assertIn('sources originales ne sont pas incluses', notice)
            self.assertNotIn('sept ZIP', notice)
            rapport = (RACINE/'documentation/EduplanBf_documentation_D3_rapport_v5.md').read_text()
            self.assertNotIn('EXX', rapport)
            self.assertNotIn('sept ZIP', rapport)
            self.assertIn('sources originales ne sont pas incluses', rapport)

    def test_limites_strictes_octets_et_pages(self):
        m = self.module()
        m.valider_limites([49_999_999]*9, 15)
        for sizes, pages in [([50_000_000],1), ([1],16), ([1],0), ([49_999_999]*11,1)]:
            with self.assertRaises(ValueError): m.valider_limites(sizes,pages)

    def test_archive_refuse_traversal_et_dechets(self):
        m = self.module()
        with tempfile.TemporaryDirectory() as td:
            for name in ['../secret', '/absolute', 'code/__pycache__/a.pyc', '.venv/bin/python', 'code/.DS_Store', 'code/a.bak']:
                p=Path(td)/'test.zip'
                with zipfile.ZipFile(p,'w') as z: z.writestr(name,'x')
                with self.assertRaises(ValueError,msg=name): m.verifier_archive(p)
            with zipfile.ZipFile(p,'w') as z: z.writestr('code/test.py','print(1)')
            m.verifier_archive(p)

if __name__ == '__main__': unittest.main()
