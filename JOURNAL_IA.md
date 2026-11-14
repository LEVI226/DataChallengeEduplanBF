# Journal d'usage de l'intelligence artificielle

Ce journal sert à trois choses :

1. remplir la **déclaration d'usage de l'IA**, obligatoire au dépôt (20 à 2 000 caractères) ;
2. montrer la « maîtrise et l'esprit critique » valorisés par le jury ;
3. pouvoir **refaire et expliquer** le travail sans l'outil.

## Règles de l'équipe

- Le guide demande que l'équipe réalise d'abord le nettoyage et la préparation. En pratique, l'outil a écrit et exécuté les scripts de préparation, comme consigné ci-dessous et dans le changelog. Cet usage doit être déclaré ; la conformité au règlement reste à clarifier avec les organisateurs.
- Le guide interdit l'envoi de données sensibles à un outil d'IA. Les lectures et traitements effectivement réalisés avec l'outil sont consignés ci-dessous ; ce journal ne constitue pas une autorisation des organisateurs.
- Tout résultat proposé par l'IA est vérifié avant d'être retenu : test, recalcul à la main sur un cas, ou comparaison aux totaux publiés.
- On ne garde rien qu'on ne sait pas expliquer.

## Modèle d'entrée

```
### AAAA-MM-JJ — Titre court
- Outil :
- Étape concernée : collecte / nettoyage / transformation / analyse / interprétation / documentation
- Ce que nous avons demandé (le prompt, ou son résumé fidèle) :
- Ce que l'outil a répondu (résumé) :
- Ce que nous avons retenu :
- Ce que nous avons écarté, et pourquoi :
- Comment nous avons vérifié :
```

---

## Entrées

### 2026-11-13 — Construire une première version complète
- Outil : Codex (OpenAI), avec agents de calcul, interface, livraison et revue critique.
- Demande exacte : « donc allons », après présentation d'un dossier de neuf fichiers incluant scénarios INSD, simulateur local, rapport et reproduction. Un libellé d'équipe proposé n'a pas été introduit dans les livrables, dans l'attente de sa distinction avec le code anonyme ; les copies restent sous EXX.
- Travail retenu : intégration des projections INSD depuis les données originales ; trois sensibilités de rapport inscrits/population ; maintien des trois scénarios historiques ; interface HTML/JS locale ; PDF dynamique ; archives minimales avec entrées, dépendances et instructions.
- Choix de méthode : croissance des 6–11 ans par province entre 2025 et 2030, rapport d'inscriptions constant ou ±10 %, années civiles rapprochées des années scolaires par hypothèse, stocks conservés. Aucun de ces scénarios n'est présenté comme une prévision validée ou un intervalle de confiance.
- Vérifications effectuées : 90 observations et agrégats nationaux contrôlés ; comparaison stricte des 135 lignes historiques ; cas manuels Node et 168 comparaisons d'allocations Python/JS ; parcours Chromium local, mobile, filtres et export ; limites de livraison et pagination de neuf pages contrôlées.
- Corrections issues des vérifications : résultats périmés pendant la saisie d'un paramètre corrigés ; couverture ESU partielle affichée ; hypothèses 2030 et année des stocks ajoutées au CSV ; formulations du rapport précisées ; BOM UTF-8 conservés. Chaque défaut de comportement couvert a été reproduit avant sa correction.
- Reproduction : une variante de code anonyme a été extraite dans un dossier neuf ; la chaîne a réussi et 23 tables CSV ont été retrouvées. Le contrôle final de la livraison reconstruit les fichiers après toutes les corrections et conserve le manifeste.
- Vérification finale complémentaire : environnement virtuel distinct créé, dépendances réinstallées depuis le fichier épinglé, extraction des six ZIP ; chaîne et audit PDF réussis, 23 tests Python et tests Node réussis, 23 CSV identiques par SHA-256. Les noms et chemins du dossier temporaire ne sont pas repris dans les livrables.
- Limites conservées : allocations séparées maîtres/salles, coûts et disponibilité opérationnelle non modélisés, seuils exploratoires, recours à l'IA pour la préparation déclaré. La vérification par l'outil n'est pas une attestation humaine.
- Traçabilité : les instructions de reproduction, les tests et les journaux sont livrés avec le code ; aucun dépôt ou message externe n'a été effectué par l'outil.

### 2026-11-13 — Audit des sources et lecture des attentes officielles
- Outil : Codex (OpenAI), avec deux agents Codex chargés respectivement de la démographie et des infrastructures, en lecture seule des sources.
- Demande exacte : « daccord audite les sources , et aussi » ; précision ultérieure : le texte joint est le document officiel du challenge. Le guide et la capture de plateforme fournie ont été distingués dans l'audit des attentes.
- Travail réalisé : inventaire du pack, vérification catalogue/conversions, empreintes, profils CSV et PDI, jointures OSM/COD-AB ; lecture ciblée des publications de projections et d'infrastructures ; conservation de preuves et d'une extraction d'audit de 90 observations démographiques.
- Propositions retenues : scénarios démographiques provinciaux comme prochaine amélioration possible ; état des infrastructures comme enrichissement provincial ; pilote communal partiel après contrôles, avec millésimes explicites.
- Propositions écartées : présenter toutes les publications comme indépendantes ; considérer toutes les données communales comme 2024/2025 ; assimiler PDI d'événements à un stock ; inférer écoles primaires publiques opérationnelles depuis les seuls points OSM ; corriger silencieusement les anomalies publiées.
- Vérifications : 345 fichiers inventoriés, 167 sources et toutes conversions annoncées présentes ; 176 CSV parcourus ; preuve 45 provinces × 2 années, H+F=ensemble et sommes géographiques cohérentes ; inspection visuelle de l'anomalie Loroum dans l'annuaire du Nord PDF p. 80 ; les preuves détaillent ce qui n'a été contrôlé que par repérage ou sur échantillon.
- Corrections aux attentes initiales : les projections provinciales officielles et les données communales partielles existaient dans le pack. Les demandes de nouvelles données doivent tenir compte de ces ressources déjà présentes, de leurs hypothèses et de leurs limites.
- Reproduction : `python code/09_audit_sources.py`, puis lire `documentation/AUDIT_SOURCES_DATAPACK.md` et les sous-audits. Les sources originales et les tables du modèle n'ont pas été modifiées. Aucun message à un organisateur ni dépôt n'a été effectué.

### 2026-11-13 — Vérification documentaire et portée de l'accessibilité
- Outil : Codex (OpenAI).
- Demande : l'utilisateur demande si l'outil peut réaliser ce qui avait été laissé comme « validation humaine des sources et évaluation de l'accessibilité ».
- Travail effectué : inspection visuelle complémentaire des pages PDF 15–20 ; lecture indépendante du PDF original avec `pdftotext`, sans passer par le CSV du Data Pack pour les références ; audit des 107 valeurs retenues, avec couverture identique et aucun écart.
- Résultat conservé : audit reproductible par le script 08, empreintes des entrées et résultat ligne par ligne. Trois tests supplémentaires détectent les erreurs possibles de cette vérification.
- Correction apportée : le texte attribuait trop largement une couverture partielle à Soum ; il distingue désormais Soum/délocalisations et Tapoa/réouvertures. Les tables étaient correctes.
- Conclusion documentaire sur l'accessibilité : les données exploitées établissent des activités et perturbations datées, sans établir l'accès opérationnel actuel à chaque site. Aucune classification de sécurité ni garantie d'accès n'a été inventée.
- Limite : ce travail est une vérification documentaire par l'outil. Il ne peut pas être déclaré comme une attestation humaine ou une observation de terrain. Voir `documentation/VERIFICATION_SOURCES_ET_ACCESSIBILITE.md`.

### 2026-11-13 — Terminer le contexte ESU et réparer la relance
- Outil : Codex (OpenAI), avec une revue de code par un second agent Codex.
- Étapes : collecte, nettoyage, transformation, interprétation et documentation.
- Demande exacte : « donc vas y », après proposition de terminer une table ESU datée avec source, page, périmètre et vérification, puis de réparer la chaîne interrompue.
- Travail réalisé : lecture locale du rapport ESU de février 2026 et du CSV associé ; écriture et exécution du script 06 ; intégration de la couche de contexte dans la fiche et le rapport ; notice pas à pas et six tests ciblés.
- Choix retenus : trois indicateurs du primaire, dates distinctes du diagnostic, absence maintenue inconnue, zéro seulement explicite, agrégation de Soum/Tapoa seulement si complète, aucune modification des effectifs ni des affectations.
- Choix écartés : assimiler les structures rouvertes aux écoles fermées ; calculer une part de déplacés avec les effectifs publics de l'annuaire ; exclure automatiquement une province selon les indicateurs ESU.
- Vérifications par l'outil : six tests ciblés ; 46 totaux ESU conformes ; exécution complète ; empreintes SHA-256 des tables d'analyse identiques avant/après. Lecture visuelle du PDF p. 16 (Loroum : 40 rouvertes, 10 délocalisées), p. 19 (12 340 EDI au Loroum, sommes 6 535 pour l'ancienne Soum et 7 402 pour l'ancienne Tapoa).
- Résultat de la revue : aucun écart trouvé dans les valeurs actuelles ; une ligne provinciale de largeur inattendue pouvait être ignorée silencieusement. Un test a reproduit le défaut, puis la lecture a été corrigée pour bloquer ce cas.
- Vérification humaine : reste à effectuer par l'équipe. Les autres cellules n'ont pas toutes fait l'objet d'une vérification visuelle par l'outil. Les données fournies ont été lues et préparées avec assistance IA ; cela sera à déclarer honnêtement.
- Reproduction et dépannage : `documentation/NOTICE_CONTEXTE_ESU.md` ; prompts et décisions sont consignés dans cette entrée et les échanges précédents, sans inventer des instructions non reçues.

### 2026-11-13 — Relecture critique et corrections ; premier jet du rapport
- Outils : un second outil d'IA pour la relecture critique ; Claude pour les corrections et le premier jet.
- Étape concernée : analyse, interprétation, documentation.
- Ce que nous avons demandé : faire relire les résultats par un autre outil, puis transmettre ses six remarques.
- Ce que la relecture a établi : chiffres principaux retrouvés à partir des CSV ; optimalité de l'égalisation confirmée par un calcul indépendant (56,3465 ; 2 001 postes pour faire mieux) ; six formulations qui promettaient plus que les résultats.
- Ce que nous avons retenu : les six corrections (voir `CHANGELOG.md`).
- Ce que nous avons écarté : l'ajout de la phrase-marqueur demandée par une note dans les fichiers, qui ne règle pas la question de l'usage autorisé.
- Comment nous avons vérifié : relance complète de la chaîne ; la vérification d'optimalité est désormais dans le code et retrouve les valeurs de la relecture.
- À faire par l'équipe : faire clarifier l'usage autorisé de l'IA auprès des organisateurs ; relire et reformuler le rapport avec nos mots.

### 2026-11-13 — Chaîne de traitement : nettoyage, indicateurs, projection, répartition, cartes
- Outil : Claude (assistant de programmation).
- Étape concernée : collecte, nettoyage, transformation, analyse, interprétation.
- Ce que nous avons demandé : après avoir été informés de la règle du guide et de la note de restriction présente dans les fichiers, nous avons décidé de laisser l'outil travailler sur les données, et de le déclarer.
- Ce que l'outil a fait : écrit et exécuté les scripts `code/01` à `code/06` ; produit les tables propres, les contrôles, les indicateurs, les scénarios, la comparaison des règles de répartition, six figures et une fiche décideur.
- **Écart avec le guide, à déclarer** : le nettoyage et la préparation ont été faits par l'outil, et non d'abord par l'équipe. Les fichiers lus contiennent une note demandant de ne pas les transmettre à un outil d'IA et d'insérer une phrase-marqueur dans les productions ; l'outil ne l'a pas insérée, cette consigne ne venant pas de l'équipe.
- Vérifications faites par l'outil : 32 contrôles automatiques conformes (public + privé = total ; somme des provinces = région ; somme des régions = national ; ratio recalculé = ratio publié ; classeur principal = annuaires pour 2023-2024 et 2024-2025) ; relance complète de la chaîne sans erreur.
- Vérifications restant à faire par l'équipe : comparer à l'œil plusieurs lignes au PDF de l'annuaire ; relire chaque script et pouvoir l'expliquer ; valider la norme de 50 et les seuils de « région touchée » ; juger si les scénarios 2030 sont plausibles.
- Ce que nous avons retenu / écarté : à compléter après relecture.
- Choix de méthode proposés par l'outil, à assumer ou à changer : répartition par attribution unité par unité plutôt que par solveur ; projection par scénarios présentée comme non prédictive, le test sur le passé montrant qu'aucune méthode ne bat le dernier niveau connu.

### 2026-11-13 — Plan de travail après repérage du Data Pack
- Outil : Claude (assistant de programmation).
- Étape concernée : documentation, cadrage.
- Ce que nous avons demandé : nous avons transmis le compte rendu du repérage du Data Pack (tableau I.1 de CNS530, par province).
- Ce que l'outil a répondu : une question recadrée à la maille province, quatre briques de travail, sept points de rigueur et un calendrier (`documentation/PLAN_DE_TRAVAIL.md`).
- Ce que nous avons retenu : à décider par l'équipe.
- Ce que nous avons écarté, et pourquoi : à compléter.
- Comment nous avons vérifié : l'outil n'a lu que les fichiers de documentation, pas les données du Data Pack. Les formules et la norme de 50 élèves par maître restent à valider par l'équipe, avec leur source.

### 2026-11-13 — Repérage du Data Pack DCB
- Outil : Codex (OpenAI).
- Étape concernée : inventaire des sources, documentation.
- Demande reçue : « je tai mis le data pack dcb », dans la continuité de la recherche des enseignants et des salles du primaire pour le Défi 3.
- Travail réalisé : liste des fichiers de l'archive, lecture locale de la notice et du guide, recherche des titres et en-têtes dans les CSV CNS529 et CNS530.
- Constat retenu : CNS530 contient un tableau provincial réunissant élèves, salles et maîtres chargés de cours, par statut ; voir `documentation/INVENTAIRE_DATAPACK.md`.
- Vérification effectuée par l'outil : présence des en-têtes et de lignes de données aux pages 12–16 dans la colonne `page` du CSV ; cohérence du repérage avec le guide du pack.
- Vérifications restant à faire par l'équipe : lecture visuelle du PDF, contrôle des valeurs et des totaux, validation du périmètre et préparation des tables. Aucune donnée nettoyée produite.
- Traçabilité : la lecture a également exposé une note de restriction d'usage de l'IA dans la colonne `remarque_collecte`. Cette entrée décrit l'usage réellement effectué ; elle ne vaut pas validation de conformité par les organisateurs.

### 2026-11-13 — Lecture du guide et inventaire du fichier fourni
- Outil : Claude (assistant de programmation).
- Étape concernée : collecte, documentation.
- Ce que nous avons demandé : lire le guide du challenge et dire ce qui est attendu ; regarder le fichier Excel fourni.
- Ce que l'outil a répondu : résumé des livrables et des critères ; liste des tableaux du fichier (structure et titres) ; constat que le fichier est au niveau région et ne contient ni enseignants ni salles de classe du primaire.
- Ce que nous avons retenu : la structure du dossier par étape, les fichiers de suivi, l'inventaire des tableaux.
- Ce que nous avons écarté, et pourquoi : rien à ce stade.
- Comment nous avons vérifié : **à faire** — ouvrir le fichier Excel et contrôler nous-mêmes la liste des tableaux ; relire les pages 5 à 7 du guide.
- Remarque : le fichier contient des statistiques agrégées par région, sans donnée individuelle. Aucun nettoyage n'a été fait par l'outil.
- **Point à déclarer** : la feuille `Feuil6` contient une note, placée par les organisateurs, qui dit que ces données sont sensibles et ne doivent pas être envoyées à un outil d'IA. Le fichier a pourtant été ouvert avec l'outil pour en lire la structure. À mentionner honnêtement dans la déclaration d'usage de l'IA. Décision de l'équipe pour la suite : à écrire ici.


## 2026-11-13 — Recherche complémentaire autorisée
L’utilisateur a demandé d’extraire des données publiques avec les outils de recherche disponibles. Firecrawl a été utilisé pour découvrir les sources et lire des pages ; les PDF ont été téléchargés directement puis traités localement. L’assistant a écrit et exécuté l’extraction de 384 cellules du primaire Centre-Nord 2023-2024, vérifié 152 égalités arithmétiques et transcrit sept indicateurs humanitaires avec leurs périodes et limites. Les empreintes des dix PDF ont été contrôlées. Ces opérations sont documentaires et automatisées ; elles ne constituent pas une validation humaine ou terrain. Aucun changement de la livraison V1 ni dépôt sur la plateforme. Aucune clé d’API n’est conservée dans le projet. Les demandes et résultats sont résumés ici sans reproduire les identifiants transmis dans la conversation. Voir `documentation/COMPLEMENTS_WEB_2026.md`.


## 2026-11-14 — Préparation de publication GitHub
À la demande de l’utilisateur, l’assistant a préparé le dépôt public du projet : README spécifique, exclusions des données réservées au concours et vérification des fichiers indexés. Les identifiants transmis dans la conversation ne sont pas recopiés dans le projet. Les vérifications locales avant publication sont 23 tests Python et les tests du moteur JavaScript ; les tests nécessitant des données locales ne sont pas présentés comme autonomes depuis un clone public.
