# Journal des changements

## 2026-11-16 — Méthode, indicateurs et sensibilité au seuil
- Rubrique méthode dépliable : mêmes noms que les contrôles, formules et arrondis, scénarios, départage stable et limites. Le seuil 50 reste un repère exploratoire ; ±10 % ne devient pas un intervalle de confiance.
- Tableau 40/50/60 et seuil courant : besoins initiaux, provinces avant/après, maximum après et manque restant. Même allocation pour les règles indépendantes ; recalcul pour les autres, avec note sur les différences effectivement observées et repérage accessible du seuil courant.
- Part des inscrits dans les provinces au-dessus du seuil et dispersion non pondérée reprises du moteur, avec réserves de lecture. Courbe graduée en log(1 + unités), points du tableau étendu à 40/45, budget et seuil repérés, valeurs hors plage explicites.
- Synthèse du seuil atteint nuancée pour maîtres et salles. Moteur, données et tables conservés ; contrôles sur 56 vues, exports, seuils décimaux, zéro, saisies invalides et mobile. Livraison et paquet Vercel distincts des révisions précédentes ; aucun déploiement automatique.

## 2026-11-15 — Pédagogie de l’interface EduplanBf
- Organisation conservée : paramètres, résultats nationaux, contexte démographique et territoires. Données, moteur et tables de calcul inchangés.
- Textes formels et accessibles, noms des règles orientés vers leur objectif, synthèse automatique avant/après pour les deux ressources, rappel des deux moyens et explication des provinces restant au-dessus du seuil.
- Glossaire dépliable au clavier ou au toucher ; erreurs françaises associées aux champs, scénarios et axes explicités. Les résultats et exports invalides sont effacés ; les seuils décimaux restent affichés avec leur précision.
- Vérifications : 56 vues scénario/règle/ressource, erreurs, moyens nuls et suffisants, seuils décimaux, deux exports et affichage mobile ; suite Python et moteur JavaScript. Mise à jour Vercel préparée séparément, sans publication automatique.

## 2026-11-15 — Sélection de dépôt EduplanBf
- Nom d’équipe communiqué par le participant ; générateur compatible avec les noms sans espaces et option `--sans-sources-brutes`.
- Nouvelle sélection V5 dans un dossier distinct : neuf fichiers dont six ZIP, données préparées et interface embarquée, sources et extractions brutes exclues. Les calculs V5 et anciennes livraisons sont conservés.
- Rapport et notice adaptés : restauration des sources nécessaire aux extractions initiales ; déclaration IA conservée. Le courriel et la transcription ne sont pas interprétés comme une autorisation de l’usage initial de l’IA.
- Contrôle de la sélection, pagination, intégrité et empreintes ; tests Python et moteur JavaScript. Aucun envoi plateforme ni publication.

## 2026-11-14 — V5 : objectifs de répartition et lecture démographique
- Quatrième règle : déficits entiers croissants pour maximiser les franchissements ; reliquat égalisé avec deux étapes distinctes dans les exports. La règle n'est pas présentée comme optimum conjoint des deux critères.
- Ajouts séparés _v5 : comparaison des quatre règles, détail provincial, courbe des moyens et rapport descriptif inscriptions public+privé / population projetée de 6–11 ans. Les tables historiques restent inchangées.
- Interface hors ligne : quatre règles, courbe, lecture démographique indépendante des scénarios, exports traçables. Rapport et archives V5 distincts des livraisons précédentes.
- Contrôles par cas manuels, énumération indépendante et concordance Python/JavaScript ; portée et résultats finaux dans la notice de vérification V5.


Une entrée par changement notable. La plus récente en haut.
Pour chaque entrée : la date, ce qui a changé, pourquoi, et le fichier concerné.

Modèle :

```
## AAAA-MM-JJ
### Ajouté / Modifié / Corrigé / Supprimé
- Quoi (fichier) — pourquoi.
```

---

## 2026-11-14 — V4 : lectures ciblées et préfixe anonyme
- Un participant (Data Engineer / Data Architect) a communiqué ses lectures de vingt lignes DGESS ; comparaison assistée : cent valeurs concordantes, aucun écart. Fiche V4, rapport et déclaration IA actualisés avec cette méthode et cette portée.
- Aucun code officiel affiché dans l’espace d’équipe selon le participant : EXX est conservé comme préfixe anonyme choisi, sans attente d’un identifiant non fourni.
- Les calculs restent inchangés ; V1, V2 et V3 conservées. L’usage d’IA à la préparation initiale reste à clarifier avec les organisateurs. Aucun dépôt ni push automatique.

## 2026-11-14 — Rapport V3 centré sur la décision
- Page 1 : trois chiffres clés et carte avant/après ; arbitrage entre les règles explicite dès l’ouverture. Rapport réduit à neuf pages et quatre figures, audits condensés et limites regroupées en partie 6.
- Notice : accès au tableau de bord sans installation en première ligne. Version de la livraison distincte des tables de calcul _v1 inchangées ; pas de renommage artificiel des sources ou résultats.
- Fiche de 20 lignes à comparer aux PDF, couvrant les 13 régions : toutes NON_VERIFIE, aucun contrôle humain inventé ni formulaire rempli écrasé.
- Message initial du panneau de détail corrigé ; tests navigateur initial, retour valide, exports, mobile et absence de requêtes HTTP. 31 tests Python et moteur JavaScript réussis.
- V1 et V2 conservées ; aucun dépôt, hébergement ou push effectué.

## 2026-11-14 — Livraison V2 avec audits et compléments communaux
- Rapport actualisé en onze pages, sept parties ; conclusions provinciales inchangées, rapprochements récents et données communales intégrés avec leurs limites.
- Dix fichiers de dépôt dont sept ZIP ; sources complémentaires séparées pour respecter 50 Mo par fichier. EXX reste provisoire ; V1 intacte.
- Générateur versionné, protection des dossiers, exclusion des produits futurs en V1, refus de doublons ; tests de régression inclus.
- Reproduction en environnement neuf : chaîne, compléments, audit ESU, 28 tests Python et moteur JavaScript réussis ; 38 CSV identiques par SHA-256.
- Aucun dépôt ni push ; preuves : `documentation/VERIFICATION_LIVRAISON_V2.md`.

## 2026-11-14 — Rapprochement DGESS/ODFA et communes Centre-Est/Est
- Extraction de 1 125 cellules sources et d’une table de 1 005 cellules pour 57 communes, huit provinces et deux régions, sur cinq indicateurs 2023-2024 dont les fermetures d’écoles.
- 645 contrôles : 622 conformes, 21 alertes présentes dans les publications de l’Est, deux relations invérifiables dues à une case source vide. Aucune imputation ni correction silencieuse.
- Extraction de 135 cellules de tous les enseignants directement du PDF CNS529 ; 45 contrôles femmes + hommes = total conformes. Les 39 comparaisons régionales ODFA 2024 / DGESS 2023-2024 concordent.
- Trois divergences avec les annuaires régionaux précisées : salles et tous enseignants au Centre-Nord, total des élèves à l’Est. Les données du modèle principal sont conservées.
- Scripts, pièces et limites : `01_collecte/rapprochement_20261114/LISEZ-MOI.md`. Aucun changement des archives V1 ni publication GitHub.

## 2026-11-14 — Données complémentaires INSD et Open Data, locales
- Acquisition de quatre séries ODFA, 2 149 observations jusqu’au libellé 2024 ; conversion traçable en CSV et 581 contrôles, dont neuf alertes conservées.
- Ajout du livret INSD Genre 2023, édition 2024 : 35 valeurs numériques sur l’accès et les motifs déclarés de non-scolarisation, issues de l’EHCVM 2021-2022.
- Archivage des métadonnées publiques EHCVM et RGPH ; aucun fichier individuel téléchargé. Divergences Centre-Nord et limites des périodes documentées.
- Résultats et reproduction : `01_collecte/complements_insd_20261114/LISEZ-MOI.md`. Aucun changement du modèle, de la livraison V1 ou du dépôt distant GitHub.

## 2026-11-14 — Préparation du dépôt GitHub public
- Ajout d’un README public et de règles Git excluant sources, tables, données embarquées, archives de livraison, caches et identifiants.
- Conservation locale de la livraison complète ; publication du code, des tests et de la documentation technique.
- Vérifications avant publication : 23 tests Python, tests du moteur JavaScript et contrôle des fichiers indexés.

## 2026-11-13 — Compléments web publics, hors livraison V1
- Ajout de dix PDF avec URL et SHA-256, dont les trois annuaires INSD 2024 manquants de la collection régionale du pack.
- Extraction de 384 cellules du primaire Centre-Nord 2023-2024 ; 152 contrôles arithmétiques conformes. Script de reproduction sans API et sept observations humanitaires nationales datées.
- Signalement des divergences de la fiche Centre-Nord, de l’ancienneté du communiqué UNICEF et de l’absence de correction du PDF Nord en ligne. Seuil de simulation maintenu, référence réglementaire non authentifiée.
- Détails : `documentation/COMPLEMENTS_WEB_2026.md`. Aucun changement aux calculs ou archives de `livraison_v1`.

## 2026-11-13

### Première version complète : INSD, simulateur local et livraison
- Vérification finale depuis les six ZIP dans un environnement virtuel neuf : chaîne, audit PDF, 23 tests Python et moteur Node réussis ; 23 CSV identiques par SHA-256. Preuves et portée dans `documentation/VERIFICATION_LIVRAISON_V1.md`.
- `code/demographie_insd.py`, script 04 et tests : extraction reproductible des 90 populations provinciales 6–11 ans 2025/2030, facteurs et provenance ; trois scénarios INSD ajoutés aux trois historiques, dont les 135 lignes antérieures sont conservées sans changement.
- Référence INSD aux seuils 50/50 : 2 567 677 inscrits simulés, 7 855 maîtres et 6 839 salles supplémentaires ; sensibilités de rapport −10 % / +10 % explicites, à stocks existants conservés.
- `tableau_de_bord/`, `code/10_tableau_de_bord.py`, `code/libelles.py` : interface hors ligne avec carte, comparaison, filtres d'affichage et export national ; 168 cas de concordance Python/JS vérifiés.
- Correctifs après parcours navigateur : recalcul dès saisie, invalidation des résultats/export sur entrée invalide, statuts ESU partiels visibles, hypothèses futures et année des stocks conservées dans le CSV.
- `code/rapport_livraison.py`, `code/11_preparer_livraison.py` : rapport dynamique de neuf pages et neuf fichiers déposables, manifeste SHA-256, contrôles de tailles/anonymat/chemins. Les BOM UTF-8 sont conservés dans les copies tabulaires.
- Dépendances épinglées pour Python >=3.12, notice de reproduction réécrite, tests et journaux actualisés. Aucun hébergement ni envoi à la plateforme effectué.

### Audit des sources inexploitées et des attentes du guide
- `code/09_audit_sources.py` et `documentation/audit_sources/` : inventaire de 345 fichiers avec empreintes, rapprochement des 167 sources et conversions, lecture structurelle des 176 CSV, profils des 29 feuilles PDI, jointures OSM/COD-AB. Toutes les sources annoncées sont présentes ; aucune erreur de lecture CSV constatée.
- Trois paires de PDF identiques repérées, dont un document nommé alphabétisation/scolarisation contenant une brochure de chiffres clés. Les doublons ne sont pas considérés comme confirmations indépendantes.
- Sous-audit démographique : 90 observations provinciales 6–11 ans pour 2025/2030 extraites et recoupées, avec sources/pages, sexes et agrégats. Les deux publications de projections portent le même contenu statistique. Anomalies hors horizons et dans les extractions de localités documentées sans correction imputée.
- Sous-audit infrastructures : données communales confirmées dans dix régions, avec dates variables et anomalies publiées ; états murs/toitures provinciaux repérés, sans fabriquer leur intersection. Seuils normatifs non établis par la recherche ciblée.
- `documentation/AUDIT_SOURCES_DATAPACK.md`, `AUDIT_ATTENTES_GUIDE.md` : synthèse des possibilités et limites, état des livrables. Rapport principal et LISEZ-MOI mis à jour pour distinguer les nouvelles sources auditées des données déjà intégrées.
- Les tables du modèle sont conservées ; l'audit prépare leur enrichissement sans modifier les résultats actuels ni effectuer de dépôt.

### Vérification documentaire exhaustive des valeurs ESU
- `code/08_verifier_pdf_esu.py` : audit facultatif par une lecture directe et indépendante du PDF original ; 107 valeurs comparées sans écart et couverture identique. Empreintes du PDF et de la table conservées dans le CSV d'audit.
- `tests/test_verification_pdf_esu.py` : trois tests supplémentaires, portant le total à neuf ; vérification des annexes, des inversions de valeurs, des omissions et des doublons.
- `documentation/VERIFICATION_SOURCES_ET_ACCESSIBILITE.md` : vérifications réalisées et conclusion de l'examen documentaire de l'accessibilité. Les sources exploitées ne permettent pas d'établir l'accès opérationnel actuel ; ce n'est pas une classification d'inaccessibilité.
- Correction d'une imprécision du rapport : Soum est partielle pour les écoles délocalisées, Tapoa pour les écoles rouvertes. Les tables étaient correctes et les valeurs numériques d'analyse restent inchangées.
- Inspection visuelle complémentaire des pages PDF 15–20. Les mentions de vérification à réaliser ont été remplacées par la description de la vérification documentaire effective, sans la présenter comme une attestation humaine.

### Contexte ESU intégré et relance réparée
- `code/06_contexte_esu.py` : extraction des annexes 1, 2 et 4 du rapport ESU de février 2026 ; trois indicateurs du primaire datés du 28 février 2026. 107 observations explicites, contrôle des composantes et 46 totaux régionaux/nationaux conformes.
- Sorties ESU des étapes collecte, nettoyage, transformation et interprétation : traçabilité document/annexe/page/ligne, distinction des absences et zéros, regroupement 47 → 45 provinces avec valeur vide si couverture partielle.
- `code/00_tout_relancer.py` : appelle désormais `06_contexte_esu.py` puis `07_cartes_et_graphiques.py`. Corrige l'arrêt causé par le renommage interrompu du script des graphiques.
- `code/07_cartes_et_graphiques.py`, rapport et LISEZ-MOI : contexte ESU ajouté, périodes et périmètres explicités, sans taux EDI/effectifs ni modification des affectations. Schéma du dictionnaire actualisé dans le script 03.
- `tests/test_contexte_esu.py` : six tests ciblés. La revue a fait ajouter le refus des lignes provinciales de largeur inattendue, pour éviter de les transformer silencieusement en absences. `documentation/NOTICE_CONTEXTE_ESU.md` : reproduction, exemples calculés, lecture des absences et dépannage.
- Vérifications : relance complète sans erreur ; tests ciblés conformes ; contrôle visuel du PDF p. 16 et 19 ; empreintes des tables `04_analyse` identiques avant/après. La validation humaine du PDF reste à faire.

### Corrections après relecture critique
- Vocabulaire : « norme » remplacé par « seuil de simulation » ; « budget » précisé comme un nombre de postes, sans chiffrage financier.
- `marge_maitres` renommée `marge_comptable_maitres` : ce n'est pas un sureffectif mobilisable.
- `contexte_region` renommée `inscriptions_region`, avec des libellés qui décrivent les inscriptions et non la sécurité.
- `code/05_repartition.py` : ajout d'une analyse de sensibilité aux seuils (40 à 60) et d'une vérification indépendante de l'optimalité de la règle d'égalisation.
- Fiche décideur réécrite : arbitrage entre règles sur cinq critères, scénarios 2030 présentés comme conditionnels.
- `documentation/EXX_documentation_D3_rapport_v1.md` : premier jet du rapport, à relire et reformuler par l'équipe.

### Chaîne de traitement complète (première version)
- Décision de l'équipe : l'outil d'IA travaille sur les données ; cet usage sera déclaré au dépôt.
- `code/01_provinces_tableau_I1.py` : tableau I.1 des annuaires 2023-2024 et 2024-2025 reconstruit en table propre (45 provinces, 13 régions, 3 statuts). 16 contrôles de totaux conformes.
- `code/02_regions_series_10_ans.py` : effectifs et écoles par région sur dix ans. Correction d'un nom de région (`HAUT-BASSINS` → `HAUTS-BASSINS`). 16 contrôles conformes, dont le recoupement avec les annuaires.
- `code/03_indicateurs_provinces.py` : ratios, besoins et déficits par province (primaire public) ; dictionnaire des variables.
- `code/04_projection_2030.py` : trois scénarios à l'horizon 2029-2030 et test sur le passé.
- `code/05_repartition.py` : comparaison de trois règles de répartition, détail par province.
- `code/06_cartes_et_graphiques.py` : correspondance entre le nouveau découpage (47 provinces) et l'annuaire (45), six figures, fiche décideur.
- `code/00_tout_relancer.py` : relance les six scripts dans l'ordre. Vérifié : exécution complète sans erreur.
- Archive du Data Pack extraite dans `01_collecte/datapack_extrait/` et limites administratives dans `01_collecte/limites_administratives/` (fichiers sources non modifiés, à ne pas déposer tels quels : trop volumineux).

### À faire
- Remplacer `EXX` par le code de l'équipe dans les six scripts (variable `EQUIPE`), puis relancer.
- Rapprocher à l'œil quelques lignes de la table provinciale avec le PDF de l'annuaire.
- Confirmer la norme de 50 élèves par maître avec son texte de référence.
- Rédiger le rapport ; construire le tableau de bord.

### Plan de travail
- Ajout de `documentation/PLAN_DE_TRAVAIL.md` : question recadrée à la maille province, quatre briques, points de rigueur, calendrier jusqu'au 18 novembre. Proposition à valider par l'équipe ; aucune donnée lue pour l'écrire.

### Repérage complémentaire du Data Pack
- Ajout de `documentation/INVENTAIRE_DATAPACK.md` : archive inventoriée, tableau I.1 de CNS530 repéré aux pages PDF 12–16, sources complémentaires et contrôles restants explicités. Aucun jeu nettoyé produit.

### Ajouté
- Structure du dossier par étape (`00_sources` à `05_interpretation`, `code`, `documentation`) — pour suivre le parcours des données en cinq étapes demandé par le guide.
- `LISEZ-MOI.md`, `CHANGELOG.md`, `JOURNAL_IA.md`, `documentation/PLAN_DOCUMENTATION.md` — pour pouvoir expliquer et refaire le travail sans outil d'IA.
- `documentation/INVENTAIRE_DONNEES.md` — liste des tableaux du fichier fourni et de ce qui y manque pour le défi 3.

### Modifié
- Les deux fichiers fournis sont déplacés dans `00_sources/`, sans modification (empreintes SHA-256 vérifiées, identiques à celles de la plateforme).

### Constaté
- Le fichier principal est au niveau **région** (13 régions), pas commune. Il ne contient ni le nombre d'enseignants ni les salles de classe du primaire. La note d'intention doit être recadrée.
