"""Ajouts V5 indépendants des tables historiques : quatre règles et contexte démographique."""
from pathlib import Path
import importlib.util
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from allocation_objectifs import repartir_seuil, unites_plafond, lecture_demographique

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'EXX'


def donnees_demographiques(root=ROOT):
    source = pd.read_csv(root/'02_nettoyage/EXX_02-nettoyage_D3_engineer_primaire-provinces-statut_v1.csv')
    source = source[(source.annee_scolaire == '2024-2025') & (source.niveau == 'province')]
    public = source[source.statut == 'Public'][['region', 'province', 'eleves', 'maitres_charges_cours', 'source_document', 'source_page']].rename(columns={'eleves': 'eleves_public', 'maitres_charges_cours': 'maitres_public'})
    prive = source[source.statut == 'Prive'][['province', 'eleves']].rename(columns={'eleves': 'eleves_prive'})
    if len(public) != 45 or len(prive) != 45:
        raise ValueError('45 provinces publiques et privées attendues')
    inscriptions = public.merge(prive, on='province', validate='one_to_one')
    pop = pd.read_csv(root/'03_transformation/EXX_03-transformation_D3_architect_facteurs-demographiques-insd_v1.csv')
    pop = pop[['province', 'ensemble_2025', 'document_2025', 'page_2025']].rename(columns={'ensemble_2025': 'population_6_11_2025'})
    d = lecture_demographique(inscriptions, pop).sort_values(['region', 'province'])
    d['annee_scolaire'] = '2024-2025'
    d['annee_population'] = 2025
    return d


def main():
    spec = importlib.util.spec_from_file_location('historique', ROOT/'code/05_repartition.py')
    ancien = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ancien)
    ind = pd.read_csv(ROOT/'03_transformation/EXX_03-transformation_D3_architect_indicateurs-provinces-public_v1.csv')
    ind = ind[ind.annee_scolaire == '2024-2025'].sort_values(['region', 'province']).reset_index(drop=True)
    if len(ind) != 45 or ind.province.duplicated().any():
        raise ValueError('45 provinces uniques attendues')
    e = ind.eleves.to_numpy(float)
    comparaison, detail, courbe = [], [], []
    for res in ['maitres', 'salles']:
        stocks = ind[res].to_numpy(float)
        for plafond in range(35, 121):
            courbe.append({'ressource': res, 'plafond_ratio': plafond, 'unites_minimales': unites_plafond(e, stocks, plafond), 'annee_scolaire': '2024-2025', 'perimetre': 'primaire_public_45_provinces', 'hypothese': 'Stocks conservés, ajouts seuls, toutes provinces éligibles, sans coût ni couplage'})
        for budget in [0, 500, 1000, 2000, 3000, 5000]:
            for regle in [*ancien.REGLES, 'franchissement']:
                r = repartir_seuil(e, stocks, budget)
                a = np.asarray(r['ajout']) if regle == 'franchissement' else ancien.repartir(e, stocks, budget, regle)
                comparaison.append({'ressource': res, 'budget': budget, 'regle': regle,
                                    **ancien.mesurer(e, stocks, a), 'ratio_max_precis': float(max(e/(stocks+a))),
                                    'cout_franchissement': r['cout_franchissement'] if regle == 'franchissement' else None,
                                    'reliquat_egalise': r['reliquat'] if regle == 'franchissement' else None,
                                    'cout_province_supplementaire': r['cout_province_supplementaire'] if regle == 'franchissement' else None})
                if budget == 2000 and regle == 'franchissement':
                    for i, row in ind.iterrows():
                        detail.append({'province': row.province, 'region': row.region, 'ressource': res, 'budget': budget,
                                       'seuil': 50, 'eleves_public': int(e[i]), 'stock': int(stocks[i]),
                                       'ajout_seuil': r['ajout_seuil'][i], 'ajout_reliquat': r['ajout_reliquat'][i],
                                       'ajout_total': r['ajout'][i], 'ratio_apres': e[i]/(stocks[i]+r['ajout'][i]),
                                       'annee_scolaire': '2024-2025', 'regle': regle})
    dest = ROOT/'04_analyse'
    for name, rows in [('comparaison-objectifs', comparaison), ('franchissement-detail', detail), ('courbe-moyens', courbe)]:
        pd.DataFrame(rows).to_csv(dest/f'{PREFIX}_04-analyse_D3_scientist_{name}_v5.csv', index=False, encoding='utf-8-sig')
    demo = donnees_demographiques()
    demo.to_csv(ROOT/f'03_transformation/{PREFIX}_03-transformation_D3_architect_lecture-demographique_v5.csv', index=False, encoding='utf-8-sig')
    plt.rcParams.update({'font.size': 10})
    fig, ax = plt.subplots(figsize=(9, 4.3))
    for res, label in [('maitres', 'Maîtres'), ('salles', 'Salles')]:
        c = pd.DataFrame(courbe); c = c[c.ressource == res]
        ax.plot(c.plafond_ratio, c.unites_minimales, label=label)
    ax.set(xlabel='Plafond souhaité du ratio provincial', ylabel='Unités supplémentaires minimales', title='Moyens nécessaires — primaire public 2024–2025')
    ax.legend(); ax.grid(alpha=.2); fig.tight_layout()
    fig.savefig(ROOT/f'05_interpretation/{PREFIX}_05-interpretation_D3_analyst_courbe-moyens_v5.png', dpi=160); plt.close(fig)
    rapport = 100*demo.eleves_total.sum()/demo.population_6_11_2025.sum()
    fig, ax = plt.subplots(figsize=(9, 4.3))
    ax.scatter(demo.ratio_charge_public, demo.inscrits_pour_100_enfants, color='#176650')
    ax.axvline(50, color='gray', linestyle='--', label='Seuil de charge exploratoire : 50')
    ax.axhline(rapport, color='#b07835', linestyle=':', label=f'Rapport national : {rapport:.1f} pour 100')
    for r in demo.itertuples():
        if r.province in ['SOUROU', 'TAPOA', 'KADIOGO', 'LOROUM']:
            ax.annotate(r.province, (r.ratio_charge_public, r.inscrits_pour_100_enfants), xytext=(4, 5), textcoords='offset points', fontsize=8)
    ax.set(xlabel='Élèves du public / maître chargé de cours', ylabel='Inscrits public + privé / 100 enfants projetés de 6–11 ans', title='Deux lectures distinctes — pas un taux net de scolarisation')
    ax.legend(fontsize=8); ax.grid(alpha=.15); fig.tight_layout()
    fig.savefig(ROOT/f'05_interpretation/{PREFIX}_05-interpretation_D3_analyst_charge-demographie_v5.png', dpi=160); plt.close(fig)
    ref = [r for r in comparaison if r['ressource'] == 'maitres' and r['budget'] == 2000 and r['regle'] == 'franchissement'][0]
    print(f'V5 : {ref}; rapport démographique national {rapport:.4f} pour 100 ; aucun changement des stocks ou allocations historiques.')


if __name__ == '__main__':
    main()
