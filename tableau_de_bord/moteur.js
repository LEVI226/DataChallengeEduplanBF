/* Moteur autonome : mêmes critères que code/05_repartition.py. */
(function(root, factory) {
 'use strict';
 if(typeof module === 'object' && module.exports) module.exports = factory();
 else root.DCBEngine = factory();
})(typeof globalThis !== 'undefined' ? globalThis : this, function() {
 'use strict';
 const REGLES = ['proportionnelle','deficit_d_abord','egalisation','franchissement'];
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
  if(regle==='franchissement') return repartirSeuil(eleves,existant,budget,seuil).ajout;
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
   provinces_au_dessus_norme:eleves.filter((v,i)=>plafondStock(v,seuil)>existant[i]+ajout[i]).length,
   eleves_en_province_au_dessus_norme:eleves.reduce((a,v,i)=>a+(ratio[i]>seuil?v:0),0),
   ratio_max:round(Math.max(...ratio)),
   ratio_moyen:round(eleves.reduce((a,b)=>a+b,0)/existant.reduce((a,v,i)=>a+v+ajout[i],0)),
   ecart_type_ratios:round(Math.sqrt(ratio.reduce((a,v)=>a+(v-moyenne)**2,0)/ratio.length)),
   deficit_restant:eleves.reduce((a,v,i)=>a+Math.max(0,plafondStock(v,seuil)-existant[i]-ajout[i]),0),
   unites_donnees_sous_la_norme:ajout.reduce((a,v,i)=>a+(eleves[i]/existant[i]<=seuil?v:0),0)
  };
 }
 // Conversion décimale exacte, y compris notation exponentielle. BigInt
 // évite de créer une unité fictive à la frontière d'un seuil décimal.
 function fractionDecimale(v){
  const [base,exp='0']=String(v).toLowerCase().split('e');
  const parties=base.split('.'),decimales=(parties[1]||'').length;
  let n=BigInt(parties.join('')),d=1n,p=Number(exp)-decimales;
  if(p>=0)n*=10n**BigInt(p);else d=10n**BigInt(-p);
  return [n,d];
 }
 function plafondStock(e,seuil){
  const [en,ed]=fractionDecimale(e),[sn,sd]=fractionDecimale(seuil);
  const n=en*sd,d=ed*sn,v=Number((n+d-1n)/d);
  if(!Number.isSafeInteger(v))throw Error('Seuil trop petit pour un calcul entier fiable.');
  return v;
 }
 function unitesPlafond(eleves,existant,plafond) {
  valider(eleves,existant,plafond);
  return eleves.reduce((s,v,i)=>s+Math.max(0,plafondStock(v,plafond)-existant[i]),0);
 }
 function repartirSeuil(eleves,existant,budget,seuil=50) {
  valider(eleves,existant,seuil);
  if(!Number.isSafeInteger(budget)||budget<0) throw Error('Moyens entiers positifs ou nuls attendus.');
  const couts=eleves.map((v,i)=>Math.max(0,plafondStock(v,seuil)-existant[i]));
  const ordre=couts.map((c,i)=>i).filter(i=>couts[i]>0).sort((a,b)=>couts[a]-couts[b]||a-b);
  const ajout=eleves.map(()=>0);let reste=budget,completees=0;
  for(const i of ordre){if(couts[i]>reste)break;ajout[i]=couts[i];reste-=couts[i];completees++;}
  const ajout_seuil=ajout.slice(),reliquat=reste;
  for(let j=0;j<reste;j++){
   let meilleur=0;
   for(let i=1;i<eleves.length;i++)if(eleves[i]/(existant[i]+ajout[i])>eleves[meilleur]/(existant[meilleur]+ajout[meilleur]))meilleur=i;
   ajout[meilleur]++;
  }
  return {ajout,ajout_seuil,ajout_reliquat:ajout.map((v,i)=>v-ajout_seuil[i]),provinces_ramenees:completees,
   cout_franchissement:budget-reliquat,reliquat,cout_province_supplementaire:completees<ordre.length?ordre.slice(0,completees+1).reduce((s,i)=>s+couts[i],0):null};
 }
 return {repartir,mesurer,REGLES,repartirSeuil,unitesPlafond};
});
