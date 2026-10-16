import {normalizeWeights,priorityScores} from './decision-engine.js';
const $=s=>document.querySelector(s);const esc=s=>String(s).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
async function load(){try{const r=await fetch('../data/processed/dataset.json');if(!r.ok)throw new Error(r.status);return await r.json()}catch(e){return null}}
const DATA=await load();
const ok=!!(DATA&&DATA.sites&&DATA.sites.length);
if(!ok)document.querySelector('main').innerHTML='<div class="card" role="alert"><h2>Data failed to load</h2><p>Could not read data/processed/dataset.json. Run <code>python -m analysis.run_pipeline</code>, then serve the repository root with <code>python -m http.server</code> and open /frontend/.</p></div>';
const IND=ok?DATA.indicators.map(i=>({k:i.key,l:i.label,u:i.unit,d:i.direction,w:Math.round(i.default_weight*100),note:i.note})):[];
const SITES=ok?DATA.sites.map(s=>({id:s.id,name:s.name,lat:s.lat,lon:s.lon,type:s.record_type,period:s.period,v:s.values})):[];
const SCEN=ok?Object.fromEntries(Object.entries(DATA.scenarios).map(([n,w])=>[n,Object.fromEntries(Object.entries(w).map(([k,x])=>[k,Math.round(x*100)]))])):{};
let W={};IND.forEach(i=>W[i.k]=i.w);let sel=new Set(SITES.slice(0,3).map(s=>s.id)),sortK='name',sortD=1,cur=SITES[0]?.id,chart;
function validate(w){const v=Object.values(w);if(v.some(x=>x<0||isNaN(x)))return'Weights must be non-negative numbers.';if(v.reduce((a,b)=>a+b,0)===0)return'At least one weight must be above zero.';return''}
function score(raw){if(validate(raw))return null;const res=priorityScores(SITES.map(s=>({id:s.id,values:s.v})),IND.map(i=>({key:i.k,direction:i.d})),normalizeWeights(raw));
 return res.map(o=>({s:SITES.find(x=>x.id===o.id),sc:o.score,c:o.contrib,rank:o.rank,miss:o.missing.map(k=>IND.find(i=>i.k===k).l)}))}
const DEF=ok?score(Object.fromEntries(IND.map(i=>[i.k,i.w]))):[];
const fmt=(x,d=1)=>x==null?'—':(+x).toFixed(d);
// ---- views ----
const TABS=[['overview','Overview'],['map','Map'],['compare','Compare'],['lab','Decision Lab'],['method','Methodology'],['export','Export']];
$('#nav').innerHTML=TABS.map(t=>`<button role="tab" data-t="${t[0]}">${t[1]}</button>`).join('');
function show(t){document.querySelectorAll('section').forEach(s=>s.classList.toggle('on',s.id===t));document.querySelectorAll('nav button').forEach(b=>b.setAttribute('aria-selected',b.dataset.t===t));if(t==='compare')drawChart()}
$('#nav').onclick=e=>{if(e.target.dataset.t)show(e.target.dataset.t)};
function overview(){const cells=SITES.length*IND.length,have=SITES.reduce((a,s)=>a+IND.filter(i=>s.v[i.k]!=null).length,0);
 const top=[...DEF].filter(o=>o.sc!=null).sort((a,b)=>a.rank-b.rank)[0];const inc=DEF.filter(o=>o.miss.length||SITES.find(s=>s===o.s&&IND.some(i=>s.v[i.k]==null))).length;
 $('#overview').innerHTML=`<div class="card"><h2>Which locations should be investigated first?</h2><p class="mut">A transparent weighted-scoring demo. A high score means a site ranks highly under the chosen weights, not that it is objectively the most dangerous.</p></div>
 <div class="grid"><div class="card"><div class="big">${SITES.length}</div>locations <span class="tag">synthetic</span></div><div class="card"><div class="big">${fmt(100*have/cells,0)}%</div>indicator completeness (${have}/${cells} values)</div><div class="card"><div class="big">${IND.length}</div>indicators</div></div>
 <div class="card"><h3>Example insight (default weights)</h3><p><b>Observation:</b> ${top.s.name} ranks first with ${fmt(top.sc)} points.<br><b>Interpretation:</b> It scores high on the indicators weighted most heavily; this is a model result.<br><b>Limitation:</b> Synthetic data, user-chosen weights.<br><b>Next step:</b> Replace with verified real observations and re-run the sensitivity check.</p></div>
 <div class="card"><h3>Scope</h3><p class="mut">Decision-support prototype. It does not solve congestion and does not identify the most dangerous roads. ${SITES.filter(s=>IND.some(i=>s.v[i.k]==null)).map(s=>s.name).join(', ')} has missing data (shown as "—", never as zero).</p></div>`}
function mapView(){const la=SITES.map(s=>s.lat),lo=SITES.map(s=>s.lon),a=Math.min(...la)-.01,b=Math.max(...la)+.01,c=Math.min(...lo)-.01,d=Math.max(...lo)+.01;
 const X=o=>40+(o-c)/(d-c)*520,Y=l=>340-(l-a)/(b-a)*320;
 const dots=DEF.map(o=>{const col=o.sc==null?'#777':`hsl(${40-o.sc*.4},80%,${70-o.sc*.25}%)`;return`<g><circle tabindex="0" role="button" aria-label="${o.s.name}, score ${fmt(o.sc)}" data-id="${o.s.id}" cx="${X(o.s.lon)}" cy="${Y(o.s.lat)}" r="${o.s.id===cur?15:11}" fill="${col}" stroke="#fff" stroke-width="${o.s.id===cur?3:1}" style="cursor:pointer"/><text x="${X(o.s.lon)+16}" y="${Y(o.s.lat)+4}">${o.s.name}</text></g>`}).join('');
 const s=SITES.find(x=>x.id===cur),o=DEF.find(x=>x.s===s);
 $('#map').innerHTML=`<div class="card"><h2>Schematic map</h2><p class="mut">Illustrative layout from the sample coordinates. No basemap tiles are loaded (the hosting page blocks external map tiles). Marker colour = default priority score (derived).</p>
 <svg class="map" viewBox="0 0 600 360" id="svgmap">${dots}</svg><p class="mut">Legend: <span style="color:hsl(40,80%,70%)">low score</span> → <span style="color:hsl(0,80%,45%)">high score</span>; grey = incomplete.</p></div>
 <div class="card"><h3>${s.name} <span class="tag">synthetic</span></h3><p class="mut">${s.lat}, ${s.lon} · ${s.period}</p><ul>${IND.map(i=>`<li>${i.l}: ${s.v[i.k]==null?'<b>missing</b>':s.v[i.k]+' '+i.u} <span class="mut">(observed-type field)</span></li>`).join('')}</ul><p>Derived score: ${fmt(o.sc)} (rank ${o.rank??'n/a'})</p></div>`;
 const pick=e=>{const id=e.target.dataset?.id;if(id){cur=id;mapView()}};$('#svgmap').onclick=pick;$('#svgmap').onkeydown=e=>{if(e.key==='Enter'||e.key===' ')pick(e)}}
function compare(){const rows=SITES.filter(s=>sel.has(s.id)).sort((a,b)=>{const x=sortK==='name'?a.name:a.v[sortK],y=sortK==='name'?b.name:b.v[sortK];return(x==null)-(y==null)||(x>y?1:x<y?-1:0)*sortD});
 $('#compare').innerHTML=`<div class="card"><h2>Compare 2–4 locations</h2><div id="chk">${SITES.map(s=>`<label><input type="checkbox" value="${s.id}" ${sel.has(s.id)?'checked':''}> ${s.name}</label>`).join('')}</div><p class="mut" id="cmsg"></p>
 <div class="sc"><table><tr><th data-k="name">Location</th>${IND.map(i=>`<th data-k="${i.k}">${i.l} (${i.u})</th>`).join('')}<th>Complete</th></tr>${rows.map(s=>`<tr><td>${s.name}</td>${IND.map(i=>`<td>${s.v[i.k]??'—'}</td>`).join('')}<td>${IND.filter(i=>s.v[i.k]!=null).length}/${IND.length}</td></tr>`).join('')}</table></div>
 <p class="mut">Click a header to sort. Indicators have different units and are not combined here; only the Decision Lab normalises them.</p>
 <select id="ci" aria-label="Indicator to chart">${IND.map(i=>`<option value="${i.k}">${i.l} (${i.u})</option>`).join('')}</select><canvas id="cv" height="160" aria-label="Bar chart"></canvas></div>`;
 $('#chk').onchange=e=>{const id=e.target.value;if(e.target.checked){if(sel.size>=4){e.target.checked=false;$('#cmsg').textContent='Maximum is 4 locations.';return}sel.add(id)}else{if(sel.size<=2){e.target.checked=true;$('#cmsg').textContent='Keep at least 2 locations.';return}sel.delete(id)}compare();drawChart()};
 document.querySelectorAll('#compare th[data-k]').forEach(h=>h.onclick=()=>{sortD=sortK===h.dataset.k?-sortD:1;sortK=h.dataset.k;compare();drawChart()});$('#ci').onchange=drawChart}
function drawChart(){const cv=$('#cv');if(!cv)return;if(typeof Chart==='undefined'){cv.outerHTML='<p class="mut">Chart library unavailable; see the table above.</p>';return}
 const k=$('#ci').value,i=IND.find(x=>x.k===k),ss=SITES.filter(s=>sel.has(s.id));if(chart)chart.destroy();
 chart=new Chart(cv,{type:'bar',data:{labels:ss.map(s=>s.name),datasets:[{label:i.l+' ('+i.u+')',data:ss.map(s=>s.v[k]),backgroundColor:'#e0a43a'}]},options:{color:'#ecebe6',scales:{x:{ticks:{color:'#a3a7ad'}},y:{ticks:{color:'#a3a7ad'},title:{display:true,text:i.u,color:'#a3a7ad'}}},plugins:{legend:{labels:{color:'#ecebe6'}}}}})}
const COL=['#e0a43a','#6fa8dc','#93c47d','#c27ba0'];
function lab(){const err=validate(W),res=err?null:score(W),t=Object.values(W).reduce((a,b)=>a+b,0);
 $('#lab').innerHTML=`<div class="card"><h2>Decision Lab</h2><p class="mut">Weights are user-selected assumptions, not empirical values. Sliders are rescaled to sum to 1.</p>
 ${IND.map(i=>`<label>${i.l} (${i.d>0?'higher':'lower'} value = higher priority): <b>${W[i.k]}</b> → ${t?fmt(W[i.k]/t,2):'—'}<input type="range" min="0" max="100" value="${W[i.k]}" data-k="${i.k}" aria-label="${i.l} weight"></label>`).join('')}
 <button class="b" id="rst">Reset to default</button> <p role="alert" style="color:#f08a7a">${err}</p>
 <p class="mut">Score_i = 100 × Σ w_j · n_ij, with n_ij min-max normalised (flipped if lower = higher priority; 0.5 if all values are equal). Missing values: indicator dropped for that site and remaining weights renormalised; site flagged incomplete.</p></div>
 ${res?`<div class="card sc"><h3>Ranking</h3><table><tr><th>Rank</th><th>Site</th><th>Score</th><th>Before</th><th>Contributions</th></tr>${[...res].sort((a,b)=>(a.rank??99)-(b.rank??99)).map(o=>{const d=DEF.find(x=>x.s===o.s).rank;const ch=o.rank==null?'':o.rank<d?' ▲':o.rank>d?' ▼':'';return`<tr><td>${o.rank??'—'}${ch}</td><td>${o.s.name}${o.miss.length?' <span class="tag">incomplete</span>':''}</td><td>${fmt(o.sc)}</td><td>${d}</td><td><div class="bar" title="${IND.map(i=>i.l+': '+fmt(o.c[i.k]??0)).join(', ')}">${IND.map((i,n)=>`<i style="width:${o.c[i.k]??0}%;background:${COL[n]}"></i>`).join('')}</div></td></tr>`}).join('')}</table>
 <p class="mut">${IND.map((i,n)=>`<span style="color:${COL[n]}">■</span> ${i.l}`).join(' ')}</p></div>${sens()}`:''}`;
 document.querySelectorAll('#lab input[type=range]').forEach(r=>r.oninput=()=>{W[r.dataset.k]=+r.value;lab();const el=document.querySelector(`[data-k="${r.dataset.k}"]`);el&&el.focus()});$('#rst').onclick=()=>{IND.forEach(i=>W[i.k]=i.w);lab()}}
function sens(){const R={};Object.entries(SCEN).forEach(([n,w])=>score(w).forEach(o=>(R[o.s.id]=R[o.s.id]||[]).push(o.rank)));
 return`<div class="card sc"><h3>Sensitivity analysis</h3><table><tr><th>Site</th>${Object.keys(SCEN).map(n=>`<th>${n}</th>`).join('')}<th>Range</th></tr>${SITES.map(s=>{const r=R[s.id],v=r.filter(x=>x!=null),g=v.length?Math.max(...v)-Math.min(...v):0;return`<tr><td>${s.name}</td>${r.map(x=>`<td>${x??'—'}</td>`).join('')}<td>${g}${g>=2?' <span class="tag">sensitive</span>':''}</td></tr>`}).join('')}</table><p class="mut">Rank range ≥ 2 across scenarios is flagged as sensitive (an arbitrary, documented cut-off). Sensitive rankings should not be treated as firm.</p></div>`}
function method(){$('#method').innerHTML=`<div class="card"><h2>Methodology</h2><p><b>Question:</b> if resources were limited, which locations should be investigated first, and on what evidence?</p>
<h3>Data</h3><p>Dataset: synthetic sample loaded from data/processed/dataset.json (produced by the Python pipeline; one value deliberately missing). Source: generated for this demo, not from any publisher. Period: invented. Licence: none needed. Limitation: no real-world meaning.</p>
<p class="mut">Candidate real sources (unverified): data.gov.bd transport, RHD traffic survey, Mendeley Bangladeshi Traffic Flow Dataset, OpenStreetMap (ODbL). Their coverage, licences and coordinates still need checking.</p>
<h3>Indicators</h3><ul>${IND.map(i=>`<li>${i.l} (${i.u}): ${i.note}</li>`).join('')}</ul>
<h3>Scoring</h3><p>Min-max normalisation per indicator, direction-adjusted; weighted sum ×100; missing indicators excluded and weights renormalised; ties share a rank. Sensitivity: four weighting scenarios.</p>
<h3>Cannot conclude</h3><p>That any site is objectively dangerous, congested, or that an intervention will work.</p>
<h3>Glossary</h3><p class="mut"><b>Min-max normalisation:</b> rescales values to 0–1. <b>Sensitivity analysis:</b> checking whether rankings change when weights change.</p></div>`}
function exp(){const res=score(W);const rows=[['site','lat','lon',...IND.map(i=>i.k+'_'+i.u),'score','rank','record_type']];
 (res||[]).forEach(o=>rows.push([o.s.name,o.s.lat,o.s.lon,...IND.map(i=>o.s.v[i.k]??''),o.sc==null?'':fmt(o.sc,2),o.rank??'',o.s.type]));
 $('#export').innerHTML=`<div class="card"><h2>Export</h2><p class="mut">CSV reflects the current Decision Lab weights (${IND.map(i=>i.k+'='+W[i.k]).join(', ')}). Direct file download is not available on this page, so copy the text below. PDF export is a planned feature.</p><textarea id="csv" readonly>${esc(rows.map(r=>r.join(',')).join('\n'))}</textarea><button class="b" id="cp">Copy CSV</button> <span id="cm" class="mut"></span></div>`;
 $('#cp').onclick=()=>{$('#csv').select();try{navigator.clipboard.writeText($('#csv').value);$('#cm').textContent='Copied'}catch(e){$('#cm').textContent='Select and copy manually'}}}
function all(){overview();mapView();compare();lab();method();exp()}if(ok){all();show('overview')}
document.querySelector('nav').addEventListener('click',e=>{if(e.target.dataset.t==='export')exp();if(e.target.dataset.t==='lab')lab()});
