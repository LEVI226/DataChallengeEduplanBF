"""Vérifie la pédagogie avec les vrais calculs et exports, sur bureau et mobile."""
import csv
import io
from pathlib import Path
import sys
from playwright.sync_api import sync_playwright


def verifier(dossier=None):
    dossier = Path(dossier or Path(__file__).resolve().parents[1] / 'tableau_de_bord')
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(accept_downloads=True, viewport={'width': 1440, 'height': 1000})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto((dossier / 'index.html').resolve().as_uri())
        assert page.locator('#synthese').is_visible(), 'Une synthèse de décision doit ouvrir les résultats'
        assert page.locator('#parametres-form').evaluate('(f) => f.noValidate')
        assert 'maîtres supplémentaires' in page.locator('#perimetre').inner_text()
        assert 'salles supplémentaires' in page.locator('#perimetre').inner_text()
        # Les 56 vues doivent expliquer les valeurs du moteur, sans calcul parallèle approximatif.
        scenarios = page.locator('#scenario option').evaluate_all('(xs) => xs.map(x => x.value)')
        for scenario in scenarios:
            page.locator('#scenario').select_option(scenario)
            for regle in ['egalisation', 'deficit_d_abord', 'proportionnelle', 'franchissement']:
                page.locator('#regle').select_option(regle)
                for ressource in ['maitres', 'salles']:
                    page.locator('#ressource').select_option(ressource)
                    attendu = page.evaluate('''([scenario, regle, ressource]) => {
                        const d=window.DCB_DATA, e=d.provinces.map(p=>p.demandes[scenario]);
                        const stock=d.provinces.map(p=>p[ressource]);
                        const ajout=DCBEngine.repartir(e,stock,2000,regle,50);
                        return DCBEngine.mesurer(e,stock,ajout,50);
                    }''', [scenario, regle, ressource])
                    texte = page.locator('#synthese').inner_text().replace('\u202f', '').replace('\xa0', '')
                    assert str(attendu['deficit_restant']) in texte
                    assert str(attendu['ratio_max']).replace('.', ',') in texte
                    assert ('maître' if ressource == 'maitres' else 'salle') in texte
                    assert all('Avant :' in x and 'Après :' in x for x in page.locator('.kpi .before').all_inner_texts())
                    assert 'salle' in page.locator('#moyens-titre').inner_text() if ressource == 'salles' else 'maître' in page.locator('#moyens-titre').inner_text()
        page.locator('#scenario').select_option('actuel')
        page.locator('#regle').select_option('proportionnelle')
        page.locator('#ressource').select_option('maitres')
        assert '3\u202f724' in page.locator('#synthese').inner_text()
        assert 'toutes les provinces sont servies' not in page.locator('#regle-description').inner_text().lower()
        for field, value, message in [('budget-maitres', '-1', '0 et 100'),
                                      ('budget-maitres', '1.5', 'entier'),
                                      ('budget-maitres', '100001', '0 et 100'),
                                      ('budget-maitres', '', 'obligatoire'),
                                      ('seuil-salles', '0', 'strictement positif')]:
            page.locator('#'+field).fill(value)
            page.locator('button[type=submit]').click()
            assert message in page.locator('#erreur').inner_text()
            assert page.locator('#'+field).get_attribute('aria-invalid') == 'true'
            assert page.locator('#synthese').inner_text() == ''
            assert page.locator('#export').is_disabled()
            page.locator('#'+field).fill('2000' if field.startswith('budget') else '50')
            assert page.locator('#erreur').is_hidden()
        page.locator('#budget-maitres').fill('0')
        assert '5\u202f061' in page.locator('#synthese').inner_text()
        page.locator('#regle').select_option('egalisation')
        page.locator('#budget-maitres').fill('6000')
        assert 'Toutes les provinces' in page.locator('#synthese').inner_text()
        page.locator('#budget-maitres').fill('2000')
        for seuil in ['43.85', '0.04']:
            page.locator('#seuil-maitres').fill(seuil)
            assert 'seuil choisi de '+seuil.replace('.', ',') in page.locator('#synthese').inner_text()
        page.locator('#seuil-maitres').fill('50')
        page.locator('#glossaire summary').click()
        assert page.locator('#glossaire').get_attribute('open') is not None
        assert 'Maîtres chargés de cours' in page.locator('#glossaire').inner_text()
        page.locator('#regle').select_option('franchissement')
        with page.expect_download() as download:
            page.locator('#export').click()
        rows = list(csv.DictReader(io.StringIO(Path(download.value.path()).read_text(encoding='utf-8-sig')), delimiter=';'))
        assert len(rows) == 45
        assert sum(int(r['maitres_ajoutes']) for r in rows) == 2000
        assert sum(int(r['maitres_ajout_seuil']) for r in rows) == 1856
        assert next(r for r in rows if r['province'] == 'LOROUM')['maitres_ajoutes'] == '161'
        with page.expect_download() as download:
            page.locator('#export-demographie').click()
        rows = list(csv.DictReader(io.StringIO(Path(download.value.path()).read_text(encoding='utf-8-sig')), delimiter=';'))
        assert len(rows) == 45 and sum(int(r['eleves_total']) for r in rows) == 3308096
        page.screenshot(path='/tmp/eduplanbf-pedagogie-bureau.png', full_page=True)
        page.set_viewport_size({'width': 390, 'height': 844})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.locator('#ressource').select_option('salles')
        assert 'salle' in page.locator('#synthese').inner_text()
        page.screenshot(path='/tmp/eduplanbf-pedagogie-mobile.png', full_page=True)
        assert not errors, errors
        browser.close()
    print('Pédagogie : 56 vues, synthèses, deux ressources, erreurs françaises, glossaire, exports et mobile OK.')


if __name__ == '__main__':
    verifier(sys.argv[1] if len(sys.argv) > 1 else None)
