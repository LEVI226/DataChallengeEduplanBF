# Vérification de la livraison V4 — 14 novembre 2026

Dix fichiers de dépôt, sept ZIP, rapport de neuf pages et quatre figures. EXX est un préfixe anonyme choisi ; le participant a confirmé qu’aucun code officiel n’est affiché dans l’espace d’équipe. L’absence de code ne conduit pas à inventer un identifiant attribué.

## Lecture ciblée transmise par le participant

Le participant a communiqué ses lectures de vingt lignes des annuaires DGESS, sous ses rôles Data Engineer / Data Architect. L’assistant a comparé ces transcriptions aux tables et consigné cent valeurs concordantes, aucun écart, dans FICHE_CONTROLE_HUMAIN_v4.csv. Chaque ligne conserve année, province, statut, document, page, constat, rôle et date. Les groupes pédagogiques sont distingués des maîtres chargés de cours.

Le rapport et la déclaration IA expliquent ce partage des tâches. Le contrôle est ciblé et rapporté par ce participant ; il ne constitue pas un audit indépendant par deux personnes, une validation exhaustive ou une vérification de terrain. L’usage initial de l’IA à la préparation reste déclaré et à clarifier avec les organisateurs.

## Reproduction technique

Sept ZIP extraits dans un dossier vide, dépendances épinglées installées dans un environnement virtuel neuf sur macOS / Python 3.14.7. Les commandes suivantes ont terminé avec code 0 : chaîne principale 00, compléments 12, audit PDF ESU 08, unittest, moteur JavaScript et test navigateur.

- 33 tests Python réussis ; contrôle des lignes documentées et rejet des identifiants dupliqués inclus.
- Tests navigateur : données locales, scénarios, saisies invalides, exports, mobile, absence de requêtes HTTP/HTTPS.
- 38 CSV du modèle et des compléments comparés, identiques par SHA-256.
- Fiche V4 : vingt lignes CONFORME, toutes avec constat, rôle et date. Aucun statut ajouté automatiquement par le générateur.
- Rapport PDF à auteur vide, neuf pages. Pages de limites et de reproduction inspectées visuellement par l’assistant.
- Livraisons V1, V2 et V3 conformes à leurs manifestes conservés ; aucune réécriture par V4.

Les tests et audits sont assistés. La lecture du participant et la comparaison par l’assistant sont distinguées de la validation de terrain. Aucun test Windows/Linux revendiqué. Aucun dépôt plateforme ou push effectué pour V4.
