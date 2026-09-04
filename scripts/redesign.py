#!/usr/bin/env python3
"""Rediseño sobrio + ajustes de contenido sobre public/index.html (ahora fuente de verdad del frontend)."""
import re, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'public', 'index.html')
src = open(P, encoding='utf-8').read()

def rep(old, new, count=1):
    global src
    n = src.count(old)
    if n != count: sys.exit(f'ANCLA ({n} veces, esperaba {count}): {old[:100]!r}')
    src = src.replace(old, new)
def rep_between(ini, fin, new):
    global src
    assert src.count(ini) == 1, ini[:80]
    a = src.index(ini); b = src.index(fin, a)
    src = src[:a] + new + src[b:]

# ---------- Tipografía ----------
rep('<link href="https://fonts.googleapis.com/css2?family=Alfa+Slab+One&family=Archivo:wght@400;500;600;700;800&family=Spline+Sans+Mono:wght@400;500;600&display=swap" rel="stylesheet">',
    '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">')

# ---------- CSS completo ----------
CSS = r'''
:root{
  --tinta:#15171C; --gris:#5B606B; --gris-suave:#8A8F99; --linea:#E2E3E8; --linea-fuerte:#C9CBD3;
  --hueso:#F6F6F4; --blanco:#FFFFFF; --crema:#EEF1F8;
  --cobalto:#1B3A8F; --cobalto-osc:#10265F; --cobalto-mid:#2F55C4; --cobalto-claro:#EDF1FA;
  --bus:#E8ECF6; --bus-osc:#8A6A17; --rojo:#B42318; --rojo-soft:#FCEBE9;
  --ok:#1E7A4F; --ok-soft:#E8F4EE; --warn:#9A6B0A; --warn-soft:#FBF3DF; --mal:#B42318; --mal-soft:#FCEBE9;
  --maqui:#1B3A8F;
  --sombra:0 1px 2px rgba(21,23,28,.05);
  --radio:10px;
  color-scheme: only light;
}
*{margin:0;padding:0;box-sizing:border-box}
html{color-scheme:only light;background:var(--hueso) !important}
body{background:var(--hueso) !important;color:var(--tinta);font-family:'Inter',system-ui,-apple-system,sans-serif;font-size:16px;line-height:1.55;-webkit-font-smoothing:antialiased}
.disp{font-weight:600;letter-spacing:-.01em}
.mono{font-family:'IBM Plex Mono',ui-monospace,monospace}
.wrap{max-width:1060px;margin:0 auto;padding:0 24px}
a{color:var(--cobalto)}
button{font-family:inherit;cursor:pointer}
:focus-visible{outline:2px solid var(--cobalto-mid);outline-offset:2px}
@media (prefers-reduced-motion: reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
h1,h2,h3,h4{font-weight:600;letter-spacing:-.015em;line-height:1.2}

/* ---------- landing ---------- */
.topbar{background:rgba(246,246,244,.92);backdrop-filter:blur(8px);border-bottom:1px solid var(--linea);position:sticky;top:0;z-index:50}
.topbar .wrap{display:flex;align-items:center;justify-content:space-between;height:60px}
.logo{font-weight:600;font-size:15.5px;color:var(--tinta);letter-spacing:-.01em}
.logo .q{color:var(--cobalto)}
.top-cta{background:var(--cobalto);color:#fff;border:1px solid var(--cobalto);border-radius:8px;padding:9px 16px;font-weight:600;font-size:14px}
.top-cta:hover{background:var(--cobalto-osc);border-color:var(--cobalto-osc)}
.hero{background:var(--blanco);border-bottom:1px solid var(--linea);position:relative}
.hero .wrap{padding:84px 24px 56px;text-align:left;max-width:1060px}
.eyebrow{font-family:'IBM Plex Mono',monospace;font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--gris);margin-bottom:22px}
.hero h1{font-size:clamp(34px,5.2vw,56px);line-height:1.1;color:var(--tinta);max-width:820px;letter-spacing:-.025em}
.hero h1 em{font-style:normal;color:var(--cobalto)}
.hero p.lede{margin:22px 0 0;font-size:18px;max-width:640px;color:var(--gris);line-height:1.6}
.hero-actions{margin-top:32px;display:flex;gap:12px;flex-wrap:wrap;align-items:center}
.btn-big{background:var(--cobalto);color:#fff;border:1px solid var(--cobalto);border-radius:8px;padding:14px 24px;font-size:15px;font-weight:600}
.btn-big:hover{background:var(--cobalto-osc);border-color:var(--cobalto-osc)}
.btn-ghost{background:transparent;color:var(--tinta);border:1px solid var(--linea-fuerte);border-radius:8px;padding:13px 20px;font-size:15px;font-weight:500}
.btn-ghost:hover{border-color:var(--tinta)}
.sello{display:inline-flex;align-items:center;gap:8px;font-family:'IBM Plex Mono',monospace;font-size:12px;color:var(--gris);border:1px solid var(--linea);border-radius:6px;padding:8px 12px;margin-top:30px;background:var(--hueso)}
.sala-strip{border-top:1px solid var(--linea);background:var(--hueso);padding:12px 0;overflow:hidden;white-space:nowrap}
.sala-track{display:inline-block;animation:desfile 90s linear infinite}
.chip-p{display:inline-flex;align-items:baseline;gap:7px;background:var(--blanco);border:1px solid var(--linea);border-radius:6px;padding:6px 12px;margin:0 5px;font-size:12.5px;color:var(--gris)}
.chip-p b{color:var(--tinta);font-weight:600}
.chip-p .mono{font-size:11px;color:var(--gris-suave)}
@keyframes desfile{from{transform:translateX(0)}to{transform:translateX(-50%)}}

.sec{padding:64px 0;background:var(--hueso)}
.sec h2{font-size:clamp(22px,3vw,30px);color:var(--tinta);margin-bottom:10px}
.sec .sub{color:var(--gris);max-width:640px;margin-bottom:32px;font-size:16.5px}
.pasos{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}
.paso{background:var(--blanco);border:1px solid var(--linea);border-radius:var(--radio);padding:22px;box-shadow:var(--sombra)}
.paso .n{font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--cobalto);letter-spacing:.08em}
.paso h3{font-size:15.5px;margin:10px 0 6px;color:var(--tinta)}
.paso p{font-size:14px;color:var(--gris)}
.ejemplos{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px}
.ej{background:var(--blanco);border:1px solid var(--linea);border-radius:var(--radio);display:flex;flex-direction:column;box-shadow:var(--sombra);overflow:hidden}
.ej .ej-in{padding:22px;display:flex;flex-direction:column;gap:10px}
.ej .quien{font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--gris)}
.ej .idea-ej{font-weight:600;font-size:16px;color:var(--tinta);line-height:1.4;letter-spacing:-.01em}
.ej .res{border-top:1px solid var(--linea);padding-top:12px;font-size:13.5px;color:var(--gris)}
.ej .res b{color:var(--tinta)}
.score-mini{display:inline-block;font-family:'IBM Plex Mono',monospace;font-weight:500;font-size:12.5px;border-radius:6px;padding:3px 8px}
.s-ok{background:var(--ok-soft);color:var(--ok)} .s-warn{background:var(--warn-soft);color:var(--warn)} .s-mal{background:var(--mal-soft);color:var(--mal)}

/* confianza y método */
.confianza{background:var(--blanco);border:1px solid var(--linea);border-radius:var(--radio);overflow:hidden;color:var(--tinta);box-shadow:var(--sombra)}
.confianza .c-in{padding:34px 30px}
.confianza h2{color:var(--tinta);font-size:clamp(20px,2.6vw,26px);margin-bottom:8px}
.conf-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:22px;margin-top:18px}
.conf-item h4{font-size:14.5px;color:var(--cobalto);margin-bottom:6px}
.conf-item p{font-size:14px;color:var(--gris)}
.honesto{background:var(--blanco);border:1px solid var(--linea);border-radius:var(--radio);padding:32px 30px;box-shadow:var(--sombra)}
.honesto h2{margin-bottom:18px;font-size:clamp(20px,2.6vw,26px)}
.honesto-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:22px}
.honesto-item h4{font-size:14.5px;color:var(--cobalto);margin-bottom:6px}
.honesto-item p{font-size:14px;color:var(--gris)}
.gracias{border-top:1px solid var(--linea);padding:28px 0 0}
.gracias h2{font-size:15px;color:var(--tinta);margin-bottom:8px}
.gracias p{font-size:14px;color:var(--gris);max-width:760px}
footer{border-top:1px solid var(--linea);padding:28px 0 48px;font-size:13px;color:var(--gris);background:var(--hueso)}
footer b{color:var(--tinta);font-weight:600}

/* ---------- app ---------- */
#app{display:none;background:var(--hueso)}
#landing{background:var(--hueso)}
.app-shell{max-width:860px;margin:0 auto;padding:28px 24px 90px;background:var(--hueso)}
.migas{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:26px}
.miga{font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.04em;padding:5px 11px;border-radius:6px;border:1px solid var(--linea);color:var(--gris);background:var(--blanco)}
.miga.act{background:var(--tinta);border-color:var(--tinta);color:#fff}
.miga.done{border-color:var(--linea);color:var(--tinta);background:var(--hueso)}
.card{background:var(--blanco);border:1px solid var(--linea);border-radius:var(--radio);padding:28px;margin-bottom:16px;box-shadow:var(--sombra)}
.card h2{font-size:20px;color:var(--tinta);margin-bottom:6px}
.card .hint{color:var(--gris);font-size:14.5px;margin-bottom:20px}
.priv{display:flex;gap:10px;align-items:flex-start;background:var(--hueso);border:1px solid var(--linea);border-radius:8px;padding:12px 15px;font-size:13.5px;color:var(--gris);margin-top:12px}
.priv b{color:var(--tinta)}
.perfiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}
.perfil-opt{border:1px solid var(--linea);border-radius:8px;padding:16px;background:var(--blanco);text-align:left;transition:border-color .15s}
.perfil-opt:hover{border-color:var(--linea-fuerte)}
.perfil-opt.sel{border-color:var(--cobalto);background:var(--cobalto-claro);box-shadow:inset 0 0 0 1px var(--cobalto)}
.perfil-opt h3{font-size:15px;color:var(--tinta)}
.perfil-opt p{font-size:13px;color:var(--gris);margin-top:4px}
textarea,input[type=text],select{width:100%;border:1px solid var(--linea-fuerte);border-radius:8px;padding:12px 14px;font-family:inherit;font-size:15px;background:var(--blanco);color:var(--tinta)}
textarea:focus,input[type=text]:focus,select:focus{border-color:var(--cobalto);outline:none;box-shadow:0 0 0 3px rgba(27,58,143,.12)}
textarea{min-height:110px;resize:vertical}
label.lbl{display:block;font-weight:600;font-size:13.5px;margin:14px 0 6px;color:var(--tinta)}
.fila-botones{display:flex;gap:10px;margin-top:22px;flex-wrap:wrap;align-items:center}
.btn{border-radius:8px;padding:12px 20px;font-size:14.5px;font-weight:600;border:1px solid var(--linea-fuerte)}
.btn-p{background:var(--cobalto);color:#fff;border-color:var(--cobalto)}
.btn-p:hover{background:var(--cobalto-osc);border-color:var(--cobalto-osc)}
.btn-p:disabled{background:var(--linea);color:var(--gris-suave);cursor:not-allowed;border-color:var(--linea)}
.btn-s{background:var(--blanco);color:var(--tinta)}
.btn-s:hover{border-color:var(--tinta)}
.btn-t{background:transparent;color:var(--gris);border:none;text-decoration:underline;text-underline-offset:3px;font-weight:500;padding:12px 6px}
.btn-t:hover{color:var(--tinta)}
.aud-tabs{display:flex;gap:6px;margin-bottom:18px;flex-wrap:wrap}
.aud-tab{border:1px solid var(--linea);background:var(--blanco);border-radius:6px;padding:8px 14px;font-size:13.5px;font-weight:500;color:var(--gris)}
.aud-tab.act{background:var(--tinta);border-color:var(--tinta);color:#fff}
.filtros{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px}
.aud-res{margin-top:16px;background:var(--cobalto-claro);border-radius:8px;padding:13px 16px;font-size:14px;color:var(--cobalto-osc)}
.aud-res b{font-family:'IBM Plex Mono',monospace;font-weight:500}
.guardadas{display:flex;flex-direction:column;gap:10px}
.aud-item{display:flex;justify-content:space-between;align-items:center;border:1px solid var(--linea);border-radius:8px;padding:12px 16px;background:var(--blanco);gap:10px;flex-wrap:wrap}
.aud-item button{font-size:13px}
.lab-link{display:inline-flex;align-items:center;gap:7px;font-family:'IBM Plex Mono',monospace;font-size:12.5px;color:var(--gris);background:transparent;border:1px solid var(--linea-fuerte);border-radius:6px;padding:7px 12px;margin-top:16px}
.lab-link:hover{color:var(--tinta);border-color:var(--tinta)}
.lab-link.abierto{color:var(--cobalto);border-color:var(--cobalto);background:var(--cobalto-claro)}
.geek{margin-top:14px;border:1px solid var(--linea);border-radius:8px;padding:18px;background:var(--hueso);display:none}
.geek .g-titulo{font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--gris);margin-bottom:8px}
.geek .g-row{display:flex;align-items:center;justify-content:space-between;gap:14px;padding:10px 0;border-bottom:1px solid var(--linea);flex-wrap:wrap}
.geek .g-row:last-child{border-bottom:none}
.geek .g-lbl{font-size:14px;font-weight:600}
.geek .g-sub{font-size:12.5px;color:var(--gris);font-weight:400}
.geek input[type=range]{width:150px;accent-color:var(--cobalto)}
.geek .g-val{font-family:'IBM Plex Mono',monospace;font-size:13px;color:var(--cobalto);min-width:36px;text-align:right}
.switch{position:relative;width:40px;height:22px;flex:none}
.switch input{opacity:0;width:0;height:0}
.slider-t{position:absolute;inset:0;background:var(--linea-fuerte);border-radius:100px;transition:.15s}
.slider-t:before{content:"";position:absolute;height:16px;width:16px;left:3px;top:3px;background:#fff;border-radius:50%;transition:.15s}
.switch input:checked + .slider-t{background:var(--cobalto)}
.switch input:checked + .slider-t:before{transform:translateX(18px)}
.plan-tabla{width:100%;border-collapse:collapse;font-size:14px;margin-top:8px}
.plan-tabla td{padding:10px 6px;border-bottom:1px solid var(--linea);vertical-align:top}
.plan-tabla td:first-child{color:var(--gris);width:190px;font-family:'IBM Plex Mono',monospace;font-size:12.5px}
.prog-caja{text-align:center;padding:40px 20px}
.prog-caja h2{font-size:20px;color:var(--tinta)}
.prog-bar{height:8px;background:var(--linea);border-radius:100px;margin:22px auto;max-width:420px;overflow:hidden}
.prog-fill{height:100%;background:var(--cobalto);width:0%;transition:width .5s;border-radius:100px}
.prog-msj{font-family:'IBM Plex Mono',monospace;font-size:12.5px;color:var(--gris)}

.dep-chips{display:flex;flex-wrap:wrap;gap:6px}
.dep-chip{border:1px solid var(--linea);background:var(--blanco);border-radius:6px;padding:6px 11px;font-size:13px;font-weight:500;color:var(--gris);transition:all .12s}
.dep-chip:hover{border-color:var(--linea-fuerte);color:var(--tinta)}
.dep-chip.sel{background:var(--tinta);border-color:var(--tinta);color:#fff}
.aud-item.aud-sel{border-color:var(--cobalto);background:var(--cobalto-claro);box-shadow:inset 0 0 0 1px var(--cobalto)}
.aud-item .aud-nombre{font-size:15px;font-weight:600;color:var(--tinta)}
.aud-item.aud-sel .aud-nombre{color:var(--cobalto-osc)}
.aud-badge{display:inline-block;font-family:'IBM Plex Mono',monospace;font-size:10.5px;background:var(--cobalto);color:#fff;border-radius:4px;padding:2px 7px;margin-left:8px;vertical-align:1px}
.aud-item .aud-desc{font-size:12.5px;color:var(--gris);margin-top:3px}
.helper{font-size:12.5px;color:var(--gris);margin-top:5px;line-height:1.45}

/* ---------- sala en vivo ---------- */
.vivo{padding:6px 2px}
.vivo-head{display:flex;justify-content:space-between;align-items:baseline;gap:12px;flex-wrap:wrap;margin-bottom:14px}
.vivo-fase{font-size:17px;font-weight:600;color:var(--tinta)}
.vivo-reloj{font-family:'IBM Plex Mono',monospace;font-size:12px;color:var(--gris)}
.vivo-pulso{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--ok);margin-right:6px;animation:pulso 1.6s ease-in-out infinite;vertical-align:1px}
@keyframes pulso{0%,100%{opacity:.35;transform:scale(.85)}50%{opacity:1;transform:scale(1.15)}}
.vivo-grid{display:grid;grid-template-columns:1.1fr .9fr;gap:14px}
@media(max-width:640px){.vivo-grid{grid-template-columns:1fr}}
.vivo-panel{background:var(--hueso);border:1px solid var(--linea);border-radius:8px;padding:14px}
.vivo-panel .vp-t{font-family:'IBM Plex Mono',monospace;font-size:10.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--gris);margin-bottom:10px}
.asientos{display:flex;flex-wrap:wrap;gap:4px}
.asiento{width:14px;height:14px;border-radius:3px;background:var(--linea);transition:background .3s,transform .2s}
.asiento.on{animation:sube .35s ease}
@keyframes sube{from{transform:scale(.4)}to{transform:scale(1)}}
.as-ok{background:var(--ok)} .as-med{background:#D9A62B} .as-mal{background:var(--rojo)}
.vivo-num{display:flex;align-items:baseline;gap:10px;margin-bottom:6px}
.vivo-score{font-family:'IBM Plex Mono',monospace;font-weight:500;font-size:40px;color:var(--tinta);line-height:1;transition:color .3s;letter-spacing:-.02em}
.vivo-score small{font-size:14px;color:var(--gris)}
.vivo-n{font-family:'IBM Plex Mono',monospace;font-size:12px;color:var(--gris)}
.objs-mini{display:flex;flex-direction:column;gap:6px;margin-top:10px}
.obj-mini{display:flex;align-items:center;gap:8px;font-size:11.5px;color:var(--gris)}
.obj-mini .om-lbl{width:92px;flex:none;text-align:right}
.obj-mini .om-track{flex:1;height:6px;background:var(--linea);border-radius:100px;overflow:hidden}
.obj-mini .om-fill{height:100%;background:var(--cobalto);border-radius:100px;width:0%;transition:width .5s}
.obj-mini .om-n{font-family:'IBM Plex Mono',monospace;width:26px;flex:none}
.feed{display:flex;flex-direction:column;gap:8px;min-height:150px}
.feed-item{background:var(--blanco);border:1px solid var(--linea);border-radius:8px;padding:10px 13px;animation:entra .4s ease}
@keyframes entra{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.feed-item .fq{font-size:13.5px;color:var(--tinta);line-height:1.4}
.feed-item .fw{font-family:'IBM Plex Mono',monospace;font-size:10.5px;color:var(--gris);margin-top:5px}
.feed-item.voz-f{border-color:var(--cobalto);background:var(--cobalto-claro)}
.vivo-nota{font-family:'IBM Plex Mono',monospace;font-size:11.5px;color:var(--gris);margin-top:12px;text-align:center}

/* reporte */
.veredicto{background:var(--cobalto-osc);color:var(--crema);border-radius:var(--radio);overflow:hidden;box-shadow:var(--sombra)}
.ver-in{padding:28px 30px;display:flex;gap:26px;align-items:center;flex-wrap:wrap}
.score-gr{font-family:'IBM Plex Mono',monospace;font-weight:500;font-size:56px;line-height:1;letter-spacing:-.03em}
.score-gr small{font-size:18px;color:#9DB0E6}
.ver-txt{flex:1;min-width:240px}
.ver-txt .linea1{font-size:18px;font-weight:600;line-height:1.4;letter-spacing:-.01em}
.ver-txt .meta-l{font-family:'IBM Plex Mono',monospace;font-size:11.5px;color:#9DB0E6;margin-top:10px}
.semaforo{width:10px;height:10px;border-radius:50%;display:inline-block;margin-right:8px;vertical-align:1px}
.rep-sec{margin-top:16px}
.rep-sec h3{font-size:16px;color:var(--tinta);margin-bottom:4px}
.rep-sec .nota-sec{font-size:13px;color:var(--gris);margin-bottom:14px}
.dims{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px}
.dim{background:var(--hueso);border:1px solid var(--linea);border-radius:8px;padding:12px 14px}
.dim .d-lbl{font-size:12px;color:var(--gris)}
.dim .d-val{font-family:'IBM Plex Mono',monospace;font-size:20px;font-weight:500;color:var(--tinta)}
.dim .d-barra{height:5px;background:var(--linea);border-radius:100px;margin-top:6px;overflow:hidden}
.dim .d-fill{height:100%;border-radius:100px}
.heat{display:flex;flex-direction:column;gap:6px}
.heat-row{display:flex;align-items:center;gap:10px}
.heat-lbl{width:150px;font-size:13px;color:var(--tinta);flex:none;text-align:right}
.heat-track{flex:1;height:18px;background:var(--hueso);border:1px solid var(--linea);border-radius:4px;overflow:hidden;position:relative}
.heat-fill{height:100%}
.heat-n{font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--gris);width:88px;flex:none}
.obj-list{display:flex;flex-direction:column;gap:8px}
.obj{display:flex;align-items:center;gap:12px;background:var(--hueso);border:1px solid var(--linea);border-radius:8px;padding:12px 16px}
.obj .pct{font-family:'IBM Plex Mono',monospace;font-weight:500;font-size:16px;color:var(--cobalto);width:52px;flex:none}
.obj p{font-size:14px}
.voces{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px}
.voz{background:var(--blanco);border:1px solid var(--linea);border-radius:var(--radio);overflow:hidden;box-shadow:var(--sombra)}
.voz-ficha{background:var(--hueso);border-bottom:1px solid var(--linea);color:var(--tinta);padding:11px 16px;display:flex;justify-content:space-between;gap:10px;align-items:baseline}
.voz-ficha .quien-v{font-weight:600;font-size:14px}
.voz-ficha .seg{font-family:'IBM Plex Mono',monospace;font-size:10.5px;color:var(--gris);text-align:right}
.voz-cuerpo{padding:14px 16px;font-size:14px;color:var(--tinta);line-height:1.55}
.voz-nota{padding:0 16px 14px;font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--gris)}
.riesgos li{margin:8px 0 8px 18px;font-size:14.5px}
.equivoca{background:var(--blanco);border:1px solid var(--linea);border-left:3px solid var(--warn);border-radius:var(--radio);padding:20px 22px}
.equivoca h3{color:var(--tinta)}
.equivoca li{margin:7px 0 7px 18px;font-size:14px;color:var(--gris)}
.pasos-sig{background:var(--blanco);border:1px solid var(--linea);border-left:3px solid var(--ok);border-radius:var(--radio);padding:20px 22px}
.pasos-sig h3{color:var(--tinta)}
.pasos-sig li{margin:7px 0 7px 18px;font-size:14px;color:var(--gris)}
.rep-meta{font-family:'IBM Plex Mono',monospace;font-size:11.5px;color:var(--gris);background:var(--hueso);border:1px solid var(--linea);border-radius:8px;padding:14px 16px;margin-top:20px;line-height:1.6}
.err-caja{background:var(--mal-soft);border:1px solid #F0C4BE;color:#7C2E20;border-radius:8px;padding:14px 16px;font-size:14px;margin-top:14px;display:none}
.cmp-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.cmp-col{background:var(--hueso);border:1px solid var(--linea);border-radius:8px;padding:16px}
.cmp-col h4{font-size:14px;color:var(--tinta);margin-bottom:8px}
@media(max-width:640px){.heat-lbl{width:104px;font-size:11.5px}.cmp-grid{grid-template-columns:1fr}.score-gr{font-size:44px}.hero .wrap{padding:56px 24px 40px}}
'''
rep_between('<style>', '</style>', '<style>' + CSS)

# ---------- HTML del landing ----------
rep('<div class="sello">⚗ Esto es un ensayo, no una encuesta. Las personas son sintéticas; las proporciones son reales.</div>',
    '<div class="sello">Esto es un ensayo, no una encuesta. Las personas son sintéticas; las proporciones son reales.</div>')
rep('  <div class="toldo-franja"></div><div class="toldo"></div>\n', '')
rep('<div class="confianza"><div class="toldo-mini" style="height:8px;background:repeating-linear-gradient(90deg,var(--bus) 0 22px,var(--crema) 22px 44px)"></div><div class="c-in">',
    '<div class="confianza"><div class="c-in">')
rep('<div class="ej"><div class="toldo-mini"></div><div class="ej-in">', '<div class="ej"><div class="ej-in">', count=3)
rep('Lo único que persiste: las audiencias que decidas guardar (visibles solo en tu dispositivo) y los votos anónimos de la comunidad, que son conteos agregados, nunca ideas.',
    'Lo único que persiste son las audiencias que decidas guardar, y quedan únicamente en tu dispositivo.')
rep('<div class="honesto-item"><h4>Qué queda fuera</h4><p>Política. Esta sala ensaya ideas, marcas y proyectos. La opinión pública no se fabrica, ni siquiera en sintético.</p></div>',
    '<div class="honesto-item"><h4>Qué queda fuera</h4><p>Política, religión y afirmaciones de salud. Esta sala ensaya ideas, marcas y proyectos; no se usa para medir creencias ni para validar tratamientos, y la opinión pública no se fabrica, ni siquiera en sintético.</p></div>')
rep_between('  <div class="gracias">', '  </div>\n</div></section>\n\n<footer>',
'''  <div class="gracias">
    <h2>Sobre el dataset</h2>
    <p>Esta sala usa <b>Nemotron-Personas-El-Salvador</b>, un dataset abierto de 148,000 personas sintéticas publicado en 2026 por NVIDIA junto con ANIA (Agencia Nacional de Inteligencia Artificial de El Salvador) y WideLabs, bajo licencia CC BY 4.0 y fundamentado en las distribuciones del Censo 2024. Es un proyecto independiente: no está afiliado a las instituciones que produjeron el dataset. Las personas son ficticias; ninguna representa a un ciudadano real.</p>
''')
rep('  Hecho en El Salvador 🇸🇻 sobre el dataset abierto <b>Nemotron-Personas-El-Salvador</b> de <b>ANIA · NVIDIA · WideLabs</b> (CC BY 4.0, Censo 2024). Proyecto independiente de exploración. Tu idea no se almacena; los votos de la comunidad son anónimos y agregados.',
    '  Dataset: <b>Nemotron-Personas-El-Salvador</b> (NVIDIA · ANIA · WideLabs, CC BY 4.0, base Censo 2024). Proyecto independiente. Tu idea no se almacena.')
rep('<h3>🌱 Emprendedor</h3>', '<h3>Emprendedor</h3>')
rep('<h3>🎯 Creativo / Marca</h3>', '<h3>Creativo / Marca</h3>')
rep('<h3>📐 Investigador</h3>', '<h3>Investigador</h3>')
rep('<h3>🔭 Explorador</h3>', '<h3>Explorador</h3>')
rep('<div class="priv">🔒<span>', '<div class="priv"><span>')
rep('>🧠 Modo experto</button>', '>Modo experto</button>')

# ---------- Filtro de temas ----------
rep("  const pol=/(president|diputad|alcald|partido|elecci|votá por|vote por|campaña política|bukele|asamblea legislativa|reelecci|candidat)/i;",
    "  const pol=RE_TEMAS_EXCLUIDOS;")
rep("if(pol.test(t)){err.style.display='block';err.textContent='Esta sala ensaya ideas, marcas y proyectos. Los temas político-electorales quedan fuera por diseño: una sala de ensayo no debe usarse para fabricar opinión pública.';return}",
    "if(pol.test(t)){err.style.display='block';err.textContent='Esta sala ensaya ideas, marcas y proyectos. Quedan fuera por diseño los temas político-electorales, los religiosos y las afirmaciones de salud: una sala de ensayo no debe usarse para fabricar opinión sobre creencias ni para validar tratamientos.';return}")
rep("/* ================= UTILIDADES ================= */",
    """/* ================= TEMAS EXCLUIDOS ================= */
// Misma lista que el servidor (netlify/functions/api/lib/comun.mts). Tres bloques: política, religión, salud.
const RE_TEMAS_EXCLUIDOS=new RegExp([
  'president|diputad|alcald|partido pol|elecci|votá por|vote por|campaña política|bukele|asamblea legislativa|reelecci|candidat|plebiscit|referénd|referend',
  'religi|iglesia|\\\\bpastor(?:es)?\\\\b|sacerdot|evang[eé]l|cat[oó]lic|\\\\bbiblia|b[ií]blic|\\\\bdios\\\\b|\\\\bcristo\\\\b|cristian(?:o|a|os|as|ismo|dad)\\\\b|\\\\bculto\\\\b|\\\\bsecta|musulm|isl[aá]m|jud[ií]o|ate[ií]smo|diezmo|\\\\bmisa\\\\b|\\\\btemplo',
  'milagros[oa]|cura(?:r|s|n|ción)?\\\\b[^.]{0,40}\\\\b(?:c[aá]ncer|diabetes|vih|sida|covid|depresi)|remedio (?:natural|casero)|suplemento|medicamento|vacuna|tratamiento (?:médico|medico|natural)'
].join('|'),'i');

/* ================= UTILIDADES ================= */""")

# ---------- Votos: fuera ----------
rep("<p class=\"nota-sec\">Ocho personas del panel, seleccionadas por polos de reacción, con su ficha censal visible. Debajo de cada una puedes indicar si opinarías igual: con tu micro-perfil el voto cuenta como calibración; sin él, solo como pulso general. Los votos son anónimos y agregados, visibles entre quienes usen esta sala.</p>",
    "<p class=\"nota-sec\">Ocho personas del panel, seleccionadas por polos de reacción, con su ficha censal visible.</p>")
rep("  cont.innerHTML=html; paso(7); renderVoces(); cargarVotos();", "  cont.innerHTML=html; paso(7); renderVoces();")
rep_between("      +'<div class=\"voz-voto\">", "    cont.appendChild(div);", "      ;\n")
rep_between("let votoPend={};", "/* ================= EXPORT + RESET ================= */", "")
rep("/* ================= VOCES + VOTOS ================= */", "/* ================= VOCES ================= */")

open(P, 'w', encoding='utf-8').write(src)
print('OK', len(src))
