/* Moteur autonome : mêmes critères que code/05_repartition.py. */
(function(root, factory) {
 'use strict';
 if(typeof module === 'object' && module.exports) module.exports = factory();
 else root.DCBEngine = factory();
})(typeof globalThis !== 'undefined' ? globalThis : this, function() {
 'use strict';
 const REGLES = ['proportionnelle','deficit_d_abord','egalisation'];
 function valider(eleves, existant, seuil) {
  if(!Array.isArray(eleves)||!eleves.length||!Array.isArray(existant)||existant.length!==eleves.length) throw Error('Les tableaux doivent être non vides et de même longueur.');
  if(!eleves.every(v=>typeof v==='number'&&Number.isFinite(v)&&v>=0)) throw Error('Effectifs invalides.');
  if(!existant.every(v=>typeof v==='number'&&Number.isSafeInteger(v)&&v>0)) throw Error('Chaque stock doit être un entier strictement positif.');
  if(typeof seuil!=='number'||!Number.isFinite(seuil)||seuil<=0) throw Error('Le seuil de simulation doit être strictement positif.');
 }
 function repartir(eleves, existant, budget, regle, seuil=50) {
  valider(eleves,existant,seuil);
  if(!Number.isSafeInteger(budget)||budget<0) throw Error('Les moyens doivent être un entier positif ou nul.');
  if(!REGLES.includes(regle)) throw Error('Règle inconnue.');
  const ajout=eleves.map(()=>0);
  if(!budget) return ajout;
  if(regle==='proportionnelle') {
   const total=eleves.reduce((a,b)=>a+b,0);
   const quotas=eleves.map(v=>total ? budget*v/total : budget/eleves.length);
   quotas.forEach((v,i)=>ajout[i]=Math.floor(v));
   const ordre=quotas.map((v,i)=>({i,reste:v-ajout[i]})).sort((a,b)=>b.reste-a.reste||a.i-b.i);
   const reste=budget-ajout.reduce((a,b)=>a+b,0);
   for(let j=0;j<reste;j++) ajout[ordre[j].i]++;
   return ajout;
  }
  for(let j=0;j<budget;j++) {
   let scores=eleves.map((v,i)=>regle==='deficit_d_abord' ? v/seuil-existant[i]-ajout[i] : v/(existant[i]+ajout[i]));
   if(regle==='deficit_d_abord'&&!scores.some(v=>v>0)) scores=eleves.map((v,i)=>v/(existant[i]+ajout[i]));
   let meilleur=0;
   for(let i=1;i<scores.length;i++) if(scores[i]>scores[meilleur]) meilleur=i;
   ajout[meilleur]++;
  }
  return ajout;
 }
 function mesurer(eleves,existant,ajout,seuil=50) {
  valider(eleves,existant,seuil);
  if(!Array.isArray(ajout)||ajout.length!==eleves.length||!ajout.every(v=>Number.isSafeInteger(v)&&v>=0)) throw Error('Ajouts invalides.');
  const ratio=eleves.map((v,i)=>v/(existant[i]+ajout[i]));
  const moyenne=ratio.reduce((a,b)=>a+b,0)/ratio.length;
  const round=v=>Math.round((v+Number.EPSILON)*10)/10;
  return {
   provinces_au_dessus_norme:ratio.filter(v=>v>seuil).length,
   eleves_en_province_au_dessus_norme:eleves.reduce((a,v,i)=>a+(ratio[i]>seuil?v:0),0),
   ratio_max:round(Math.max(...ratio)),
   ratio_moyen:round(eleves.reduce((a,b)=>a+b,0)/existant.reduce((a,v,i)=>a+v+ajout[i],0)),
   ecart_type_ratios:round(Math.sqrt(ratio.reduce((a,v)=>a+(v-moyenne)**2,0)/ratio.length)),
   deficit_restant:eleves.reduce((a,v,i)=>a+Math.max(0,Math.ceil(v/seuil)-existant[i]-ajout[i]),0),
   unites_donnees_sous_la_norme:ajout.reduce((a,v,i)=>a+(eleves[i]/existant[i]<=seuil?v:0),0)
  };
 }
 return {repartir,mesurer,REGLES};
});
