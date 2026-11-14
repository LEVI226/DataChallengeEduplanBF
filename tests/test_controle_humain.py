"""Un contrôle humain déclaré doit conserver des références et un constat réels."""
from pathlib import Path
import csv,sys,tempfile,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
class ControleHumainTest(unittest.TestCase):
 def fiche(self,path,missing=False,duplicate=False):
  rows=[dict(id_controle=f'C{i:02d}',statut_controle_humain='CONFORME',role_verificateur_a_remplir='Data Engineer / Data Architect',date_verification_a_remplir='2026-11-14',constat_pdf_a_remplir='Lecture transmise par le participant') for i in range(1,21)]
  if missing:rows[-1]['constat_pdf_a_remplir']=''
  if duplicate:rows[-1]['id_controle']='C01'
  with path.open('w',newline='') as f:
   w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 def test_compte_uniquement_lignes_documentees(self):
  from controle_humain import bilan
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'fiche.csv';self.fiche(p);self.assertEqual(bilan(p)['conformes_documentees'],20)
   self.fiche(p,missing=True);self.assertEqual(bilan(p)['conformes_documentees'],19)
 def test_refuse_controles_dupliques(self):
  from controle_humain import bilan
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'fiche.csv';self.fiche(p,duplicate=True)
   with self.assertRaises(ValueError):bilan(p)
if __name__=='__main__':unittest.main()
