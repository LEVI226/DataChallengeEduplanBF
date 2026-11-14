"""Rapport à sept parties : chiffres relus dans les CSV à chaque génération."""
from pathlib import Path
from html import escape
import pandas as pd

DECLARATION_IA = (
    "Claude et Codex ont été utilisés pour explorer les sources, préparer et nettoyer les données, "
    "écrire et exécuter le code, vérifier les calculs et les documents, et rédiger les livrables. "
    "L'assistance IA à la préparation des données s'écarte de la consigne du guide et est déclarée. "
    "Les contrôles automatiques, lectures documentaires et revues assistées ne constituent ni une "
    "attestation humaine ni une validation de terrain. Le journal complet des usages et limites est "
    "fourni dans JOURNAL_IA.md de l'archive code."
)


def fmt(x, decimals=0):
    return f'{float(x):,.{decimals}f}'.replace(',', ' ').replace('.', ',')


def lire(root, dossier, fragment):
    paths = list((root/dossier).glob(f'*_{fragment}_v1.csv'))
    if len(paths) != 1:
        raise ValueError(f'Table unique attendue : {dossier}/{fragment}, {len(paths)} trouvée(s)')
    return pd.read_csv(paths[0])


def contenu(root):
    d = lire(root,'03_transformation','indicateurs-provinces-public')
    d = d[d.annee_scolaire == '2024-2025']
    sens = lire(root,'04_analyse','sensibilite-seuils')
    comp = lire(root,'04_analyse','repartition-comparaison-regles')
    proj = lire(root,'04_analyse','besoins-provinces-2030')
    back = lire(root,'04_analyse','projection-test-sur-le-passe').groupby('methode').erreur_moyenne_pct.mean()
    proof = lire(root,'04_analyse','preuve-optimalite-egalisation')
    pop = lire(root,'02_nettoyage','population-provinces-6-11-insd')
    controles = lire(root,'02_nettoyage','controles-demographie-insd')
    from libelles import SCENARIOS
    blocks = []
    def h(s): blocks.append(('h',s))
    def p(s): blocks.append(('p',s))
    def table(headers, rows): blocks.append(('table', [headers]+rows))
    def page(): blocks.append(('page',None))
    def fig(fragment, caption):
        paths=list((root/'05_interpretation').glob(f'*_{fragment}_v1.png'))
        if len(paths)!=1: raise ValueError(fragment)
        blocks.append(('fig',(paths[0],caption)))
    h('1. Le défi')
    p('Répartir les maîtres et les salles du primaire public : rendre visible l’arbitrage')
    p('Data Challenge Burkina — édition Éducation 2026 — Défi 3 — Version finale V1')
    p('Comment répartir des moyens supplémentaires entre provinces lorsque l’objectif est de réduire les disparités de charge ? La solution compare trois règles pour un même nombre de maîtres ou de salles, puis permet de modifier les hypothèses dans un simulateur local.')
    p(f'La référence porte sur {len(d)} anciennes provinces et {fmt(d.eleves.sum())} élèves inscrits dans le primaire public en 2024–2025. Le nombre d’inscrits est une observation administrative ; il ne représente pas tous les enfants en âge de fréquenter le primaire.')
    p('Le décideur visé prépare les affectations et la programmation des infrastructures. Il dispose d’un diagnostic, de scénarios conditionnels et d’une répartition détaillée. Les quantités sont des unités physiques ; aucun coût ni budget monétaire n’est estimé.')
    p('La note d’intention visait une optimisation communale avec programmation entière. Les données nationales comparables conduisent ici à une maille provinciale. Le choix retenu rend explicite l’objectif optimisé et ses limites opérationnelles.')
    p('Lecture : données et préparation ; méthode ; résultats observés et scénarios ; réponse au défi ; reproduction et sources. Les graphiques et toutes les valeurs calculées sont issus des tables livrées.')
    page(); h('2. Les données')
    table(['Source / producteur','Période et maille','Usage'],[
        ['Classeur du challenge / DGESS-MENAPLN','2015–2016 à 2024–2025 ; régions','Séries des effectifs et écoles'],
        ['Annuaires primaire CNS529 et CNS530 / DGESS','2023–2024 et 2024–2025 ; provinces','Élèves, maîtres chargés de cours, salles'],
        ['RGPH2019, volume 4 / INSD, janvier 2023','Projections 2025 et 2030 ; provinces','Population 6–11 ans et facteurs de croissance'],
        ['Rapport ESU février 2026 / DGESS-MEBAPLN','Au 28 février 2026 ; nouveau découpage','Contexte éducatif daté'],
        ['Limites administratives COD-AB / Data Pack','Découpage depuis août 2025','Carte reliée aux anciennes provinces']])
    p('Les maîtres chargés de cours ne couvrent pas tout le personnel enseignant. Les salles sont des stocks déclarés ; leur état n’est pas intégré aux calculs de répartition présentés. Les séries régionales offrent dix observations annuelles ; les annuaires provinciaux exploités en offrent deux.')
    p(f'L’INSD projette {fmt(pop[pop.annee==2025].ensemble.sum())} enfants de 6–11 ans en 2025 et {fmt(pop[pop.annee==2030].ensemble.sum())} en 2030 dans le périmètre retenu. Ces populations ne sont pas des inscriptions. Le modèle maintient ou fait varier le rapport inscrits publics/population, qui n’est pas un taux net de scolarisation.')
    p('Les annexes ESU ne distinguent pas public et privé. Leur observation 2025–2026 ne corrige ni ne complète arithmétiquement les effectifs publics 2024–2025. Les réouvertures sont celles intervenues depuis le début de la crise et restant fonctionnelles à la date du rapport, pas le flux du seul mois.')
    p('Le nouveau découpage cartographique est ramené aux anciennes provinces. Les composantes de Soum et Tapoa sont réunies, sans compter deux fois les effectifs ; la géométrie reste une représentation de correspondance administrative.')
    page(); h('3. La préparation')
    table(['Traitement','Règle et trace'],[
        ['Extraction du tableau I.1','Lecture des lignes du CSV de PDF, report des territoires, sélection du public'],
        ['Formats et libellés','Espaces numériques et virgules normalisés ; noms et années harmonisés'],
        ['Séries régionales','Passage du format large au format long ; rapprochement aux annuaires'],
        ['Projections INSD','Lecture des groupes 6–11 ans H/F/ensemble, années et provinces ; document/page/ligne conservés'],
        ['ESU et carte','Correspondance administrative ; agrégation seulement si toutes les composantes sont connues']])
    p('Les totaux publiés sont conservés comme points de contrôle. Public + privé doit égaler total ; les provinces doivent retrouver leurs régions et le national ; les ratios sont recalculés ; le classeur et les annuaires sont rapprochés sur leurs années communes. Les scripts interrompent la chaîne lorsque leurs contrôles obligatoires échouent.')
    p(f'L’extraction INSD conserve {len(pop)} observations province-année et {len(controles)} contrôles documentés. Elle vérifie les sexes, les agrégats et la couverture des provinces. Le volume publié en 2023 repose sur le recensement de 2019 : ce décalage est conservé dans l’interprétation. La structure par sexe et âge des provinces est supposée identique à celle de leur région ; ces projections ne constituent pas un scénario des déplacements récents.')
    p('Aucune absence ESU n’est transformée implicitement en zéro. Les valeurs manquantes et les couvertures partielles restent identifiées ; un zéro explicite est conservé. Les rapprochements automatiques et la vérification du PDF par le script 08 ont une trace séparée.')
    p('L’audit documentaire a confirmé des sources démographiques utilisables et repéré des possibilités communales partielles. Les anomalies détaillées restent dans les preuves d’audit ; les annuaires régionaux non harmonisés ne sont pas incorporés aux calculs provinciaux présentés.')
    p('Les sources originales restent dans leur format et leur chemin de collecte. Les archives fournissent les entrées minimales de la chaîne courante ; le Data Pack complet n’est pas redistribué dans cette livraison.')
    page(); h('4. La méthode')
    p('Pour une province : ratio = inscrits / stock ; besoin au seuil = plafond(inscrits / seuil) ; unités à ajouter = maximum(0, besoin − stock). Chaque calcul est effectué séparément pour les maîtres et pour les salles.')
    p('Le seuil de 50 élèves par maître est une hypothèse de simulation, sans norme officielle établie ici. Le seuil par salle est distinct, fixé également à 50 pour la comparaison. Le simulateur permet de modifier les deux seuils et les moyens séparément.')
    table(['Règle','Affectation des unités entières'],[
        ['Prorata des élèves','Selon les parts d’inscrits ; restes distribués de façon déterministe'],
        ['Déficit d’abord','Une unité à la province dont le manque au seuil est le plus grand'],
        ['Égalisation','Une unité à la province dont le ratio courant est le plus élevé']])
    p('Les égalités sont départagées par un ordre stable. Aucun stock n’est retiré, toutes les unités sont affectées et les provinces restent éligibles. Maîtres et salles sont alloués indépendamment, sans contrainte commune de site ou d’occupation.')
    pr=proof[(proof.ressource=='maitres')&(proof.budget==2000)].iloc[0]
    p(f'Optimalité précise : avec une seule ressource, des stocks positifs, des élèves fixes, des ajouts entiers non négatifs, toutes les provinces éligibles et aucun couplage ni coût différencié, l’égalisation minimise le maximum des ratios. Pour {fmt(pr.budget)} maîtres, le maximum atteint {fmt(pr.pire_ratio_obtenu,4)} ; atteindre ce plafond exige {fmt(pr.unites_pour_ce_plafond)} unités et tout plafond strictement inférieur en exige au moins {fmt(pr.unites_pour_un_plafond_plus_bas)}. Cette preuve ne vaut pas pour un objectif de coût ou d’accessibilité.')
    p('INSD : élèves 2030 = élèves publics de référence × (population 6–11 ans 2030 / population 6–11 ans 2025) × facteur de rapport. Le facteur vaut 0,9, 1 ou 1,1. Le rattachement 2025 ↔ année scolaire 2024–2025 et 2030 ↔ 2029–2030 est une hypothèse. Les trois scénarios historiques sont conservés : tendance régionale, croissance nationale, retour au maximum régional.')
    p('Les stocks de maîtres et salles restent constants : aucun départ, retraite ou perte de salle n’est prévu. Les scénarios ne forment ni une prévision validée ni un intervalle de confiance.')
    page(); h('5. Les résultats')
    p(f'En 2024–2025, {fmt((d.eleves_par_maitre>50).sum())} provinces sur {len(d)} dépassent 50 élèves par maître. Atteindre ce seuil partout demanderait {fmt(d.deficit_maitres.sum())} maîtres et {fmt(d.deficit_salles.sum())} salles supplémentaires. Les stocks déclarés sont de {fmt(d.maitres.sum())} maîtres et {fmt(d.salles.sum())} salles.')
    worst=d.sort_values('eleves_par_maitre',ascending=False).head(5)
    p('Provinces aux ratios par maître les plus élevés : '+', '.join(f'{r.province.title()} ({fmt(r.eleves_par_maitre,1)})' for r in worst.itertuples())+'.')
    p(f'La marge comptable des provinces sous le seuil représente {fmt(d.marge_comptable_maitres.sum())} unités. Elle ne constitue pas une réserve de personnels transférables. L’écart entre maîtres et salles est un signal comptable ; il ne garantit aucune occupation effective des classes.')
    fig('carte-eleves-par-maitre','Figure 1 — Élèves par maître chargé de cours, primaire public 2024–2025. Source : DGESS, CNS530, tableau I.1 ; correspondance COD-AB.')
    table(['Seuil simulé','Provinces au-dessus','Maîtres à ajouter'],[[str(r.seuil),fmt(r.provinces_au_dessus),fmt(r.deficit_total)] for r in sens[sens.ressource=='maitres'].itertuples()])
    page(); p('Résultats — comparer un même nombre de moyens')
    sel=comp[(comp.ressource=='maitres')&comp.budget.isin([0,2000])]
    labels={'situation actuelle':'Situation actuelle','proportionnelle':'Prorata','deficit_d_abord':'Déficit d’abord','egalisation':'Égalisation'}
    table(['Règle / 2 000 maîtres','Pire ratio','Écart type','Provinces > 50','Déficit restant'],[[labels[r.regle],fmt(r.ratio_max,1),fmt(r.ecart_type_ratios,1),fmt(r.provinces_au_dessus_norme),fmt(r.deficit_restant)] for r in sel.itertuples()])
    pro=sel[sel.regle=='proportionnelle'].iloc[0]; ega=sel[sel.regle=='egalisation'].iloc[0]
    p(f'Le prorata laisse {fmt(pro.provinces_au_dessus_norme)} provinces au-dessus du seuil contre {fmt(ega.provinces_au_dessus_norme)} pour l’égalisation, mais son pire ratio reste {fmt(pro.ratio_max,1)} contre {fmt(ega.ratio_max,1)}. Le prorata favorise le franchissement du seuil par des provinces proches de celui-ci ; l’égalisation réduit d’abord les charges extrêmes.')
    p(f'Le prorata affecte {fmt(pro.unites_donnees_sous_la_norme)} postes à des provinces déjà sous le seuil dans la situation initiale. Les règles ciblant les déficits laissent le même déficit total dans cet exemple. Aucun classement unique des règles ne remplace le choix d’objectif du décideur.')
    fig('comparaison-regles','Figure 2 — Comparaisons des trois règles selon les moyens ajoutés. Source : tables de répartition, script 05 ; élèves et stocks DGESS 2024–2025.')
    p('Le tableau de bord hors ligne applique les calculs sur toutes les provinces ; un filtre de région ne change que l’affichage. Les exports permettent de conserver scénario, seuils, stocks, ajouts et ratios.')
    page(); p('Résultats — horizon 2029–2030 et contexte ESU')
    sums=proj.groupby('scenario')[['eleves_projetes','maitres_a_ajouter','salles_a_ajouter']].sum()
    order=['demographie_insd_moins10','demographie_insd','demographie_insd_plus10','tendance_longue','croissance_nationale','retour_au_pic']
    table(['Scénario','Inscrits simulés','Maîtres +','Salles +'],[[SCENARIOS[s][0],*[fmt(sums.loc[s,c]) for c in sums.columns]] for s in order])
    p('Les écarts entre scénarios mesurent une dépendance aux hypothèses. Ils ne donnent pas une probabilité d’atteinte des effectifs. La conservation des stocks exclut les besoins de remplacement et les dégradations futures.')
    p('Validation historique : moyenne des erreurs régionales absolues en pourcentage, sur les origines disponibles à horizon trois ans : '+', '.join(f'{SCENARIOS[s][0] if s in SCENARIOS else "dernier niveau connu"} : {fmt(back[s],1)} %' for s in ['tendance_longue','croissance_nationale','retour_au_pic','dernier_niveau'])+'. Aucune des trois méthodes historiques ne bat la référence naïve en moyenne. Ce test ne valide pas les scénarios INSD, qui relèvent d’une autre hypothèse.')
    esu=lire(root,'03_transformation','contexte-esu-provinces')
    p('Le contexte ESU au 28 février 2026 est présenté côte à côte dans les tables, avec statuts de renseignement et traçabilité des annexes. Les élèves déplacés ne sont pas ajoutés aux inscriptions de l’annuaire. Les structures rouvertes ou délocalisées ne constituent pas une mesure des sites accessibles pour une affectation.')
    fig('besoins-2030','Figure 3 — Besoins additionnels des scénarios à stocks constants, seuils simulés. Source : tables de projection, script 04 ; DGESS et INSD, volume 4.')
    page(); h('6. La réponse au défi')
    p('La solution rend une décision provinciale explicite et révisable : constater les charges, fixer un objectif, comparer des règles à moyens identiques et exporter une proposition détaillée. L’INSD enrichit désormais les scénarios provinciaux ; le simulateur local rend leurs hypothèses visibles et modifiables.')
    p('Si le décideur choisit de réduire la pire charge observée, l’égalisation répond à cet objectif dans le modèle. S’il privilégie le nombre de provinces franchissant un seuil, l’exemple montre que le prorata peut obtenir un meilleur résultat sur ce critère. La préférence politique et les contraintes de terrain doivent donc précéder le choix final.')
    p('Une affectation opérationnelle reste conditionnelle : vérifier les écoles et salles utilisables, les personnels disponibles, l’accès, la sécurité et l’accueil. Une baisse des inscriptions peut provenir de fermetures ou déplacements ; un ratio favorable ne prouve pas un besoin faible.')
    p('Les limites déterminantes sont la maille provinciale, les millésimes distincts, l’absence de coûts, de mobilité des personnels et de contraintes conjointes maîtres–salles. Le signal ESU informe la discussion sans déclencher une exclusion automatique. L’accessibilité n’est pas établie par les sources exploitées.')
    p('Les prolongements utiles sont une collecte communale comparable, la confirmation des sites, la prise en compte des remplacements et des coûts, puis un modèle conjoint avec contraintes. Ils demandent des données nouvelles et une validation métier ; ils ne sont pas implicitement résolus par le prototype.')
    p('La livraison fournit des éléments vérifiables : données par étape, scripts, tests, preuves de source, rapport et tableau de bord utilisable hors ligne. Les vérifications assistées documentent les résultats calculés, sans constituer une validation humaine du dossier ou une certification d’affectation.')
    page(); h('7. La reproduction')
    p('Extraire les six ZIP dans un même dossier : ils recréent 00_sources, 01_collecte à 05_interpretation, code, tests, documentation et tableau_de_bord. Installer Python 3.12 ou supérieur (version testée : 3.14.7) et les dépendances épinglées : python -m pip install -r requirements.txt ; puis python code/00_tout_relancer.py. La chaîne 01→07→10 reconstruit les tables, figures et données du simulateur.')
    p('Ouvrir tableau_de_bord/index.html directement dans un navigateur, sans serveur ni réseau. Vérifier les tests avec python -m unittest discover -s tests -v et node tests/test_moteur.js. Pour la livraison : python code/11_preparer_livraison.py --equipe EXX --sortie livraison_v1 ; remplacer EXX par le code anonyme attribué, par exemple E07.')
    p('Le script 08 vérifie facultativement les valeurs ESU dans le PDF fourni. Le script 09 est un audit facultatif du Data Pack complet original : il nécessite ce pack complet et ne peut pas être reproduit avec les seules sources minimales livrées. Les preuves d’audit déjà produites restent consultables.')
    p('Sources et références précises')
    p('DGESS / MENAPLN : Données statistiques du préscolaire et du primaire 2016–2025, classeur du challenge, feuilles effectifs et écoles. DGESS : Annuaire statistique de l’enseignement primaire 2023–2024 (CNS529) et 2024–2025 (CNS530), tableau I.1, PDF p. 12–16.')
    p(f'INSD : RGPH 2019, volume 4, Projections démographiques 2020–2035, janvier 2023 ; tableaux provinciaux de groupes d’âges 6–11 ans, PDF p. {int(pop.page.min())}–{int(pop.page.max())} pour les lignes 2025/2030 exploitées. Chaque valeur livrée conserve document, page et ligne.')
    p('DGESS / MEBAPLN : Rapport statistique mensuel ESU de février 2026, publié en mars 2026, observation au 28 février 2026 ; annexes 1, 2 et 4, PDF p. 15–20. COD-AB : limites administratives du Burkina Faso, couche admin2 du Data Pack, correspondance documentée vers les anciennes provinces.')
    p('Usage de l’intelligence artificielle — déclaration')
    p(DECLARATION_IA)
    return blocks


def generer_rapport(root, equipe='EXX'):
    """Même contenu pour Markdown et PDF ; pagination contrôlée à neuf pages."""
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, KeepTogether
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.enums import TA_LEFT
    import matplotlib
    font=Path(matplotlib.get_data_path())/'fonts/ttf'
    for name,file in [('DejaVu','DejaVuSans.ttf'),('DejaVuBold','DejaVuSans-Bold.ttf')]:
        if name not in pdfmetrics.getRegisteredFontNames(): pdfmetrics.registerFont(TTFont(name,str(font/file)))
    pdfmetrics.registerFontFamily('DejaVu',normal='DejaVu',bold='DejaVuBold')
    docs=root/'documentation'; docs.mkdir(exist_ok=True)
    md=docs/f'{equipe}_documentation_D3_rapport_v1.md'; pdf=md.with_suffix('.pdf')
    styles=getSampleStyleSheet()
    body=ParagraphStyle('Corps',fontName='DejaVu',fontSize=9.7,leading=14.2,spaceAfter=11,textColor=colors.HexColor('#22313b'))
    heading=ParagraphStyle('Partie',parent=body,fontName='DejaVuBold',fontSize=20,leading=25,spaceAfter=23,textColor=colors.HexColor('#12334b'))
    cell=ParagraphStyle('Cellule',parent=body,fontSize=8,leading=11,spaceAfter=0)
    caption=ParagraphStyle('Legende',parent=body,fontSize=8,leading=11,spaceAfter=12)
    story=[]; markdown=['# Répartir les maîtres et les salles du primaire public\n']
    for kind,value in contenu(root):
        if kind=='page': story.append(PageBreak()); continue
        if kind in ('p','h'):
            story.append(Paragraph(escape(value),heading if kind=='h' else body))
            markdown.append(('## ' if kind=='h' else '')+value+'\n')
        elif kind=='table':
            rows=[[Paragraph(escape(str(c)),cell) for c in row] for row in value]
            widths=[480/len(value[0])]*len(value[0])
            t=Table(rows,colWidths=widths,hAlign='LEFT',repeatRows=1)
            t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e4ecee')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.6,colors.HexColor('#6b868d')),('BOTTOMPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),8),('LINEBELOW',(0,1),(-1,-1),.25,colors.HexColor('#ccd7dc'))]))
            story.extend([t,Spacer(1,14)])
            markdown.extend(['| '+' | '.join(map(str,value[0]))+' |','| '+' | '.join(['---']*len(value[0]))+' |'])
            markdown.extend('| '+' | '.join(map(str,r))+' |' for r in value[1:]); markdown.append('')
        elif kind=='fig':
            path,cap=value
            img=Image(str(path)); factor=min(480/img.imageWidth,195/img.imageHeight)
            img.drawWidth=img.imageWidth*factor;img.drawHeight=img.imageHeight*factor
            story.append(KeepTogether([img,Spacer(1,6),Paragraph(escape(cap),caption)]))
            markdown.append(f'![{cap}](../05_interpretation/{path.name})\n')
    md.write_text('\n'.join(markdown),encoding='utf-8')
    def footer(canvas,doc):
        canvas.saveState(); canvas.setFont('DejaVu',8);canvas.setFillColor(colors.HexColor('#647680'))
        canvas.drawString(55,30,'Défi 3 · Primaire public · Rapport V1');canvas.drawRightString(535,30,str(doc.page));canvas.restoreState()
    doc=SimpleDocTemplate(str(pdf),pagesize=(595.28,841.89),rightMargin=55,leftMargin=55,topMargin=48,bottomMargin=48,title='Répartition provinciale des maîtres et salles — Défi 3',author='',creator='Générateur du rapport D3',subject='Simulation du primaire public')
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    return md,pdf
