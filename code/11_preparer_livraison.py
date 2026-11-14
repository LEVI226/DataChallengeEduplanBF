"""Construit la livraison et son manifeste, sans upload (V1 : neuf fichiers ; V2 : dix).

Usage : python code/11_preparer_livraison.py --equipe E07 --sortie livraison_v1
Les sources originales sont copiées sans modification ; les produits EXX sont adaptés.
"""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import re
import shutil
import sys
import zipfile

RACINE = Path(__file__).resolve().parents[1]
if str(RACINE/'code') not in sys.path: sys.path.insert(0,str(RACINE/'code'))
from rapport_livraison import generer_rapport, DECLARATION_IA, declaration_ia

ETAPES = [('01_collecte','01-collecte','engineer'),('02_nettoyage','02-nettoyage','engineer'),('03_transformation','03-transformation','architect'),('04_analyse','04-analyse','scientist'),('05_interpretation','05-interpretation','analyst')]
INTERDITS = {'.venv','venv','__pycache__','.DS_Store','.git','node_modules'}
TEXTES = {'.py','.md','.txt','.csv','.json','.js','.html','.css','.svg'}


def valider_equipe(equipe):
    if equipe != 'EXX' and re.fullmatch(r'E\d{2}',equipe) is None:
        raise ValueError('Code anonyme attendu : EXX ou E suivi de deux chiffres, par exemple E07.')
    return equipe


def valider_limites(tailles, pages):
    if any(t >= 50_000_000 or t < 0 for t in tailles): raise ValueError('Chaque fichier doit être inférieur à 50 000 000 octets.')
    if sum(tailles) >= 500_000_000: raise ValueError('Le total doit être inférieur à 500 000 000 octets.')
    if not 1 <= pages <= 15: raise ValueError('Le rapport doit compter de 1 à 15 pages.')


def chemin_autorise(name):
    p=PurePosixPath(name)
    return (not p.is_absolute() and '..' not in p.parts and '\\' not in name and ':' not in name
            and not any(v in INTERDITS for v in p.parts)
            and not any(v.startswith('PLAN_') for v in p.parts)
            and not p.name.endswith(('.pyc','.bak','.backup','~')))


def verifier_archive(path):
    with zipfile.ZipFile(path) as z:
        if len(z.namelist())!=len(set(z.namelist())):raise ValueError('Noms dupliqués dans l’archive')
        for name in z.namelist():
            if not chemin_autorise(name): raise ValueError(f'Chemin interdit : {name}')
        if z.testzip() is not None: raise ValueError(f'Archive corrompue : {path.name}')


def adapter(data, equipe):
    text=data.decode('utf-8-sig')
    text=text.replace('EXX',equipe)
    # Les chemins de session sont supprimés dans les copies, jamais dans les sources.
    text=re.sub(re.escape(str(Path.home().parent)) + r'/[A-Za-z0-9_.-]+/[^\s`\"\'<>]*', '[chemin local]', text)
    return text.encode('utf-8-sig' if data.startswith(b'\xef\xbb\xbf') else 'utf-8')


def ajouter(z, fichier, root, equipe, original=False):
    nom=fichier.relative_to(root).as_posix()
    if not original: nom=nom.replace('EXX',equipe)
    if not chemin_autorise(nom): raise ValueError(nom)
    data=fichier.read_bytes()
    if not original and fichier.suffix in TEXTES: data=adapter(data,equipe)
    # Aucun chemin utilisateur ne doit sortir, même dans les sources tabulaires.
    if fichier.suffix in TEXTES and re.search((re.escape(str(Path.home().parent))+r'/[A-Za-z0-9_.-]+/').encode(),data):
        raise ValueError(f'Chemin personnel détecté : {nom}')
    info=zipfile.ZipInfo(nom,date_time=(2026,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
    info.external_attr=0o644 << 16
    z.writestr(info,data)


def notice_archive(z, dossier, contenu):
    z.writestr(f'{dossier}/LISEZ-MOI.md',contenu)


def sources_minimales(root):
    pack=root/'01_collecte/datapack_extrait/DataPack_DCB_2026'
    motifs=['CNS529_*.csv','CNS530_*.csv','INSD_RGPH2019_Vol4_*.csv','Rapport_statistique_mensuel_ESU_Février_2026.csv',
            'CNS529_*.pdf','CNS530_*.pdf','INSD_RGPH2019_Vol4_*.pdf','Rapport_statistique_mensuel_ESU_Février_2026.pdf']
    files=[]
    for motif in motifs:
        found=list(pack.rglob(motif))
        if len(found)!=1: raise ValueError(f'Source unique attendue {motif} : {len(found)}')
        files.extend(found)
    return files


def version_fichier_autorisee(path,version):
    m=re.search(r'_v(\d+)\.',Path(path).name,re.IGNORECASE)
    return m is None or int(m[1])<=version


def produits_etape(dossier,version):
    files=[]
    for f in sorted(Path(dossier).glob('*')):
        if f.is_file() and f.suffix in TEXTES|{'.png'} and version_fichier_autorisee(f,version):files.append(f)
    return files


def construire(root=RACINE,equipe='EXX',sortie='livraison_v1',version=1):
    from pypdf import PdfReader
    if type(version) is not int or version not in (1,2,3,4,5):raise ValueError('version attendue : 1, 2, 3, 4 ou 5')
    equipe=valider_equipe(equipe); root=Path(root)
    output=Path(sortie); output=output if output.is_absolute() else root/output
    if (output/'MANIFESTE.json').exists() and json.loads((output/'MANIFESTE.json').read_text()).get('version')!=version:
        raise ValueError('La version du dossier existant est différente ; utiliser un autre dossier de sortie.')
    output.mkdir(parents=True,exist_ok=True)
    complement=None
    if version==3:
        from controle_humain import preparer
        preparer(root)
    elif version>=4:
        from controle_humain import preparer_version4
        preparer_version4(root)
    declaration=declaration_ia(root,version)
    if version>=2:
        from complements_livraison import preparer_synthese, fichiers_complements
        preparer_synthese(root);complement=fichiers_complements(root)
    # Dossier dédié seulement : ne jamais supprimer silencieusement un autre travail.
    attendus={f'{equipe}_{etape}_D3_{role}_donnees_v{version}.zip' for _,etape,role in ETAPES}
    attendus|={f'{equipe}_documentation_D3_code_v{version}.zip',f'{equipe}_documentation_D3_rapport_v{version}.pdf',f'{equipe}_documentation_D3_notice_v{version}.md',f'{equipe}_documentation_D3_usage-IA_v{version}.md','MANIFESTE.json'}
    if version>=2:attendus.add(f'{equipe}_01-collecte_D3_engineer_sources-complementaires_v{version}.zip')
    inconnus={p.name for p in output.iterdir()}-attendus
    if inconnus: raise ValueError(f'Le dossier de sortie contient des fichiers étrangers : {sorted(inconnus)}')
    md,pdf=generer_rapport(root,equipe,version=version)
    pages=len(PdfReader(pdf).pages)
    records=[]
    def record(path,cat): records.append({'path':path.name,'category':cat})
    for dossier,etape,role in ETAPES:
        path=output/f'{equipe}_{etape}_D3_{role}_donnees_v{version}.zip'
        with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
            for f in produits_etape(root/dossier,version):ajouter(z,f,root,equipe)
            if complement:
                for f in complement[dossier]:
                    if f.parent!=root/dossier:ajouter(z,f,root,equipe)
            if dossier=='01_collecte':
                for f in sorted((root/'00_sources').iterdir()):
                    if f.is_file() and f.suffix in {'.pdf','.xlsx'}: ajouter(z,f,root,equipe,original=True)
                for f in sources_minimales(root): ajouter(z,f,root,equipe,original=True)
                ajouter(z,root/'01_collecte/limites_administratives/bfa_admin2.geojson',root,equipe,original=True)
            notice_archive(z,dossier,f'# Étape {etape}\n\nExtraire à la racine commune aux {7 if version>=2 else 6} archives. Les chemins recréent {dossier}/ sans dossier redondant.\nLes produits et leurs traces sont fournis ici. La collecte fournit les sources minimales originales au chemin attendu.\nReproduction : python code/00_tout_relancer.py ; voir LISEZ-MOI.md à la racine de l’archive code.\n')
        verifier_archive(path);record(path,f'donnees_{etape}')
    if complement:
        supp=output/f'{equipe}_01-collecte_D3_engineer_sources-complementaires_v{version}.zip'
        with zipfile.ZipFile(supp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
            for f in complement['sources']:ajouter(z,f,root,equipe,original=True)
            notice_archive(z,'01_collecte/complements_web','Sources complémentaires : trois PDF régionaux et quatre réponses ODFA. Extraire avec les six autres ZIP à une même racine ; reproduction sans API : python code/12_verifier_complements.py. Les PDF et JSON originaux sont conservés ; les HTML, le catalogue global et les microdonnées individuelles sont exclus. Les autres sources mentionnées dans les registres de recherche ne sont pas nécessaires à cette sélection.\n')
        verifier_archive(supp);record(supp,'donnees_01-collecte')
    code=output/f'{equipe}_documentation_D3_code_v{version}.zip'
    with zipfile.ZipFile(code,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for dossier in ['code','tests','tableau_de_bord']:
            for f in sorted((root/dossier).rglob('*')):
                if f.is_file() and chemin_autorise(f.relative_to(root).as_posix()): ajouter(z,f,root,equipe)
        if complement:
            for f in complement['code']:ajouter(z,f,root,equipe)
        for f in [root/'LISEZ-MOI.md',root/'JOURNAL_IA.md',root/'CHANGELOG.md',*sorted(root.glob('requirements*.txt'))]: ajouter(z,f,root,equipe)
        for f in sorted((root/'documentation').rglob('*')):
            rel=f.relative_to(root).as_posix()
            if version>=4 and f.name.startswith('FICHE_CONTROLE_HUMAIN_v3.'):continue
            if f.is_file() and chemin_autorise(rel) and version_fichier_autorisee(f,version) and f.suffix in {'.md','.csv','.json'} and not f.name.startswith(('CONTRAT_','EXX_documentation_D3_rapport')):
                if re.search(r'_documentation_D3_rapport_v\d+\.md$',f.name):continue
                ajouter(z,f,root,equipe)
        # La version courante du rapport est toujours présente, y compris code EXX.
        ajouter(z,md,root,equipe)
        z.writestr('DECLARATION_IA.md','# Déclaration d’usage de l’IA\n\n'+declaration+'\n')
    verifier_archive(code);record(code,'code')
    pdf_copie=output/pdf.name; shutil.copyfile(pdf,pdf_copie);record(pdf_copie,'rapport_pdf')
    usage=output/f'{equipe}_documentation_D3_usage-IA_v{version}.md'
    usage.write_text('# Usage de l’intelligence artificielle\n\n'+declaration+'\n\nLe journal détaillé figure dans l’archive code. Les sources originales ne sont pas modifiées.\n',encoding='utf-8');record(usage,'usage_ia')
    notice=output/f'{equipe}_documentation_D3_notice_v{version}.md';record(notice,'notice')
    # Les tailles figurent dans la notice ; sa taille propre converge en quelques passes.
    notice.write_text('',encoding='utf-8')
    for _ in range(6):
        tableau='\n'.join(f'| {r["path"]} | {r["category"]} | {(output/r["path"]).stat().st_size} |' for r in records)
        value=f'''# Notice de livraison — Défi 3 V{version}

Pour consulter sans installation : extraire les sept ZIP à partir de V2 (six en V1) dans un même dossier, puis ouvrir tableau_de_bord/index.html. Aucun Python ni réseau n’est requis pour utiliser l’interface fournie.

{10 if version>=2 else 9} fichiers à déposer ; MANIFESTE.json est un contrôle voisin, à ne pas déposer.

| Fichier | Catégorie | Octets |
| --- | --- | ---: |
{tableau}

Rapport : {pages} pages. Chaque fichier < 50 000 000 octets ; total < 500 000 000.
Extraire les {7 if version>=2 else 6} ZIP ensemble. Installer `python -m pip install -r requirements.txt`, puis lancer `python code/00_tout_relancer.py`. Ouvrir `tableau_de_bord/index.html` hors ligne.
Tests : `python -m unittest discover -s tests -v` ; `node tests/test_moteur.js`.
{'Compléments : python code/12_verifier_complements.py ; nécessite Poppler (pdftotext), sans API. Les nouvelles sources restent hors du simulateur.' if version>=2 else ''}
Audit 09 facultatif : exige le Data Pack complet original, absent de cette livraison minimale. Le script 08 utilise le PDF ESU fourni.

Versions : V{version} désigne le rapport et les archives. Les noms internes _v1 identifient les calculs et tables historiques inchangés ; les ajouts V5 portent _v5. Les sources originales gardent leurs noms.
{'Contrôle humain : fiche de 20 lignes à remplir dans documentation/FICHE_CONTROLE_HUMAIN_v3.csv ; aucun contrôle de ces lignes n’est encore déclaré réalisé.' if version==3 else ''}

{'Contrôle humain : vingt lignes documentées, cent valeurs concordantes ; fiche documentation/FICHE_CONTROLE_HUMAIN_v4.csv. Préfixe EXX anonyme choisi : aucun code officiel affiché dans l’espace d’équipe.' if version>=4 else ''}

Déclaration IA : {declaration}
'''
        previous=notice.stat().st_size;notice.write_text(value,encoding='utf-8')
        if notice.stat().st_size==previous: break
    for r in records:
        p=output/r['path'];r['size']=p.stat().st_size;r['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
    if len(records)!=(10 if version>=2 else 9): raise ValueError('Nombre de fichiers déposables inattendu.')
    valider_limites([r['size'] for r in records],pages)
    metadata=PdfReader(pdf).metadata
    if metadata.author: raise ValueError('Auteur PDF non vide.')
    if not 20<=len(declaration)<=2000: raise ValueError('Déclaration IA hors limites.')
    manifeste={'version':version,'equipe':equipe,'rapport_pages':pages,'total_bytes':sum(r['size'] for r in records),'fichiers_a_deposer':records,'manifest_non_deposable':True}
    (output/'MANIFESTE.json').write_text(json.dumps(manifeste,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'dossier':output.name,'fichiers':len(records),'pages':pages,'octets':manifeste['total_bytes']},ensure_ascii=False))
    return manifeste


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--equipe',default='EXX');parser.add_argument('--sortie',default='livraison_v1')
    parser.add_argument('--version',type=int,choices=[1,2,3,4,5],default=1)
    args=parser.parse_args(); construire(equipe=args.equipe,sortie=args.sortie,version=args.version)

if __name__=='__main__': main()
