# État du dossier au regard du guide officiel

Lecture du document fourni par les organisateurs et du texte joint par
l'utilisateur, 13 novembre 2026. Ce contrôle décrit les preuves présentes
et les écarts ; il ne vaut pas acceptation du dossier par le jury.

## Exigences et preuves

| Attente | Preuve dans le projet | État et action utile |
|---|---|---|
| Répondre au Défi 3 : répartition des infrastructures et enseignants | Diagnostic provincial, scénarios, comparaison de règles, cartes et fiche | Couvert par un prototype provincial ; contraintes opérationnelles encore simplifiées |
| Solution utilisable et relançable | `code/00_tout_relancer.py`, LISEZ-MOI, interface locale et sources minimales | V1 construite, dépendances épinglées, relance depuis les archives extraites vérifiée |
| Documentation de 15 pages maximum | Rapport dynamique Markdown/PDF en sept parties | PDF V1 de neuf pages, pagination contrôlée ; notices complémentaires concises |
| Dépôts suivant les cinq étapes | `01_collecte` à `05_interpretation`, journaux et sorties | Présents ; sélectionner les fichiers à déposer et écrire un inventaire de chaque archive |
| Missions Engineer, Architect, Analyst et Scientist | Collecte/préparation ; dictionnaire et flux ; graphiques ; scénarios/répartition | Preuves techniques présentes ; les deux personnes doivent pouvoir expliquer leurs choix et leur répartition des missions |
| Sources : producteur, publication, année | Rapport et registre d'audit avec sources, périodes et URL | Sources INSD intégrées au modèle avec document/page/ligne ; les autres enrichissements restent distingués |
| Contrôles des totaux | 32 contrôles de base, 46 ESU, audit PDF et preuves démographiques | Contrôles disponibles ; ne pas présenter les nouvelles familles simplement repérées comme intégralement validées |
| Géographies et années cohérentes | Correspondance 47/45 provinces, anciens/nouveaux codes, années scolaires explicites | À préserver pour chaque nouvelle jointure ; OSM requiert les anciens codes en entrée |
| Usage limité au concours et traçabilité de l'IA | JOURNAL_IA, changelog, sources conservées | Usage avec l'outil consigné ; aucun envoi ni dépôt sur la plateforme effectué par cet audit |
| Préparation par l'équipe avant l'aide de l'IA, règle p. 7 | Le journal indique que l'outil a écrit/exécuté la préparation | Écart déclaré, pas conformité démontrée. La déclaration d'usage doit rester exacte ; sa présence ne transforme pas cet écart en autorisation des organisateurs |

## Ce que le guide n'impose pas

Le guide propose une analyse, un tableau de bord, une carte, un outil d'aide
à la décision ou une prévision. Un tableau de bord interactif n'est donc
pas à lui seul une condition obligatoire. Il ne prescrit pas non plus
l'utilisation d'un solveur : l'objectif, les contraintes, les comparaisons
et la justification de la méthode doivent être compréhensibles.

La commune figure dans les exemples de données et de solution ; le Défi 3
donne aussi les ratios par province comme exemple. Une solution provinciale
est cohérente avec le guide si sa portée et ses limites sont expliquées.
L'audit révèle toutefois des données communales partielles qu'il serait
possible de mobiliser dans une extension ciblée.

Une certification de sécurité ou d'accessibilité de chaque site n'est pas
un livrable demandé dans le guide. Notre outil doit surtout éviter de
présenter une simulation comme une affectation de terrain confirmée.

## Points à préparer avant le dépôt

Mise à jour V1 : le rapport, l'interface et les neuf fichiers ont été produits.
Les étapes ci-dessous restent la procédure de contrôle d'une version de dépôt ;
elles ne doivent pas être lues comme une absence de livrables.

1. Fixer la version finale de la méthode et des résultats à défendre.
2. Produire le PDF final de 15 pages au plus ; synthétiser les conclusions
   des audits, sans supposer que les pièces supplémentaires échappent à cette limite.
3. Remplacer `EXX` par le code d'équipe dans les scripts et noms de dépôt,
   puis relancer et vérifier les chemins ; garder l'anonymat demandé par la plateforme.
4. Préparer les archives de code et de données par étape, avec LISEZ-MOI,
   versions de dépendances et fichiers sources nécessaires à la reproduction.
   Le pack extrait de 910 Mo ne doit pas être confondu avec un fichier de dépôt.
5. Renseigner la déclaration IA avec les tâches réellement réalisées,
   les contrôles, corrections et limites. Le guide n'annonce pas d'équivalence
   entre transparence et autorisation de tout usage.

La capture de plateforme fournie dans l'échange ajoute 20 fichiers au plus,
50 Mo par fichier et 500 Mo au total, avec catégories Données/Code/Documentation.
Ces limites viennent de cette capture, pas du texte du guide. Elles n'ont
pas été revérifiées sur la plateforme en ligne. Préparer une sélection
compacte et n'envoyer aucune source brute volumineuse par défaut.

## Critères du jury : où se trouvent les preuves

- Innovation : comparaison transparente des règles et des arbitrages.
- Rigueur : contrôles, références simples, sensibilité, hypothèses explicites.
- Visualisation et expérience : cartes et fiche existantes ; tester leur
  compréhension avec une personne de l'équipe avant présentation.
- Impact : résultats simulés, sans les présenter comme des effets observés.
- Faisabilité : ressources exprimées en postes/salles, coûts et contraintes
  encore à compléter pour une mise en œuvre concrète.
- Reproductibilité : chaîne, journaux, tests et audit ; compléter le dossier
  de distribution et vérifier la relance dans un environnement neuf.
