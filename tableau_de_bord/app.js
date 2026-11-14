/* Interface locale sans dépendance réseau. */
(function() {
 'use strict';
 const $=id=>document.getElementById(id);
 const fmt=(v,d=0)=>Number(v).toLocaleString('fr-FR',{maximumFractionDigits:d,minimumFractionDigits:d});
 const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const labels={egalisation:'Égalisation des ratios',deficit_d_abord:'Déficit d’abord',proportionnelle:'Proportionnelle aux élèves'};
 const descriptions={egalisation:'Chaque unité va à la province dont le ratio élèves / ressource est le plus élevé, puis les ratios sont recalculés.',deficit_d_abord:'Chaque unité va au plus grand déficit exprimé en unités au seuil choisi. Une fois les déficits couverts, les ratios sont égalisés.',proportionnelle:'Les moyens sont répartis au prorata des élèves, avec arrondi au plus fort reste. En cas d’égalité, l’ordre des provinces dans les données est conservé.'};
 let data, state, selected=null;
 function erreur(e){$('erreur').hidden=false;$('erreur').textContent='Simulation indisponible : '+e.message;}
 function valeur(id,entier){const input=$(id);if(!input.value.trim())throw Error('Complétez tous les paramètres.');const v=Number(input.value);if(!Number.isFinite(v)||(entier&&(!Number.isSafeInteger(v)||v<0||v>100000))||(!entier&&v<=0))throw Error(entier?'Les moyens doivent être des entiers entre 0 et 100 000 unités.':'Les seuils doivent être strictement positifs.');return v;}
 function initialiser(){
  data=window.DCB_DATA;
  if(!data||!window.DCBEngine)throw Error('Le fichier donnees.js ou moteur.js est absent. Conservez les quatre scripts et la feuille de style avec index.html.');
  if(!Array.isArray(data.provinces)||data.provinces.length!==45)throw Error('Le jeu attendu doit contenir exactement 45 provinces.');
  if(!Array.isArray(data.scenarios)||!data.scenarios.some(s=>s.id==='actuel'))throw Error('Les scénarios attendus sont absents.');
  if(new Set(data.provinces.map(p=>p.province)).size!==45)throw Error('Les provinces doivent être uniques.');
  $('scenario').innerHTML=data.scenarios.map(s=>`<option value="${esc(s.id)}">${esc(s.label)}</option>`).join('');
  $('region').innerHTML+=[...new Set(data.provinces.map(p=>p.region))].sort((a,b)=>a.localeCompare(b,'fr')).map(v=>`<option value="${esc(v)}">${esc(v)}</option>`).join('');
  $('sources').innerHTML=(data.sources||[]).map(s=>`<li><strong>${esc(s.titre)}</strong> · ${esc(s.producteur)}${s.detail?' — '+esc(s.detail):''}</li>`).join('');
  $('version').textContent=`Annuaire ${data.meta.annee} · Horizon ${data.meta.horizon} · Version des données ${data.meta.version||'1'}.`;
  $('esu-note').textContent=`ESU au ${dateFr(data.meta.date_esu)} (février 2026) : données de contexte, public et privé non distingués. Les valeurs absentes sont affichées « non renseigné » et ne valent pas zéro.`;
  $('parametres-form').addEventListener('submit',e=>{e.preventDefault();calculer();});
  $('parametres-form').addEventListener('change',calculer);
  $('parametres-form').addEventListener('input',calculer);
  $('ressource').addEventListener('change',()=>{if(state)afficher();});
  $('region').addEventListener('change',()=>{if(state){carte();tableau();}});
  $('export').addEventListener('click',exporter);
  calculer();
 }
 function hypotheseComplete(scenario){return scenario.description+(scenario.id!=='actuel'&&data.meta.hypothese_2030?' '+data.meta.hypothese_2030:'');}
 function dateFr(v){if(!v)return 'date non renseignée';const m=/^(\d{4})-(\d{2})-(\d{2})$/.exec(v);return m?`${m[3]}/${m[2]}/${m[1]}`:v;}
 function invalider(){
  state=null;$('export').disabled=true;
  for(const id of ['kpis','comparaison','lignes','perimetre','signal','compte-lignes','regle-description'])$(id).textContent='';
  $('carte').replaceChildren();$('detail').textContent='Résultats indisponibles tant que les paramètres sont invalides.';
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
  state=next;$('export').disabled=false;$('erreur').hidden=true;afficher();$('statut').textContent='Simulation calculée · 45 provinces';
 }catch(e){state=null;erreur(e);$('statut').textContent='Corrigez les paramètres pour recalculer.';$('kpis').innerHTML='';$('comparaison').innerHTML='';$('lignes').innerHTML='';$('carte').replaceChildren();$('detail').textContent='Résultats indisponibles tant que les paramètres sont invalides.';}}
 function afficher(){
  const r=$('ressource').value, res=state.resultats[r],apres=res.regles[state.regle].apres,avant=res.avant;
  $('perimetre').textContent=`Ensemble national · 45 provinces · ${state.scenario.label} · ${fmt(state.budgets[r])} ${r==='maitres'?'maîtres':'salles'} supplémentaires · seuil de simulation ${fmt(state.seuils[r],1)}.`;
  const cards=[['ratio_moyen','Élèves / '+(r==='maitres'?'maître':'salle')+' · national',1],['ratio_max','Pire ratio provincial',1],['provinces_au_dessus_norme','Provinces au-dessus du seuil',0],['deficit_restant','Déficit total · unités',0]];
  $('kpis').innerHTML=cards.map(([key,label,d])=>`<div class="kpi"><span class="label">${label}</span><strong>${fmt(apres[key],d)}</strong><span class="before">Avant : ${fmt(avant[key],d)} → Après allocation</span></div>`).join('');
  $('comparaison').innerHTML=DCBEngine.REGLES.map(regle=>{const a=res.regles[regle].apres;return `<tr class="${regle===state.regle?'selected':''}"><td>${labels[regle]}${regle===state.regle?' · sélectionnée':''}</td><td>${fmt(a.deficit_restant)}</td><td>${fmt(a.provinces_au_dessus_norme)}</td><td>${fmt(a.ratio_max,1)}</td><td>${fmt(a.ratio_moyen,1)}</td></tr>`;}).join('');
  $('regle-description').textContent=descriptions[state.regle]+' Les égalités suivent l’ordre d’entrée. Le budget entier est entièrement réparti, même si le seuil est déjà atteint.';
  const m=state.resultats.maitres,s=state.resultats.salles;
  const signal=data.provinces.reduce((v,p,i)=>v+Math.max(0,p.maitres+m.regles[state.regle].ajout[i]-p.salles-s.regles[state.regle].ajout[i]),0);
  $('signal').textContent=`Signal comptable : somme des écarts positifs entre maîtres et salles après allocation = ${fmt(signal)}. Les ressources sont allouées séparément ; cet écart ne permet pas de déduire une situation individuelle de classe ou d’enseignant.`;
  $('titre-carte').textContent=`Élèves / ${r==='maitres'?'maître':'salle'} · après allocation`;
  carte();tableau();if(selected!==null)detail(selected);else $('detail').innerHTML='<p class="eyebrow">PROVINCE</p><h3>Sélectionnez un territoire</h3><p>Survolez ou sélectionnez une province pour consulter son allocation et le contexte ESU.</p>';
 }
 function visibles(){return data.provinces.map((p,i)=>({p,i})).filter(({p})=>!$('region').value||p.region===$('region').value);}
 function ratios(i,r){const stock=state.resultats[r].stock[i],ajout=state.resultats[r].regles[state.regle].ajout[i];return {avant:state.eleves[i]/stock,apres:state.eleves[i]/(stock+ajout),ajout};}
 function tableau(){const lignes=visibles();$('compte-lignes').textContent=`${lignes.length} provinces affichées sur 45 · export toujours national · ${state.scenario.label}`;
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
   const ratio=ratios(i,r).apres;path.setAttribute('fill',couleur(ratio/state.seuils[r]));path.setAttribute('fill-rule','evenodd');path.setAttribute('class','province'+(selected===i?' active':''));path.setAttribute('tabindex','0');path.setAttribute('role','button');path.setAttribute('aria-label',`${p.province}, ${fmt(ratio,1)} élèves par ${r==='maitres'?'maître':'salle'} après allocation`);
   const title=document.createElementNS(svg.namespaceURI,'title');title.textContent=`${p.province} · ${p.region}\n${fmt(state.eleves[i])} élèves · ratio après : ${fmt(ratio,1)}\n+${fmt(ratios(i,r).ajout)} ${r==='maitres'?'maîtres':'salles'}\nESU au ${dateFr(data.meta.date_esu)} : déplacés ${esuValeur(p.esu,'eleves_deplaces')}`;path.append(title);
   path.addEventListener('mouseenter',()=>detail(i));path.addEventListener('focus',()=>detail(i));path.addEventListener('click',()=>{selected=i;detail(i);carte();});path.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();selected=i;detail(i);carte();}});svg.append(path);
  }
 }
 function esuValeur(esu,key){
  const absent=!esu||esu[key]===null||esu[key]===undefined;
  if(esu&&esu[key+'_statut']==='partiel')return absent?'partiel · total non renseigné':fmt(esu[key])+' (partiel, total non établi)';
  return absent?'non renseigné':fmt(esu[key]);
 }
 function detail(i){const p=data.provinces[i],m=ratios(i,'maitres'),s=ratios(i,'salles');
  $('detail').innerHTML=`<p class="eyebrow">${esc(p.region)}</p><h3>${esc(p.province)}</h3><p class="small">${esc(state.scenario.label)} · ${fmt(state.eleves[i])} élèves</p><dl><dt>Maîtres · stock + ajout</dt><dd>${fmt(p.maitres)} + ${fmt(m.ajout)}</dd><dt>Élèves / maître</dt><dd>${fmt(m.avant,1)} → ${fmt(m.apres,1)}</dd><dt>Salles · stock + ajout</dt><dd>${fmt(p.salles)} + ${fmt(s.ajout)}</dd><dt>Élèves / salle</dt><dd>${fmt(s.avant,1)} → ${fmt(s.apres,1)}</dd></dl><hr><h3>Contexte ESU · ${esc(dateFr(data.meta.date_esu))}</h3><dl><dt>Écoles rouvertes</dt><dd>${esuValeur(p.esu,'ecoles_rouvertes')}</dd><dt>Écoles délocalisées</dt><dd>${esuValeur(p.esu,'ecoles_delocalisees')}</dd><dt>Élèves déplacés</dt><dd>${esuValeur(p.esu,'eleves_deplaces')}</dd></dl><p class="small">Public / privé non distingués. Valeur absente : non renseigné. Ce contexte daté ne garantit pas l’accessibilité actuelle.</p>`;
 }
 function exporter(){if(!state){erreur(Error('Recalculez une simulation valide avant l’export.'));return;}
  const entete=['annee_scolaire','annee_stocks','scenario','hypothese','regle','budget_maitres_unites','budget_salles_unites','seuil_simulation_maitres','seuil_simulation_salles','perimetre','province','region','eleves','maitres_existants','maitres_ajoutes','ratio_maitre_avant','ratio_maitre_apres','salles_existantes','salles_ajoutees','ratio_salle_avant','ratio_salle_apres','date_esu'];
  const rows=data.provinces.map((p,i)=>{const m=ratios(i,'maitres'),s=ratios(i,'salles');return [state.scenario.id==='actuel'?data.meta.annee:data.meta.horizon,data.meta.annee,state.scenario.id,hypotheseComplete(state.scenario),state.regle,state.budgets.maitres,state.budgets.salles,state.seuils.maitres,state.seuils.salles,'national_45_provinces',p.province,p.region,state.eleves[i],p.maitres,m.ajout,m.avant.toFixed(6),m.apres.toFixed(6),p.salles,s.ajout,s.avant.toFixed(6),s.apres.toFixed(6),data.meta.date_esu];});
  const quote=v=>'"'+String(v??'').replace(/"/g,'""')+'"';const csv='\ufeff'+[entete,...rows].map(row=>row.map(quote).join(';')).join('\r\n');const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download=`allocation_45_provinces_${state.scenario.id}_${state.regle}.csv`;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
 }
 try{initialiser();}catch(e){erreur(e);}
})();
