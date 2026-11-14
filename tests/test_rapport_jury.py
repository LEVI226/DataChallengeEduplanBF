"""Le jury doit voir résultat, arbitrage et preuve visuelle dès la première page."""
from pathlib import Path
import sys,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
class RapportJuryTest(unittest.TestCase):
 def test_resume_et_carte_avant_premier_saut(self):
  from rapport_livraison import contenu
  blocks=contenu(ROOT,version=3);first=blocks[:next(i for i,b in enumerate(blocks) if b[0]=='page')]
  text=str(first)
  self.assertIn('2 000',text);self.assertIn('30',text)
  self.assertTrue(any(k=='fig' and 'cartes-avant-apres' in str(v[0]) for k,v in first))
  self.assertIn('56',text)
  self.assertEqual(sum(k=='h' for k,v in blocks),7)
  self.assertNotIn('Préparation — rapprochement des publications et données communales',str(blocks))

 def test_page_finale_ouvre_sans_installation(self):
  from rapport_livraison import contenu
  b=contenu(ROOT,version=3);i=next(i for i,x in enumerate(b) if x==('h','7. La reproduction'))
  self.assertIn('sans installation',b[i+1][1])

 def test_v5_quatre_regles_et_demographie(self):
  from rapport_livraison import contenu
  blocks=contenu(ROOT,version=5)
  text=str(blocks)
  self.assertIn('Franchissement du seuil',text)
  self.assertIn('1 856',text)
  self.assertIn('144',text)
  self.assertIn('76,4',text)
  self.assertIn('pas un taux net',text)
  self.assertEqual(sum(k=='h' for k,v in blocks),7)

if __name__=='__main__':unittest.main()
