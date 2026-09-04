// Router de /api/*. Endpoints:
//   GET  /api/estado        cuota usada hoy por esta conexión + modelo + tamaño del ensayo gratuito
//   POST /api/ensayo        reserva un ensayo (cuota por IP) y devuelve un token firmado
//
// Clave propia: si la solicitud trae la cabecera x-clave-propia (API key de Anthropic del usuario), las llamadas
// al modelo se hacen con esa clave, sin cuota y con el panel completo. La clave no se guarda ni se registra.
//   POST /api/evaluar       panel cuantitativo: idea + ids (≤10) -> respuestas
//   POST /api/voces         voces cualitativas: idea + items (≤2) -> reacciones
//   POST /api/adversarial   idea (+contexto) -> 3 riesgos
//   POST /api/sintesis      idea + resumen + perfil -> síntesis
import type { Context, Config } from '@netlify/functions';
import { ErrorApi, json, leerJSON, validarIdea, respuestaLenta } from './lib/comun.mts';
import { firmar, verificar, hashIP, type TokenEnsayo } from './lib/token.mts';
import { reservarEnsayo, consumirLlamada, presupuestoLlamadas, estadoCuota, limites, contar, resumenStats } from './lib/cuota.mts';
import { timingSafeEqual } from 'node:crypto';
import { leerPersonas, validarIds, fichaPublica } from './lib/personas.mts';
import { evaluarLote, generarVoces, adversarial, sintesis, modelo } from './lib/claude.mts';
import { randomBytes } from 'node:crypto';
import { diaUTC } from './lib/comun.mts';

const LENTES: Record<string, { nombre: string; enfoque: string }> = {
  emprendedor: { nombre: 'Emprendedor', enfoque: 'viabilidad de negocio, quién sería el primer cliente, riesgo principal y qué validar antes de invertir' },
  creativo: { nombre: 'Creativo / Marca', enfoque: 'claridad del mensaje, diferenciación frente a lo que ya existe, tono y credibilidad del claim' },
  investigador: { nombre: 'Investigador', enfoque: 'solidez metodológica, tamaño de efecto entre segmentos, límites del instrumento y qué validar con panel humano' },
  explorador: { nombre: 'Explorador', enfoque: 'lectura general de la reacción salvadoreña, lo más sorprendente del resultado' },
};

function clavePropia(req: Request): string | undefined {
  const v = (req.headers.get('x-clave-propia') || '').trim();
  if (!v) return undefined;
  if (!/^sk-ant-[A-Za-z0-9_-]{20,}$/.test(v)) throw new ErrorApi(400, 'La clave no tiene el formato de una API key de Anthropic (empieza con sk-ant-).');
  return v;
}

async function autorizar(body: any, req: Request, ip: string): Promise<{ t: TokenEnsayo; clave?: string }> {
  const t = verificar(body?.token);
  if (t.h !== hashIP(ip)) throw new ErrorApi(401, 'El token no corresponde a esta conexión.');
  const clave = clavePropia(req);
  if (t.p && !clave) throw new ErrorApi(401, 'Este ensayo se abrió con clave propia; vuelve a ingresarla.');
  if (!t.p && clave) throw new ErrorApi(401, 'Este ensayo se abrió sin clave; ejecútalo de nuevo desde el plan.');
  await consumirLlamada(t.e, t.c);
  return { t, clave };
}

export default async (req: Request, context: Context) => {
  const url = new URL(req.url);
  const ruta = url.pathname.replace(/^\/api\/?/, '').replace(/\/$/, '');
  const ip = context.ip || req.headers.get('x-nf-client-connection-ip') || '';
  try {
    if (ruta === 'estado' && req.method === 'GET') {
      const e = await estadoCuota(hashIP(ip));
      const gratis = !!Netlify.env.get('ANTHROPIC_API_KEY') || Netlify.env.get('MODELO_MOCK') === '1';
      return json({ ok: true, usados: e.usados, limite: e.limite, usadosMes: e.usadosMes, limiteMes: e.limiteMes, presupuestoAgotado: e.presupuestoAgotado, nGratis: limites().nGratis, gratis, modelo: modelo() });
    }

    if (ruta === 'visita' && req.method === 'POST') {
      await contar(`v/${diaUTC()}`);
      return new Response(null, { status: 204 });
    }

    if (ruta === 'stats' && req.method === 'GET') {
      const esperado = Netlify.env.get('STATS_TOKEN') || '';
      const dado = url.searchParams.get('t') || '';
      const a = Buffer.from(dado), b = Buffer.from(esperado);
      if (!esperado || a.length !== b.length || !timingSafeEqual(a, b)) throw new ErrorApi(404, 'Ruta no encontrada');
      const filas = await resumenStats(30);
      const tot = filas.reduce((acc, f) => ({ visitas: acc.visitas + f.visitas, gratis: acc.gratis + f.gratis, propia: acc.propia + f.propia, completados: acc.completados + f.completados, gasto: acc.gasto + f.gastoCentavos }), { visitas: 0, gratis: 0, propia: 0, completados: 0, gasto: 0 });
      const fila = (f: { dia: string; visitas: number; gratis: number; propia: number; completados: number; gastoCentavos: number }) =>
        `${f.dia.padEnd(12)}${String(f.visitas).padStart(8)}${String(f.gratis).padStart(9)}${String(f.propia).padStart(9)}${String(f.completados).padStart(12)}${('$' + (f.gastoCentavos / 100).toFixed(2)).padStart(10)}`;
      const txt = ['¿Qué dirá El Salvador? · uso de los últimos 30 días (UTC)', '',
        'fecha'.padEnd(12) + 'visitas'.padStart(8) + 'gratis'.padStart(9) + 'propia'.padStart(9) + 'completados'.padStart(12) + 'gasto'.padStart(10),
        '-'.repeat(60), ...filas.map(fila), '-'.repeat(60),
        fila({ dia: 'total', visitas: tot.visitas, gratis: tot.gratis, propia: tot.propia, completados: tot.completados, gastoCentavos: tot.gasto }), '',
        'visitas: cargas del landing (una por pestaña y sesión). gratis/propia: ensayos iniciados por tipo.',
        'completados: ensayos que llegaron a la síntesis. gasto: costo real de las llamadas con la clave del servidor.'].join('\n');
      return new Response(txt, { status: 200, headers: { 'Content-Type': 'text/plain; charset=utf-8', 'Cache-Control': 'no-store' } });
    }

    if (ruta === 'ensayo' && req.method === 'POST') {
      const body = await leerJSON(req);
      const plan = body?.plan || {};
      const clave = clavePropia(req);
      const adv = !!plan.adv, cmp = !!plan.cmp;
      // Nivel gratuito: panel de muestra (ENSAYO_N_GRATIS) y una sola corrida. Con clave propia: hasta 140 y 3 corridas.
      const n = clave ? Math.min(140, Math.max(40, parseInt(plan.n, 10) || 80)) : limites().nGratis;
      const k = clave ? Math.min(3, Math.max(1, parseInt(plan.k, 10) || 1)) : 1;
      const h = hashIP(ip);
      const restantes = clave ? null : (await reservarEnsayo(h)).restantes;
      const t: TokenEnsayo = { e: randomBytes(9).toString('base64url'), x: Date.now() + 25 * 60 * 1000, c: presupuestoLlamadas({ n, k, adv, cmp }), h, ...(clave ? { p: 1 as const } : {}) };
      await contar(`e/${diaUTC()}/${clave ? 'propia' : 'gratis'}`);
      return json({ ok: true, token: firmar(t), ensayo: t.e, restantes, n, k, propia: !!clave, llamadasMax: t.c, modelo: modelo() });
    }

    if (ruta === 'evaluar' && req.method === 'POST') {
      const body = await leerJSON(req);
      const { clave } = await autorizar(body, req, ip);
      const idea = validarIdea(body.idea);
      const ids = validarIds(body.ids, 10);
      const ronda = Math.min(3, Math.max(1, parseInt(body.ronda, 10) || 1));
      return respuestaLenta(async () => {
        const personas = await leerPersonas(ids);
        const respuestas = await evaluarLote(idea, personas, ronda, clave);
        const porId = new Map(personas.map((p) => [p.id, p]));
        return { respuestas: respuestas.map((r) => ({ ...r, ficha: fichaPublica(porId.get(r.id)!) })) };
      });
    }

    if (ruta === 'voces' && req.method === 'POST') {
      const body = await leerJSON(req);
      const { clave } = await autorizar(body, req, ip);
      const idea = validarIdea(body.idea);
      const items = Array.isArray(body.items) ? body.items.slice(0, 2) : [];
      const ids = validarIds(items.map((x: any) => x?.id), 2);
      const previas: Record<number, { i: number; obj: string }> = {};
      items.forEach((x: any, k: number) => { previas[ids[k]] = { i: Math.min(5, Math.max(1, parseInt(x?.i, 10) || 3)), obj: String(x?.obj || 'OTRA').slice(0, 12) }; });
      return respuestaLenta(async () => {
        const personas = await leerPersonas(ids);
        const voces = await generarVoces(idea, personas, previas, clave);
        const porId = new Map(personas.map((p) => [p.id, p]));
        return { voces: voces.map((v) => ({ ...v, ficha: fichaPublica(porId.get(v.id)!) })) };
      });
    }

    if (ruta === 'adversarial' && req.method === 'POST') {
      const body = await leerJSON(req);
      const { clave } = await autorizar(body, req, ip);
      const idea = validarIdea(body.idea);
      const contexto = String(body.contexto || '').slice(0, 600);
      return respuestaLenta(async () => ({ riesgos: await adversarial(idea, contexto, clave) }));
    }

    if (ruta === 'sintesis' && req.method === 'POST') {
      const body = await leerJSON(req);
      const { clave } = await autorizar(body, req, ip);
      const idea = validarIdea(body.idea);
      const resumen = String(body.resumen || '').slice(0, 900);
      const lente = LENTES[String(body.perfil)] || LENTES.explorador;
      return respuestaLenta(async () => { const r = await sintesis(idea, resumen, lente, clave); await contar(`c/${diaUTC()}/${clave ? 'propia' : 'gratis'}`); return { sintesis: r }; });
    }

    throw new ErrorApi(404, 'Ruta no encontrada');
  } catch (e: any) {
    const status = e instanceof ErrorApi ? e.status : 500;
    if (status >= 500) console.error('api', ruta, e);
    return json({ ok: false, codigo: e?.codigo, error: e?.message || 'Error interno' }, status);
  }
};

export const config: Config = { path: '/api/*' };
