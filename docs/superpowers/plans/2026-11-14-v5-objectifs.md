# V5 — objectifs et lecture démographique

Périmètre approuvé : quatrième règle, courbe des moyens et lecture démographique distincte, interface et rapport ; conserver V4.

Architecture : ajouts dans allocation_objectifs.py et script 13 ; tables _v5 distinctes des calculs historiques ; moteur navigateur concordant ; rapport V5 fondé sur V4.

1. Tests manuels et énumération exhaustive pour maximiser le nombre de provinces ramenées au seuil ; validation des entrées et du reliquat. Compléter les plus petits déficits puis égaliser les ratios avec le reliquat. Ne pas prétendre que le second critère est globalement optimal.
2. Courbe de moyens minimaux pour un plafond provincial, aux stocks conservés, et rapport inscriptions public+privé / population 6–11 ans 2025 ; jointures 45 provinces vérifiées, pas de taux net ni modification des allocations.
3. Interface : quatrième règle, décomposition du budget, courbe accessible et tableau démographique, exports avec contexte ; tests Python/JS et navigation.
4. Rapport V5 ≤15 pages, notice, journaux, archives versionnées. Réexécution depuis sept ZIP dans un dossier neuf ; comparaison des CSV, limites, anonymat et intégrité V1–V4. Aucun push ni dépôt automatique.

Relecture indépendante : cas Zondoma, 39 420 élèves / seuil 43,8 : calcul décimal exact requis (900 postes, déficit 9). Ajouté au moteur Python/JS et aux régressions sur les données réelles.
