"""Régression navigateur facultative : .venv/bin/python DataChallenge/tests/verifier_interface.py.

Nécessite Playwright et son Chromium installés séparément ; non exécutée par unittest.
"""
import csv
import io
from pathlib import Path
from playwright.sync_api import sync_playwright


def verifier():
    url = (Path(__file__).resolve().parents[1] / 'tableau_de_bord/index.html').as_uri()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(accept_downloads=True)
        errors = []
        network = []
        page.on('request', lambda request: network.append(request.url) if request.url.startswith(('http://','https://')) else None)
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('console', lambda message: errors.append(message.text) if message.type == 'error' else None)
        page.goto(url)
        assert page.locator('#lignes tr').count() == 45
        assert 'Sélectionnez un territoire' in page.locator('#detail').inner_text(), 'La simulation initiale valide doit inviter à sélectionner une province'
        # fill émet input, sans blur/change : aucune ancienne simulation ne doit rester exportable.
        page.locator('#budget-maitres').fill('-1')
        assert page.locator('#erreur').is_visible(), 'Une saisie négative doit signaler immédiatement son erreur'
        assert page.locator('#lignes tr').count() == 0
        assert page.locator('#kpis .kpi').count() == 0
        assert page.locator('#export').is_disabled()
        page.locator('#budget-maitres').fill('0')
        assert page.locator('#erreur').is_hidden()
        assert 'Sélectionnez un territoire' in page.locator('#detail').inner_text(), 'Le rétablissement sans province sélectionnée doit rétablir l’invitation'
        assert '0 maîtres supplémentaires' in page.locator('#perimetre').inner_text()
        page.locator('#region').select_option(label='SAHEL')
        assert page.locator('#lignes tr').count() < 45
        with page.expect_download() as info:
            page.locator('#export').click()
        rows = list(csv.DictReader(io.StringIO(Path(info.value.path()).read_text(encoding='utf-8-sig')), delimiter=';'))
        assert len(rows) == 45
        assert {row['budget_maitres_unites'] for row in rows} == {'0'}
        assert sum(int(row['maitres_ajoutes']) for row in rows) == 0
        assert 'annee_stocks' in rows[0], 'Le CSV doit préciser l’année des stocks observés'
        assert {row['annee_stocks'] for row in rows} == {'2024-2025'}
        page.locator('#scenario').select_option('demographie_insd')
        hypothesis = page.locator('#hypothese').inner_text()
        assert 'Années civiles 2025/2030' in hypothesis and 'stocks de maîtres et de salles conservés' in hypothesis
        page.locator('#region').select_option('')
        page.locator('[data-province]').filter(has_text='SOUM').click()
        assert 'partiel' in page.locator('#detail').inner_text()
        page.locator('[data-province]').filter(has_text='TAPOA').click()
        assert 'partiel' in page.locator('#detail').inner_text()
        page.locator('#budget-maitres').fill('2000')
        assert '2\u202f000 maîtres supplémentaires' in page.locator('#perimetre').inner_text()
        with page.expect_download() as info:
            page.locator('#export').click()
        rows = list(csv.DictReader(io.StringIO(Path(info.value.path()).read_text(encoding='utf-8-sig')), delimiter=';'))
        assert sum(int(row['maitres_ajoutes']) for row in rows) == 2000
        assert 'annee_stocks' in rows[0], 'Le CSV doit préciser l’année des stocks observés'
        assert {row['annee_stocks'] for row in rows} == {'2024-2025'}
        assert all('Années civiles 2025/2030' in row['hypothese'] and 'stocks de maîtres et de salles conservés' in row['hypothese'] for row in rows)
        page.set_viewport_size({'width': 390, 'height': 844})
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
        assert not errors, errors
        assert not network, network
        browser.close()
    print('Interface : input sans blur, erreur immédiate, invalidation/export, scénarios, statuts ESU, CSV national et mobile OK.')


if __name__ == '__main__':
    verifier()
