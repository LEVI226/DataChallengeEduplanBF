# Contrat de l'interface locale V1

L'export Python produit `tableau_de_bord/donnees.js`, chargé par un script local,
contenant `window.DCB_DATA`. Aucun fetch ni CDN n'est nécessaire.

```javascript
{
  meta: {annee:"2024-2025", horizon:"2029-2030", date_esu:"2026-02-28", source:"DGESS / INSD", version:"1"},
  scenarios: [
    {id:"actuel", label:"Situation 2024–2025", description:"Inscriptions observées"},
    {id:"demographie_insd", label:"2030 · référence INSD", description:"Rapport inscrits publics / population 6–11 ans constant"}
  ],
  provinces: [{
    province:"BANWA", region:"BOUCLE DU MOUHOUN", eleves:23416,
    maitres:374, salles:404, groupes_pedagogiques:377,
    inscriptions_region:"proches du maximum",
    demandes:{actuel:23416, demographie_insd:25000},
    esu:{ecoles_rouvertes:168, ecoles_delocalisees:5, eleves_deplaces:4155,
         ecoles_rouvertes_statut:"renseigne", ecoles_delocalisees_statut:"renseigne", eleves_deplaces_statut:"renseigne"}
  }],
  geometries:{BANWA:[[[longitude,latitude], [longitude,latitude]]]},
  sources:[{titre:"Annuaire primaire 2024–2025", producteur:"DGESS", detail:"Tableau I.1"}]
}
```

Les nombres d'exemple dans ce contrat illustrent la forme ; l'export réel vient
des tables. Les six scénarios 2030 gardent les identifiants Python :
`tendance_longue`, `croissance_nationale`, `retour_au_pic`, `demographie_insd`,
`demographie_insd_moins10`, `demographie_insd_plus10`, auxquels s'ajoute `actuel`.
Les valeurs ESU inconnues valent `null`, jamais zéro implicite.

Moteur JS testable depuis Node : module CommonJS et variable navigateur
`DCBEngine`, fonctions `repartir(eleves, existant, budget, regle, seuil)` et
`mesurer(eleves, existant, ajout, seuil)`. Les trois règles Python sont
`proportionnelle`, `deficit_d_abord`, `egalisation`. Les unités sont entières,
le budget est entièrement réparti ; les égalités sont départagées par ordre
d'entrée, stable. Les paramètres invalides doivent être refusés.

L'interface calcule toujours sur les 45 provinces. Une sélection de région
filtre seulement la carte/table ; les indicateurs de comparaison portent
explicitement sur l'ensemble national. Maîtres et salles sont simulés
séparément ; leur différence doit être présentée comme un signal comptable,
sans supposer une correspondance automatique classe/maître.

Présentation : français, typographie système, bleu nuit/ivoire/vert, carte SVG
et graphiques lisibles. Contrôles : scénario, moyens de maîtres et de salles,
seuils séparés, règle, ressource affichée et filtre de région. Table exportable
avec paramètres, année/scénario, province/région, élèves, stocks, ajouts et ratios.
Les scénarios et les indicateurs ESU doivent garder leurs hypothèses et dates.
