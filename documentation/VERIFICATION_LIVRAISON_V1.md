# Vérification de la livraison V1

La vérification a été effectuée sur les calculs et les fichiers de cette
version, avec Python 3.14.7. Elle est assistée par IA ; elle ne certifie pas
les observations des sources ni les conditions d'affectation sur le terrain.

## Reproduction depuis le dossier de dépôt

Les six ZIP ont été extraits ensemble dans un dossier neuf. Un environnement
virtuel Python distinct a été créé et les dépendances ont été installées
depuis `requirements.txt`. Dans ce nouvel environnement :

1. `python code/00_tout_relancer.py` : code de sortie 0.
2. `python code/08_verifier_pdf_esu.py` : 107 valeurs conformes au PDF fourni.
3. `python -m unittest discover -s tests -v` : 23 tests réussis.
4. `node tests/test_moteur.js` : cas manuels et invariants réussis.

Les **23 CSV** présents à la racine des étapes 02 à 05 ont été régénérés
ou vérifiés, puis comparés aux fichiers de travail par SHA-256 : **aucun écart**.
Les sources minimales suffisent donc à cette chaîne. Le script 09 reste un
audit facultatif du pack complet ; il n'est pas requis par la reproduction.

## Interface locale

- Concordance exacte sur 168 cas Python/JavaScript : sept situations,
  deux ressources, quatre moyens et trois règles.
- Parcours Chromium via `file://` : 45 provinces, filtres d'affichage,
  changement de scénario, saisie sans perte de focus et paramètres invalides.
- Les résultats et l'export sont retirés en cas de saisie invalide.
- L'export conserve les 45 provinces, paramètres, années des stocks et des
  inscriptions, ainsi que les hypothèses complètes pour 2030.
- Les couvertures ESU partielles et inconnues sont distinguées ; aucun total
  inconnu n'est remplacé par zéro.
- Affichage mobile de 390 pixels sans débordement de page ; tableaux à
  défilement horizontal. Aucune erreur JavaScript observée.

## Rapport et intégrité

Le rapport PDF comporte **neuf pages**, sept parties et trois figures.
La pagination, le texte extrait, les chiffres de référence et les métadonnées
ont été contrôlés. Plusieurs pages ont été inspectées visuellement, notamment
les tableaux, figures et pages de méthode/reproduction. L'auteur PDF est vide.

Les neuf fichiers déposables et leurs tailles/empreintes sont décrits dans
`livraison_v1/MANIFESTE.json`. Le manifeste n'est pas un dixième fichier à
déposer. Le constructeur contrôle les plafonds, les chemins d'archives,
l'absence de fichiers d'environnement et les chemins personnels.

Une variante sous code anonyme de démonstration a également été construite
et relancée après extraction. Cela vérifie l'adaptation des copies ; le code
EXX de cette livraison reste provisoire tant que le code de plateforme n'est
pas confirmé. Le nom de l'équipe n'a pas été introduit dans les livrables.

## Limites de cette vérification

Le contrôle de reproduction a été réalisé sur macOS avec les versions
épinglées. Le fonctionnement sous Windows ou Linux n'a pas été exécuté dans
cette session. L'interface utilise des fonctions standard de navigateur et
reste indépendante de Python pour sa consultation.

La livraison ne résout pas les inconnues de coûts, de disponibilité des
enseignants, de fonctionnement effectif des écoles et d'accès aux sites.
Les allocations restent des simulations aux hypothèses affichées.
