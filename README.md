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

Les équipes disposant des ressources du concours doivent restaurer les sources minimales dans leurs chemins d'origine. Les sept archives de livraison V5, disponibles séparément dans l'espace de travail de l'équipe, s'extraient dans un même dossier et recréent ces chemins. Les entrées attendues sont précisées dans les scripts et dans le tableau ci-dessous.

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

Les fichiers de concours utilisent `EXX` comme préfixe anonyme choisi ; aucun code officiel n'est affiché selon le participant. Le nom du compte GitHub ne doit pas être repris dans les fichiers soumis au jury.

## Dernière version de livraison

La V5 ajoute un quatrième objectif : maximiser le nombre de provinces ramenées au seuil, puis utiliser le reliquat sur les ratios les plus élevés. Le tri des déficits entiers croissants est exact pour le nombre de franchissements sous les hypothèses décrites ; le départage du reliquat n'est pas revendiqué comme optimum conjoint.

La courbe des moyens affiche les unités minimales nécessaires pour un plafond provincial. Une lecture séparée rapporte les inscriptions public + privé de tous âges à la population projetée de 6–11 ans ; ce n'est pas un taux net de scolarisation et elle ne modifie pas les allocations. Les données historiques `_v1` sont conservées ; les ajouts portent `_v5`.

```sh
python code/00_tout_relancer.py
python code/12_verifier_complements.py
python code/11_preparer_livraison.py --equipe EXX --version 5 --sortie livraison_v5
```

La chaîne inclut le script 13 avant la génération de l'interface. La fiche V4 conserve les lectures de vingt lignes communiquées par un participant et leur comparaison assistée ; aucun nouveau contrôle humain ou de terrain n'est revendiqué. L'usage initial de l'IA à la préparation reste à clarifier avec les organisateurs. Les données et livraisons privées ne sont pas incluses dans ce dépôt public.
