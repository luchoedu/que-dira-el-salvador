// Utilidades compartidas por los endpoints de /api/*

export class ErrorApi extends Error {
  status: number;
  codigo?: string;   // p. ej. 'cuota' o 'presupuesto': el cliente decide cómo mostrarlo
  constructor(status: number, mensaje: string, codigo?: string) { super(mensaje); this.status = status; this.codigo = codigo; }
}

export function json(data: unknown, status = 200, extra: Record<string, string> = {}): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', ...extra },
  });
}

export function env(nombre: string, porDefecto?: string): string {
  const v = Netlify.env.get(nombre) ?? porDefecto;
  if (v === undefined) throw new ErrorApi(500, `Falta configurar la variable ${nombre}`);
  return v;
}

export function envInt(nombre: string, porDefecto: number): number {
  const v = Netlify.env.get(nombre);
  const n = v ? parseInt(v, 10) : NaN;
  return Number.isFinite(n) ? n : porDefecto;
}

export async function leerJSON<T = any>(req: Request, maxBytes = 64 * 1024): Promise<T> {
  const txt = await req.text();
  if (txt.length > maxBytes) throw new ErrorApi(413, 'Solicitud demasiado grande');
  try { return JSON.parse(txt) as T; } catch { throw new ErrorApi(400, 'JSON inválido'); }
}

export function diaUTC(d = new Date()): string { return d.toISOString().slice(0, 10); }

/** Misma lista que el cliente (public/index.html, RE_TEMAS_EXCLUIDOS). Tres bloques: política, religión, salud. */
export const RE_TEMAS_EXCLUIDOS = new RegExp([
  'president|diputad|alcald|partido pol|elecci|votá por|vote por|campaña política|bukele|asamblea legislativa|reelecci|candidat|plebiscit|referénd|referend',
  'religi|iglesia|\\bpastor(?:es)?\\b|sacerdot|evang[eé]l|cat[oó]lic|\\bbiblia|b[ií]blic|\\bdios\\b|\\bcristo\\b|cristian(?:o|a|os|as|ismo|dad)\\b|\\bculto\\b|\\bsecta|musulm|isl[aá]m|jud[ií]o|ate[ií]smo|diezmo|\\bmisa\\b|\\btemplo',
  'milagros[oa]|cura(?:r|s|n|ción)?\\b[^.]{0,40}\\b(?:c[aá]ncer|diabetes|vih|sida|covid|depresi)|remedio (?:natural|casero)|suplemento|medicamento|vacuna|tratamiento (?:médico|medico|natural)',
].join('|'), 'i');

export function validarIdea(idea: unknown): string {
  if (typeof idea !== 'string') throw new ErrorApi(400, 'Falta la idea');
  const t = idea.replace(/\s+/g, ' ').trim();
  if (t.length < 12) throw new ErrorApi(400, 'La idea es demasiado corta');
  if (t.length > 700) throw new ErrorApi(400, 'La idea es demasiado larga (máx. 700 caracteres)');
  if (RE_TEMAS_EXCLUIDOS.test(t)) throw new ErrorApi(400, 'Esta sala no ensaya temas político-electorales, religiosos ni afirmaciones de salud');
  return t;
}

/**
 * Respuesta en streaming: envía espacios de "latido" mientras se espera al modelo y al final el JSON.
 * Netlify da 60 s a las funciones que hacen streaming (frente a 10 s a las síncronas), y el JSON
 * admite espacios iniciales, así que el cliente puede seguir usando res.json().
 */
export function respuestaLenta(trabajo: () => Promise<unknown>): Response {
  const enc = new TextEncoder();
  const stream = new ReadableStream({
    start(ctrl) {
      const latido = setInterval(() => { try { ctrl.enqueue(enc.encode(' ')); } catch { /* cerrado */ } }, 4000);
      trabajo()
        .then((data) => { ctrl.enqueue(enc.encode(JSON.stringify({ ok: true, ...(data as object) }))); })
        .catch((e) => {
          const status = e instanceof ErrorApi ? e.status : 500;
          console.error('api error', status, e?.message);
          ctrl.enqueue(enc.encode(JSON.stringify({ ok: false, status, codigo: e?.codigo, error: e?.message || 'Error interno' })));
        })
        .finally(() => { clearInterval(latido); try { ctrl.close(); } catch { /* ya cerrado */ } });
    },
  });
  return new Response(stream, {
    status: 200,
    headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', 'X-Accel-Buffering': 'no' },
  });
}
