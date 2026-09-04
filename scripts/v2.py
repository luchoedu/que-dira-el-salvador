#!/usr/bin/env python3
"""Segunda pasada de estructura (propuesta aprobada): cabecera + pasos, Modo con fichas, Plan como orden
de trabajo, reporte con iconos y semáforo, home con vista previa y iconos."""
import sys, os, re
P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'public', 'index.html')
src = open(P, encoding='utf-8').read()
def rep(old, new, count=1):
    global src
    n = src.count(old)
    if n != count: sys.exit(f'ANCLA ({n}, esperaba {count}): {old[:100]!r}')
    src = src.replace(old, new)
def rep_between(ini, fin, new, incl_fin=False):
    global src
    assert src.count(ini) == 1, ini[:80]
    a = src.index(ini); b = src.index(fin, a) + (len(fin) if incl_fin else 0)
    src = src[:a] + new + src[b:]

SPRITE = '''<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>
<symbol id="i-sliders" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><path d="M4 7h10M18 7h2M4 17h4M12 17h8"/><circle cx="16" cy="7" r="2"/><circle cx="10" cy="17" r="2"/></symbol>
<symbol id="i-split" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><path d="M12 4v16M4 9l8-5 8 5M4 15l8 5 8-5"/></symbol>
<symbol id="i-bars" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><path d="M4 6h12M4 12h16M4 18h8"/></symbol>
<symbol id="i-alert" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M12 4l9 16H3z"/><path d="M12 10v4M12 17h.01"/></symbol>
<symbol id="i-shield" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l7 3v5c0 5-3.5 8-7 10-3.5-2-7-5-7-10V6z"/><path d="M9 12l2 2 4-4"/></symbol>
<symbol id="i-quote" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M6 15c-1.7 0-3-1.3-3-3V8h5v5c0 1.7-1.3 3-2 3zM16 15c-1.7 0-3-1.3-3-3V8h5v5c0 1.7-1.3 3-2 3z"/></symbol>
<symbol id="i-info" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/></symbol>
<symbol id="i-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></symbol>
<symbol id="i-users" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><circle cx="9" cy="8" r="3"/><path d="M3 19c0-3 3-5 6-5s6 2 6 5"/><circle cx="17" cy="9" r="2.4"/><path d="M16 14c2.5 0 5 1.6 5 4"/></symbol>
<symbol id="i-pencil" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M4 20l4-1 11-11-3-3L5 16z"/><path d="M13 8l3 3"/></symbol>
<symbol id="i-check" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12l4 4 10-10"/></symbol>
<symbol id="i-doc" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M7 3h7l5 5v13H7z"/><path d="M14 3v5h5M10 13h6M10 17h6"/></symbol>
<symbol id="i-target" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3"/></symbol>
<symbol id="i-columns" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="4" y="5" width="7" height="14" rx="1.5"/><rect x="13" y="5" width="7" height="14" rx="1.5"/></symbol>
<symbol id="i-briefcase" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"><rect x="3" y="8" width="18" height="12" rx="2"/><path d="M9 8V5h6v3M3 13h18"/></symbol>
<symbol id="i-megaphone" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"><path d="M4 10v4h3l8 5V5L7 10z"/><path d="M18 9c1.3 1.3 1.3 4.7 0 6"/></symbol>
<symbol id="i-chart" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><path d="M4 20h16M7 17v-6M12 17V7M17 17v-3"/></symbol>
<symbol id="i-compass" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M15.5 8.5l-2 5-5 2 2-5z"/></symbol>
<symbol id="i-lock" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"><rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 018 0v3"/></symbol>
<symbol id="i-user-off" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><circle cx="12" cy="8" r="3.5"/><path d="M5 20c0-3.5 3-6 7-6s7 2.5 7 6M16 4l4 4M20 4l-4 4"/></symbol>
<symbol id="i-clock" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></symbol>
</defs></svg>
'''
rep('<body>\n', '<body>\n' + SPRITE)
ic = lambda name, size=15: f'<svg width="{size}" height="{size}" aria-hidden="true"><use href="#{name}"/></svg>'

# Home: hero con vista previa
rep('''<header class="hero">
  <div class="wrap">
    <div class="eyebrow">''', '''<header class="hero">
  <div class="wrap hero-grid">
   <div class="hero-copy">
    <div class="eyebrow">''')
rep('''    <div class="sello">Esto es un ensayo, no una encuesta. Las personas son sintéticas; las proporciones son reales.</div>
  </div>
  <div class="sala-strip">''', '''    <div class="sello">Esto es un ensayo, no una encuesta. Las personas son sintéticas; las proporciones son reales.</div>
   </div>
   <div class="preview" aria-label="Ejemplo de reporte">
    <div class="etq">Ejemplo de reporte</div>
    <div class="mini-idea">"Campaña de banco digital: 'Tu dinero, sin filas ni horarios'."</div>
    <div class="mini-ver"><div class="sc">7.1<small>/10</small></div><div><div class="sem"><i></i>Conecta</div><p>El mensaje se entiende; la credibilidad cae en mayores de 50 y zona rural.</p></div></div>
    <div class="mini-dims">
      <div><div class="v">4.4</div><div class="l">Comprensión</div><div class="g"><i style="width:88%;background:var(--ok)"></i></div></div>
      <div><div class="v">3.9</div><div class="l">Atractivo</div><div class="g"><i style="width:78%;background:var(--ok)"></i></div></div>
      <div><div class="v">3.1</div><div class="l">Credibilidad</div><div class="g"><i style="width:62%;background:var(--warn)"></i></div></div>
      <div><div class="v">3.6</div><div class="l">Relevancia</div><div class="g"><i style="width:72%;background:var(--warn)"></i></div></div>
      <div><div class="v">3.5</div><div class="l">Intención</div><div class="g"><i style="width:70%;background:var(--warn)"></i></div></div>
    </div>
    <div class="mini-heat">
      <div><span>18–29</span><em><i style="width:78%;background:var(--ok)"></i></em><b>7.8</b></div>
      <div><span>Urbano</span><em><i style="width:73%;background:var(--ok)"></i></em><b>7.3</b></div>
      <div><span>Rural</span><em><i style="width:55%;background:var(--warn)"></i></em><b>5.5</b></div>
      <div><span>60+</span><em><i style="width:44%;background:var(--mal)"></i></em><b>4.4</b></div>
    </div>
   </div>
  </div>
  <div class="sala-strip">''')

for n, icon in [(1, 'i-target'), (2, 'i-pencil'), (3, 'i-users'), (4, 'i-check')]:
    rep(f'<div class="paso"><div class="n">PASO {n}</div>', f'<div class="paso"><div class="ic">{ic(icon)}</div><div class="n">PASO {n}</div>')
rep('<div class="conf-item"><h4>No se guarda en ningún lado</h4>', f'<div class="conf-item"><div class="ic">{ic("i-lock")}</div><h4>No se guarda en ningún lado</h4>')
rep('<div class="conf-item"><h4>Sin cuentas, sin correos</h4>', f'<div class="conf-item"><div class="ic">{ic("i-user-off")}</div><h4>Sin cuentas, sin correos</h4>')
rep('<div class="conf-item"><h4>El ensayo muere con la sesión</h4>', f'<div class="conf-item"><div class="ic">{ic("i-clock")}</div><h4>El ensayo muere con la sesión</h4>')
for perfil, icon in [('emprendedor', 'i-briefcase'), ('creativo', 'i-megaphone'), ('investigador', 'i-chart'), ('explorador', 'i-compass')]:
    rep(f'<button class="perfil-opt" data-perfil="{perfil}"><h3>', f'<button class="perfil-opt" data-perfil="{perfil}"><div class="ic">{ic(icon, 16)}</div><h3>')

# App: cabecera + pasos
rep('''<div id="app"><div class="app-shell">
  <div class="migas" id="migas"></div>''', '''<div id="app">
<nav class="topbar app-top"><div class="wrap">
  <div class="logo">¿Qué dirá <span class="q">El Salvador</span>?</div>
  <button class="btn-t app-salir" onclick="irLanding()">Volver al inicio</button>
</div></nav>
<div class="stepper">
  <div class="wrap"><div class="pasos-nav" id="migas"></div>
  <div class="stepper-m" id="migasM"><div class="fila"><b></b><span></span></div><div class="barra"><i></i></div></div></div>
</div>
<div class="app-shell">''')
rep('''  const m=document.getElementById('migas'); m.innerHTML='';
  PASOS.forEach((p,i)=>{const d=document.createElement('span');d.className='miga'+(i+1===n?' act':(i+1<n?' done':''));d.textContent=p;m.appendChild(d)});''',
'''  const m=document.getElementById('migas'); m.innerHTML='';
  PASOS.forEach((p,i)=>{const d=document.createElement('div');d.className='paso-nav'+(i+1===n?' act':(i+1<n?' done':''));d.innerHTML='<i>'+(i+1<n?'✓':(i+1))+'</i><span>'+p+'</span>';m.appendChild(d)});
  const mm=document.getElementById('migasM');
  if(mm){mm.querySelector('b').textContent=PASOS[n-1];mm.querySelector('span').textContent='Paso '+n+' de '+PASOS.length;mm.querySelector('.barra i').style.width=(n/PASOS.length*100)+'%'}''')

# Modo
rep_between('''    <p class="hint">El ensayo estándar incluye panel de 80 personas''', '''    <div class="geek" id="geekPanel">''', f'''    <p class="hint">El ensayo estándar cubre la mayoría de los casos. Cada conexión dispone de un número limitado de ensayos por día.</p>
    <div class="specs">
      <div class="spec"><div class="ic">{ic("i-users", 16)}</div><div><b>80 personas</b><span>panel muestreado de la audiencia elegida</span></div></div>
      <div class="spec"><div class="ic">{ic("i-sliders", 16)}</div><div><b>5 dimensiones</b><span>elección forzada 1–5 y objeción principal</span></div></div>
      <div class="spec"><div class="ic">{ic("i-shield", 16)}</div><div><b>Pase adversarial</b><span>una corrida dedicada a buscar por qué falla</span></div></div>
    </div>
    <div class="exp"><div><b>Modo experto</b><span>Tamaño del panel, corridas de estabilidad, semilla y exportación de datos crudos.</span></div><label class="switch"><input type="checkbox" id="labToggle" onchange="toggleLab()"><span class="slider-t"></span></label></div>
''')
rep('''function toggleLab(){
  const p=document.getElementById('geekPanel'), t=document.getElementById('labToggle');
  const abierto=p.style.display==='block';
  p.style.display=abierto?'none':'block';
  t.classList.toggle('abierto',!abierto);
  S.modo=abierto?'std':'geek';
}''', '''function toggleLab(){
  const p=document.getElementById('geekPanel'), t=document.getElementById('labToggle');
  const abrir=t.checked;
  p.style.display=abrir?'block':'none';
  S.modo=abrir?'geek':'std';
}''')

# Plan
rep('''    <table class="plan-tabla" id="planTabla"></table>
    <div class="err-caja" id="errRun"></div>
    <div class="fila-botones"><button class="btn btn-p" id="btnRun" onclick="ejecutar()">Ejecutar ensayo</button><button class="btn btn-t" onclick="paso(4)">← Ajustar</button></div>''',
'''    <div id="planCont"></div>
    <div class="err-caja" id="errRun"></div>''')
rep('''    <h2>Plan del ensayo</h2>
    <p class="hint">Esto es exactamente lo que va a ejecutarse. Nada corre sin tu aprobación, y tu idea no queda almacenada en ninguna parte.</p>''',
'''    <div class="plan-top"><div><h2>Plan del ensayo</h2><p class="hint" style="margin:0">Esto es exactamente lo que va a ejecutarse.</p></div><span class="chip ok">''' + ic('i-check', 12) + ''' Nada corre sin tu aprobación</span></div>''')
rep_between('''  const t=document.getElementById('planTabla');''', '''  paso(5);
}''', '''  const cmp=!!S.comparar;
  const poolA=filtrarPersonas(cmp?S.comparar.a.filtros:S.audiencia.filtros);
  const poolB=cmp?filtrarPersonas(S.comparar.b.filtros):null;
  if(!poolA.length||(cmp&&!poolB.length)){alert('Una de las audiencias quedó vacía con esos filtros.');return}
  const nEf=cmp?Math.floor(S.n/2):S.n;
  const llamadasQ=Math.ceil(nEf/10)*(cmp?2:1)*S.k, llamadasV=4, extra=(S.adv?1:0)+1;
  const kv=(k,v)=>'<div class="kv"><span>'+k+'</span><b>'+v+'</b></div>';
  const li=t=>'<li>'+t+'</li>';
  const chico=poolA.length<nEf||(cmp&&poolB.length<nEf);
  let html='<div class="plan-head"><div class="cita">"'+esc(S.idea.slice(0,220))+(S.idea.length>220?'…':'')+'"</div>'
    +'<div class="meta"><span>Lente: '+LENTES[S.perfil].nombre+'</span><span>Audiencia: '+(cmp?esc(S.comparar.a.nombre)+' vs '+esc(S.comparar.b.nombre):esc(S.audiencia.nombre))+'</span><span>Semilla '+S.seed+'</span></div></div>';
  html+='<div class="plan-grid">'
    +'<div class="pcol"><h4>'+icono('i-users',14)+' Quién opina</h4>'
      +kv('Pool disponible',cmp?num(poolA.length)+' y '+num(poolB.length):num(poolA.length))
      +kv('Panel',cmp?'n = '+nEf+' + '+nEf:'n = '+nEf)
      +kv('Muestreo','aleatorio')
      +kv('Corridas',S.k)
      +(chico?'<p class="helper" style="margin-top:10px"><b>Pool menor que el panel:</b> habrá repetición de personas y el intervalo saldrá amplio.</p>':'')
    +'</div>'
    +'<div class="pcol"><h4>'+icono('i-sliders',14)+' Instrumento</h4><ul>'
      +li('5 dimensiones en elección forzada 1–5')+li('Objeción principal por persona')+li('8 voces por polos de reacción')+li('Pase adversarial: '+(S.adv?'sí':'no'))
    +'</ul></div>'
    +'<div class="pcol"><h4>'+icono('i-doc',14)+' Qué se entrega</h4><ul>'
      +li('Veredicto con intervalo bootstrap 95 %')+li('Mapa por segmento y polarización')+li('Objeciones rankeadas')+li('"Dónde se equivoca este ensayo" y próximos pasos')+(S.raw?li('JSON crudo con las respuestas'):'')
    +'</ul></div></div>';
  html+='<div class="plan-foot"><div class="datos">'
    +'<div><b>~'+(llamadasQ+llamadasV+extra)+' llamadas</b>al modelo · 1–3 min</div>'
    +'<div><b>'+(S.estado?(Math.max(0,S.estado.limite-S.estado.usados))+' de '+S.estado.limite:'—')+'</b>ensayos disponibles hoy</div>'
    +'</div><div class="fila-botones" style="margin:0"><button class="btn btn-t" onclick="paso(4)">← Ajustar</button><button class="btn btn-p" id="btnRun" onclick="ejecutar()">Ejecutar ensayo '+icono('i-arrow',14)+'</button></div></div>';
  document.getElementById('planCont').innerHTML=html;
  paso(5);
}''')
rep('''function hashStr(s){''', '''function icono(n,s){s=s||15;return '<svg width="'+s+'" height="'+s+'" aria-hidden="true"><use href="#'+n+'"/></svg>'}
function secH(icon,titulo){return '<div class="sec-h"><div class="ic">'+icono(icon)+'</div><h3>'+titulo+'</h3></div>'}
function semaforoTxt(s){return s>=6.8?'Conecta':s>=5?'Reacción mixta':'No convence'}
function hashStr(s){''')

# Reporte
rep('''+'<div class="linea1"><span class="semaforo" style="background:'+colorScore(a.score)+'"></span>'+esc(R.sintesis?.linea||veredictoLocal(a))+'</div>\'''',
    '''+'<div class="sem" style="--semc:'+colorScore(a.score)+'"><i></i>'+semaforoTxt(a.score)+'</div><div class="linea1">'+esc(R.sintesis?.linea||veredictoLocal(a))+'</div>\'''')
rep('''<h3>La afinación #1</h3>''', "'+secH('i-target','La afinación #1')+'")
rep('''<h3>Las cinco dimensiones</h3>''', "'+secH('i-sliders','Las cinco dimensiones')+'")
rep('''<h3>Polarización: '+pTxt+'%</h3>''', "'+secH('i-split','Polarización: '+pTxt+'%')+'")
rep('''<h3 style="margin-top:18px">El mapa por segmento</h3>''', "'+secH('i-bars','El mapa por segmento').replace('class=\"sec-h\"','class=\"sec-h sec-h2\"')+'")
rep('''<h3>Comparación de audiencias</h3>''', "'+secH('i-columns','Comparación de audiencias')+'")
rep('''<h3>Las objeciones, rankeadas</h3>''', "'+secH('i-alert','Las objeciones, rankeadas')+'")
rep('''<h3>Pase adversarial: por qué podría fallar</h3>''', "'+secH('i-shield','Pase adversarial: por qué podría fallar')+'")
rep('''<h3>Las voces de la sala</h3>''', "'+secH('i-quote','Las voces de la sala')+'")
rep('''<h3>Dónde este ensayo probablemente se equivoca</h3>''', "'+secH('i-info','Dónde este ensayo probablemente se equivoca')+'")
rep('''<h3>Próximos pasos en el mundo real ('+lente.nombre.toLowerCase()+')</h3>''', "'+secH('i-arrow','Próximos pasos en el mundo real ('+lente.nombre.toLowerCase()+')')+'")
rep('''  a.objs.slice(0,4).forEach(o=>{html+='<div class="obj"><div class="pct">'+o.pct+'%</div><p><b>'+esc(OBJS[o.obj]||o.obj)+'</b></p></div>'});''',
    '''  const topObj=a.objs[0]?.pct||1;
  a.objs.slice(0,4).forEach(o=>{html+='<div class="obj"><div class="pct">'+o.pct+'%</div><p><b>'+esc(OBJS[o.obj]||o.obj)+'</b></p><div class="bar"><i style="width:'+Math.round(o.pct/topObj*100)+'%"></i></div></div>'});''')

CSS = r'''
/* ---------- v2: iconos, cabecera de app, pasos, modo, plan, reporte, home ---------- */
.ic{width:28px;height:28px;border-radius:7px;background:var(--cobalto-claro);color:var(--cobalto);display:grid;place-items:center;flex:none}
.ic svg{display:block}
.paso .ic,.conf-item .ic{margin-bottom:12px}
.perfil-opt .ic{width:32px;height:32px;border-radius:8px;margin-bottom:12px}
.perfil-opt.sel .ic{background:var(--cobalto);color:#fff}
.app-top{position:static}
.app-salir{padding:8px 0;font-size:13.5px}
.stepper{background:var(--blanco);border-bottom:1px solid var(--linea)}
.stepper .wrap{padding-top:14px;padding-bottom:14px}
.pasos-nav{display:grid;grid-template-columns:repeat(7,1fr)}
.paso-nav{display:flex;flex-direction:column;align-items:center;gap:8px;position:relative;font-size:12px;color:var(--gris-suave)}
.paso-nav::before{content:"";position:absolute;top:11px;left:calc(-50% + 11px);right:calc(50% + 11px);height:1px;background:var(--linea-fuerte)}
.paso-nav:first-child::before{display:none}
.paso-nav i{width:22px;height:22px;border-radius:50%;border:1px solid var(--linea-fuerte);background:var(--blanco);display:grid;place-items:center;font-family:'IBM Plex Mono',monospace;font-size:11px;font-style:normal;color:var(--gris-suave);position:relative;z-index:1}
.paso-nav.done{color:var(--tinta)}.paso-nav.done i{background:var(--tinta);border-color:var(--tinta);color:#fff}
.paso-nav.done::before,.paso-nav.act::before{background:var(--tinta)}
.paso-nav.act{color:var(--cobalto);font-weight:600}.paso-nav.act i{background:var(--cobalto);border-color:var(--cobalto);color:#fff;box-shadow:0 0 0 4px var(--cobalto-claro)}
.stepper-m{display:none}
.stepper-m .fila{display:flex;justify-content:space-between;align-items:baseline;font-size:13.5px}
.stepper-m .fila b{font-weight:600;color:var(--cobalto)}
.stepper-m .fila span{font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--gris)}
.stepper-m .barra{height:3px;background:var(--linea);border-radius:2px;margin-top:8px;overflow:hidden}
.stepper-m .barra i{display:block;height:100%;width:0;background:var(--cobalto);transition:width .3s}
.app-shell{padding-top:var(--esp-4)}
.migas{display:none}

.specs{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.spec{border:1px solid var(--linea);border-radius:8px;padding:14px 16px;background:var(--hueso);display:flex;gap:12px;align-items:flex-start}
.spec .ic{width:32px;height:32px;border-radius:8px}
.spec b{display:block;font-family:'IBM Plex Mono',monospace;font-weight:500;font-size:16px;color:var(--tinta)}
.spec span{font-size:12.5px;color:var(--gris)}
.exp{display:flex;justify-content:space-between;align-items:center;gap:16px;border-top:1px solid var(--linea);margin-top:20px;padding-top:18px}
.exp b{font-size:14px;font-weight:600;display:block}.exp span{font-size:13px;color:var(--gris)}
.lab-link{display:none}

.plan-top{display:flex;justify-content:space-between;align-items:flex-start;gap:16px;flex-wrap:wrap;margin-bottom:var(--esp-4)}
.chip{display:inline-flex;align-items:center;gap:6px;font-family:'IBM Plex Mono',monospace;font-size:11px;padding:5px 9px;border-radius:5px;background:var(--hueso);border:1px solid var(--linea);color:var(--gris);white-space:nowrap}
.chip.ok{background:var(--ok-soft);border-color:#BFE0CE;color:var(--ok)}
.plan-head .cita{font-size:17px;font-weight:600;letter-spacing:-.01em;max-width:60ch;line-height:1.4}
.plan-head .meta{font-family:'IBM Plex Mono',monospace;font-size:11.5px;color:var(--gris);margin-top:8px;display:flex;gap:14px;flex-wrap:wrap}
.plan-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:var(--esp-4)}
.pcol{border:1px solid var(--linea);border-radius:8px;background:var(--hueso);padding:16px}
.pcol h4{display:flex;align-items:center;gap:8px;font-size:11px;letter-spacing:.08em;text-transform:uppercase;font-family:'IBM Plex Mono',monospace;font-weight:500;color:var(--gris);margin-bottom:12px}
.pcol h4 svg{color:var(--cobalto)}
.kv{display:flex;justify-content:space-between;gap:10px;font-size:13px;padding:7px 0;border-top:1px solid var(--linea)}
.kv:first-of-type{border-top:none;padding-top:0}
.kv span{color:var(--gris)}.kv b{font-family:'IBM Plex Mono',monospace;font-weight:500;font-size:12.5px;text-align:right;white-space:nowrap}
.pcol ul{list-style:none;font-size:13px;display:flex;flex-direction:column;gap:6px}
.pcol ul li{display:flex;gap:8px;align-items:flex-start}
.pcol ul li::before{content:"";width:5px;height:5px;border-radius:50%;background:var(--cobalto);flex:none;margin-top:8px}
.plan-foot{display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap;margin-top:var(--esp-4);padding-top:18px;border-top:1px solid var(--linea)}
.plan-foot .datos{display:flex;gap:24px;flex-wrap:wrap}
.plan-foot .datos div{font-size:12.5px;color:var(--gris)}
.plan-foot .datos b{display:block;font-family:'IBM Plex Mono',monospace;font-weight:500;font-size:14px;color:var(--tinta)}
.btn svg{vertical-align:-2px;margin-left:2px}

.sec-h{display:flex;align-items:center;gap:10px;margin-bottom:4px}
.sec-h h3{margin:0}
.sec-h2{margin-top:var(--esp-4)}
.rep-sec .nota-sec{margin-left:38px}
.veredicto .sem{display:inline-flex;align-items:center;gap:6px;font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.06em;text-transform:uppercase;background:rgba(255,255,255,.08);color:#EEF1F8;border-radius:5px;padding:4px 9px;margin-bottom:10px}
.veredicto .sem i{width:7px;height:7px;border-radius:50%;background:var(--semc,#F2CE7B);display:block}
.obj .bar{flex:none;width:90px;height:6px;background:var(--linea);border-radius:100px;overflow:hidden;margin-left:auto}
.obj .bar i{display:block;height:100%;background:var(--cobalto)}
.obj p{flex:1;min-width:0}
.equivoca .sec-h .ic{background:var(--warn-soft);color:var(--warn)}
.pasos-sig .sec-h .ic{background:var(--ok-soft);color:var(--ok)}

.hero-grid{display:grid;grid-template-columns:1.05fr .95fr;gap:48px;align-items:center}
.preview{border:1px solid var(--linea);border-radius:12px;background:var(--hueso);padding:16px;position:relative}
.preview .etq{position:absolute;top:-10px;left:14px;font-family:'IBM Plex Mono',monospace;font-size:10.5px;letter-spacing:.08em;text-transform:uppercase;background:var(--blanco);border:1px solid var(--linea);border-radius:4px;padding:2px 8px;color:var(--gris)}
.preview .mini-idea{font-size:12.5px;font-weight:600;color:var(--tinta);margin:4px 0 10px;line-height:1.4}
.preview .mini-ver{background:var(--cobalto-osc);color:#EEF1F8;border-radius:8px;padding:14px 16px;display:flex;gap:14px;align-items:center}
.preview .mini-ver .sc{font-family:'IBM Plex Mono',monospace;font-size:32px;font-weight:500;color:#F2CE7B;line-height:1;flex:none}
.preview .mini-ver .sc small{font-size:12px;color:#9DB0E6}
.preview .mini-ver .sem{display:inline-flex;align-items:center;gap:5px;font-family:'IBM Plex Mono',monospace;font-size:10px;letter-spacing:.06em;text-transform:uppercase;color:#7FE0B2;margin-bottom:4px}
.preview .mini-ver .sem i{width:6px;height:6px;border-radius:50%;background:#7FE0B2;display:block}
.preview .mini-ver p{font-size:12.5px;font-weight:600;line-height:1.35;margin:0}
.preview .mini-dims{display:grid;grid-template-columns:repeat(5,1fr);gap:6px;margin-top:10px}
.preview .mini-dims div{background:var(--blanco);border:1px solid var(--linea);border-radius:6px;padding:8px;min-width:0}
.preview .mini-dims .v{font-family:'IBM Plex Mono',monospace;font-size:14px;font-weight:500}
.preview .mini-dims .l{font-size:9.5px;color:var(--gris);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.preview .mini-dims .g{height:3px;background:var(--linea);margin-top:5px;border-radius:2px;overflow:hidden}
.preview .mini-dims .g i{display:block;height:100%}
.preview .mini-heat{margin-top:10px;display:flex;flex-direction:column;gap:5px}
.preview .mini-heat div{display:flex;align-items:center;gap:8px;font-size:10.5px;color:var(--gris)}
.preview .mini-heat span{width:64px;text-align:right}
.preview .mini-heat em{flex:1;height:8px;background:var(--blanco);border:1px solid var(--linea);border-radius:3px;overflow:hidden;font-style:normal}
.preview .mini-heat em i{display:block;height:100%}
.preview .mini-heat b{font-family:'IBM Plex Mono',monospace;font-weight:500;width:26px}

@media(max-width:900px){
  .hero-grid{grid-template-columns:1fr;gap:28px}
  .specs,.plan-grid{grid-template-columns:1fr 1fr}
}
@media(max-width:640px){
  .pasos-nav{display:none}
  .stepper-m{display:block}
  .stepper .wrap{padding-top:10px;padding-bottom:10px}
  .specs,.plan-grid{grid-template-columns:1fr}
  .plan-foot{flex-direction:column;align-items:stretch}
  .plan-foot .fila-botones .btn-p{flex:1}
  .plan-top{flex-direction:column}
  .rep-sec .nota-sec{margin-left:0}
  .preview{padding:12px}
  .preview .mini-dims{gap:4px}
  .preview .mini-dims div{padding:6px 5px}
  .obj .bar{display:none}
}
'''
rep('</style>', CSS + '</style>')
open(P, 'w', encoding='utf-8').write(src); print('v2 OK', len(src))
