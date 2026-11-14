"""Présentation V3 pour le jury : résumé visuel, arbitrage et limites regroupées."""
from pathlib import Path
from rapport_livraison import lire,fmt,DECLARATION_IA,declaration_ia

def contenu_jury(root,base,version=3):
    pages=[[]]
    for kind,value in base:
        if kind=='page':pages.append([])
        else:pages[-1].append((kind,value))
    d=lire(root,'03_transformation','indicateurs-provinces-public');d=d[d.annee_scolaire=='2024-2025']
    comp=lire(root,'04_analyse','repartition-comparaison-regles')
    sel=comp[(comp.ressource=='maitres')&(comp.budget==2000)]
    ega=sel[sel.regle=='egalisation'].iloc[0];pro=sel[sel.regle=='proportionnelle'].iloc[0]
    initial=comp[(comp.ressource=='maitres')&(comp.budget==0)].iloc[0]
    carte=next((Path(root)/'05_interpretation').glob('*_cartes-avant-apres_v1.png'))
    pages[0]=[
        ('h','1. Le défi'),
        ('p','Mieux affecter les maîtres et les salles du primaire public'),
        ('p','Data Challenge Burkina · Défi 3 · Rapport V3'),
        ('kpis',[
            ['Provinces au-dessus du seuil',f'{fmt(initial.provinces_au_dessus_norme)} / {len(d)}','Situation observée 2024–2025'],
            ['Pire ratio provincial',f'{fmt(initial.ratio_max)} → {fmt(ega.ratio_max)}','Élèves par maître chargé de cours'],
            ['Moyens ajoutés dans la simulation','2 000','Maîtres, répartis entre les provinces']]),
        ('p','À nombre de postes égal, la règle d’affectation change fortement les disparités. L’égalisation concentre les ajouts sur les charges extrêmes et ramène le pire ratio provincial de '+fmt(initial.ratio_max,1)+' à '+fmt(ega.ratio_max,1)+' élèves par maître.'),
        ('fig',(carte,'Figure 1 — Situation observée, puis deux répartitions de 2 000 maîtres : prorata et égalisation. Primaire public 2024–2025 ; DGESS CNS530 et calculs du modèle. Même échelle de couleurs.')),
        ('p',f'L’arbitrage à décider : le prorata laisse {fmt(pro.provinces_au_dessus_norme)} provinces au-dessus de 50 élèves par maître, contre {fmt(ega.provinces_au_dessus_norme)} pour l’égalisation ; son pire ratio reste {fmt(pro.ratio_max,1)}. Le choix dépend de l’objectif : réduire les charges extrêmes ou faire franchir le seuil à davantage de provinces.'),
        ('p','L’outil livré permet au décideur de modifier les moyens, comparer trois règles, examiner les provinces et exporter la répartition. Il s’ouvre dans un navigateur, sans installation ni connexion.'),
        ('p','Cadre de lecture : 45 anciennes provinces, inscriptions du primaire public, seuil exploratoire de 50 élèves par maître. Les résultats présentés sont des simulations à stocks existants conservés ; les limites et conditions de mise en œuvre sont regroupées en partie 6.')]
    # Les audits occupent un paragraphe dans la préparation ; les preuves restent dans les CSV.
    prep=[]
    for k,v in pages[2]:
        if k=='p' and v.startswith('L’extraction INSD conserve'):
            v='L’extraction INSD conserve 90 observations province-année, avec leurs sexes, agrégats, document, page et ligne. Les deux contrôles démographiques et la couverture des 45 provinces sont vérifiés.'
        elif k=='p' and v.startswith('L’audit documentaire a confirmé'):
            v='Rapprochement des publications : 39/39 comparaisons régionales ODFA 2024 / DGESS 2023–2024 concordent sur écoles, salles et tous enseignants. Les tableaux communaux Centre-Est et Est fournissent 1 005 cellules pour 57 communes et leurs totaux ; 622 contrôles sont conformes, 21 signalent des incohérences publiées et deux restent non vérifiables. La case source vide de Bissiga est conservée. Les CSV donnent les pages et les trois divergences régionales ; la DGESS reste la référence du modèle national.'
        prep.append((k,v))
    pages[2]=prep
    # Quatrième figure : la carte déjà présente devient un complément du résumé.
    for i,(k,v) in enumerate(pages[4]):
        if k=='fig':pages[4][i]=(k,(v[0],v[1].replace('Figure 1','Figure 2')))
    for i,(k,v) in enumerate(pages[5]):
        if k=='fig':pages[5][i]=(k,(v[0],v[1].replace('Figure 2','Figure 3')))
    for i,(k,v) in enumerate(pages[6]):
        if k=='fig':pages[6][i]=(k,(v[0],v[1].replace('Figure 3','Figure 4')))
    # Les réserves transversales vont dans la réponse au défi ; hypothèses locales restent visibles.
    pages[3]=[(k,v) for k,v in pages[3] if not (k=='p' and v.startswith('Les stocks de maîtres et salles restent constants'))]
    pages[7]=[
        ('h','6. La réponse au défi'),
        ('p','La solution transforme des statistiques dispersées en une proposition d’affectation explicite : diagnostic provincial, règles comparées à moyens identiques, carte avant/après et export détaillé. L’apport central est de rendre l’arbitrage mesurable et reproductible.'),
        ('p','Utilisation proposée : fixer le nombre de postes et de salles, choisir l’objectif, comparer les trois répartitions, puis examiner les territoires concernés avec les services locaux. Le simulateur calcule instantanément les effets dans le modèle ; le fichier exporté conserve les paramètres et les hypothèses.'),
        ('p','Apport communal : les 57 communes documentent écoles, salles, élèves, enseignants et fermetures pour insécurité en 2023–2024. Elles enrichissent l’examen local sans modifier les allocations nationales 2024–2025. Exemple d’alerte publié : 64 écoles fermées dans les trois communes de la Kompienga, contre 36 au récapitulatif provincial. Les deux valeurs restent signalées ; aucun statut actuel de sécurité n’en est déduit.'),
        ('table',[
            ['Limite','Conséquence pour la décision'],
            ['Seuil de 50 exploratoire ; unités physiques','Comparer les sensibilités ; aucun coût ou budget FCFA estimé'],
            ['Stocks et inscriptions administratifs','La présence effective des maîtres et l’état des salles demandent un examen local'],
            ['Allocations provinciales, ressources séparées','Coûts, mobilité, disponibilité et couplage maître–salle ne sont pas optimisés'],
            ['Scénarios 2030 à stocks constants','Pas de retraites, remplacements ni dégradations futurs ; ce ne sont pas des intervalles de confiance'],
            ['Millésimes et géographies distincts','ESU 2026 et fermetures 2023–2024 restent des contextes datés ; aucune addition aux inscriptions'],
            ['Préparation et vérification assistées par IA','Usages déclarés ; contrôle humain de lignes sources encore à effectuer']]),
        ('p','Les priorités de mise en œuvre sont la confirmation des sites et des personnels, puis l’ajout de coûts et de contraintes conjointes. Les scénarios INSD reposent sur les projections RGPH2019 publiées en 2023, une structure par sexe/âge provinciale supposée régionale et un rattachement explicite des années civiles aux années scolaires ; les déplacements récents ne sont pas modélisés.'),
        ('p','Les neuf alertes historiques ODFA restent non résolues. Les concordances récentes peuvent refléter la même collecte DGESS ; elles vérifient la publication et l’extraction, pas des collectes indépendantes. La fiche de contrôle humain fournie doit être remplie avant toute déclaration de vérification humaine de ces lignes.')]
    last=[]
    for k,v in pages[8]:
        if k=='p':
            v=v.replace('Extraire les six ZIP','Extraire les sept ZIP').replace('python code/11_preparer_livraison.py --equipe EXX --sortie livraison_v1','python code/11_preparer_livraison.py --equipe EXX --version 3 --sortie livraison_v3')
        if k=='p' and v.startswith('Extraire les sept ZIP'):
            v='Recalculer : installer Python 3.12 ou supérieur et les dépendances épinglées avec python -m pip install -r requirements.txt ; puis lancer python code/00_tout_relancer.py. La chaîne 01→07→10 reconstruit tables, figures et données du simulateur.'
        elif k=='p' and v.startswith('Ouvrir tableau_de_bord'):
            v='Tests : python -m unittest discover -s tests -v ; node tests/test_moteur.js. Livraison : python code/11_preparer_livraison.py --equipe EXX --version 3 --sortie livraison_v3. Remplacer EXX uniquement par le code anonyme attribué.'
        last.append((k,v))
    last.insert(1,('p','Consulter sans installation : extraire les sept ZIP dans un même dossier, puis ouvrir tableau_de_bord/index.html dans un navigateur. Aucun Python, serveur, compte ou accès réseau n’est nécessaire pour utiliser l’interface fournie.'))
    idx=next(i for i,b in enumerate(last) if b[0]=='p' and b[1].startswith('Le script 08'))
    last.insert(idx,('p','Reproduire les compléments : installer Poppler (pdftotext), puis lancer python code/12_verifier_complements.py, sans API. La notice distingue la version V3 de la livraison et les sorties de calcul _v1 inchangées. Les dépendances épinglées ont été testées sur macOS avec Python 3.14.7 ; Windows et Linux n’ont pas été testés.'))
    last.insert(idx+1,('p','Compléments : INSD, annuaires régionaux 2024 Centre-Est et Est, éditions décembre 2025, observations 2023–2024 ; ODFA, séries extraites le 14 novembre 2026 ; CNS529, tableau IV.1.3, PDF p. 206–212 pour tous les enseignants. Registres et CSV livrés conservent URL, périodes et pages.'))
    pages[8]=last
    if version==4:
        for i,page in enumerate(pages):
            for j,(kind,value) in enumerate(page):
                if kind=='p':
                    value=value.replace('Rapport V3','Rapport V4').replace('version V3','version V4').replace('--version 3 --sortie livraison_v3','--version 4 --sortie livraison_v4').replace('Remplacer EXX uniquement par le code anonyme attribué.','EXX est un préfixe anonyme choisi ; aucun code officiel n’est affiché dans l’espace d’équipe.')
                    if value==DECLARATION_IA:value=declaration_ia(root,4)
                    if value.startswith('Le script 08'):
                        value='Audit PDF ESU : python code/08_verifier_pdf_esu.py. Le script 09 audite le Data Pack complet et exige ce pack original, hors livraison minimale. Les preuves déjà produites restent consultables.'
                    value=value.replace('La fiche de contrôle humain fournie doit être remplie avant toute déclaration de vérification humaine de ces lignes.','Un participant (rôles Data Engineer / Data Architect) a communiqué ses lectures de vingt lignes des PDF DGESS ; l’assistant les a comparées aux tables : cent valeurs concordantes, fiche du 14 novembre 2026. Ce contrôle ciblé ne vaut pas validation exhaustive ni vérification de terrain.')
                    pages[i][j]=(kind,value)
                elif kind=='table':
                    pages[i][j]=(kind,[[str(cell).replace('Usages déclarés ; contrôle humain de lignes sources encore à effectuer','Usages déclarés ; lecture de vingt lignes par un participant et comparaison assistée, contrôle ciblé') for cell in row] for row in value])
    out=[]
    for i,page in enumerate(pages):
        if i:out.append(('page',None))
        out.extend(page)
    return out
