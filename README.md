# Planification des moyens du primaire — Data Challenge Burkina

Code d'une solution au défi 3 du Data Challenge Burkina, édition Éducation 2026 : comparer des règles d'affectation des enseignants et des salles de classe entre provinces, puis explorer des scénarios conditionnels à l'horizon 2030.

## Contenu du dépôt public

- `code/` : préparation, indicateurs, scénarios, allocation, contrôles et construction des livrables.
- `tableau_de_bord/` : interface hors ligne et moteur de simulation en JavaScript.
- `tests/` : contrôles Python et JavaScript.
- `documentation/` : méthode de travail et contrat de l'interface.
- `CHANGELOG.md` et `JOURNAL_IA.md` : historique des changements et usage déclaré de l'IA.

Les données sources, les tables produites, les rapports chiffrés et les archives de soumission sont exclus de ce dépôt public : le guide réserve l'utilisation des données au concours. `tableau_de_bord/donnees.js`, qui embarque les données et les géométries, est également exclu. Le tableau de bord ne peut donc pas fonctionner à partir de ce seul clone. Aucune clé d'API n'est nécessaire pour exécuter les calculs.

## Reproduire avec les données autorisées

Python 3.12 ou supérieur. Dans la racine du projet :

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Les équipes disposant des ressources du concours doivent restaurer les sources minimales dans leurs chemins d'origine. Les six archives de livraison, disponibles séparément dans l'espace de travail de l'équipe, s'extraient dans un même dossier et recréent ces chemins. Les entrées attendues sont précisées dans les scripts et dans le tableau ci-dessous.

| Entrées | Utilisation |
|---|---|
| Classeur statistique DGESS 2016–2025 | Séries régionales |
| Annuaires du primaire CNS529 et CNS530 et leurs CSV | Tables provinciales et contrôles |
| Projections démographiques INSD, volume 4 | Scénarios conditionnels |
| Rapport ESU de février 2026 | Contexte daté |
| Limites administratives COD-AB | Cartographie |

Une fois les sources autorisées restaurées :

```sh
python code/00_tout_relancer.py
```

Ouvrir ensuite `tableau_de_bord/index.html`. L'interface générée fonctionne hors ligne. Le script `09_audit_sources.py` exige le pack complet, distinct des sources minimales.

## Vérifier

```sh
python -m unittest discover -s tests -v
node tests/test_moteur.js
```

Certains contrôles nécessitent les sources ou résultats locaux exclus du dépôt public. Le test JavaScript du moteur utilise des exemples synthétiques. Les tests de navigation facultatifs demandent les dépendances de `requirements-dev.txt` et le fichier de données généré.

## Interprétation

Le seuil de 50 élèves par maître ou par salle est un paramètre de simulation. Les scénarios 2030 sont conditionnels et ne sont pas des intervalles de confiance. Les allocations comparent plusieurs critères ; les données agrégées ne suffisent pas à garantir l'accessibilité opérationnelle d'une école.

Les fichiers de concours restent anonymisés avec `EXX` tant que le code anonyme attribué par la plateforme n'est pas connu. Le nom du compte GitHub ne doit pas être repris dans les fichiers soumis au jury.
