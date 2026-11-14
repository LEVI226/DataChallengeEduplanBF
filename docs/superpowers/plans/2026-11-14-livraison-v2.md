# Livraison V2 — plan de réalisation

Objectif approuvé : actualiser rapport et archives avec les audits et données communales, sans changer les allocations provinciales ni écraser V1. Travail sur la branche livraison-v2, dans le dossier contenant les données locales ignorées par Git ; aucun worktree supplémentaire ni copie du pack complet.

- [x] Ajouter une version au générateur existant, avec valeur par défaut V1 et protection des dossiers de sortie.
- [x] Définir une liste explicite de compléments : trois PDF régionaux, quatre réponses ODFA et leurs requêtes, extractions/contrôles et scripts locaux. Exclure le catalogue global de 32 Mo, fichiers HTML, caches et autres sources non utilisées.
- [x] Produire un rapport V2 en sept parties, au plus 15 pages, avec synthèse du rapprochement, cases manquantes, fermetures historiques et divergence des définitions d’enseignants.
- [x] Préparer cinq archives d’étapes, une archive supplémentaire de sources pour respecter 50 Mo, une archive code, PDF et deux notices ; EXX provisoire, total dix fichiers.
- [x] Tester les contrats de version et sélection ; régénérer le dossier ; vérifier anonymat, tailles et intégrité.
- [x] Extraire les sept ZIP dans un dossier neuf, reproduire chaîne principale et compléments, comparer les CSV ; inspecter le PDF et vérifier V1 intacte.
- [x] Livrer des liens locaux et rappeler les éléments humains restant avant envoi. Aucun push ni dépôt plateforme dans cette tâche.
