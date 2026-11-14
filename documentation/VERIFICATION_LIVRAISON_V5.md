# Vérification de la livraison V5 — 14 novembre 2026

## Périmètre

Quatrième règle de répartition, courbe des moyens minimaux et lecture démographique séparée. Les stocks et les 23 tables historiques restent identiques aux archives V4. Les nouvelles sorties portent _v5. Aucun envoi plateforme, hébergement ou push effectué.

## Résultats et preuve

Primaire public 2024–2025, 45 provinces, seuil exploratoire de 50 : 23 provinces sont ramenées au seuil pour 1 856 maîtres, dont 161 au Loroum. Les 144 postes restants sont répartis sur les ratios les plus élevés ; le maximum final est 64,4241 et sept provinces restent au-dessus. Ramener 24 provinces au seuil coûterait au minimum 2 057 postes.

Le tri des déficits entiers croissants maximise le nombre de franchissements dans le modèle à ajouts seuls, coût unitaire identique et éligibilité de toutes les provinces. Le départage du reliquat n'est pas revendiqué comme optimum conjoint. Des cas réduits sont vérifiés par énumération indépendante de toutes les allocations possibles.

La relecture indépendante a identifié une erreur de plafond flottant pour les seuils décimaux : Zondoma, 39 420 élèves, 891 maîtres, seuil 43,8, exige neuf postes supplémentaires et non dix. Correction par fractions décimales exactes en Python et entiers BigInt en JavaScript ; cas réel ajouté aux tests et vérifié dans le navigateur.

La lecture démographique utilise 3 308 096 inscrits public + privé de tous âges et 4 328 008 enfants de 6–11 ans projetés en 2025 : rapport national 76,4346 pour 100. Ce n'est pas un taux net de scolarisation, ni une mesure des enfants non scolarisés. Elle reste fixe lors des changements de scénario et ne modifie aucune allocation. Les valeurs supérieures à 100 sont conservées.

## Reproduction et interface

Sept ZIP extraits dans un dossier vide ; environnement virtuel neuf sur macOS, Python 3.12.7. Dépendances épinglées et dépendances de développement installées. Chaîne 00 (01→07→13→10), compléments 12 et audit PDF ESU 08 terminés sans erreur.

- 42 tests Python réussis ; tests du moteur JavaScript réussis.
- Concordance des trois règles historiques : 168 situations Python/JavaScript ; quatrième règle et deux étapes : 280 situations supplémentaires, dont des seuils décimaux, stocks des deux ressources et scénarios.
- Test navigateur Chromium : quatre règles, saisies invalides, calcul immédiat, rétablissement, allocations et décomposition exportées, seuil 43,8, courbe, contexte démographique inchangé par les scénarios, export démographique, filtres, ESU partiel, mobile, absence de requêtes HTTP/HTTPS.
- 27 CSV des étapes 02–05 et 15 CSV complémentaires régénérés à l'identique par empreintes ou comparaison des octets, soit 42 tables.
- Rapport : onze pages, six figures, auteur PDF vide ; les deux pages ajoutées ont été inspectées visuellement par l'assistant, ainsi que la présentation de l'interface.
- Dix fichiers déposables, dont sept ZIP ; limites de nombre, taille et poids total contrôlées par le générateur et le manifeste. Chaque ZIP est intègre et sans doublon de chemin.
- Archives V1–V4 conservées à l'identique par SHA-256. Aucun fichier du dossier d'essais de l'autre IA ni prompt privé inclus dans la livraison.

Les tests et la relecture restent assistés. La fiche V4 conserve les lectures de vingt lignes transmises par un participant et leur comparaison assistée ; aucune nouvelle vérification humaine ou de terrain n'est revendiquée. Aucune validation Windows/Linux. La clarification des organisateurs sur la préparation initiale avec l'IA reste nécessaire.
