# Plan de travail — Défi 3 — du 13 au 18 novembre 2026

Proposition à valider par l'équipe. Rien ici n'a été vérifié sur les données.

## 1. Question recadrée

> Avec un nombre donné de nouveaux maîtres et de nouvelles salles de classe, quelle répartition entre les provinces réduit le plus les déficits par rapport aux normes, aujourd'hui et à l'horizon 2030 ?

- **Maille :** la province (tableau I.1 de l'annuaire primaire 2024-2025).
- **Périmètre :** le primaire public pour la répartition (l'État affecte ses moyens au public) ; le privé est montré pour le contexte.
- **Décideur visé :** direction centrale ou directeur régional qui prépare les affectations et les constructions.

Écart avec la note d'intention : la maille passe de la commune à la province. À dire clairement dans la documentation, partie 2.

## 2. Les quatre briques

| Brique | Contenu | Données | Rôle |
|---|---|---|---|
| A. Diagnostic | Élèves par maître, élèves par salle, groupes pédagogiques par salle, déficit en maîtres et en salles par province | Tableau I.1 (2024-2025, et 2023-2024 pour comparer) | Analyst |
| B. Projection 2030 | Effectifs par région sur dix ans, prolongés selon trois scénarios (bas, central, haut), puis ventilés par province | Classeur principal ; projections INSD si exploitables | Scientist |
| C. Répartition | Nombres entiers de maîtres et de salles par province, sous contrainte de budget | Sorties de A et B | Scientist |
| D. Restitution | Carte, classement des provinces, simulateur « et si », fiche d'une page | Sorties de A, B, C | Analyst |

Les rôles Engineer (collecte, nettoyage) et Architect (schéma, dictionnaire des variables) portent sur les quatre briques.

## 3. Formules à valider

- `besoin_maitres = eleves / norme_eleves_par_maitre`
- `deficit_maitres = max(0, besoin_maitres − maitres)`
- `besoin_salles = groupes_pedagogiques` (un groupe sans salle = une classe sous abri ou en double flux)
- `deficit_salles = max(0, besoin_salles − salles)`

La norme (50 élèves par maître dans la note d'intention) doit être citée avec sa source, et rester un paramètre du simulateur.

## 4. Points de rigueur

1. **Méthodes de comparaison obligatoires.** Comparer la répartition optimisée à deux règles simples : répartition proportionnelle aux effectifs, et affectation « au plus déficitaire d'abord ».
2. **Dire ce que l'optimisation apporte vraiment.** Si l'objectif est seulement de minimiser la somme des déficits avec un seul budget, la règle « au plus déficitaire d'abord » donne déjà le meilleur résultat. L'optimisation devient utile quand on ajoute : un objectif d'équité (réduire le pire déficit), un minimum par province, le lien maîtres-salles (un maître affecté a besoin d'une salle), des provinces non accessibles.
3. **Piège des provinces en crise.** Une province où des écoles ont fermé peut afficher un bon ratio parce que les élèves sont partis. Un ratio bas n'y signifie pas un bon niveau de service. À signaler avec l'évolution des effectifs et du nombre d'écoles de la région.
4. **Projection.** Dix points par région, avec une rupture vers 2022/2023 : rester simple (tendance, scénarios) et tester la méthode sur le passé, par exemple prévoir 2024/2025 à partir des années précédentes.
5. **Ventilation région → province.** C'est une hypothèse (part de chaque province dans sa région). À écrire comme telle.
6. **Maîtres chargés de cours.** Ce n'est pas tout le personnel enseignant. Garder ce libellé exact.
7. **Totaux.** Public + privé = total ; somme des provinces = région ; somme des régions = national.

## 5. Calendrier

| Jour | Membre 1 (Engineer, Architect) | Membre 2 (Analyst, Scientist) | Dépôt du jour |
|---|---|---|---|
| Sam. 14 | Reconstruire le tableau I.1 (2024-2025) en table propre ; contrôles des totaux ; journal de nettoyage | Nettoyer les effectifs par région du classeur principal ; contrôles | `01_collecte`, `02_nettoyage` |
| Dim. 15 | Table 2023-2024 ; dictionnaire des variables ; schéma des données | Indicateurs et déficits par province ; premiers graphiques | `03_transformation` |
| Lun. 16 | Limites géographiques des provinces pour la carte ; jointures | Projection 2030 et test sur le passé ; répartition et comparaison aux règles simples | `04_analyse` |
| Mar. 17 | Scripts numérotés ; relance complète depuis zéro | Tableau de bord, simulateur, fiche d'une page ; premier jet du rapport | `05_interpretation`, rapport v1 |
| Mer. 18 | Relecture croisée, LISEZ-MOI, déclaration d'usage de l'IA | Rapport final (15 pages au plus) | Version finale **avant 18 h** |

Déposer une version chaque jour : la dernière fait foi, et un dépôt tôt protège d'une panne de connexion le dernier soir.

## 6. Priorité si le temps manque

1. Diagnostic provincial propre et vérifié (A).
2. Répartition comparée aux règles simples (C).
3. Carte et fiche d'une page (D).
4. Projection 2030 (B).
5. Simulateur interactif.

Mieux vaut A, C et D solides et documentés qu'un outil complet non vérifié.
