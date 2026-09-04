#!/usr/bin/env python3
"""Tres capas: nivel gratuito (40 personas, 1/día), clave propia (BYOK) y código abierto. Landing + Modo + plan."""
import sys, os
P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'public', 'index.html')
src = open(P, encoding='utf-8').read()
def rep(old, new, count=1):
    global src
    n = src.count(old)
    if n != count: sys.exit(f'ANCLA ({n}, esperaba {count}): {old[:100]!r}')
    src = src.replace(old, new)
ic = lambda name, size=15: f'<svg width="{size}" height="{size}" aria-hidden="true"><use href="#{name}"/></svg>'

# ---------- estado + api con cabecera ----------
rep("  resultado:null, ensayoId:null, estado:null, token:null\n};", "  resultado:null, ensayoId:null, estado:null, token:null, clave:null\n};\ntry{S.clave=sessionStorage.getItem('clave')||null}catch(e){}")
rep("  const r=await fetch('/api/'+ruta,{method:metodo||(body?'POST':'GET'),headers:{'Content-Type':'application/json'},body:body?JSON.stringify(body):undefined});",
    "  const cab={'Content-Type':'application/json'}; if(S.clave)cab['x-clave-propia']=S.clave;\n  const r=await fetch('/api/'+ruta,{method:metodo||(body?'POST':'GET'),headers:cab,body:body?JSON.stringify(body):undefined});")

# ---------- Modo: fichas dinámicas + clave ----------
rep('<p class="hint">El ensayo estándar cubre la mayoría de los casos. Cada conexión dispone de un número limitado de ensayos por día.</p>',
    '<p class="hint" id="modoHint">Sin clave, cada conexión tiene un ensayo de muestra al día. Con tu propia clave de Anthropic, la sala completa y sin límite.</p>')
rep('<div class="spec"><div class="ic">' + ic("i-users", 16) + '</div><div><b>80 personas</b><span>panel muestreado de la audiencia elegida</span></div></div>',
    '<div class="spec"><div class="ic">' + ic("i-users", 16) + '</div><div><b id="specN">40 personas</b><span id="specNsub">ensayo de muestra · con clave propia, 80</span></div></div>')
rep('''    <div class="exp"><div><b>Modo experto</b><span>Tamaño del panel, corridas de estabilidad, semilla y exportación de datos crudos.</span></div><label class="switch"><input type="checkbox" id="labToggle" onchange="toggleLab()"><span class="slider-t"></span></label></div>
''', '''    <div class="exp"><div><b>Modo experto</b><span>Tamaño del panel, corridas de estabilidad, semilla y exportación de datos crudos.</span></div><label class="switch"><input type="checkbox" id="labToggle" onchange="toggleLab()"><span class="slider-t"></span></label></div>
    <div class="exp clave-row"><div><b>Usar mi propia clave de Anthropic</b><span>Sin límite diario y con la sala completa: hasta 140 personas y corridas de estabilidad. La clave no se guarda en ningún servidor: vive solo en esta pestaña y se usa únicamente para llamar al modelo. <a href="https://console.anthropic.com/settings/keys" target="_blank" rel="noopener">¿Dónde la consigo?</a></span></div></div>
    <div class="clave-caja">
      <div class="clave-form" id="claveForm"><input type="password" id="claveInput" placeholder="sk-ant-…" autocomplete="off" spellcheck="false" aria-label="API key de Anthropic"><button class="btn btn-s" onclick="guardarClave()">Usar clave</button></div>
      <div class="clave-activa" id="claveActiva" style="display:none"><span class="chip ok">''' + ic('i-check', 12) + ''' <span id="claveTxt">Clave activa</span></span><button class="btn btn-t" onclick="quitarClave()">Quitar</button></div>
      <div class="helper" id="claveError" style="color:var(--mal);display:none"></div>
    </div>
''')
# aviso en el panel experto
rep('''      <div class="g-titulo">Parámetros del instrumento</div>''', '''      <div class="g-titulo">Parámetros del instrumento</div><p class="helper" id="geekAviso" style="margin-bottom:10px;color:var(--warn);display:none">Sin clave propia, el panel queda en 40 personas y una corrida. Semilla, pase adversarial y exportación sí aplican.</p>''')

rep('''function toggleLab(){''', '''function pintarClave(){
  const act=!!S.clave, nG=(S.estado&&S.estado.nGratis)||40;
  const f=document.getElementById('claveForm'), a=document.getElementById('claveActiva');
  if(f)f.style.display=act?'none':'flex'; if(a)a.style.display=act?'flex':'none';
  if(act)document.getElementById('claveTxt').textContent='Clave activa · termina en '+S.clave.slice(-4)+' · sin límite diario';
  const n=document.getElementById('specN'), ns=document.getElementById('specNsub');
  if(n)n.textContent=(act?80:nG)+' personas';
  if(ns)ns.textContent=act?'panel muestreado de la audiencia elegida':'ensayo de muestra · con clave propia, 80';
  ['gN','gK'].forEach(id=>{const e=document.getElementById(id);if(e)e.disabled=!act});
  const av=document.getElementById('geekAviso'); if(av)av.style.display=act?'none':'block';
  const h=document.getElementById('modoHint'); if(h)h.textContent=act?'Estás usando tu propia clave: el ensayo estándar es de 80 personas y no hay límite diario.':'Sin clave, cada conexión tiene un ensayo de muestra al día. Con tu propia clave de Anthropic, la sala completa y sin límite.';
}
function guardarClave(){
  const inp=document.getElementById('claveInput'), err=document.getElementById('claveError');
  const v=(inp.value||'').trim();
  if(!/^sk-ant-[A-Za-z0-9_-]{20,}$/.test(v)){err.style.display='block';err.textContent='Eso no parece una API key de Anthropic: empiezan con sk-ant-.';return}
  err.style.display='none'; S.clave=v; inp.value='';
  try{sessionStorage.setItem('clave',v)}catch(e){}
  pintarClave();
}
function quitarClave(){S.clave=null;try{sessionStorage.removeItem('clave')}catch(e){}pintarClave()}
function toggleLab(){''')
rep("async function irApp(){try{S.estado=await api('estado')}catch(e){S.estado=null}await personasListas;",
    "async function irApp(){try{S.estado=await api('estado')}catch(e){S.estado=null}pintarClave();await personasListas;")

# ---------- leerGeek: nivel gratuito ----------
rep('''  } else {S.n=80;S.k=1;S.adv=true;S.raw=false;S.seed=503}
}''', '''  } else {S.n=80;S.k=1;S.adv=true;S.raw=false;S.seed=503}
  if(!S.clave){S.n=(S.estado&&S.estado.nGratis)||40;S.k=1}
}''')
# plan: pie con cuota o clave
rep("    +'<div><b>'+(S.estado?(Math.max(0,S.estado.limite-S.estado.usados))+' de '+S.estado.limite:'—')+'</b>ensayos disponibles hoy</div>'",
    "    +(S.clave?'<div><b>Clave propia</b>sin límite diario · el costo va a tu cuenta</div>':'<div><b>'+(S.estado?(Math.max(0,S.estado.limite-S.estado.usados))+' de '+S.estado.limite:'—')+'</b>ensayos de muestra disponibles hoy</div>')")
rep("    S.token=r.token; S.ensayoServidor=r.ensayo; S.modelo=r.modelo;\n    if(S.estado){S.estado.usados=Math.max(0,S.estado.limite-r.restantes)}",
    "    S.token=r.token; S.ensayoServidor=r.ensayo; S.modelo=r.modelo;\n    if(r.n)S.n=r.n; if(r.k)S.k=r.k;\n    if(S.estado&&r.restantes!==null&&r.restantes!==undefined){S.estado.usados=Math.max(0,S.estado.limite-r.restantes)}")

# ---------- Landing: tres formas ----------
rep('''<section class="sec" style="padding-top:0"><div class="wrap">
  <div class="honesto">''', '''<section class="sec" id="formas" style="padding-top:0"><div class="wrap">
  <h2>Tres formas de usar la sala</h2>
  <p class="sub">Queremos que probar una idea sea fácil, no un proyecto. Por eso hay tres caminos, y los tres llevan al mismo reporte.</p>
  <div class="formas">
    <div class="forma"><div class="ic">''' + ic('i-check') + '''</div><div class="f-etq">Gratis · sin registro</div><h3>Prueba con un ensayo de muestra</h3><p>Cada conexión tiene un ensayo al día con un panel de 40 personas. Alcanza para ver cómo reacciona El Salvador a tu idea. Lo pagamos nosotros.</p></div>
    <div class="forma"><div class="ic">''' + ic('i-lock') + '''</div><div class="f-etq">Con tu propia clave</div><h3>Desbloquea la sala completa</h3><p>Con una API key de Anthropic no hay límite diario: paneles de hasta 140 personas, corridas de estabilidad y datos crudos. Cada ensayo cuesta alrededor de US$0.20 en tu cuenta. La clave no se guarda: vive solo en tu pestaña. <a href="https://console.anthropic.com/settings/keys" target="_blank" rel="noopener">Cómo obtener una clave</a></p></div>
    <div class="forma"><div class="ic">''' + ic('i-doc') + '''</div><div class="f-etq">Código abierto</div><h3>Llévate la sala entera</h3><p>Todo el proyecto es abierto: el dataset preparado, los scripts y un despliegue en Netlify listo para tu propia instancia. Si quieres adaptarla a otro país o a tu equipo, ese es el camino. <span class="mono" style="font-size:12px;color:var(--gris-suave)">Repositorio en GitHub · pronto</span></p></div>
  </div>
</div></section>

<section class="sec" style="padding-top:0"><div class="wrap">
  <div class="honesto">''')
# CSS
rep('</style>', '''
/* ---------- tres formas + clave ---------- */
.formas{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.forma{background:var(--blanco);border:1px solid var(--linea);border-radius:var(--radio);padding:var(--esp-4);box-shadow:var(--sombra)}
.forma .ic{margin-bottom:14px}
.forma .f-etq{font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--cobalto);margin-bottom:6px}
.forma h3{font-size:16px;margin-bottom:8px}
.forma p{font-size:14px;color:var(--gris)}
.forma a{color:var(--cobalto);font-weight:500}
.clave-row{margin-top:18px}
.clave-caja{margin-top:12px}
.clave-form{display:flex;gap:10px;align-items:center}
.clave-form input{flex:1;font-family:'IBM Plex Mono',monospace;font-size:13.5px;max-width:420px}
.clave-activa{display:flex;gap:12px;align-items:center;flex-wrap:wrap}
.geek input:disabled{opacity:.4}
@media(max-width:900px){.formas{grid-template-columns:1fr}}
@media(max-width:640px){.clave-form{flex-direction:column;align-items:stretch}.clave-form input{max-width:none}}
</style>''')
open(P, 'w', encoding='utf-8').write(src); print('v3 OK', len(src))
