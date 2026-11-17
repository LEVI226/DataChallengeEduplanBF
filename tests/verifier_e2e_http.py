"""Parcours HTTP du paquet public exact, avec exports recoupés au moteur Python.

Usage : python tests/verifier_e2e_http.py [dossier_public]
Les preuves sont privées dans 06_preparation_depot/verification_e2e_2026-11-16/.
"""
import csv
from functools import lru_cache, partial
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import io
import json
import math
from fractions import Fraction
from pathlib import Path
import statistics
import sys
import threading
import time

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'code'))
from allocation_objectifs import repartir_seuil

SPEC = importlib.util.spec_from_file_location('reference_python', ROOT / 'code/05_repartition.py')
REFERENCE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REFERENCE)


def nombre(texte):
    return float(texte.replace('\u202f', '').replace('\xa0', '').replace(' ', '').replace(',', '.').replace('%', ''))


def verifier(dossier=None):
    dossier = Path(dossier or ROOT / '06_preparation_depot/EduplanBf_vercel_public_methode').resolve()
    preuves = ROOT / '06_preparation_depot/verification_e2e_2026-11-16'
    (preuves / 'exports').mkdir(parents=True, exist_ok=True)
    hashes = {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in dossier.iterdir()}
    assert set(hashes) == {'index.html', 'app.js', 'moteur.js', 'donnees.js', 'style.css'}
    data = json.loads((dossier / 'donnees.js').read_text().removeprefix('window.DCB_DATA=').removesuffix(';\n'))
    provinces = data['provinces']
    regles = ['egalisation', 'deficit_d_abord', 'proportionnelle', 'franchissement']
    rapport = {'date': '2026-11-16', 'paquet': str(dossier), 'sha256': hashes,
               'navigateur': 'Chromium', 'transport': 'HTTP local, compte vierge',
               'matrice': [], 'parcours': [], 'erreurs_js': [], 'erreurs_console': [],
               'requetes_externes': [], 'requetes_en_ecriture': [], 'reponses_en_erreur': []}

    @lru_cache(maxsize=None)
    def calcul(scenario, regle, ressource, budget=2000, seuil=50):
        e = [p['demandes'][scenario] for p in provinces]
        stocks = [p[ressource] for p in provinces]
        if regle == 'franchissement':
            phases = repartir_seuil(e, stocks, budget, seuil)
            ajouts = phases['ajout']
        else:
            phases = None
            ajouts = REFERENCE.repartir(e, stocks, budget, regle, norme=seuil).tolist()
        ratios = [v/(s+a) for v, s, a in zip(e, stocks, ajouts)]
        manques = [max(0, math.ceil(Fraction(str(v))/Fraction(str(seuil))) - s-a)
                   for v, s, a in zip(e, stocks, ajouts)]
        return {'e': e, 'stocks': stocks, 'ajouts': ajouts, 'ratios': ratios,
                'maximum': max(ratios), 'moyenne': sum(e)/(sum(stocks)+sum(ajouts)),
                'provinces': sum(v > 0 for v in manques), 'manque': sum(manques),
                'part': 100*sum(v for v, m in zip(e, manques) if m > 0)/sum(e),
                'dispersion': statistics.pstdev(ratios), 'phases': phases}

    class Handler(SimpleHTTPRequestHandler):
        def log_message(self, *_):
            pass

    serveur = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(dossier)))
    fil = threading.Thread(target=serveur.serve_forever, daemon=True)
    fil.start()
    origine = f'http://127.0.0.1:{serveur.server_port}'
    debut = time.perf_counter()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(accept_downloads=True, viewport={'width': 1440, 'height': 1000})
            page = context.new_page()
            page.set_default_timeout(90000)
            page.on('pageerror', lambda e: rapport['erreurs_js'].append(str(e)))
            page.on('console', lambda m: rapport['erreurs_console'].append(m.text) if m.type == 'error' else None)
            page.on('request', lambda r: rapport['requetes_externes'].append(r.url)
                    if r.url.startswith(('http://', 'https://')) and not r.url.startswith(origine+'/') else None)
            page.on('request', lambda r: rapport['requetes_en_ecriture'].append({'url': r.url, 'method': r.method})
                    if r.method not in ['GET', 'HEAD'] else None)
            page.on('response', lambda r: rapport['reponses_en_erreur'].append({'url': r.url, 'status': r.status})
                    if r.status >= 400 else None)
            response = page.goto(origine+'/', wait_until='networkidle')
            assert response.status == 200
            assert page.locator('#lignes tr').count() == 45
            assert page.locator('#comparaison tr').count() == 4
            assert page.locator('#demo-table tr').count() == 45
            assert page.locator('#erreur').is_hidden()
            for name in hashes:
                r = page.request.get(origine+'/'+name)
                assert r.status == 200 and hashlib.sha256(r.body()).hexdigest() == hashes[name]
            rapport['parcours'].append('Chargement HTTP et empreintes des cinq fichiers')
            demo = page.locator('#demo-table').inner_text()

            for scenario in [s['id'] for s in data['scenarios']]:
                page.locator('#scenario').select_option(scenario)
                for regle in regles:
                    page.locator('#regle').select_option(regle)
                    with page.expect_download() as info:
                        page.locator('#export').click()
                    download = info.value
                    destination = preuves / 'exports' / download.suggested_filename
                    download.save_as(destination)
                    rows = list(csv.DictReader(io.StringIO(destination.read_text(encoding='utf-8-sig')), delimiter=';'))
                    assert len(rows) == 45 and len({r['province'] for r in rows}) == 45
                    assert {r['scenario'] for r in rows} == {scenario}
                    assert {r['regle'] for r in rows} == {regle}
                    assert {r['annee_stocks'] for r in rows} == {'2024-2025'}
                    record = {'scenario': scenario, 'regle': regle, 'export': destination.name, 'provinces': len(rows)}
                    for ressource, singulier in [('maitres', 'maitre'), ('salles', 'salle')]:
                        attendu = calcul(scenario, regle, ressource)
                        for i, row in enumerate(rows):
                            assert row['province'] == provinces[i]['province']
                            assert int(row['eleves']) == attendu['e'][i]
                            assert int(row[f'{ressource}_existants' if ressource == 'maitres' else 'salles_existantes']) == attendu['stocks'][i]
                            assert int(row[f'{ressource}_ajoutes' if ressource == 'maitres' else 'salles_ajoutees']) == attendu['ajouts'][i]
                            assert abs(float(row[f'ratio_{singulier}_apres'])-attendu['ratios'][i]) <= 0.000000501
                            if regle == 'franchissement':
                                assert int(row[f'{ressource}_ajout_seuil']) == attendu['phases']['ajout_seuil'][i]
                                assert int(row[f'{ressource}_ajout_reliquat']) == attendu['phases']['ajout_reliquat'][i]
                        assert sum(attendu['ajouts']) == 2000
                        page.locator('#ressource').select_option(ressource)
                        kpis = [nombre(x) for x in page.locator('#kpis strong').all_inner_texts()]
                        assert abs(kpis[0]-attendu['moyenne']) <= 0.051
                        assert abs(kpis[1]-attendu['maximum']) <= 0.051
                        assert kpis[2:] == [attendu['provinces'], attendu['manque']]
                        assert abs(nombre(page.locator('#part-eleves-apres').inner_text())-attendu['part']) <= 0.051
                        assert abs(nombre(page.locator('#dispersion-apres').inner_text())-attendu['dispersion']) <= 0.051
                        for seuil in [40, 50, 60]:
                            a = calcul(scenario, regle, ressource, 2000, seuil)
                            cellules = page.locator(f'#sensibilite-table tr[data-seuil="{seuil}"] td').all_inner_texts()
                            assert nombre(cellules[3]) == a['provinces']
                            assert abs(nombre(cellules[4])-a['maximum']) <= 0.051
                            assert nombre(cellules[5]) == a['manque']
                        record[ressource] = {'moyenne_apres': kpis[0], 'maximum_apres': kpis[1],
                                             'provinces_au_dessus': kpis[2], 'manque_restant': kpis[3]}
                    assert page.locator('#demo-table').inner_text() == demo
                    rapport['matrice'].append(record)
                print('Scénario contrôlé :', scenario, '· 4 exports × 45 provinces × 2 ressources', flush=True)

            page.locator('#scenario').select_option('actuel')
            page.locator('#regle').select_option('egalisation')
            page.locator('#ressource').select_option('maitres')
            synthese = page.locator('#synthese').inner_text()
            # Les treize filtres ne doivent changer ni la simulation ni la portée nationale du CSV.
            regions = page.locator('#region option').evaluate_all('(xs)=>xs.map(x=>x.value).filter(Boolean)')
            assert len(regions) == 13
            for region in regions:
                page.locator('#region').select_option(region)
                attendu = sum(p['region'] == region for p in provinces)
                assert page.locator('#lignes tr').count() == attendu
                assert page.locator('#carte .province').count() == attendu
                assert page.locator('#synthese').inner_text() == synthese
                page.locator('#carte .province').first.focus()
                page.keyboard.press('Enter')
                assert page.locator('#detail h3').first.inner_text() in {p['province'] for p in provinces if p['region'] == region}
            with page.expect_download() as info:
                page.locator('#export').click()
            rows = list(csv.DictReader(io.StringIO(Path(info.value.path()).read_text(encoding='utf-8-sig')), delimiter=';'))
            assert len(rows) == 45
            page.locator('#region').select_option('')
            for province in ['SOUM', 'TAPOA']:
                page.locator('[data-province]').filter(has_text=province).click()
                assert 'partiel' in page.locator('#detail').inner_text()
            for province in [p['province'] for p in provinces]:
                page.locator('[data-province]').filter(has_text=province).click()
                assert page.locator('#detail h3').first.inner_text() == province
            rapport['parcours'].append('13 filtres régionaux, sélection carte au clavier, 45 fiches et couvertures ESU partielles')
            print('Carte, filtres et 45 fiches : OK', flush=True)

            for identifiant in ['glossaire', 'methode']:
                page.locator('#'+identifiant+' summary').focus()
                page.keyboard.press('Enter')
                assert page.locator('#'+identifiant).get_attribute('open') is not None
            for fichier in ['moteur.js', 'app.js']:
                assert page.locator(f'#methode a[href="{fichier}"]').count() == 1
                assert page.request.get(origine+'/'+fichier).status == 200
            rapport['parcours'].append('Glossaire et méthode accessibles au clavier ; liens du code servis en HTTP')

            for champ in ['budget-maitres', 'budget-salles', 'seuil-maitres', 'seuil-salles']:
                invalides = ['', '-1', '1.5', '100001'] if champ.startswith('budget') else ['', '0', '-1']
                for valeur in invalides:
                    page.locator('#'+champ).fill(valeur)
                    page.locator('button[type=submit]').click()
                    assert page.locator('#erreur').is_visible()
                    assert page.locator('#'+champ).get_attribute('aria-invalid') == 'true'
                    assert page.locator('#'+champ).evaluate('(x)=>x===document.activeElement')
                    assert page.locator('#export').is_disabled()
                    for vide in ['synthese', 'lignes', 'sensibilite-table', 'indicateurs-complementaires', 'courbe-reperes']:
                        assert page.locator('#'+vide).inner_text() == ''
                    assert 'Value must' not in page.locator('#erreur').inner_text()
                    page.locator('#'+champ).fill('2000' if champ.startswith('budget') else '50')
                    assert page.locator('#erreur').is_hidden()
            rapport['parcours'].append('14 saisies invalides, focus du champ, messages français, effacement et rétablissement immédiat')

            for regle in regles:
                page.locator('#regle').select_option(regle)
                page.locator('#budget-maitres').fill('0')
                page.locator('#budget-salles').fill('1')
                with page.expect_download() as info:
                    page.locator('#export').click()
                rows = list(csv.DictReader(io.StringIO(Path(info.value.path()).read_text(encoding='utf-8-sig')), delimiter=';'))
                assert sum(int(r['maitres_ajoutes']) for r in rows) == 0
                assert sum(int(r['salles_ajoutees']) for r in rows) == 1
                page.locator('#budget-maitres').fill('2000')
                page.locator('#budget-salles').fill('2000')
            page.locator('#regle').select_option('franchissement')
            page.locator('#seuil-maitres').fill('43.8')
            page.locator('#budget-maitres').fill('9')
            assert '1 province ramenée' in page.locator('#franchissement-detail').inner_text()
            page.locator('#seuil-maitres').fill('0.04')
            assert '0,04' in page.locator('#synthese').inner_text()
            assert 'hors de la plage' in page.locator('#courbe-reperes').inner_text()
            page.locator('#seuil-maitres').fill('50')
            page.locator('#regle').select_option('egalisation')
            page.locator('#budget-maitres').fill('6000')
            assert 'ne signifie pas que les conditions d’enseignement sont satisfaisantes' in page.locator('#synthese').inner_text()
            rapport['parcours'].append('Budgets distincts 0/1, seuil décimal 43,8, seuil hors plage 0,04 et moyens dépassant le besoin')

            # Les bornes hautes passent aussi par l'interface complète, sans modifier le moteur.
            timings = []
            for regle in regles:
                page.locator('#regle').select_option(regle)
                t = time.perf_counter()
                page.locator('#budget-maitres').fill('100000')
                page.locator('#budget-salles').fill('100000')
                assert page.locator('#erreur').is_hidden()
                with page.expect_download() as info:
                    page.locator('#export').click()
                rows = list(csv.DictReader(io.StringIO(Path(info.value.path()).read_text(encoding='utf-8-sig')), delimiter=';'))
                assert sum(int(r['maitres_ajoutes']) for r in rows) == 100000
                assert sum(int(r['salles_ajoutees']) for r in rows) == 100000
                timings.append({'regle': regle, 'secondes_deux_saisies_et_export': round(time.perf_counter()-t, 2)})
                page.locator('#budget-maitres').fill('2000')
                page.locator('#budget-salles').fill('2000')
            rapport['borne_haute'] = timings
            print('Bornes hautes 100 000 / 100 000 : OK', flush=True)

            with page.expect_download() as info:
                page.locator('#export-demographie').click()
            destination = preuves / 'exports' / info.value.suggested_filename
            info.value.save_as(destination)
            rows = list(csv.DictReader(io.StringIO(destination.read_text(encoding='utf-8-sig')), delimiter=';'))
            assert len(rows) == 45 and sum(int(r['eleves_total']) for r in rows) == 3308096
            assert float(next(r for r in rows if r['province'] == 'KADIOGO')['inscrits_pour_100_enfants']) > 100
            rapport['parcours'].append('Export démographique : 45 lignes, total 3 308 096, valeurs supérieures à 100 conservées')
            page.locator('#regle').select_option('egalisation')
            page.screenshot(path=str(preuves / 'bureau.png'), full_page=True)
            for largeur in [320, 390, 768, 1440]:
                page.set_viewport_size({'width': largeur, 'height': 900})
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), largeur
                assert page.locator('#export').is_visible()
            page.set_viewport_size({'width': 390, 'height': 844})
            page.locator('#ressource').select_option('salles')
            page.screenshot(path=str(preuves / 'mobile.png'), full_page=True)
            rapport['parcours'].append('Largeurs 320, 390, 768 et 1440 pixels, sans débordement horizontal de page')
            page.reload(wait_until='networkidle')
            assert page.locator('#budget-maitres').input_value() == '2000'
            assert page.locator('#budget-salles').input_value() == '2000'
            assert page.locator('#lignes tr').count() == 45
            rapport['parcours'].append('Rechargement : valeurs par défaut et résultats restaurés')
            assert not rapport['erreurs_js'], rapport['erreurs_js']
            assert not rapport['erreurs_console'], rapport['erreurs_console']
            assert not rapport['requetes_externes'], rapport['requetes_externes']
            assert not rapport['requetes_en_ecriture'], rapport['requetes_en_ecriture']
            assert not rapport['reponses_en_erreur'], rapport['reponses_en_erreur']
            context.close()
            browser.close()
        assert hashes == {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in dossier.iterdir()}
        rapport['statut'] = 'REUSSI'
    except Exception as e:
        rapport['statut'] = 'ECHEC'
        rapport['erreur'] = repr(e)
        raise
    finally:
        rapport['duree_secondes'] = round(time.perf_counter()-debut, 2)
        (preuves / 'rapport.json').write_text(json.dumps(rapport, ensure_ascii=False, indent=2)+'\n')
        serveur.shutdown()
        serveur.server_close()
        fil.join(timeout=2)
    print('E2E HTTP réussi : 28 exports, 2 520 allocations provinciales et ratios recoupés au moteur Python ; preuves :', preuves, flush=True)


if __name__ == '__main__':
    verifier(sys.argv[1] if len(sys.argv) > 1 else None)
