"""Contrôles navigateur de la méthode, des seuils et des indicateurs territoriaux."""
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
        assert page.locator('#methode').count() == 1, 'La méthode doit être consultable dans la page'
        assert 'Seuil courant' in page.locator('#sensibilite-table tr.selected td').first.inner_text()
        assert page.locator('#sensibilite-table tr.selected').get_attribute('aria-current') == 'true'
        page.locator('#methode summary').focus()
        page.keyboard.press('Enter')
        assert page.locator('#methode').get_attribute('open') is not None
        texte = page.locator('#methode').inner_text()
        for nom in page.locator('#regle option').all_inner_texts():
            assert nom in texte
        assert 'pas des intervalles de confiance' in texte
        assert 'non arrondi' in texte
        assert 'retraites' in texte and 'recrutements' in texte
        scenarios = page.locator('#scenario option').evaluate_all('(xs) => xs.map(x=>x.value)')
        for scenario in scenarios:
            page.locator('#scenario').select_option(scenario)
            for regle in ['egalisation', 'proportionnelle', 'deficit_d_abord', 'franchissement']:
                page.locator('#regle').select_option(regle)
                for ressource in ['maitres', 'salles']:
                    page.locator('#ressource').select_option(ressource)
                    # Recalcul de chaque seuil : ne pas réévaluer une allocation figée pour une règle dépendante.
                    attendu = page.evaluate('''([scenario,regle,r]) => {
                        const d=DCB_DATA,e=d.provinces.map(p=>p.demandes[scenario]),s=d.provinces.map(p=>p[r]);
                        return [40,50,60].map(t=>{
                            const a=DCBEngine.repartir(e,s,2000,regle,t);
                            return {t,avant:DCBEngine.mesurer(e,s,e.map(()=>0),t),apres:DCBEngine.mesurer(e,s,a,t)};
                        });
                    }''', [scenario, regle, ressource])
                    for ligne in attendu:
                        cells = page.locator(f'#sensibilite-table tr[data-seuil="{ligne["t"]}"] td').all_inner_texts()
                        chiffres = [c.replace('\u202f', '').replace('\xa0', '').replace(',', '.') for c in cells]
                        assert float(chiffres[0].split()[0]) == ligne['t']
                        assert [float(c) for c in chiffres[1:]] == [
                            ligne['avant']['deficit_restant'], ligne['avant']['provinces_au_dessus_norme'],
                            ligne['apres']['provinces_au_dessus_norme'], ligne['apres']['ratio_max'], ligne['apres']['deficit_restant']]
                    note = page.locator('#sensibilite-note').inner_text()
                    assert 'ne dépend pas du seuil' in note if regle in ['egalisation', 'proportionnelle'] else 'peut modifier la répartition' in note
                    m = attendu[1]['apres']
                    total = page.evaluate('DCB_DATA.provinces.reduce((s,p)=>s+p.demandes[document.getElementById("scenario").value],0)')
                    part = 100*m['eleves_en_province_au_dessus_norme']/total
                    assert abs(float(page.locator('#part-eleves-apres').inner_text().replace(',', '.').replace(' %', '')) - part) <= 0.051
                    assert float(page.locator('#dispersion-apres').inner_text().replace(',', '.')) == m['ecart_type_ratios']
                    assert 'pas la situation individuelle' in page.locator('#indicateurs-complementaires').inner_text()
                    assert page.locator('#courbe-moyens [data-repere="budget"]').get_attribute('data-budget') == '2000'
                    assert page.locator('#courbe-moyens [data-repere="seuil"]').count() == 1
                    assert page.locator('#courbe-moyens circle[data-plafond="40"]').count() == 1
        page.locator('#scenario').select_option('actuel')
        page.locator('#regle').select_option('egalisation')
        page.locator('#ressource').select_option('maitres')
        ajouts = []
        for seuil in ['40', '50', '60']:
            page.locator('#seuil-maitres').fill(seuil)
            with page.expect_download() as info:
                page.locator('#export').click()
            rows = list(csv.DictReader(io.StringIO(Path(info.value.path()).read_text(encoding='utf-8-sig')), delimiter=';'))
            ajouts.append({r['province']: r['maitres_ajoutes'] for r in rows})
        assert ajouts[0] == ajouts[1] == ajouts[2]
        assert 'ne signifie pas que les conditions d’enseignement sont satisfaisantes' in page.locator('#synthese').inner_text()
        assert '56,3' in page.locator('#synthese').inner_text()
        page.locator('#seuil-maitres').fill('43.85')
        assert page.locator('#sensibilite-table tr[data-seuil="43.85"].selected').count() == 1
        page.locator('#seuil-maitres').fill('0.04')
        assert 'hors de la plage' in page.locator('#courbe-reperes').inner_text()
        page.locator('#budget-maitres').fill('0')
        assert page.locator('#courbe-moyens [data-repere="budget"]').get_attribute('data-budget') == '0'
        assert 'NaN' not in page.locator('#courbe-moyens').inner_html()
        page.locator('#seuil-maitres').fill('0')
        for identifiant in ['sensibilite-table', 'indicateurs-complementaires', 'courbe-reperes']:
            assert page.locator('#'+identifiant).inner_text() == ''
        page.locator('#seuil-maitres').fill('50')
        page.locator('#budget-maitres').fill('2000')
        page.screenshot(path='/tmp/eduplanbf-methode-bureau.png', full_page=True)
        page.set_viewport_size({'width': 390, 'height': 844})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path='/tmp/eduplanbf-methode-mobile.png', full_page=True)
        assert not errors, errors
        browser.close()
    print('Méthode : 56 vues, sensibilité recalculée, allocations/export stables, indicateurs, repères, seuils décimaux, zéro et mobile OK.')


if __name__ == '__main__':
    verifier(sys.argv[1] if len(sys.argv) > 1 else None)
