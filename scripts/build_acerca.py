#!/usr/bin/env python3
"""Convierte docs/acerca.md (texto público) en public/acerca.html con el estilo del sitio (conversor Markdown mínimo, sin dependencias)."""
import re, html, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
md = open(os.path.join(ROOT, 'docs', 'acerca.md'), encoding='utf-8').read()

def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    t = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', t)
    return t

out = []; i = 0; lines = md.split('\n')
while i < len(lines):
    l = lines[i]
    if l.startswith('```'):
        j = i + 1; buf = []
        while j < len(lines) and not lines[j].startswith('```'): buf.append(lines[j]); j += 1
        out.append('<pre><code>' + html.escape('\n'.join(buf)) + '</code></pre>'); i = j + 1; continue
    if l.startswith('|'):
        rows = []
        while i < len(lines) and lines[i].startswith('|'):
            if not re.match(r'^\|\s*-', lines[i]): rows.append([c.strip() for c in lines[i].strip('|').split('|')])
            i += 1
        h = rows[0]; body = rows[1:]
        out.append('<div class="tabla"><table><thead><tr>' + ''.join(f'<th>{inline(c)}</th>' for c in h) + '</tr></thead><tbody>' +
                   ''.join('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in r) + '</tr>' for r in body) + '</tbody></table></div>'); continue
    m = re.match(r'^(#{1,3})\s+(.*)', l)
    if m:
        n = len(m.group(1)); out.append(f'<h{n}>{inline(m.group(2))}</h{n}>'); i += 1; continue
    if re.match(r'^\s*[-*]\s+', l) or re.match(r'^\s*\d+\.\s+', l):
        ordered = bool(re.match(r'^\s*\d+\.', l)); items = []
        def es_item(t): return bool(re.match(r'^\s*[-*]\s+', t) or re.match(r'^\s*\d+\.\s+', t))
        def es_cont(t): return bool(items) and t.startswith((' ', '\t')) and t.strip() != '' and not es_item(t)
        while i < len(lines) and (es_item(lines[i]) or es_cont(lines[i])):
            if es_cont(lines[i]): items[-1] += ' ' + lines[i].strip()
            else: items.append(re.sub(r'^\s*([-*]|\d+\.)\s+', '', lines[i]))
            i += 1
        tag = 'ol' if ordered else 'ul'
        out.append(f'<{tag}>' + ''.join(f'<li>{inline(x)}</li>' for x in items) + f'</{tag}>'); continue
    if l.strip() == '': i += 1; continue
    para = []
    while i < len(lines) and lines[i].strip() and not lines[i].startswith(('#', '```', '|')) and not re.match(r'^\s*([-*]|\d+\.)\s+', lines[i]):
        para.append(lines[i].strip()); i += 1
    out.append('<p>' + inline(' '.join(para)) + '</p>')

cuerpo = '\n'.join(out)
page = f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Acerca del proyecto · ¿Qué dirá El Salvador?</title>
<meta name="description" content="Qué es la sala de ensayo, cómo funciona, cómo instalar tu propia instancia y créditos.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<meta name="theme-color" content="#1B3A8F">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root{{--tinta:#15171C;--gris:#5B606B;--linea:#E2E3E8;--hueso:#F6F6F4;--blanco:#fff;--cobalto:#1B3A8F;--cobalto-claro:#EDF1FA}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--hueso);color:var(--tinta);font-family:'Inter',system-ui,sans-serif;font-size:15.5px;line-height:1.6;-webkit-font-smoothing:antialiased}}
.topbar{{background:rgba(246,246,244,.92);backdrop-filter:blur(8px);border-bottom:1px solid var(--linea);position:sticky;top:0}}
.topbar .wrap{{display:flex;align-items:center;justify-content:space-between;height:60px}}
.wrap{{max-width:820px;margin:0 auto;padding:0 24px}}
.logo{{font-weight:600;font-size:15.5px;color:var(--tinta);text-decoration:none}} .logo .q{{color:var(--cobalto)}}
.topbar a.btn{{background:var(--cobalto);color:#fff;border-radius:8px;padding:9px 16px;font-weight:600;font-size:14px;text-decoration:none}}
main{{padding:48px 0 96px}}
h1{{font-size:32px;letter-spacing:-.025em;line-height:1.15;margin-bottom:8px}}
h2{{font-size:22px;letter-spacing:-.015em;margin:40px 0 12px;padding-top:24px;border-top:1px solid var(--linea)}}
h3{{font-size:16px;margin:22px 0 8px}}
p{{margin:0 0 14px;max-width:70ch;color:#2A2D35}}
ul,ol{{margin:0 0 14px 22px}} li{{margin:6px 0;max-width:68ch}}
a{{color:var(--cobalto)}}
code{{font-family:'IBM Plex Mono',monospace;font-size:13px;background:var(--cobalto-claro);padding:1px 5px;border-radius:4px}}
pre{{background:var(--blanco);border:1px solid var(--linea);border-radius:8px;padding:14px 16px;overflow-x:auto;margin:0 0 16px}}
pre code{{background:none;padding:0;font-size:13px;line-height:1.6}}
.tabla{{overflow-x:auto;margin:0 0 16px}} table{{border-collapse:collapse;width:100%;font-size:14px}}
th,td{{text-align:left;padding:9px 10px;border-bottom:1px solid var(--linea);vertical-align:top}} th{{font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--gris);font-weight:500}}
footer{{border-top:1px solid var(--linea);padding:24px 0 48px;font-size:13px;color:var(--gris)}}
</style>
</head>
<body>
<nav class="topbar"><div class="wrap"><a class="logo" href="/">¿Qué dirá <span class="q">El Salvador</span>?</a><a class="btn" href="/">Ir a la sala</a></div></nav>
<main><div class="wrap">
{cuerpo}
</div></main>
<footer><div class="wrap">Un proyecto de <b>Eduardo Aguilar (lucho)</b>. Proyecto independiente · las personas del panel son sintéticas.</div></footer>
</body></html>
'''
open(os.path.join(ROOT, 'public', 'acerca.html'), 'w', encoding='utf-8').write(page)
print('acerca.html', len(page))
