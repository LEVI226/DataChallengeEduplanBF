"""Complète V4 : quatre règles, courbe des moyens et contexte démographique."""
from pathlib import Path
import pandas as pd
from rapport_livraison import fmt, declaration_ia


def completer(root, blocks):
    root = Path(root)
    c = pd.read_csv(root/'04_analyse/EXX_04-analyse_D3_scientist_comparaison-objectifs_v5.csv')
    d = pd.read_csv(root/'03_transformation/EXX_03-transformation_D3_architect_lecture-demographique_v5.csv')
    courbe = pd.read_csv(root/'04_analyse/EXX_04-analyse_D3_scientist_courbe-moyens_v5.csv')
    sel = c[(c.ressource == 'maitres') & (c.budget == 2000)]
    f = sel[sel.regle == 'franchissement'].iloc[0]
    national = 100*d.eleves_total.sum()/d.population_6_11_2025.sum()
    labels = {'proportionnelle': 'Prorata', 'deficit_d_abord': 'Déficit d’abord', 'egalisation': 'Égalisation', 'franchissement': 'Franchissement du seuil'}
    out = []
    for kind, value in blocks:
        if kind == 'p':
            value = value.replace('Rapport V4', 'Rapport V5').replace('version V4', 'version V5').replace('--version 4 --sortie livraison_v4', '--version 5 --sortie livraison_v5')
            value = value.replace('comparer trois règles', 'comparer quatre règles').replace('comparer les trois répartitions', 'comparer les quatre répartitions')
            value = value.replace('La chaîne 01→07→10', 'La chaîne 01→07→13→10')
            if value.startswith('Claude et Codex ont aidé'): value = declaration_ia(root,5)
            if value.startswith('L’arbitrage à décider :'):
                value += f' Le franchissement du seuil laisse sept provinces au-dessus et un pire ratio de {fmt(f.ratio_max,1)} après répartition du reliquat.'
        if kind == 'table' and value[0][0] == 'Règle':
            value = [*value, ['Franchissement du seuil', 'Déficits entiers croissants ; reliquat sur les ratios les plus élevés']]
        if kind == 'table' and str(value[0][0]).startswith('Règle / 2 000'):
            # Le tableau historique garde sa ligne initiale, calculée par le script 05.
            value = [value[0], value[1], *[[labels[r.regle], fmt(r.ratio_max,1), fmt(r.ecart_type_ratios,1), fmt(r.provinces_au_dessus_norme), fmt(r.deficit_restant)] for r in sel.itertuples()]]
        out.append((kind, value))
        if kind == 'table' and value[0][0] == 'Règle':
            out.append(('p', 'Optimalité du nombre de franchissements : chaque province coûte son déficit entier pour atteindre le seuil. Toute sélection de k provinces coûte au moins la somme des k plus petits déficits. Le tri croissant maximise donc ce nombre, à coût unitaire identique, toutes provinces éligibles, sans couplage ni retrait. Le reliquat est réparti par égalisation ; ce départage n’est pas revendiqué comme optimum conjoint des deux critères.'))
    pos = next(i for i, b in enumerate(out) if b == ('h', '6. La réponse au défi'))-1
    extras = [
        ('page', None), ('p', 'Résultats — un quatrième objectif et le coût d’un plafond'),
        ('p', f'Franchissement du seuil, 2 000 maîtres : les 23 plus petits déficits totalisent {fmt(f.cout_franchissement)} postes. Le Loroum en reçoit 161 et atteint le seuil de 50. Ramener 24 provinces au seuil exigerait au minimum {fmt(f.cout_province_supplementaire)} postes. Les {fmt(f.reliquat_egalise)} postes restants sont distribués sur les ratios les plus élevés ; le maximum final est {fmt(f.ratio_max_precis,4)}. Les 2 000 postes sont entièrement affectés et sept provinces restent au-dessus du seuil.'),
        ('p', 'Cette règle privilégie le nombre de franchissements, tandis que l’égalisation privilégie les charges extrêmes. Les quatre répartitions sont des solutions comparées, pas un front de Pareto démontré. La décomposition provinciale distingue les ajouts de franchissement et ceux du reliquat.'),
        ('fig', (root/'05_interpretation/EXX_05-interpretation_D3_analyst_courbe-moyens_v5.png', 'Figure 5 — Unités minimales pour ramener chaque province sous un plafond donné. DGESS CNS530, primaire public 2024–2025 ; stocks conservés et ressources séparées.')),
        ('table', [['Plafond provincial', 'Maîtres minimaux', 'Salles minimales'], *[[str(v), fmt(courbe[(courbe.ressource=='maitres') & (courbe.plafond_ratio==v)].iloc[0].unites_minimales), fmt(courbe[(courbe.ressource=='salles') & (courbe.plafond_ratio==v)].iloc[0].unites_minimales)] for v in [50,55,60]]]),
        ('page', None), ('p', 'Résultats — charge des inscrits et contexte démographique'),
        ('p', f'Le primaire public et privé compte {fmt(d.eleves_total.sum())} inscrits de tous âges, rapportés à {fmt(d.population_6_11_2025.sum())} enfants de 6–11 ans projetés en 2025 : {fmt(national,1)} inscrits pour 100 enfants projetés au niveau national. La charge par maître demeure calculée sur les seuls élèves et maîtres du public. Les périmètres sont différents.'),
        ('fig', (root/'05_interpretation/EXX_05-interpretation_D3_analyst_charge-demographie_v5.png', 'Figure 6 — Charge du public et inscriptions public + privé rapportées à la population projetée. DGESS CNS530 et INSD RGPH2019, volume 4. Les lignes sont des repères analytiques, pas des catégories officielles.')),
        ('table', [['Province', 'Élèves / maître public', 'Inscrits / 100 enfants projetés'], *[[r.province, fmt(r.ratio_charge_public,1), fmt(r.inscrits_pour_100_enfants,1)] for r in d[d.province.isin(['SOUROU','TAPOA','KADIOGO'])].itertuples()]]),
        ('p', 'Ce rapport n’est pas un taux net de scolarisation ni une mesure des enfants non scolarisés : les élèves ne sont pas limités à la tranche 6–11 ans, la population est projetée à partir du RGPH2019 et les déplacements récents ne sont pas modélisés. Une valeur supérieure à 100 est conservée. Une faible valeur invite à un examen local, sans prouver une cause ou une proportion réelle de non-scolarisation. Ce contexte ne modifie aucune allocation ni aucun scénario 2030.')]
    out[pos:pos] = extras
    return out
