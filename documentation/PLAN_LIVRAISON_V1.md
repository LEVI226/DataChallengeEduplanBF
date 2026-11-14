# Version complète du dossier D3 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Livrer des scénarios provinciaux enrichis par INSD, un simulateur local hors ligne, un rapport PDF et neuf fichiers de dépôt vérifiés.

**Architecture:** La chaîne Python existante reste la référence des données. Une extraction reproductible lit les projections INSD et alimente le script 04. Une interface HTML/JS locale consomme un export de ces résultats ; ses répartitions sont comparées à celles de Python. Un outil de livraison génère PDF et archives, puis une extraction neuve vérifie la reproduction.

**Tech Stack:** Python/pandas/numpy/openpyxl/matplotlib ; HTML/CSS/JavaScript sans CDN ; ReportLab/pypdf pour le rapport ; Playwright pour les parcours locaux.

**Spec:** Périmètre présenté dans l'échange et approuvé par « donc allons » ; détails du contrat dans `CONTRAT_INTERFACE_V1.md`.

## Global Constraints

- Primaire public, 45 anciennes provinces ; aucune allocation de terrain certifiée.
- Les seuils sont des paramètres de simulation, pas des normes officielles établies.
- Sources originales conservées ; pas d'imputation des valeurs ESU manquantes.
- Données démographiques 2025/2030 rattachées explicitement aux années scolaires 2024/25 et 2029/30 par hypothèse.
- Conserver les trois scénarios historiques ; ajouter INSD à rapport inscrits/population constant et sensibilités −10 % / +10 %.
- Interface locale, sans publication ni transmission des données ; lien de dépôt facultatif.
- Neuf fichiers visés, chacun inférieur à 50 000 000 octets, ensemble inférieur à 500 000 000 ; rapport au plus 15 pages.
- Aucun nom de membre/équipe ni chemin personnel dans les fichiers de livraison. Code d'équipe EXX en attente de précision.

## Tâche 1 — Intégration INSD

Fichiers : `code/demographie_insd.py`, `code/04_projection_2030.py`, tests dédiés.

- [x] Écrire des cas manuels couvrant les en-têtes d'années variables, la normalisation des 45 provinces, les doublons, sexes et dénominateurs nuls.
- [x] Constater leur échec avant implémentation.
- [x] Extraire les 90 observations 2025/2030 du CSV original, conserver document/page/ligne et vérifier les contrôles de la source.
- [x] Produire les facteurs provinciaux et ajouter les trois scénarios INSD sans supprimer les scénarios historiques.
- [x] Passer les tests, puis contrôler les agrégats 2025/2030 et la relance 04→05.

## Tâche 2 — Simulateur local

Fichiers : `tableau_de_bord/index.html`, `style.css`, `moteur.js`, `app.js`, tests Node ; export Python `code/10_tableau_de_bord.py`.

- [x] Tester les répartitions sur exemples manuels, budget zéro, plafonds et refus d'entrées invalides.
- [x] Construire les contrôles de moyens/seuils/horizon/règle, la carte SVG, les comparaisons, la table et l'export CSV.
- [x] Charger `donnees.js` localement ; filtrer l'affichage sans changer le périmètre national des calculs.
- [x] Comparer les sorties JS à Python sur les données réelles et plusieurs budgets.
- [x] Vérifier les parcours dans Chromium, les erreurs console et la lecture mobile.

## Tâche 3 — Rapport et livraison

Fichiers : rapport Markdown actualisé ; génération PDF ; `code/11_preparer_livraison.py` ; requirements ; notice et journal IA de livraison.

- [x] Produire le PDF à partir des chiffres et figures actuels ; vérifier la pagination et lire les rendus.
- [x] Constituer les cinq archives de données, l'archive code, le PDF et les deux notices Markdown.
- [x] Inclure les entrées minimales permettant la relance ; ne pas embarquer le Data Pack complet.
- [x] Contrôler les tailles, le contenu des archives, les chemins, les métadonnées et l'anonymat.
- [x] Extraire les six ZIP dans un dossier neuf, relancer avec les dépendances déclarées et comparer les résultats.

## Tâche 4 — Revue et trace finale

- [x] Faire relire les nouveaux calculs et l'interface ; corriger les défauts importants.
- [x] Mettre à jour LISEZ-MOI, changelog, journal IA, déclaration IA et manifeste des fichiers.
- [x] Livrer les liens vers l'interface locale, le PDF et le dossier des neuf fichiers.

## Décisions d'exécution

- Ruling: travail dans le dossier existant sans Git — le projet n'est pas un dépôt Git ; pas de création de branche ou de copie du pack de 910 Mo. Les fichiers modifiés sont sauvegardés et les archives finales servent de version révisable.
- Ruling: interface hors ligne — elle répond au besoin d'utilisation et à la fiche de dépôt sans exiger d'hébergement.
- Les sous-tâches de calcul et d'interface peuvent avancer indépendamment selon le contrat ; la livraison attend leur vérification.

## Clôture V1

- Tâche 1 : complète, revue calcul propre ; extraction INSD, six scénarios et historiques préservés.
- Tâche 2 : complète, défauts de saisie et de traçabilité CSV reproduits puis corrigés ; revue finale propre.
- Tâche 3 : complète, neuf fichiers / neuf pages / 36 851 018 octets ; reproduction dans un environnement virtuel neuf, 23 CSV identiques par SHA-256.
- Tâche 4 : complète, 23 tests Python et tests Node/navigateur réussis ; artefacts reconstruits après corrections et vérifiés contre les sources actuelles.
- Ruling: EXX reste le code provisoire — le libellé fourni peut être un nom d’équipe ; sa distinction du code anonyme a été demandée. Aucun nom d’équipe ni envoi n’est introduit pour terminer une V1 locale révisable.
