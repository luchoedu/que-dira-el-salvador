#!/usr/bin/env python3
"""Genera public/index.html a partir del artefacto original aplicando los cambios de despliegue:
- índice completo de 148,000 personas (public/data) en lugar de la muestra embebida de 1,000
- llamadas al modelo a través de /api/* (la API key vive en Netlify) con cuota por conexión
- audiencias en localStorage, votos en /api/votos
- filtros nuevos: estado civil y tipo de hogar
"""
import re, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(ROOT, 'original', 'que-dira-el-salvador.artifact.html'), encoding='utf-8').read()

def rep(old, new, count=1):
    global src
    n = src.count(old)
    if n != count:
        sys.exit(f'ANCLA no encontrada exactamente {count} vez/veces ({n}): {old[:90]!r}')
    src = src.replace(old, new)

def rep_between(ini, fin, new, keep_fin=True):
    """Reemplaza desde `ini` (inclusive) hasta `fin` (exclusive si keep_fin)."""
    global src
    a = src.index(ini); b = src.index(fin, a)
    assert src.count(ini) == 1, ini[:80]
    src = src[:a] + new + (src[b:] if keep_fin else src[b + len(fin):])

# ---------- 1. Datos: índice completo ----------
ini = 'const PERSONAS_GZ="'
fin = '\nconst PRESETS=['
rep_between(ini, fin, r'''const DATA_V='1';
let PERSONAS=[],DEPTOS=[],EDUS=[],CIVILES=[],HOGARES=[],DICT=null,SALA=[];
async function _gunzipBuf(buf){
  if(typeof DecompressionStream!=='undefined'){
    const stream=new Blob([buf]).stream().pipeThrough(new DecompressionStream('gzip'));
    return new Uint8Array(await new Response(stream).arrayBuffer());
  }
  // respaldo para navegadores viejos: pako desde cdnjs
  await new Promise((res,rej)=>{const s=document.createElement('script');
    s.src='https://cdnjs.cloudflare.com/ajax/libs/pako/2.1.0/pako.min.js';s.onload=res;s.onerror=rej;document.head.appendChild(s)});
  return pako.ungzip(new Uint8Array(buf));
}
// El índice trae, para las 148,000 personas, solo los campos de filtro (1 byte por columna).
// Los textos completos viven en el servidor y solo viajan al modelo para las personas muestreadas.
const personasListas=(async()=>{
  const [dict,bin,sala]=await Promise.all([
    fetch('/data/dict.json?v='+DATA_V).then(r=>r.json()),
    fetch('/data/index.bin.gz?v='+DATA_V).then(r=>r.arrayBuffer()),
    fetch('/data/sala.json?v='+DATA_V).then(r=>r.json())
  ]);
  DICT=dict;SALA=sala;
  const n=dict.n, raw=await _gunzipBuf(bin);
  const col=i=>raw.subarray(i*n,(i+1)*n);
  const C={};dict.columnas.forEach((c,i)=>C[c]=col(i));
  const deptoDeMuni=dict.muniDepto.map(i=>dict.deptos[i]);
  const arr=new Array(n);
  for(let i=0;i<n;i++)arr[i]={id:i,sexo:dict.sexo[C.sexo[i]],edad:C.edad[i],zona:dict.zona[C.zona[i]],muni:dict.munis[C.muni[i]],depto:deptoDeMuni[C.muni[i]],edu:dict.edu[C.edu[i]],civil:dict.civil[C.civil[i]],hogar:dict.hogar[C.hogar[i]],idiomas:dict.idiomas[C.idiomas[i]]};
  PERSONAS=arr;DEPTOS=dict.deptos.slice();EDUS=dict.edu.slice();CIVILES=dict.civil.slice();HOGARES=dict.hogar.slice();
})();
const ETQ_CIVIL={casado:'Casado/a',soltero:'Soltero/a',union_libre:'Unión libre',separado:'Separado/a',viudo:'Viudo/a',divorciado:'Divorciado/a'};
const ETQ_HOGAR={extendido:'Hogar extendido',nuclear:'Hogar nuclear',monoparental:'Hogar monoparental',pareja:'Pareja sin hijos en casa',unipersonal:'Vive solo/a'};
const ETQ_EDU={ninguno:'Sin escolaridad',primaria:'Primaria',secundaria:'Secundaria',bachillerato:'Bachillerato',tecnico:'Técnico',universitario:'Universitario',posgrado:'Posgrado'};
const etq=(m,k)=>m[k]||k;
// Persistencia local (audiencias): solo en este dispositivo.
const storageLocal={async get(k){try{const v=localStorage.getItem(k);return v==null?null:{value:v}}catch(e){return null}},async set(k,v){localStorage.setItem(k,v)}};
// Llamadas a la API propia (la API key del modelo nunca sale del servidor).
async function api(ruta,body,metodo){
  const r=await fetch('/api/'+ruta,{method:metodo||(body?'POST':'GET'),headers:{'Content-Type':'application/json'},body:body?JSON.stringify(body):undefined});
  let data=null; try{data=await r.json()}catch(e){}
  if(!r.ok||!data||data.ok===false){const e=new Error((data&&data.error)||('Error '+r.status));e.status=(data&&data.status)||r.status;throw e}
  return data;
}''')

# ---------- 2. Presets + filtros nuevos ----------
rep(" {nombre:'Departamento de San Salvador',filtros:{deptos:['San Salvador'],zona:'',sexo:'',edadMin:null,edadMax:null,edu:''},preset:true}\n];",
    " {nombre:'Departamento de San Salvador',filtros:{deptos:['San Salvador'],zona:'',sexo:'',edadMin:null,edadMax:null,edu:''},preset:true},\n {nombre:'Hogares monoparentales',filtros:{deptos:[],zona:'',sexo:'',edadMin:null,edadMax:null,edu:'',hogar:'monoparental'},preset:true},\n {nombre:'Educación superior (técnico o más)',filtros:{deptos:[],zona:'',sexo:'',edadMin:null,edadMax:null,edu:'',eduMin:'tecnico'},preset:true}\n];")

rep("    if(f.edu&&p.edu!==f.edu)return false;\n    return true;",
    "    if(f.edu&&p.edu!==f.edu)return false;\n    if(f.eduMin&&EDUS.indexOf(p.edu)<EDUS.indexOf(f.eduMin))return false;\n    if(f.civil&&p.civil!==f.civil)return false;\n    if(f.hogar&&p.hogar!==f.hogar)return false;\n    return true;")

# selects nuevos en "Construir audiencia"
rep('''          <label class="lbl">Educación</label><select id="fEdu"><option value="">Todas</option></select><p class="helper">Nivel educativo alcanzado, según la clasificación del censo.</p>
        </div>''',
'''          <label class="lbl">Educación</label><select id="fEdu"><option value="">Todas</option></select><p class="helper">Nivel educativo alcanzado, según la clasificación del censo.</p>
        </div>
        <div>
          <label class="lbl">Estado civil</label><select id="fCivil"><option value="">Todos</option></select>
          <label class="lbl">Tipo de hogar</label><select id="fHogar"><option value="">Todos</option></select><p class="helper">Con quién vive, según el censo: nuclear, extendido, monoparental, pareja o unipersonal.</p>
        </div>''')

rep("  const fe=document.getElementById('fEdu'); EDUS.forEach(d=>{const o=document.createElement('option');o.value=d;o.textContent=d;fe.appendChild(o)});\n  ['fZona','fSexo','fEdadMin','fEdadMax','fEdu'].forEach(id=>document.getElementById(id).addEventListener('input',previewCrear));\n  document.getElementById('resRep').innerHTML=descPool(PERSONAS)+' Muestra viva de la sala: <b>'+PERSONAS.length+'</b> personas cargadas de 148,000 del dataset.';",
    "  const fe=document.getElementById('fEdu'); EDUS.forEach(d=>{const o=document.createElement('option');o.value=d;o.textContent=etq(ETQ_EDU,d);fe.appendChild(o)});\n  const fc=document.getElementById('fCivil'); CIVILES.forEach(d=>{const o=document.createElement('option');o.value=d;o.textContent=etq(ETQ_CIVIL,d);fc.appendChild(o)});\n  const fh=document.getElementById('fHogar'); HOGARES.forEach(d=>{const o=document.createElement('option');o.value=d;o.textContent=etq(ETQ_HOGAR,d);fh.appendChild(o)});\n  ['fZona','fSexo','fEdadMin','fEdadMax','fEdu','fCivil','fHogar'].forEach(id=>document.getElementById(id).addEventListener('input',previewCrear));\n  document.getElementById('resRep').innerHTML=descPool(PERSONAS)+' La sala completa: las <b>'+PERSONAS.length.toLocaleString('es-SV')+'</b> personas del dataset están disponibles para el muestreo.';")

rep("    edu:document.getElementById('fEdu').value};",
    "    edu:document.getElementById('fEdu').value, civil:document.getElementById('fCivil').value, hogar:document.getElementById('fHogar').value};")

# ---------- 3. Audiencias en localStorage ----------
rep("window.storage.get('audiencias')", "storageLocal.get('audiencias')", count=2)
rep("window.storage.set('audiencias',", "storageLocal.set('audiencias',", count=2)

# ---------- 4. Estado de cuota al entrar a la app ----------
rep("async function irApp(){await personasListas;",
    "async function irApp(){try{S.estado=await api('estado')}catch(e){S.estado=null}await personasListas;")
rep("  resultado:null, ensayoId:null\n};", "  resultado:null, ensayoId:null, estado:null, token:null\n};")

# fila de cuota en el plan
rep("    ['Costo estimado','~'+(llamadasQ+llamadasV+extra)+' llamadas al modelo · centavos de dólar · ~1–3 min']\n  ];",
    "    ['Costo estimado','~'+(llamadasQ+llamadasV+extra)+' llamadas al modelo · ~1–3 min'],\n    ['Tu cuota',S.estado?((Math.max(0,S.estado.limite-S.estado.usados))+' de '+S.estado.limite+' ensayos disponibles hoy para tu conexión'):'sin conexión con la sala']\n  ];")

# ---------- 5. Ejecución: llamadas vía /api ----------
ini = "async function llamarClaude(prompt){"
fin = "function progreso(pct,msj){"
rep_between(ini, fin, r'''function mezclarPersona(p,ficha){return Object.assign({},p,ficha||{})}

async function evaluarLote(lote,ronda){
  const data=await api('evaluar',{token:S.token,idea:S.idea,ids:lote.map(p=>p.id),ronda});
  return data.respuestas.map(r=>{const base=lote.find(p=>p.id===r.id)||lote[0];return {...r,persona:mezclarPersona(base,r.ficha)}});
}

async function generarVoces(sel){
  const voces=[];
  for(let i=0;i<sel.length;i+=2){
    const par=sel.slice(i,i+2);
    try{
      const data=await api('voces',{token:S.token,idea:S.idea,items:par.map(x=>({id:x.persona.id,i:x.i,obj:x.obj}))});
      data.voces.forEach(o=>{const m=sel.find(s=>s.persona.id===o.id);if(m)voces.push({...m,persona:mezclarPersona(m.persona,o.ficha),reaccion:o.reaccion})});
    }catch(e){/* una voz caída no tumba el ensayo */}
    const ult=voces[voces.length-1];
    if(ult)vivoFeed('"'+ult.reaccion.slice(0,110)+(ult.reaccion.length>110?'…':'')+'"',ult.persona.nombre+', '+ult.persona.edad+' · '+ult.persona.muni+' · voz completa',true);
    progreso(null,'Escuchando a '+(par[0]?.persona.nombre||'la sala')+'…');
  }
  return voces;
}

function seleccionarVoces(resps){
  const orden=[...resps].sort((a,b)=>b.i-a.i);
  const pick=new Set(); const out=[];
  const add=x=>{if(x&&!pick.has(x.persona.id)){pick.add(x.persona.id);out.push(x)}};
  add(orden[0]); add(orden[1]);                       // los que más prenden
  add(orden[orden.length-1]); add(orden[orden.length-2]); // los que más rechazan
  add(resps.find(r=>r.persona.zona==='rural'));
  add(resps.find(r=>r.persona.edad>=55));
  add(resps.find(r=>r.persona.edad<=28));
  add(orden[Math.floor(orden.length/2)]);
  let i=0; while(out.length<8&&i<orden.length){add(orden[i]);i++}
  return out.slice(0,8);
}

// Corre tareas con un máximo de concurrencia, conservando el orden de los resultados.
async function enParalelo(tareas,max){
  const out=new Array(tareas.length); let sig=0;
  async function obrero(){while(sig<tareas.length){const i=sig++;out[i]=await tareas[i]()}}
  await Promise.all(Array.from({length:Math.min(max,tareas.length)},obrero));
  return out;
}

async function ejecutar(){
  leerGeek();
  document.getElementById('errRun').style.display='none';
  const cmp=!!S.comparar;
  const nEf=cmp?Math.floor(S.n/2):S.n;
  // 1. Reservar el ensayo (cuota por conexión). Si no hay cupo, se informa antes de abrir la sala.
  try{
    const r=await api('ensayo',{plan:{n:S.n,k:S.k,adv:S.adv,cmp}});
    S.token=r.token; S.ensayoServidor=r.ensayo; S.modelo=r.modelo;
    if(S.estado){S.estado.usados=Math.max(0,S.estado.limite-r.restantes)}
  }catch(e){
    const err=document.getElementById('errRun');
    err.style.display='block'; err.textContent=(e.status===429?'⏳ ':'')+e.message; return;
  }
  paso(6);
  S.ensayoId=hashStr(S.idea+'|'+(cmp?S.comparar.a.nombre+S.comparar.b.nombre:S.audiencia.nombre));
  vivoInit(cmp?nEf*2:nEf, cmp?S.comparar.a.nombre+' vs '+S.comparar.b.nombre:S.audiencia.nombre);
  vivoFase('El panel entra a la sala…');
  try{
    const grupos=cmp?[{nombre:S.comparar.a.nombre,filtros:S.comparar.a.filtros},{nombre:S.comparar.b.nombre,filtros:S.comparar.b.filtros}]
                    :[{nombre:S.audiencia.nombre,filtros:S.audiencia.filtros}];
    const totalPasos=grupos.length*S.k*Math.ceil(nEf/10)+4+(S.adv?1:0)+1;
    let hecho=0; const avanza=()=>{hecho++;progreso(Math.min(96,hecho/totalPasos*100))};
    const resultados=[];
    for(const g of grupos){
      const pool=filtrarPersonas(g.filtros);
      const corridas=[];
      for(let k=0;k<S.k;k++){
        const panel=muestrear(pool,nEf,S.seed+k*97);
        const lotes=[]; for(let i=0;i<panel.length;i+=10)lotes.push(panel.slice(i,i+10));
        // Hasta 3 lotes en paralelo: el ensayo tarda un tercio y cada respuesta aparece al llegar.
        const partes=await enParalelo(lotes.map((lote,li)=>async()=>{
          progreso(null,'Panel de '+g.nombre+': personas '+(li*10+1)+'–'+Math.min(li*10+10,panel.length)+(S.k>1?' · corrida '+(k+1):''));
          let out=[];
          try{out=await evaluarLote(lote,k+1)}
          catch(e){ if(e.status===429||e.status===401)throw e; try{out=await evaluarLote(lote,k+1)}catch(e2){} }
          if(k===0)out.forEach((r,ri)=>vivoResp(r,ri*160));
          if(li===0&&k===0)vivoFase('Primeras reacciones…');
          avanza();
          return out;
        }),3);
        const resps=partes.flat();
        if(k===0)vivoFase('El panel completo respondió');
        if(!resps.length) throw new Error('El panel no devolvió respuestas. Revisa tu conexión e intenta de nuevo.');
        corridas.push(resps);
      }
      resultados.push({grupo:g,corridas});
    }
    vivoFase('Ocho voces toman la palabra');progreso(null,'Seleccionando voces por polos de reacción…');
    const principal=resultados[0].corridas[0];
    const agg=agregarTodo(resultados);
    const contexto='Score global '+agg.score.toFixed(1)+'/10. Objeciones principales: '+agg.objs.slice(0,3).map(o=>o.obj+' '+o.pct+'%').join(', ')+'. Mejor segmento: '+agg.mejorSeg+'. Peor: '+agg.peorSeg+'.';
    // Voces y pase adversarial corren a la vez.
    const [voces,adversarial]=await Promise.all([
      generarVoces(seleccionarVoces(principal)).then(v=>{avanza();return v}),
      (async()=>{ if(!S.adv)return null; vivoFase('Los escépticos toman la palabra');progreso(null,'Pase adversarial: buscando por qué falla…');
        try{const r=await api('adversarial',{token:S.token,idea:S.idea,contexto});avanza();return r.riesgos}catch(e){avanza();return null} })()
    ]);
    vivoFase('El analista redacta el reporte…');progreso(null,'Sintetizando el reporte con tu lente de '+LENTES[S.perfil].nombre.toLowerCase()+'…');
    let sintesis=null;
    for(let intento=0;intento<2&&!sintesis;intento++){
    try{
      const resumen='Score global '+agg.score.toFixed(1)+'/10, comprensión '+agg.dims.c.toFixed(1)+', atractivo '+agg.dims.a.toFixed(1)+', credibilidad '+agg.dims.cr.toFixed(1)+', relevancia '+agg.dims.r.toFixed(1)+', intención '+agg.dims.i.toFixed(1)+' (sobre 5). Polarización '+(agg.polar*100).toFixed(0)+'%. Objeción principal: '+agg.objTop+' ('+agg.objTopPct+'%). Mejor segmento: '+agg.mejorSeg+'. Peor: '+agg.peorSeg+'.'+(agg.cmpB?' Audiencia B ('+agg.cmpB.nombre+'): '+agg.cmpB.score.toFixed(1)+'/10.':'');
      const r=await api('sintesis',{token:S.token,idea:S.idea,resumen,perfil:S.perfil});
      sintesis=r.sintesis;
    }catch(e){ if(e.status===429)break; }
    }
    avanza(); progreso(100,'Listo.'); vivoFase('Ensayo completo'); vivoFin();
    S.resultado={agg,resultados,voces,adversarial,sintesis,cmp};
    setTimeout(renderReporte,400);
  }catch(e){
    vivoFin(); paso(5);
    const err=document.getElementById('errRun');
    err.style.display='block'; err.textContent='El ensayo no pudo completarse: '+e.message+' Puedes reintentar; el plan se mantiene.';
  }
}
''')

# ---------- 6. Segmentos nuevos ----------
rep("    {nombre:'Ed. superior',f:r=>/superior|universit|técnic/i.test(r.persona.edu)},",
    "    {nombre:'Ed. superior',f:r=>['tecnico','universitario','posgrado'].includes(r.persona.edu)},\n    {nombre:'Hogar monoparental',f:r=>r.persona.hogar==='monoparental'},\n    {nombre:'Vive solo/a',f:r=>r.persona.hogar==='unipersonal'},")

# ---------- 7. Votos vía API ----------
ini = "async function confirmarVoto(pid){"
fin = "function pintarVoto(pid,d){"
rep_between(ini, fin, r'''async function confirmarVoto(pid){
  const val=votoPend[pid]; if(val===undefined)return;
  const edad=document.getElementById('mpe-'+pid).value, zona=document.getElementById('mpz-'+pid).value;
  let d;
  try{const r=await api('votos',{ensayo:S.ensayoId,pid:String(pid),val:val?1:0,cal:(edad&&zona)?1:0});d=r.voto}catch(e){
    document.getElementById('vr-'+pid).textContent='No se pudo guardar el voto.';return}
  document.getElementById('mp-'+pid).style.display='none';
  pintarVoto(pid,d);
}
''')
ini = "async function cargarVotos(){"
fin = "/* ================= EXPORT + RESET ================= */"
rep_between(ini, fin, r'''async function cargarVotos(){
  try{const r=await api('votos?ensayo='+encodeURIComponent(S.ensayoId));
    Object.entries(r.votos||{}).forEach(([pid,d])=>pintarVoto(pid,d));
  }catch(e){/* sin votos aún */}
}

''')

# ---------- 8. Desfile del landing con sala.json ----------
rep("  const rnd=mulberry(42); const picks=[];\n  const idx=new Set(); while(idx.size<18)idx.add(Math.floor(rnd()*PERSONAS.length));\n  idx.forEach(i=>picks.push(PERSONAS[i]));\n",
    "  const picks=SALA.slice(0,24);\n")

# ---------- 9. Textos de metodología / privacidad / voz ----------
rep("' de '+PERSONAS.length+' personas cargadas del dataset Nemotron-Personas-El-Salvador",
    "' de las '+PERSONAS.length.toLocaleString('es-SV')+' personas del dataset Nemotron-Personas-El-Salvador")
rep("Esto es un ensayo generador de hipótesis, no una encuesta: las personas son sintéticas, las proporciones son reales. Semilla '+S.seed+'.</div>';",
    "Esto es un ensayo generador de hipótesis, no una encuesta: las personas son sintéticas, las proporciones son reales. Semilla '+S.seed+'. Modelo: '+esc(S.modelo||'Claude')+'.</div>';")
rep("<p>El texto de tu idea se envía una única vez al modelo para generar las reacciones y no se utiliza para ningún otro fin.",
    "<p>El texto de tu idea pasa por nuestro servidor solo para construir las preguntas al modelo; el servidor no la guarda, solo cuenta ensayos por conexión para evitar abusos.")
rep("+'<div class=\"voz-nota\">'+esc(p.ocup)+' · intención '+v.i+'/5 · objeción: '+esc(OBJS[v.obj]||v.obj)+'</div>'",
    "+'<div class=\"voz-nota\">'+esc(p.ocup||'')+(p.civil?' · '+esc(etq(ETQ_CIVIL,p.civil)).toLowerCase():'')+(p.hogar?' · '+esc(etq(ETQ_HOGAR,p.hogar)).toLowerCase():'')+' · intención '+v.i+'/5 · objeción: '+esc(OBJS[v.obj]||v.obj)+'</div>'")
rep("'<div class=\"voz-ficha\"><div class=\"quien-v\">'+esc(p.nombre)+', '+p.edad+'</div><div class=\"seg\">'+esc(p.zona)+' · '+esc(p.muni)+'<br>'+esc(p.depto)+' · '+esc(p.edu)+'</div></div>'",
    "'<div class=\"voz-ficha\"><div class=\"quien-v\">'+esc(p.nombre)+', '+p.edad+'</div><div class=\"seg\">'+esc(p.zona)+' · '+esc(p.muni)+'<br>'+esc(p.depto)+' · '+esc(etq(ETQ_EDU,p.edu))+'</div></div>'")
rep("<div class=\"eyebrow\">La sala de ensayo · base censal 2024 · dataset de 148,000 personas sintéticas</div>",
    "<div class=\"eyebrow\">La sala de ensayo · base censal 2024 · las 148,000 personas sintéticas del dataset</div>")
rep("<p class=\"hint\">El ensayo estándar incluye panel de 80 personas, instrumento de 5 dimensiones y pase adversarial. Para la mayoría de los casos, es todo lo necesario.</p>",
    "<p class=\"hint\">El ensayo estándar incluye panel de 80 personas, instrumento de 5 dimensiones y pase adversarial. Para la mayoría de los casos, es todo lo necesario. Cada conexión dispone de un número limitado de ensayos por día.</p>")
# favicon + descripción
rep("<title>¿Qué dirá El Salvador? · Ensayá tu idea</title>",
    "<title>¿Qué dirá El Salvador? · Ensayá tu idea</title>\n<meta name=\"description\" content=\"Prueba tu idea de negocio, campaña o producto con un panel sintético de 148,000 personas basado en el censo salvadoreño. Resultados en minutos, sin registro.\">\n<link rel=\"icon\" href=\"data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><rect width=%22100%22 height=%22100%22 rx=%2218%22 fill=%22%2314337F%22/><text x=%2250%22 y=%2270%22 font-size=%2260%22 text-anchor=%22middle%22 fill=%22%23FFC53D%22 font-family=%22serif%22 font-weight=%22bold%22>?</text></svg>\">")

os.makedirs(os.path.join(ROOT, 'public'), exist_ok=True)
out = os.path.join(ROOT, 'public', 'index.html')
open(out, 'w', encoding='utf-8').write(src)
print('OK ->', out, len(src), 'bytes')
