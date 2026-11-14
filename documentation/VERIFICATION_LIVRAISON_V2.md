# Vérification de la livraison V2 — 14 novembre 2026

Dix fichiers déposables : cinq archives d’étapes, une seconde archive de sources, une archive code, un PDF et deux notices. Le manifeste voisin est un contrôle, pas un fichier à déposer. Rapport de onze pages et sept parties. Le modèle provincial et le simulateur conservent leurs données.

## Reproduction depuis les archives

Les sept ZIP ont été extraits dans un dossier vide et les dépendances épinglées installées dans un environnement virtuel neuf. Sur macOS / Python 3.14.7, toutes les commandes suivantes ont terminé avec le code 0 :

```sh
python code/00_tout_relancer.py
python code/12_verifier_complements.py
python code/08_verifier_pdf_esu.py
python -m unittest discover -s tests -v
node tests/test_moteur.js
```

Les 28 tests Python passent. Les 38 CSV comparés, modèle principal et compléments livrés, sont identiques aux tables de travail par SHA-256. Le script 12 demande Poppler (`pdftotext`), sans API ni clé. Les alertes documentaires sont reproduites comme alertes, sans correction implicite.

## Contenu et intégrité

- 151 chemins uniques dans les sept ZIP avant ajout de cette note ; aucune collision ni doublon interne. La note ajoute un seul chemin documentaire.
- Aucun chemin personnel, nom d’équipe ou format de clé détecté dans les fichiers texte livrés.
- Rapport PDF : auteur vide, onze pages ; pages des nouveaux audits et de reproduction inspectées visuellement par l’assistant.
- 39 rapprochements ODFA récents/DGESS conformes. Compléments communaux : 622 contrôles conformes, 21 alertes et deux relations non vérifiables ; périodes et champs d’enseignants distincts.
- Les neuf fichiers déposables V1 restent identiques à leur manifeste SHA-256 d’origine.
- Revue indépendante assistée : défaut de sélection des versions corrigé et testé ; aucun P1/P2 restant signalé.

## Avant l’envoi

EXX reste provisoire ; le nom de l’équipe n’est pas le code anonyme. La consigne du guide sur la préparation initiale et l’usage effectif de l’IA demandent une clarification des organisateurs : la déclaration ne vaut pas autorisation. L’équipe doit relire et pouvoir défendre le dossier. Le lien GitHub public n’est pas destiné à la fiche aveugle.

Aucun dépôt plateforme ni push effectué pour cette V2. Windows et Linux non exécutés. Les audits ne certifient pas l’accessibilité ou la sécurité actuelle des écoles.
