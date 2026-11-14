"""
ETAPE 5 — Interprétation et visualisation : cartes, graphiques et fiche pour le décideur.

Entrées : sorties des scripts 02 à 06, limites des provinces (COD-AB du Data Pack).
Sorties : table de correspondance des provinces (03_transformation), figures PNG, fond de carte
          simplifié et fiche d'une page (05_interpretation).

Lancer depuis le dossier DataChallenge :  python code/07_cartes_et_graphiques.py
"""
from pathlib import Path
import json
import unicodedata

import matplotlib
matplotlib.use("Agg")                         # pas de fenêtre : on écrit des fichiers
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.colors import TwoSlopeNorm
import numpy as np
import pandas as pd
from libelles import SCENARIOS

EQUIPE = "EXX"
RACINE = Path(__file__).resolve().parent.parent
NORME = 50
BUDGET = 2000
F_GEOJSON = RACINE / "01_collecte" / "limites_administratives" / "bfa_admin2.geojson"
F_INDICATEURS = RACINE / "03_transformation" / f"{EQUIPE}_03-transformation_D3_architect_indicateurs-provinces-public_v1.csv"
F_EFFECTIFS = RACINE / "02_nettoyage" / f"{EQUIPE}_02-nettoyage_D3_engineer_primaire-effectifs-regions-sexe_v1.csv"
F_ECOLES = RACINE / "02_nettoyage" / f"{EQUIPE}_02-nettoyage_D3_engineer_primaire-ecoles-regions-statut_v1.csv"
F_COMPARAISON = RACINE / "04_analyse" / f"{EQUIPE}_04-analyse_D3_scientist_repartition-comparaison-regles_v1.csv"
F_DETAIL = RACINE / "04_analyse" / f"{EQUIPE}_04-analyse_D3_scientist_repartition-detail-provinces_v1.csv"
F_ESU = RACINE / "05_interpretation" / f"{EQUIPE}_05-interpretation_D3_analyst_contexte-esu-affectations_v1.csv"
F_2030 = RACINE / "04_analyse" / f"{EQUIPE}_04-analyse_D3_scientist_repartition-horizon-2030_v1.csv"
F_TEST = RACINE / "04_analyse" / f"{EQUIPE}_04-analyse_D3_scientist_projection-test-sur-le-passe_v1.csv"
F_SENSIBILITE = RACINE / "04_analyse" / f"{EQUIPE}_04-analyse_D3_scientist_sensibilite-seuils_v1.csv"
F_PREUVE = RACINE / "04_analyse" / f"{EQUIPE}_04-analyse_D3_scientist_preuve-optimalite-egalisation_v1.csv"
F_CORRESPONDANCE = RACINE / "03_transformation" / f"{EQUIPE}_03-transformation_D3_architect_correspondance-provinces-carte_v1.csv"
SORTIE = RACINE / "05_interpretation"
PREFIXE = f"{EQUIPE}_05-interpretation_D3_analyst_"

# Noms de l'ancien découpage écrits autrement dans la carte et dans l'annuaire
EXCEPTIONS = {"BALE": "LES BALE", "KOMANDJARI": "KOMONDJARI"}
LIBELLES_REGLES = {"proportionnelle": "Au prorata des élèves", "deficit_d_abord": "Au plus grand déficit d'abord",
                   "egalisation": "Égalisation des ratios"}


def sans_accent(texte):
    brut = unicodedata.normalize("NFD", str(texte).upper())
    return "".join(c for c in brut if unicodedata.category(c) != "Mn").replace("-", " ").strip()


def charger_carte(pas=12):
    """Lit les limites des provinces. Renvoie (table de correspondance, {province de l'annuaire: [polygones]})."""
    carte = json.load(open(F_GEOJSON, encoding="utf-8"))
    lignes, polygones = [], {}
    for entite in carte["features"]:
        p = entite["properties"]
        ancien = sans_accent(p["adm2_name_old"])
        annuaire = EXCEPTIONS.get(ancien, ancien)
        lignes.append({"province_annuaire": annuaire, "province_nouveau_decoupage": p["adm2_name"], "code_nouveau": p["adm2_pcode"],
                       "region_nouveau_decoupage": p["adm1_name"], "province_ancien_decoupage": p["adm2_name_old"],
                       "code_ancien": p["adm2_pcode_old"], "valide_depuis": p["valid_on"]})
        g = entite["geometry"]
        parties = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        for partie in parties:
            contour = np.asarray(partie[0])[:, :2]
            if len(contour) > 60:                      # on allège le tracé : un point sur `pas`
                contour = np.vstack([contour[::pas], contour[:1]])
            polygones.setdefault(annuaire, []).append(np.round(contour, 4))
    return pd.DataFrame(lignes).sort_values("province_annuaire"), polygones


def dessiner_carte(ax, polygones, valeurs, titre, vmin, vmax, etiquettes=()):
    """Carte par province. valeurs : Series indexée par le nom de province de l'annuaire."""
    echelle = TwoSlopeNorm(vmin=vmin, vcenter=NORME, vmax=vmax)     # la norme est au centre de l'échelle
    formes, couleurs = [], []
    for province, contours in polygones.items():
        for contour in contours:
            formes.append(contour); couleurs.append(valeurs.get(province, np.nan))
    collection = PolyCollection(formes, array=np.clip(couleurs, vmin, vmax), cmap="RdYlGn_r", norm=echelle, edgecolor="white", linewidth=0.6)
    ax.add_collection(collection); ax.autoscale_view(); ax.set_aspect("equal"); ax.axis("off"); ax.set_title(titre, fontsize=11)
    for province in etiquettes:
        centre = np.vstack(polygones[province]).mean(axis=0)
        ax.annotate(f"{province.title()}\n{valeurs[province]:.0f}", centre, ha="center", va="center", fontsize=7, fontweight="bold")
    return collection


def enregistrer(nom):
    chemin = SORTIE / f"{PREFIXE}{nom}_v1.png"
    plt.savefig(chemin, dpi=160, bbox_inches="tight"); plt.close()
    return chemin.name


def main():
    SORTIE.mkdir(exist_ok=True)
    ind = pd.read_csv(F_INDICATEURS)
    ind = ind[ind.annee_scolaire == ind["annee_scolaire"].max()].set_index("province")
    annee = ind["annee_scolaire"].iloc[0]
    detail = pd.read_csv(F_DETAIL).set_index("province")
    esu = pd.read_csv(F_ESU).set_index("province")
    if esu.index.duplicated().any() or set(esu.index) != set(ind.index):
        raise ValueError("Le contexte ESU doit couvrir les 45 provinces sans doublon")
    loroum_esu = esu.loc["LOROUM"]
    edi_loroum = f"{int(loroum_esu['esu_eleves_deplaces']):,}".replace(",", " ")
    comparaison = pd.read_csv(F_COMPARAISON)
    figures = []

    # ---- Correspondance carte <-> annuaire, avec contrôle ----
    correspondance, polygones = charger_carte()
    manquantes = sorted(set(ind.index) - set(polygones))
    assert not manquantes, f"Provinces de l'annuaire absentes de la carte : {manquantes}"
    correspondance.to_csv(F_CORRESPONDANCE, index=False, encoding="utf-8-sig")
    json.dump({p: [c.tolist() for c in cs] for p, cs in polygones.items()},
              open(SORTIE / f"{PREFIXE}fond-de-carte-provinces-simplifie_v1.json", "w", encoding="utf-8"))

    # ---- Figure 1 : carte des élèves par maître ----
    fig, ax = plt.subplots(figsize=(9, 7))
    pires = ind["eleves_par_maitre"].nlargest(6).index
    c = dessiner_carte(ax, polygones, ind["eleves_par_maitre"], f"Élèves par maître chargé de cours — primaire public, {annee}", 30, 85, pires)
    barre = fig.colorbar(c, ax=ax, shrink=0.6); barre.set_label(f"Élèves par maître (seuil de simulation : {NORME} ; échelle bornée à 85)")
    fig.text(0.5, 0.06, "Source : DGESS, annuaire statistique de l'enseignement primaire. Limites : COD-AB. "
             "Soum et Tapoa, scindées dans le nouveau découpage, portent la valeur de l'ancienne province.", ha="center", fontsize=7)
    figures.append(enregistrer("carte-eleves-par-maitre"))

    # ---- Figure 2 : classement des provinces ----
    t = ind.sort_values("eleves_par_maitre")
    couleurs = t["inscriptions_region"].map({"très en dessous du maximum": "#b2182b", "en dessous du maximum": "#ef8a62", "proches du maximum": "#67a9cf"})
    fig, ax = plt.subplots(figsize=(9, 11))
    ax.barh([f"{p.title()} ({r.title()})" for p, r in zip(t.index, t["region"])], t["eleves_par_maitre"], color=couleurs)
    ax.axvline(NORME, color="black", linestyle="--", linewidth=1)
    ax.text(NORME + 0.5, -1.2, f"seuil de simulation : {NORME}", fontsize=8)
    ax.set_xlabel("Élèves par maître chargé de cours"); ax.tick_params(axis="y", labelsize=7)
    ax.set_title(f"Élèves par maître par province — primaire public, {annee}\n"
                 f"{(t['eleves_par_maitre'] > NORME).sum()} provinces sur {len(t)} au-dessus du seuil de simulation")
    ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=c) for c in ["#b2182b", "#ef8a62", "#67a9cf"]],
              labels=["Inscriptions de la région < 80 % de leur maximum sur dix ans", "Entre 80 et 95 %", "Proches du maximum (ne mesure pas la sécurité)"], loc="lower right", fontsize=8)
    figures.append(enregistrer("classement-provinces"))

    # ---- Figure 3 : dix ans d'effectifs et d'écoles par région ----
    eff = pd.read_csv(F_EFFECTIFS); eco = pd.read_csv(F_ECOLES)
    series = [("Élèves du primaire", eff[(eff.sexe == "Total") & (eff.niveau == "region")].pivot(index="annee_scolaire", columns="region", values="eleves")),
              ("Écoles primaires", eco[(eco.statut == "Total") & (eco.niveau == "region")].pivot(index="annee_scolaire", columns="region", values="ecoles"))]
    fig, axes = plt.subplots(1, 2, figsize=(15, 5.5), sharey=True)
    for ax, (titre, serie) in zip(axes, series):
        indice = serie / serie.iloc[0] * 100
        for region in indice.columns:
            fort = indice[region].min() < 75
            ax.plot(range(len(indice)), indice[region], linewidth=2.2 if fort else 0.9, alpha=1 if fort else 0.55,
                    label=region.title() if fort else None, color=None if fort else "grey")
        ax.axhline(100, color="black", linewidth=0.6)
        ax.set_xticks(range(len(indice))); ax.set_xticklabels([a[2:4] + "/" + a[7:9] for a in indice.index], fontsize=8)
        ax.set_title(f"{titre} — indice 100 en 2015/2016"); ax.legend(fontsize=8, title="Régions passées sous 75")
    axes[0].set_ylabel("Indice")
    figures.append(enregistrer("dix-ans-par-region"))

    # ---- Figure 4 : comparaison des règles de répartition ----
    cm = comparaison[(comparaison.ressource == "maitres") & (comparaison.budget > 0)]
    actuel = comparaison[(comparaison.ressource == "maitres") & (comparaison.budget == 0)].iloc[0]
    fig, axes = plt.subplots(1, 3, figsize=(17, 4.8))
    for regle, groupe in cm.groupby("regle"):
        axes[0].plot(groupe["budget"], groupe["ratio_max"], marker="o", label=LIBELLES_REGLES[regle])
        axes[1].plot(groupe["budget"], groupe["ecart_type_ratios"], marker="o", label=LIBELLES_REGLES[regle])
        axes[2].plot(groupe["budget"], groupe["unites_donnees_sous_la_norme"], marker="o", label=LIBELLES_REGLES[regle])
    axes[0].axhline(NORME, color="black", linestyle="--", linewidth=1); axes[0].axhline(actuel["ratio_max"], color="grey", linestyle=":")
    axes[0].set_title("Pire ratio élèves par maître parmi les provinces"); axes[0].set_ylabel("Élèves par maître")
    axes[1].set_title("Dispersion des ratios entre provinces (écart-type)")
    axes[2].set_title("Maîtres affectés à des provinces déjà sous le seuil")
    for ax in axes:
        ax.set_xlabel("Nombre de postes de maître à répartir"); ax.legend(fontsize=8)
    fig.suptitle(f"Trois règles de répartition, à nombre de postes égal — primaire public, {annee}", y=1.02)
    figures.append(enregistrer("comparaison-regles"))

    # ---- Figure 5 : cartes avant / après ----
    fig, axes = plt.subplots(1, 3, figsize=(19, 4.6))
    dessiner_carte(axes[0], polygones, ind["eleves_par_maitre"], "Situation actuelle", 30, 85)
    dessiner_carte(axes[1], polygones, detail["ratio_maitre_apres_proportionnelle"], f"+{BUDGET} maîtres au prorata des élèves", 30, 85)
    c = dessiner_carte(axes[2], polygones, detail["ratio_maitre_apres_egalisation"], f"+{BUDGET} maîtres, égalisation des ratios", 30, 85)
    fig.colorbar(c, ax=axes, shrink=0.55, label=f"Élèves par maître (seuil de simulation : {NORME})")
    fig.suptitle(f"Effet de {BUDGET} maîtres supplémentaires selon la règle de répartition — primaire public", fontsize=13, y=1.0)
    figures.append(enregistrer("cartes-avant-apres"))

    # ---- Figure 6 : besoins à l'horizon 2030 ----
    h = pd.read_csv(F_2030).set_index("scenario")
    noms = {s: label.replace("2030 · ", "").replace(" historique ", "\nhistorique ").replace("rapport ", "\nrapport ") for s, (label, _) in SCENARIOS.items()}
    fig, ax = plt.subplots(figsize=(13, 5.4))
    x = np.arange(len(h)); largeur = 0.38
    b1 = ax.bar(x - largeur / 2, h["maitres_a_ajouter"], largeur, label="Maîtres à ajouter")
    b2 = ax.bar(x + largeur / 2, h["salles_a_ajouter"], largeur, label="Salles à ajouter")
    ax.bar_label(b1, fmt="%d", fontsize=8); ax.bar_label(b2, fmt="%d", fontsize=8)
    ax.set_xticks(x); ax.set_xticklabels([noms[s] for s in h.index], fontsize=8, rotation=12, ha="right"); ax.legend()
    ax.set_title(f"Primaire public en 2029-2030 : ajouts nécessaires pour atteindre le seuil de {NORME}\n(scénarios conditionnels : effectifs actuels supposés conservés ; ce n'est pas un intervalle de confiance)", fontsize=10)
    figures.append(enregistrer("besoins-2030"))

    # ---- Fiche d'une page pour le décideur (tous les chiffres viennent des tables) ----
    test = pd.read_csv(F_TEST).groupby("methode")["erreur_moyenne_pct"].mean().round(0)
    ligne = lambda regle: comparaison[(comparaison.ressource == "maitres") & (comparaison.budget == BUDGET) & (comparaison.regle == regle)].iloc[0]
    prop, egal = ligne("proportionnelle"), ligne("egalisation")
    top = detail.sort_values("maitres_ajoutes_egalisation", ascending=False).head(8)
    sens = pd.read_csv(F_SENSIBILITE)
    sens_m = sens[sens.ressource == "maitres"]
    preuve = pd.read_csv(F_PREUVE)
    pr = preuve[(preuve.ressource == "maitres") & (preuve.budget == BUDGET)].iloc[0]
    defi = ligne("deficit_d_abord")
    fiche = [
        f"# Fiche décideur — répartition des maîtres et des salles du primaire public ({annee})\n",
        f"Seuil de simulation : **{NORME} élèves par maître chargé de cours** et {NORME} élèves par salle. "
        "Ces seuils sont des hypothèses de travail, à remplacer par les normes officielles une fois leur texte de référence établi.\n",
        "## Constat\n",
        f"- **{(ind['eleves_par_maitre'] > NORME).sum()} provinces sur {len(ind)}** dépassent le seuil de {NORME} élèves par maître.",
        f"- Pour que chaque province atteigne le seuil, il faudrait **{int(ind['deficit_maitres'].sum())} maîtres** et **{int(ind['deficit_salles'].sum())} salles** de plus.",
        f"- Le ratio va de **{ind['eleves_par_maitre'].min():.0f}** ({ind['eleves_par_maitre'].idxmin().title()}) à **{ind['eleves_par_maitre'].max():.0f}** élèves par maître ({ind['eleves_par_maitre'].idxmax().title()}).",
        f"- Ailleurs, l'écart comptable au seuil représente {int(ind['marge_comptable_maitres'].sum())} postes. "
        "**Ce n'est pas un sureffectif mobilisable** : une moyenne provinciale masque les écoles, les distances et les groupes pédagogiques.\n",
        "## Sensibilité du constat au seuil retenu\n",
        "| Seuil (élèves par maître) | Provinces au-dessus | Maîtres à ajouter |\n|---|---|---|",
        *[f"| {int(r.seuil)} | {int(r.provinces_au_dessus)} | {int(r.deficit_total)} |" for r in sens_m.itertuples()],
        f"\n## À nombre de postes égal, la règle d'affectation change fortement les disparités ({BUDGET} postes de maître)\n",
        "« Postes » désigne un nombre de maîtres à affecter. Aucun chiffrage financier n'est fait.\n",
        "| Règle | Pire ratio provincial | Dispersion entre provinces | Provinces au-dessus du seuil | Déficit restant | Postes affectés sous le seuil |\n|---|---|---|---|---|---|",
        f"| Situation actuelle | {actuel['ratio_max']} | {actuel['ecart_type_ratios']} | {actuel['provinces_au_dessus_norme']} | {actuel['deficit_restant']} | — |",
        f"| Au prorata des élèves | {prop['ratio_max']} | {prop['ecart_type_ratios']} | {prop['provinces_au_dessus_norme']} | {prop['deficit_restant']} | {prop['unites_donnees_sous_la_norme']} |",
        f"| Au plus grand déficit d'abord | {defi['ratio_max']} | {defi['ecart_type_ratios']} | {defi['provinces_au_dessus_norme']} | {defi['deficit_restant']} | {defi['unites_donnees_sous_la_norme']} |",
        f"| Égalisation des ratios | {egal['ratio_max']} | {egal['ecart_type_ratios']} | {egal['provinces_au_dessus_norme']} | {egal['deficit_restant']} | {egal['unites_donnees_sous_la_norme']} |\n",
        "**Aucune règle n'est la meilleure sur tous les critères : c'est un arbitrage.**\n",
        "- L'égalisation réduit le plus le pire ratio et les écarts entre provinces, mais ne fait passer aucune province sous le seuil à ce niveau de moyens.",
        "- Le prorata fait passer quelques provinces proches du seuil en dessous, mais laisse les provinces les plus chargées presque inchangées et affecte une part des postes à des provinces déjà sous le seuil.",
        "- Les deux règles qui ciblent les déficits laissent le même déficit total.",
        f"- Vérification indépendante : avec {BUDGET} postes, le pire ratio obtenu par l'égalisation est {pr['pire_ratio_obtenu']} ; "
        f"l'atteindre demande {int(pr['unites_pour_ce_plafond'])} postes et faire mieux en demanderait au moins {int(pr['unites_pour_un_plafond_plus_bas'])}. "
        "La règle est donc optimale pour cet objectif précis, avec ces données et ces hypothèses.\n",
        f"## Où iraient les postes avec la règle d'égalisation ({BUDGET} postes)\n",
        "| Province | Région | Élèves par maître | Postes proposés | Ratio après |\n|---|---|---|---|---|",
        *[f"| {p.title()} | {r.region.title()} | {r.eleves_par_maitre} | {int(r.maitres_ajoutes_egalisation)} | {r.ratio_maitre_apres_egalisation} |" for p, r in top.iterrows()],
        "\nCe tableau est une simulation, pas une recommandation opérationnelle : voir les limites.\n",
        "## Contexte provincial ESU — observation du 28 février 2026\n",
        f"Au Loroum : **{edi_loroum} élèves déplacés du primaire**, "
        f"{int(loroum_esu['esu_ecoles_rouvertes'])} écoles primaires rouvertes restant fonctionnelles et "
        f"{int(loroum_esu['esu_ecoles_delocalisees'])} écoles primaires délocalisées. " +
        "Ces indicateurs ne sont pas des nombres d'écoles fermées et ne déterminent pas l'accessibilité de la province.\n",
        "Le contexte ESU concerne 2025–2026, avec un statut public/privé non distingué dans les tableaux ; "
        "le diagnostic concerne le public en 2024–2025. Aucun taux entre ces populations, ajout aux effectifs ou retrait n'est calculé. "
        "Les affectations simulées restent inchangées. Une absence de ligne ESU reste non renseignée ; "
        "une couverture partielle de Soum ou de Tapoa ne devient pas un total.\n",
        f"[Note de contexte ESU]({PREFIXE}note-contexte-esu_v1.md) et "
        f"[table des affectations avec contexte]({PREFIXE}contexte-esu-affectations_v1.csv). "
        "Source : DGESS/MEBAPLN, rapport ESU de février 2026, annexes 1, 2 et 4, PDF p. 15–20.\n",
        "## À l'horizon 2029-2030 : scénarios conditionnels\n",
        *[f"- {noms[s].replace(chr(10), ' ')} : {int(r.maitres_a_ajouter)} maîtres et {int(r.salles_a_ajouter)} salles à ajouter." for s, r in h.iterrows()],
        "\nCes chiffres supposent que tous les maîtres et toutes les salles d'aujourd'hui sont conservés : ni départs, ni retraites, ni salles perdues, ni contrainte de recrutement. "
        "Les scénarios INSD utilisent le rapport entre inscriptions publiques et population 6–11 ans de la province : "
        "maintenu à sa référence ou modifié de −10 % / +10 %. Les années civiles 2025/2030 sont rapprochées "
        "des années scolaires 2024/25 et 2029/30 par hypothèse. Les scénarios ne forment pas un intervalle de confiance.\n",
        "## Limites à connaître avant de décider\n",
        "- **Ce sont des scénarios, pas des prévisions.** Testées sur le passé à 3 ans, nos méthodes se trompent de "
        f"{int(test['tendance_longue'])} à {int(test['retour_au_pic'])} % en moyenne par région, et ne font pas mieux que de garder le dernier niveau connu ({int(test['dernier_niveau'])} %).",
        "- **L'indicateur régional mesure les inscriptions, pas la sécurité.** Une région « proche de son maximum » peut contenir une province très touchée. "
        "La couche ESU décrit des réouvertures, des délocalisations et des élèves déplacés ; "
        "les fermetures et l'accessibilité restent à établir avant toute recommandation opérationnelle.",
        "- **Un ratio favorable n'est pas toujours un bon service.** Là où des écoles ont fermé, les élèves partis ne sont plus comptés.",
        "- **La maille est la province.** Les écarts entre communes et entre écoles d'une même province restent invisibles.",
        "- **Les maîtres chargés de cours** ne sont pas tout le personnel enseignant.",
        "- La sécurité, le logement et l'accessibilité ne sont pas dans le calcul.",
        "- Les seuils élèves par maître et élèves par salle restent à justifier séparément par leur texte de référence.\n",
        "Sources : DGESS, annuaires statistiques de l'enseignement primaire 2023-2024 et 2024-2025 ; données statistiques 2016-2025.",
    ]
    (SORTIE / f"{PREFIXE}fiche-decideur_v1.md").write_text("\n".join(fiche) + "\n", encoding="utf-8")

    print("Correspondance carte-annuaire :", len(correspondance), "provinces du nouveau découpage ->", correspondance["province_annuaire"].nunique(), "provinces de l'annuaire")
    print("Figures :", *figures, sep="\n  ")
    print("Fiche :", f"{PREFIXE}fiche-decideur_v1.md")


if __name__ == "__main__":
    main()
