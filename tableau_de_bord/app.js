/* Interface locale sans dépendance réseau. */
(function() {
 'use strict';
 const $=id=>document.getElementById(id);
 const fmt=(v,d=0)=>Number(v).toLocaleString('fr-FR',{maximumFractionDigits:d,minimumFractionDigits:d});
 const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const labels={egalisation:'Réduire les charges les plus élevées',deficit_d_abord:'Combler les plus gros manques en nombre',proportionnelle:'Répartir selon le nombre d’élèves',franchissement:'Amener le plus de provinces au seuil'};
 const scenariosLisibles={actuel:'Situation observée en 2024–2025',demographie_insd:'2030 · projection de référence de l’INSD',demographie_insd_moins10:'2030 · INSD, rapport inscrits / population réduit de 10 %',demographie_insd_plus10:'2030 · INSD, rapport inscrits / population augmenté de 10 %',tendance_longue:'2030 · prolongation de la tendance régionale',croissance_nationale:'2030 · croissance historique nationale',retour_au_pic:'2030 · maximum régional historique ou tendance supérieure'};
 const libelleScenario=s=>scenariosLisibles[s.id]||s.label;
 function descriptionRegle(regle,r){
  const unite=r==='maitres'?'maître':'salle',pluriel=r==='maitres'?'maîtres':'salles';
  const textes={
   egalisation:`Chaque ${unite} supplémentaire va à la province qui compte le plus d’élèves par ${unite}. Les charges sont recalculées après chaque ajout pour réduire les situations les plus chargées.`,
   deficit_d_abord:`Chaque ${unite} supplémentaire va à la province dont le manque au seuil est le plus élevé en nombre de ${pluriel}. Ce manque est recalculé après chaque ajout. Une petite province très chargée peut ne rien recevoir. Une fois les manques couverts, les ajouts réduisent les charges les plus élevées.`,
   proportionnelle:`Les ${pluriel} sont répartis selon la part des élèves de chaque province, avec un arrondi au plus fort reste pour obtenir des unités entières. Avec peu de moyens, certaines provinces peuvent ne rien recevoir. Cette règle peut aussi attribuer des moyens à des provinces déjà sous le seuil.`,
   franchissement:`Les plus petits manques entiers sont comblés en premier pour amener le plus de provinces au seuil. Les ${pluriel} restants vont ensuite aux provinces les plus chargées. Une province très chargée peut donc recevoir des moyens. Le nombre de provinces ramenées au seuil est maximal dans ce modèle ; le partage du reliquat n’est pas revendiqué comme un optimum conjoint.`
  };return textes[regle];
 }
 let data, state, selected=null;
 function erreur(e){$('erreur').hidden=false;$('erreur').textContent='Simulation indisponible : '+e.message;}
 function valeur(id,entier){
  const input=$(id),ressource=id.endsWith('maitres')?'maîtres':'salles';
  let message='';const v=Number(input.value);
  if(!input.value.trim())message=`Le champ « ${entier?'nombre de '+ressource+' supplémentaires':'seuil pour les '+ressource} » est obligatoire.`;
  else if(!Number.isFinite(v)||(entier&&(!Number.isSafeInteger(v)||v<0||v>100000)))message=`Le nombre de ${ressource} supplémentaires doit être un entier entre 0 et 100 000.`;
  else if(!entier&&v<=0)message=`Le seuil pour les ${ressource} doit être strictement positif.`;
  if(message){input.setAttribute('aria-invalid','true');input.setAttribute('aria-describedby','erreur');throw Error(message);}return v;
 }
 function initialiser(){
  data=window.DCB_DATA;
  if(!data||!window.DCBEngine)throw Error('Le fichier donnees.js ou moteur.js est absent. Conservez les quatre scripts et la feuille de style avec index.html.');
  if(!Array.isArray(data.provinces)||data.provinces.length!==45)throw Error('Le jeu attendu doit contenir exactement 45 provinces.');
  if(!Array.isArray(data.scenarios)||!data.scenarios.some(s=>s.id==='actuel'))throw Error('Les scénarios attendus sont absents.');
  if(new Set(data.provinces.map(p=>p.province)).size!==45)throw Error('Les provinces doivent être uniques.');
  $('scenario').innerHTML=data.scenarios.map(s=>`<option value="${esc(s.id)}">${esc(libelleScenario(s))}</option>`).join('');
  $('region').innerHTML+=[...new Set(data.provinces.map(p=>p.region))].sort((a,b)=>a.localeCompare(b,'fr')).map(v=>`<option value="${esc(v)}">${esc(v)}</option>`).join('');
  $('sources').innerHTML=(data.sources||[]).map(s=>`<li><strong>${esc(s.titre)}</strong> · ${esc(s.producteur)}${s.detail?' — '+esc(s.detail):''}</li>`).join('');
  $('version').textContent=`Annuaire ${data.meta.annee} · Horizon ${data.meta.horizon} · Version des données ${data.meta.version||'1'}.`;
  $('esu-note').textContent=`Éducation en situation d’urgence au ${dateFr(data.meta.date_esu)} : ces données ne distinguent pas le public et le privé. « Non renseigné » signifie que l’information est absente, et non qu’elle vaut zéro.`;
  $('parametres-form').addEventListener('submit',e=>{e.preventDefault();calculer();$('parametres-form').querySelector('[aria-invalid="true"]')?.focus();});
  $('parametres-form').addEventListener('change',calculer);
  $('parametres-form').addEventListener('input',calculer);
  $('ressource').addEventListener('change',()=>{if(state)afficher();});
  $('region').addEventListener('change',()=>{if(state){carte();tableau();}});
  $('export').addEventListener('click',exporter);
  afficherDemographie();$('export-demographie').addEventListener('click',exporterDemographie);
  calculer();
 }
 function hypotheseComplete(scenario){return scenario.description+(scenario.id!=='actuel'&&data.meta.hypothese_2030?' '+data.meta.hypothese_2030:'');}
 function dateFr(v){if(!v)return 'date non renseignée';const m=/^(\d{4})-(\d{2})-(\d{2})$/.exec(v);return m?`${m[3]}/${m[2]}/${m[1]}`:v;}
 function invalider(){
  state=null;$('export').disabled=true;
  for(const input of $('parametres-form').querySelectorAll('input')){input.removeAttribute('aria-invalid');input.removeAttribute('aria-describedby');}
  for(const id of ['synthese','kpis','indicateurs-complementaires','comparaison','lignes','perimetre','signal','compte-lignes','regle-description','franchissement-detail','courbe-table','courbe-contexte','courbe-reperes','sensibilite-table','sensibilite-note','sensibilite-contexte'])$(id).textContent='';
  $('courbe-moyens').replaceChildren();$('carte').replaceChildren();$('detail').textContent='Résultats indisponibles tant que les paramètres sont invalides.';
 }
 function calculer(){invalider();try{
  const scenario=data.scenarios.find(s=>s.id===$('scenario').value);
  $('hypothese').textContent=`Hypothèse · ${hypotheseComplete(scenario)}`;
  const eleves=data.provinces.map(p=>p.demandes[scenario.id]);
  const next={scenario,eleves,regle:$('regle').value,budgets:{maitres:valeur('budget-maitres',true),salles:valeur('budget-salles',true)},seuils:{maitres:valeur('seuil-maitres',false),salles:valeur('seuil-salles',false)},resultats:{}};
  for(const r of ['maitres','salles']){
   const stock=data.provinces.map(p=>p[r]);
   next.resultats[r]={stock,avant:DCBEngine.mesurer(eleves,stock,eleves.map(()=>0),next.seuils[r]),regles:{}};
   for(const regle of DCBEngine.REGLES){const ajout=DCBEngine.repartir(eleves,stock,next.budgets[r],regle,next.seuils[r]);next.resultats[r].regles[regle]={ajout,apres:DCBEngine.mesurer(eleves,stock,ajout,next.seuils[r])};}
  }
  state=next;$('export').disabled=false;$('erreur').hidden=true;afficher();$('statut').textContent='Résultats à jour · 45 provinces';
 }catch(e){state=null;erreur(e);$('statut').textContent='Veuillez corriger les valeurs signalées pour relancer le calcul.';$('kpis').innerHTML='';$('comparaison').innerHTML='';$('lignes').innerHTML='';$('carte').replaceChildren();$('detail').textContent='Résultats indisponibles tant que les paramètres sont invalides.';}}
 function afficher(){
  const r=$('ressource').value, res=state.resultats[r],apres=res.regles[state.regle].apres,avant=res.avant;
  const unite=r==='maitres'?'maître':'salle',pluriel=r==='maitres'?'maîtres':'salles',seuil=state.seuils[r].toLocaleString('fr-FR',{maximumSignificantDigits:15});
  $('perimetre').textContent=`Ensemble national · 45 provinces · ${libelleScenario(state.scenario)} · ${fmt(state.budgets.maitres)} maîtres supplémentaires et ${fmt(state.budgets.salles)} salles supplémentaires. Résultats affichés : ${pluriel}, au seuil choisi de ${seuil} élèves par ${unite}. Les deux ressources sont réparties séparément.`;
  let conclusion=apres.provinces_au_dessus_norme===0?`Toutes les provinces atteignent le seuil choisi de ${seuil} élèves par ${unite}. Manque restant : 0 ${pluriel}.`:`${fmt(apres.provinces_au_dessus_norme)} provinces sur 45 restent au-dessus du seuil choisi de ${seuil}. Avant tout ajout, atteindre ce seuil partout demandait ${fmt(avant.deficit_restant)} ${pluriel} supplémentaires. Après cette répartition, il en manque encore ${fmt(apres.deficit_restant)}.`;
  if(apres.provinces_au_dessus_norme===0)conclusion+=` Le seuil est une valeur de référence choisie ; l’atteindre ne signifie pas que les conditions d’enseignement sont satisfaisantes. Le maximum provincial reste à ${fmt(apres.ratio_max,1)} élèves par ${unite}.`;
  if(apres.provinces_au_dessus_norme>0&&avant.provinces_au_dessus_norme===apres.provinces_au_dessus_norme&&apres.ratio_max<avant.ratio_max)conclusion+=' Le nombre de provinces au-dessus du seuil reste identique, même si les charges diminuent : une amélioration ne suffit pas toujours à atteindre le seuil.';
  $('synthese').textContent=`Avec ${fmt(state.budgets[r])} ${pluriel} supplémentaires, la moyenne nationale passe de ${fmt(avant.ratio_moyen,1)} à ${fmt(apres.ratio_moyen,1)} élèves par ${unite}. Le maximum provincial passe de ${fmt(avant.ratio_max,1)} à ${fmt(apres.ratio_max,1)} ; la province qui atteint ce maximum peut changer. ${conclusion}`;
  const cards=[['ratio_moyen',`Élèves par ${unite} (moyenne nationale)`,1],['ratio_max',`Maximum provincial (élèves par ${unite})`,1],['provinces_au_dessus_norme',`Provinces au-dessus du seuil de ${seuil}`,0],['deficit_restant',`${r==='maitres'?'Maîtres manquants':'Salles manquantes'} pour atteindre le seuil`,0]];
  $('kpis').innerHTML=cards.map(([key,label,d])=>`<div class="kpi"><span class="label">${label}</span><strong>${fmt(apres[key],d)}</strong><span class="before">Avant : ${fmt(avant[key],d)} · Après : ${fmt(apres[key],d)}</span></div>`).join('');
  const totalEleves=state.eleves.reduce((s,v)=>s+v,0),part=m=>totalEleves?fmt(100*m.eleves_en_province_au_dessus_norme/totalEleves,1)+' %':'non calculable';
  $('indicateurs-complementaires').innerHTML=`<h3>Deux lectures complémentaires</h3><p class="small">${esc(labels[state.regle])} · ${pluriel} · seuil de ${seuil}. Les indicateurs restent nationaux, même avec un filtre régional.</p><div class="complement-grid"><div><h4>Élèves inscrits dans les provinces au-dessus du seuil</h4><p>Avant : ${part(avant)} · Après : <strong id="part-eleves-apres">${part(apres)}</strong></p><p class="small">Après répartition : ${fmt(apres.eleves_en_province_au_dessus_norme)} inscrits sur ${fmt(totalEleves)}. Cette part décrit des territoires, pas la situation individuelle de chaque élève.</p></div><div><h4>Dispersion des charges provinciales</h4><p>Avant : ${fmt(avant.ecart_type_ratios,1)} · Après : <strong id="dispersion-apres">${fmt(apres.ecart_type_ratios,1)}</strong> élèves par ${unite}</p><p class="small">Écart-type non pondéré : chaque province compte autant. Une valeur plus faible signifie des ratios plus proches de leur moyenne simple ; ce n’est pas un jugement global sur l’équité.</p></div></div>`;
  $('methode-regles').innerHTML=DCBEngine.REGLES.map(regle=>`<dt>${esc(labels[regle])}</dt><dd>${esc(descriptionRegle(regle,r))}</dd>`).join('');
  $('comparaison').innerHTML=DCBEngine.REGLES.map(regle=>{const a=res.regles[regle].apres;return `<tr class="${regle===state.regle?'selected':''}"><td>${labels[regle]}${regle===state.regle?' · sélectionnée':''}</td><td>${fmt(a.deficit_restant)}</td><td>${fmt(a.provinces_au_dessus_norme)}</td><td>${fmt(a.ratio_max,1)}</td><td>${fmt(a.ratio_moyen,1)}</td></tr>`;}).join('');
  $('regle-description').textContent=descriptionRegle(state.regle,r)+` En cas d’égalité, l’ordre de la liste des provinces s’applique. La totalité des moyens est répartie, même si le seuil est déjà atteint. La moyenne nationale est identique pour les quatre règles : elles répartissent le même nombre de ${pluriel} pour les mêmes inscriptions ; seule la répartition territoriale change.`;
  const f=DCBEngine.repartirSeuil(state.eleves,res.stock,state.budgets[r],state.seuils[r]);
  $('franchissement-detail').textContent=state.regle==='franchissement'?`${fmt(f.provinces_ramenees)} ${f.provinces_ramenees===1?'province ramenée':'provinces ramenées'} au seuil : ${fmt(f.cout_franchissement)} unités. Les ${fmt(f.reliquat)} unités restantes réduisent ensuite les charges les plus élevées. ${f.cout_province_supplementaire===null?'Toutes les provinces atteignent le seuil.':`Amener une province de plus au seuil demanderait au minimum ${fmt(f.cout_province_supplementaire)} unités au total, avant le partage du reste.`}`:'';
  afficherCourbe(r);
  afficherSensibilite(r);
  const m=state.resultats.maitres,s=state.resultats.salles;
  const signal=data.provinces.reduce((v,p,i)=>v+Math.max(0,p.maitres+m.regles[state.regle].ajout[i]-p.salles-s.regles[state.regle].ajout[i]),0);
  $('signal').textContent=`Repère comptable : dans chaque province où les maîtres sont plus nombreux que les salles après répartition, on calcule cet écart ; la somme de ces écarts est ${fmt(signal)}. Ce n’est ni un nombre de salles manquantes ni un contrôle de validité de la répartition. Les maîtres et les salles sont répartis séparément ; ce repère ne décrit pas l’occupation réelle des classes.`;
  $('titre-carte').textContent=`Élèves par ${unite} après répartition`;
  carte();tableau();if(selected!==null)detail(selected);else $('detail').innerHTML='<p class="eyebrow">PROVINCE</p><h3>Sélectionnez un territoire</h3><p>Sélectionnez une province sur la carte ou dans le tableau pour consulter sa répartition et le contexte de l’éducation en situation d’urgence.</p>';
 }
 function visibles(){return data.provinces.map((p,i)=>({p,i})).filter(({p})=>!$('region').value||p.region===$('region').value);}
 function ratios(i,r){const stock=state.resultats[r].stock[i],ajout=state.resultats[r].regles[state.regle].ajout[i];return {avant:state.eleves[i]/stock,apres:state.eleves[i]/(stock+ajout),ajout};}
 function tableau(){const lignes=visibles();$('compte-lignes').textContent=`${lignes.length} provinces affichées sur 45 · le téléchargement contient toujours les 45 provinces · ${state.scenario.label}`;
  $('lignes').innerHTML=lignes.map(({p,i})=>{const m=ratios(i,'maitres'),s=ratios(i,'salles');return `<tr><td><button type="button" class="province-link" data-province="${i}">${esc(p.province)}</button><small>${esc(p.region)}</small></td><td>${fmt(state.eleves[i])}</td><td>${fmt(p.maitres)}</td><td>+${fmt(m.ajout)}</td><td>${fmt(m.avant,1)} → <strong>${fmt(m.apres,1)}</strong></td><td>${fmt(p.salles)}</td><td>+${fmt(s.ajout)}</td><td>${fmt(s.avant,1)} → <strong>${fmt(s.apres,1)}</strong></td></tr>`;}).join('');
  $('lignes').querySelectorAll('button').forEach(b=>b.addEventListener('click',()=>{selected=Number(b.dataset.province);detail(selected);carte();}));
 }
 function anneaux(g){if(!Array.isArray(g)||!g.length)return [];if(Array.isArray(g[0])&&typeof g[0][0]==='number')return [g];return g.flatMap(anneaux);}
 function carte(){
  const svg=$('carte');svg.replaceChildren();const all=data.provinces.map(p=>anneaux((data.geometries||{})[p.province]));const coords=all.flat(2);
  if(!coords.length){const text=document.createElementNS(svg.namespaceURI,'text');text.setAttribute('x','30');text.setAttribute('y','80');text.textContent='Géométries absentes : utilisez le tableau ci-dessous.';svg.append(text);return;}
  const xs=coords.map(p=>p[0]),ys=coords.map(p=>p[1]);const minX=Math.min(...xs),maxX=Math.max(...xs),minY=Math.min(...ys),maxY=Math.max(...ys);
  const correction=Math.cos((minY+maxY)/2*Math.PI/180),w=(maxX-minX)*correction,h=maxY-minY,scale=Math.min(750/w,490/h),dx=(800-w*scale)/2,dy=(540-h*scale)/2;
  const couleur=v=>v<=1?'#95bea7':v<=1.25?'#d5c687':v<=1.5?'#ce9260':'#95564e';
  const r=$('ressource').value;
  for(const {p,i} of visibles()){
   const rings=all[i];if(!rings.length)continue;
   const path=document.createElementNS(svg.namespaceURI,'path');path.setAttribute('d',rings.map(ring=>ring.map((point,j)=>`${j?'L':'M'}${(dx+(point[0]-minX)*correction*scale).toFixed(2)},${(dy+(maxY-point[1])*scale).toFixed(2)}`).join(' ')+'Z').join(' '));
   const ratio=ratios(i,r).apres;path.setAttribute('fill',couleur(ratio/state.seuils[r]));path.setAttribute('fill-rule','evenodd');path.setAttribute('class','province'+(selected===i?' active':''));path.setAttribute('tabindex','0');path.setAttribute('role','button');path.setAttribute('aria-label',`${p.province}, ${fmt(ratio,1)} élèves par ${r==='maitres'?'maître':'salle'} après répartition`);
   const title=document.createElementNS(svg.namespaceURI,'title');title.textContent=`${p.province} · ${p.region}\n${fmt(state.eleves[i])} élèves · élèves par ${r==='maitres'?'maître':'salle'} après : ${fmt(ratio,1)}\n+${fmt(ratios(i,r).ajout)} ${r==='maitres'?'maîtres':'salles'}\nESU au ${dateFr(data.meta.date_esu)} : déplacés ${esuValeur(p.esu,'eleves_deplaces')}`;path.append(title);
   path.addEventListener('mouseenter',()=>detail(i));path.addEventListener('focus',()=>detail(i));path.addEventListener('click',()=>{selected=i;detail(i);carte();});path.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();selected=i;detail(i);carte();}});svg.append(path);
  }
 }
 function esuValeur(esu,key){
  const absent=!esu||esu[key]===null||esu[key]===undefined;
  if(esu&&esu[key+'_statut']==='partiel')return absent?'partiel · total non renseigné':fmt(esu[key])+' (partiel, total non établi)';
  return absent?'non renseigné':fmt(esu[key]);
 }
 function detail(i){const p=data.provinces[i],m=ratios(i,'maitres'),s=ratios(i,'salles');
  $('detail').innerHTML=`<p class="eyebrow">${esc(p.region)}</p><h3>${esc(p.province)}</h3><p class="small">${esc(libelleScenario(state.scenario))} · ${fmt(state.eleves[i])} élèves</p><dl><dt>Maîtres : existants + ajoutés</dt><dd>${fmt(p.maitres)} + ${fmt(m.ajout)}</dd><dt>Élèves par maître : avant → après</dt><dd>${fmt(m.avant,1)} → ${fmt(m.apres,1)}</dd><dt>Salles : existantes + ajoutées</dt><dd>${fmt(p.salles)} + ${fmt(s.ajout)}</dd><dt>Élèves par salle : avant → après</dt><dd>${fmt(s.avant,1)} → ${fmt(s.apres,1)}</dd></dl><p class="small">Pourquoi ces ajouts ? ${esc(descriptionRegle(state.regle,'maitres'))} La même règle est appliquée séparément aux salles. Les nombres ci-dessus résultent de ${fmt(state.budgets.maitres)} maîtres et ${fmt(state.budgets.salles)} salles répartis nationalement.</p><hr><h3>Éducation en situation d’urgence · ${esc(dateFr(data.meta.date_esu))}</h3><dl><dt>Écoles rouvertes</dt><dd>${esuValeur(p.esu,'ecoles_rouvertes')}</dd><dt>Écoles délocalisées</dt><dd>${esuValeur(p.esu,'ecoles_delocalisees')}</dd><dt>Élèves déplacés</dt><dd>${esuValeur(p.esu,'eleves_deplaces')}</dd></dl><p class="small">Ces données ne distinguent pas le public et le privé. « Non renseigné » signifie que l’information est absente, et non qu’elle vaut zéro. Cette situation datée ne garantit pas l’accessibilité actuelle des écoles.</p>`;
 }
 function exporter(){if(!state){erreur(Error('Recalculez une simulation valide avant l’export.'));return;}
  const entete=['annee_scolaire','annee_stocks','scenario','hypothese','regle','budget_maitres_unites','budget_salles_unites','seuil_simulation_maitres','seuil_simulation_salles','perimetre','province','region','eleves','maitres_existants','maitres_ajoutes','ratio_maitre_avant','ratio_maitre_apres','salles_existantes','salles_ajoutees','ratio_salle_avant','ratio_salle_apres','date_esu','maitres_ajout_seuil','maitres_ajout_reliquat','salles_ajout_seuil','salles_ajout_reliquat'];
  const phases={};if(state.regle==='franchissement')for(const r of ['maitres','salles'])phases[r]=DCBEngine.repartirSeuil(state.eleves,state.resultats[r].stock,state.budgets[r],state.seuils[r]);
  const rows=data.provinces.map((p,i)=>{const m=ratios(i,'maitres'),s=ratios(i,'salles');return [state.scenario.id==='actuel'?data.meta.annee:data.meta.horizon,data.meta.annee,state.scenario.id,hypotheseComplete(state.scenario),state.regle,state.budgets.maitres,state.budgets.salles,state.seuils.maitres,state.seuils.salles,'national_45_provinces',p.province,p.region,state.eleves[i],p.maitres,m.ajout,m.avant.toFixed(6),m.apres.toFixed(6),p.salles,s.ajout,s.avant.toFixed(6),s.apres.toFixed(6),data.meta.date_esu,phases.maitres?.ajout_seuil[i]??'',phases.maitres?.ajout_reliquat[i]??'',phases.salles?.ajout_seuil[i]??'',phases.salles?.ajout_reliquat[i]??''];});
  const quote=v=>'"'+String(v??'').replace(/"/g,'""')+'"';const csv='\ufeff'+[entete,...rows].map(row=>row.map(quote).join(';')).join('\r\n');const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download=`allocation_45_provinces_${state.scenario.id}_${state.regle}.csv`;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
 }
 function afficherCourbe(r){
  const stock=state.resultats[r].stock;
  const points=Array.from({length:86},(_,i)=>({x:i+35,y:DCBEngine.unitesPlafond(state.eleves,stock,i+35)}));
  const budget=state.budgets[r],seuil=state.seuils[r];
  const egalisation=state.resultats[r].regles.egalisation.ajout;
  const plafond=Math.max(...state.eleves.map((v,i)=>v/(stock[i]+egalisation[i])));
  const max=Math.max(1,budget,...points.map(p=>p.y));
  const x=v=>85+(v-35)/85*670,y=v=>275-Math.log1p(v)/Math.log1p(max)*225;
  const unite=r==='maitres'?'maître':'salle',pluriel=r==='maitres'?'maîtres':'salles';
  $('moyens-titre').textContent=`Combien de ${pluriel} ajouter pour respecter un plafond dans toutes les provinces ?`;
  $('courbe-col-plafond').textContent=`Plafond souhaité (élèves par ${unite})`;
  $('courbe-col-moyens').textContent=`Nombre minimal de ${pluriel} à ajouter`;
  $('courbe-contexte').textContent=`${libelleScenario(state.scenario)} · ${pluriel} · ensemble des 45 provinces. Besoin total avant les ajouts saisis, et non besoin restant après la simulation.`;
  const dansPlage=v=>v>=35&&v<=120;
  $('courbe-reperes').textContent=`Votre budget : ${fmt(budget)} ${pluriel}. Avec « Réduire les charges les plus élevées », le maximum obtenu est d’environ ${fmt(plafond,2)} élèves par ${unite}, sous les hypothèses du modèle. Ce repère ne décrit pas nécessairement la règle sélectionnée. Les valeurs sont arrondies. Seuil choisi : ${seuil.toLocaleString('fr-FR',{maximumSignificantDigits:15})}${dansPlage(seuil)?'.':' (hors de la plage 35–120 du graphique).'}${dansPlage(plafond)?'':' Le maximum obtenu est hors de la plage du graphique ; sa valeur reste indiquée ici.'}`;
  const graduations=[0,10,100,1000,10000,100000].filter(v=>v<=max);
  if(!graduations.some(v=>v>0&&Math.abs(y(v)-y(max))<20))graduations.push(max);
  const fixes=[40,45,50,55,60,70,80,100];
  $('courbe-moyens').innerHTML=`<title>Besoins minimaux avant ajout et repères du budget, ${esc(libelleScenario(state.scenario))}, ${r}</title><desc>Courbe de 35 à 120 élèves par ${unite}. Échelle verticale : logarithme de 1 plus le nombre d’unités. Le tableau donne les valeurs exactes.</desc>${graduations.map(v=>`<path d="M85,${y(v)} H755" stroke="#dce2db"/><text x="77" y="${y(v)+4}" text-anchor="end">${fmt(v)}</text>`).join('')}<path d="M85,50 V275 H755" fill="none" stroke="#677b82"/><polyline points="${points.map(p=>`${x(p.x)},${y(p.y)}`).join(' ')}" fill="none" stroke="#176650" stroke-width="3"/>${[35,40,50,60,80,100,120].map(v=>`<text x="${x(v)}" y="298" text-anchor="middle">${v}</text>`).join('')}${fixes.map(v=>`<circle data-plafond="${v}" cx="${x(v)}" cy="${y(DCBEngine.unitesPlafond(state.eleves,stock,v))}" r="4" fill="#176650"><title>Plafond ${v} : ${fmt(DCBEngine.unitesPlafond(state.eleves,stock,v))} ${pluriel}</title></circle>`).join('')}<path data-repere="budget" data-budget="${budget}" d="M85,${y(budget)} H755" stroke="#95564e" stroke-width="2" stroke-dasharray="7 4"><title>Votre budget : ${fmt(budget)} ${pluriel}</title></path>${dansPlage(seuil)?`<path data-repere="seuil" d="M${x(seuil)},50 V275" stroke="#365e8c" stroke-width="2" stroke-dasharray="3 4"><title>Seuil choisi : ${seuil} élèves par ${unite}</title></path>`:''}${dansPlage(plafond)?`<circle cx="${x(plafond)}" cy="${y(budget)}" r="6" fill="#95564e"><title>Avec ce budget, maximum obtenu par égalisation : environ ${fmt(plafond,2)}</title></circle>`:''}<text x="85" y="25">${r==='maitres'?'Maîtres':'Salles'} à ajouter · échelle logarithmique avec zéro</text><text x="400" y="328" text-anchor="middle">Plafond souhaité · élèves par ${unite}</text>`;
  $('courbe-table').innerHTML=fixes.map(v=>`<tr><td>${v}</td><td>${fmt(DCBEngine.unitesPlafond(state.eleves,stock,v))}</td></tr>`).join('');
 }
 function afficherSensibilite(r){
  const res=state.resultats[r],courant=state.seuils[r],budget=state.budgets[r];
  const independante=['egalisation','proportionnelle'].includes(state.regle);
  const seuils=[...new Set([40,50,60,courant])].sort((a,b)=>a-b);
  const lignes=seuils.map(seuil=>{
   const ajout=independante||seuil===courant?res.regles[state.regle].ajout:DCBEngine.repartir(state.eleves,res.stock,budget,state.regle,seuil);
   const avant=DCBEngine.mesurer(state.eleves,res.stock,state.eleves.map(()=>0),seuil);
   const apres=DCBEngine.mesurer(state.eleves,res.stock,ajout,seuil);
   return {seuil,ajout,avant,apres};
  });
  const identiques=lignes.every(ligne=>ligne.ajout.every((v,i)=>v===lignes[0].ajout[i]));
  $('sensibilite-contexte').textContent=`${libelleScenario(state.scenario)} · ${labels[state.regle]} · ${fmt(budget)} ${r==='maitres'?'maîtres':'salles'} supplémentaires. La ligne sélectionnée correspond au seuil du formulaire ; les autres lignes sont des comparaisons, sans modification de la simulation ou de l’export.`;
  $('sensibilite-table').innerHTML=lignes.map(({seuil,avant,apres})=>`<tr data-seuil="${seuil}" class="${seuil===courant?'selected':''}"${seuil===courant?' aria-current="true"':''}><td>${seuil.toLocaleString('fr-FR',{maximumSignificantDigits:15})}${seuil===courant?' <span class="current-threshold">Seuil courant</span>':''}</td><td>${fmt(avant.deficit_restant)}</td><td>${fmt(avant.provinces_au_dessus_norme)}</td><td>${fmt(apres.provinces_au_dessus_norme)}</td><td>${fmt(apres.ratio_max,1)}</td><td>${fmt(apres.deficit_restant)}</td></tr>`).join('');
  $('sensibilite-note').textContent=independante?'Cette règle ne dépend pas du seuil : les mêmes ajouts sont attribués aux mêmes provinces. Seule l’évaluation change (manque et provinces au-dessus du seuil).':`Avec cette règle, le seuil peut modifier la répartition. ${identiques?'Pour les seuils comparés ici, les ajouts restent toutefois identiques ; seule l’évaluation change.':'Pour les seuils comparés ici, les ajouts changent ; chaque ligne réexécute la règle avec le seuil indiqué.'}`;
 }
 function afficherDemographie(){
  const rows=data.demographie;
  if(!Array.isArray(rows)||rows.length!==45)throw Error('Lecture démographique des 45 provinces absente. Relancez la chaîne.');
  const ratio=100*rows.reduce((v,p)=>v+p.eleves_total,0)/rows.reduce((v,p)=>v+p.population_6_11_2025,0);
  $('demo-resume').textContent=`Repère national : ${fmt(ratio,1)} élèves inscrits de tous âges (public et privé) pour 100 enfants de 6 à 11 ans projetés en 2025. Ce contexte 2024–2025 reste fixe lorsque vous changez les moyens ou le scénario.`;
  $('demo-table').innerHTML=rows.map(p=>`<tr><td>${esc(p.province)}</td><td>${fmt(p.ratio_charge_public,1)}</td><td>${fmt(p.eleves_total)}</td><td>${fmt(p.population_6_11_2025)}</td><td>${fmt(p.inscrits_pour_100_enfants,1)}</td></tr>`).join('');
 }
 function exporterDemographie(){
  const columns=['province','region','annee_scolaire','annee_population','eleves_public','eleves_prive','eleves_total','maitres_public','ratio_charge_public','population_6_11_2025','inscrits_pour_100_enfants','source_document','source_page','document_2025','page_2025','interpretation'];
  const quote=v=>'"'+String(v??'').replace(/"/g,'""')+'"';
  const csv='\ufeff'+[columns,...data.demographie.map(p=>columns.map(c=>p[c]))].map(row=>row.map(quote).join(';')).join('\r\n');
  const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));
  const a=document.createElement('a');a.href=url;a.download='lecture_demographique_2024_2025.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
 }
 try{initialiser();}catch(e){erreur(e);}
})();
