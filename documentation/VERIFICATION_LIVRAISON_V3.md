# Vérification de la livraison V3 — 14 novembre 2026

Le rapport compte neuf pages, sept parties et quatre figures. Page 1 : trois chiffres clés, carte avant/après et arbitrage des règles. Audits condensés, limites regroupées et accès sans installation au début de la notice. La déclaration IA reste entière en dernière page.

Après extraction des sept ZIP dans un dossier vide, installation des dépendances épinglées et dépendances de test dans un environnement virtuel neuf (macOS / Python 3.14.7), ces vérifications ont terminé avec le code 0 :

```sh
python code/00_tout_relancer.py
python code/12_verifier_complements.py
python code/08_verifier_pdf_esu.py
python -m unittest discover -s tests -v
node tests/test_moteur.js
python tests/verifier_interface.py
```

31 tests Python passent. Les tests navigateur contrôlent l’invitation initiale à choisir une province, le retour à une simulation valide, les exports, les scénarios, les valeurs ESU partielles, le mobile et l’absence de requêtes HTTP/HTTPS de la page. Les 38 CSV comparés sont identiques par SHA-256. La modification d’interface ne touche aucune formule d’allocation.

Les archives V1 et V2 conservent leurs empreintes d’origine. V3 désigne les conteneurs et le rapport ; les sorties de calcul _v1 restent inchangées. Les noms dupliqués, les chemins dangereux et l’inclusion de documents de versions futures sont refusés ou filtrés. Rapport à auteur PDF vide, limites de taille et anonymat contrôlés. Les pages 1, 8 et 9 ont été inspectées visuellement par l’assistant ; aucune revue humaine du dossier n’est inférée de ces contrôles.

La fiche FICHE_CONTROLE_HUMAIN_v3.csv contient vingt lignes couvrant treize régions ; elles restent toutes NON_VERIFIE. L’utilisateur a confirmé que ce contrôle des lignes n’était pas encore réalisé. La préparation de la fiche ne vaut pas validation et la génération refuse d’écraser une fiche existante.

Revue indépendante assistée : défaut du filtre des versions futures dans la documentation corrigé et testé ; aucun P1/P2 restant signalé. Les audits historiques conservent leurs alertes ; leur reproduction ne les corrige pas.

EXX reste provisoire. La position des organisateurs sur l’usage d’IA à la préparation reste à obtenir ; le seuil de 50 reste exploratoire. Pas de dépôt plateforme, d’hébergement ni de push pour cette V3. Aucun test Windows ou Linux n’est revendiqué.
