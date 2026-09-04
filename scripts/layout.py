#!/usr/bin/env python3
"""Pasada de estructura y ritmo: escala de espaciado, contenedor del veredicto, tarjetas y móvil."""
import sys, os
P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'public', 'index.html')
src = open(P, encoding='utf-8').read()
def rep(old, new, count=1):
    global src
    n = src.count(old)
    if n != count: sys.exit(f'ANCLA ({n}): {old[:90]!r}')
    src = src.replace(old, new)

# 1. Veredicto: el score y el texto van dentro de .ver-in (que es quien lleva padding y flex)
rep("""  html+='<div class="veredicto"><div class="score-gr" style="color:""", """  html+='<div class="veredicto"><div class="ver-in"><div class="score-gr" style="color:""")
rep("""    +'</div></div>';

  if(R.sintesis?.afinacion)""", """    +'</div></div></div>';

  if(R.sintesis?.afinacion)""")
# 2. Cabecera del reporte: misma tarjeta que el resto, sin padding en línea
rep("""  html+='<div class="card" style="margin-bottom:14px;padding:20px 24px">'""", """  html+='<div class="card rep-head">'""")
# 3. Tarjeta de afinación: acento con la misma variable que el resto
rep("""style="border-left:4px solid var(--maqui)\"""", """style="border-left:3px solid var(--cobalto)\"""")

# 4. CSS de ritmo (al final del bloque de estilos, para que prevalezca)
CSS = r'''
/* ---------- ritmo y estructura ---------- */
:root{--esp-1:8px;--esp-2:12px;--esp-3:16px;--esp-4:24px;--esp-5:32px;--esp-6:48px;--esp-7:72px}
.sec{padding:var(--esp-7) 0}
.sec h2{margin-bottom:var(--esp-1)}
.sec .sub{margin-bottom:var(--esp-5)}
.hero .wrap{padding:96px 24px 64px}
.hero p.lede{margin-top:var(--esp-4)}
.hero-actions{margin-top:var(--esp-5)}
.sello{margin-top:var(--esp-5)}
.confianza .c-in,.honesto{padding:var(--esp-5)}
.conf-grid,.honesto-grid{gap:var(--esp-4) var(--esp-5)}
.pasos,.ejemplos{gap:var(--esp-3)}
.paso,.ej .ej-in{padding:var(--esp-4)}
.gracias{padding-top:var(--esp-5)}
footer{padding:var(--esp-4) 0 var(--esp-6)}

.app-shell{padding:var(--esp-5) 24px 96px}
.migas{margin-bottom:var(--esp-4)}
.card{padding:var(--esp-4);margin-bottom:var(--esp-3)}
.card h2{margin-bottom:var(--esp-1)}
.card .hint{margin-bottom:var(--esp-4)}
label.lbl{margin:var(--esp-3) 0 6px}
.filtros{gap:var(--esp-2) var(--esp-4)}
.fila-botones{margin-top:var(--esp-4);gap:var(--esp-2)}
.aud-tabs{margin-bottom:var(--esp-4)}
.aud-res{margin-top:var(--esp-3)}
.perfiles,.guardadas{gap:var(--esp-2)}
.geek{padding:var(--esp-4)}
.vivo-panel{padding:var(--esp-3)}
.vivo-head{margin-bottom:var(--esp-3)}

#p7>*{margin:0 0 var(--esp-3)}
.rep-sec{margin-top:0}
.rep-head{padding:var(--esp-4)}
.veredicto .ver-in{padding:var(--esp-5);display:flex;gap:var(--esp-5);align-items:flex-start;flex-wrap:nowrap}
.veredicto .score-gr{flex:none;min-width:150px;padding-top:2px}
.ver-txt{flex:1;min-width:0}
.ver-txt .meta-l{margin-top:var(--esp-2);line-height:1.6}
.rep-sec h3{margin-bottom:6px}
.rep-sec .nota-sec{margin-bottom:var(--esp-3)}
.equivoca,.pasos-sig{padding:var(--esp-4)}
.rep-meta{padding:var(--esp-3) var(--esp-4);margin-top:0}
.voz-cuerpo{padding:var(--esp-3)}
.voz-nota{padding:0 var(--esp-3) var(--esp-3)}
.voz-ficha{padding:var(--esp-2) var(--esp-3)}

@media(max-width:900px){
  .hero .wrap{padding:72px 24px 48px}
  .sec{padding:var(--esp-6) 0}
}
@media(max-width:640px){
  .wrap{padding:0 16px}
  .topbar .wrap{height:56px}
  .hero .wrap{padding:48px 16px 40px}
  .hero h1{font-size:32px}
  .hero p.lede{font-size:16px;margin-top:var(--esp-3)}
  .hero-actions{margin-top:var(--esp-4)}
  .hero-actions .btn-big,.hero-actions .btn-ghost{flex:1 1 100%;text-align:center}
  .sec{padding:var(--esp-6) 0}
  .sec .sub{margin-bottom:var(--esp-4)}
  .confianza .c-in,.honesto{padding:var(--esp-4) 20px}
  .paso,.ej .ej-in{padding:20px}
  .app-shell{padding:var(--esp-4) 16px 72px}
  .migas{gap:4px}
  .card{padding:20px}
  .rep-head{padding:20px}
  .fila-botones .btn{flex:1 1 auto;text-align:center}
  .fila-botones .btn-t{flex:0 0 auto}
  .aud-tab{flex:1 1 auto;text-align:center}
  .veredicto .ver-in{flex-direction:column;gap:var(--esp-2);padding:var(--esp-4) 20px}
  .veredicto .score-gr{min-width:0;font-size:48px}
  .ver-txt .linea1{font-size:17px}
  .plan-tabla td{display:block;width:100%;padding:2px 0}
  .plan-tabla td:first-child{width:100%;padding-top:12px;border-bottom:none;color:var(--gris-suave)}
  .plan-tabla td:last-child{padding-bottom:12px}
  .dims{grid-template-columns:1fr 1fr}
  .heat-lbl{width:96px}
  .obj .pct{width:44px}
  .voz-ficha{flex-direction:column;gap:2px;align-items:flex-start}
  .voz-ficha .seg{text-align:left}
  .equivoca,.pasos-sig{padding:20px}
  .vivo-score{font-size:34px}
}
'''
rep('</style>', CSS + '</style>')
open(P, 'w', encoding='utf-8').write(src); print('layout OK')
