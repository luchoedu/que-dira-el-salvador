#!/usr/bin/env node
/**
 * Sube las 148,000 personas a Netlify Blobs (store "personas", una entrada por persona,
 * JSON comprimido con gzip). Es un proceso de una sola vez (~10-20 min).
 *
 * Requiere:
 *   - data/build/personas.jsonl  (salida de `python3 scripts/build_data.py`)
 *   - NETLIFY_SITE_ID   (o un proyecto enlazado con `npx netlify link` -> .netlify/state.json)
 *   - NETLIFY_AUTH_TOKEN (o haber hecho `npx netlify login`; se lee del config del CLI)
 *
 * Uso:  node scripts/upload-personas.mjs [--desde=0] [--hasta=148000] [--concurrencia=24]
 * Es reanudable: si se corta, vuelve a correr con --desde=N.
 */
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import readline from 'node:readline';
import { gzipSync } from 'node:zlib';
import { getStore } from '@netlify/blobs';

const args = Object.fromEntries(process.argv.slice(2).map(a => { const m = a.match(/^--([^=]+)=(.*)$/); return m ? [m[1], m[2]] : [a, true]; }));
const DESDE = parseInt(args.desde ?? '0', 10);
const HASTA = parseInt(args.hasta ?? '1000000', 10);
const CONC = parseInt(args.concurrencia ?? '24', 10);

function leerToken() {
  if (process.env.NETLIFY_AUTH_TOKEN) return process.env.NETLIFY_AUTH_TOKEN;
  const candidatos = [
    path.join(os.homedir(), 'Library', 'Preferences', 'netlify', 'config.json'),
    path.join(os.homedir(), '.config', 'netlify', 'config.json'),
    path.join(os.homedir(), '.netlify', 'config.json'),
  ];
  for (const p of candidatos) {
    if (fs.existsSync(p)) {
      const cfg = JSON.parse(fs.readFileSync(p, 'utf8'));
      const uid = cfg.userId; const u = cfg.users?.[uid] ?? Object.values(cfg.users ?? {})[0];
      if (u?.auth?.token) return u.auth.token;
    }
  }
  throw new Error('No hay NETLIFY_AUTH_TOKEN ni sesión de `npx netlify login`.');
}
function leerSiteId() {
  if (process.env.NETLIFY_SITE_ID) return process.env.NETLIFY_SITE_ID;
  const p = path.join(process.cwd(), '.netlify', 'state.json');
  if (fs.existsSync(p)) { const s = JSON.parse(fs.readFileSync(p, 'utf8')); if (s.siteId) return s.siteId; }
  throw new Error('No hay NETLIFY_SITE_ID ni proyecto enlazado (`npx netlify link`).');
}

const token = leerToken();
const siteID = leerSiteId();
const store = getStore({ name: 'personas', siteID, token });

const archivo = path.join(process.cwd(), 'data', 'build', 'personas.jsonl');
if (!fs.existsSync(archivo)) throw new Error('Falta data/build/personas.jsonl (corre python3 scripts/build_data.py)');

const rl = readline.createInterface({ input: fs.createReadStream(archivo, 'utf8'), crlfDelay: Infinity });
let enCurso = 0, hechas = 0, errores = 0, linea = -1, cerrado = false;
const t0 = Date.now();
const cola = [];
let resolverDrenado = null;

async function subir(rec) {
  const cuerpo = gzipSync(Buffer.from(JSON.stringify(rec), 'utf8'), { level: 9 });
  for (let intento = 0; intento < 4; intento++) {
    try {
      await store.set(`p/${rec.id}`, cuerpo);
      return;
    } catch (e) {
      if (intento === 3) { errores++; console.error('ERROR id', rec.id, e.message); return; }
      await new Promise(r => setTimeout(r, 500 * (intento + 1)));
    }
  }
}

async function bombear() {
  while (cola.length && enCurso < CONC) {
    const rec = cola.shift(); enCurso++;
    subir(rec).finally(() => {
      enCurso--; hechas++;
      if (hechas % 1000 === 0) {
        const s = (Date.now() - t0) / 1000;
        console.log(`${hechas} subidas · ${(hechas / s).toFixed(1)}/s · errores ${errores} · último id ${rec.id}`);
      }
      bombear();
      if (!cola.length && enCurso === 0 && resolverDrenado) resolverDrenado();
    });
  }
  if (!cerrado && cola.length < CONC * 4) rl.resume();
}

rl.on('line', (l) => {
  linea++;
  if (linea < DESDE || linea >= HASTA) return;
  cola.push(JSON.parse(l));
  if (cola.length >= CONC * 8) rl.pause();
  bombear();
});
rl.on('close', async () => {
  cerrado = true;
  await new Promise(r => { resolverDrenado = r; if (!cola.length && enCurso === 0) r(); });
  console.log(`Listo: ${hechas} personas subidas, ${errores} errores, ${((Date.now() - t0) / 60000).toFixed(1)} min.`);
});
