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
