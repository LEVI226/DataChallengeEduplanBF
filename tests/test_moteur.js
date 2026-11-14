'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const target = path.join(__dirname, '../tableau_de_bord/moteur.js');
assert.ok(fs.existsSync(target), 'Le moteur doit exister');
const {repartir, mesurer} = require(target);
assert.deepEqual(repartir([100,200,20],[1,1,1],2,'franchissement',50),[1,1,0]);
const v5 = require(target).repartirSeuil([100,200,20],[1,1,1],2,50);
assert.deepEqual(v5.ajout_seuil,[1,0,0]);
assert.deepEqual(v5.ajout_reliquat,[0,1,0]);
assert.equal(v5.cout_province_supplementaire,4);
assert.equal(require(target).unitesPlafond([120,60],[1,1],50),3);
assert.equal(require(target).unitesPlafond([39420],[891],43.8),9);
assert.equal(require(target).unitesPlafond([63],[89],.7),1);
assert.deepEqual(require(target).repartirSeuil([39420],[891],9,43.8).ajout_seuil,[9]);
const e = [120, 60, 20], s = [1, 1, 1];
assert.deepEqual(repartir(e,s,3,'egalisation',50), [2,1,0]);
assert.deepEqual(repartir(e,s,3,'deficit_d_abord',50), [2,1,0]);
assert.deepEqual(repartir(e,s,3,'proportionnelle',50), [2,1,0]);
for (const r of ['egalisation','deficit_d_abord','proportionnelle']) {
 assert.deepEqual(repartir(e,s,0,r,50),[0,0,0]);
 assert.equal(repartir(e,s,20,r,50).reduce((a,b)=>a+b),20);
 assert.deepEqual(repartir([50,50,50],s,1,r,50),[1,0,0]);
}
assert.deepEqual(repartir([1,1,1],s,2,'proportionnelle',50),[1,1,0]);
assert.deepEqual(repartir([0,0], [1,1],3,'proportionnelle',50),[2,1]);
assert.deepEqual(mesurer(e,s,[2,1,0],50),{provinces_au_dessus_norme:0,eleves_en_province_au_dessus_norme:0,ratio_max:40,ratio_moyen:33.3,ecart_type_ratios:8.2,deficit_restant:0,unites_donnees_sous_la_norme:0});
assert.equal(mesurer(e,s,[0,0,0],50).deficit_restant,3);
for (const budget of [-1,1.5,NaN,Infinity,'2']) assert.throws(()=>repartir(e,s,budget,'egalisation',50));
for (const seuil of [0,-1,NaN,Infinity]) assert.throws(()=>repartir(e,s,0,'egalisation',seuil));
for (const stock of [[0,1,1],[-1,1,1],[1,1], [1,NaN,1]]) assert.throws(()=>repartir(e,stock,1,'egalisation',50));
assert.throws(()=>repartir([-1,2], [1,1],1,'egalisation',50));
assert.throws(()=>repartir(e,s,1,'inconnue',50));
assert.throws(()=>mesurer(e,s,[-1,0,0],50));
// Une énumération indépendante vérifie le meilleur pire ratio possible sur un petit cas.
const a = repartir([170,90,45], [2,1,1],4,'egalisation',50);
const obtenu = Math.max(...[170,90,45].map((v,i)=>v/([2,1,1][i]+a[i])));
for(let x=0;x<=4;x++) for(let y=0;y<=4-x;y++) {
 const z=4-x-y;
 assert.ok(obtenu<=Math.max(170/(2+x),90/(1+y),45/(1+z))+1e-12);
}
console.log('Moteur : exemples manuels, égalités stables, budget zéro, dépassement des besoins, optimalité et refus invalides OK.');
