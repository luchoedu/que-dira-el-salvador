// Lectura de personas desde Netlify Blobs (store "personas", clave p/<id>, JSON gzip).
import { gunzipSync } from 'node:zlib';
import fs from 'node:fs';
import { getStore } from '@netlify/blobs';
import { ErrorApi } from './comun.mts';

export interface Persona {
  id: number; uuid: string; nombre: string; sexo: string; edad: number; edu: string; ocup: string;
  zona: string; muni: string; depto: string; civil: string; hogar: string; idiomas: string;
  persona: string; profesional: string; familia: string; cultura: string; culinaria: string;
  deportes: string; artes: string; viajes: string; habilidades: string; habilidades_list: string[];
  hobbies: string; hobbies_list: string[]; metas: string;
}

const N_MAX = 148000;

export function validarIds(ids: unknown, max: number): number[] {
  if (!Array.isArray(ids) || !ids.length || ids.length > max) throw new ErrorApi(400, `Se esperaban entre 1 y ${max} ids`);
  const out = ids.map((x) => Number(x));
  if (out.some((n) => !Number.isInteger(n) || n < 0 || n >= N_MAX)) throw new ErrorApi(400, 'Id de persona inválido');
  return out;
}

// Solo desarrollo: PERSONAS_JSONL apunta a data/build/personas.jsonl y se lee por offset
// (data/build/personas.offsets, generado por scripts/index-jsonl.mjs) sin pasar por Blobs.
let offsets: BigUint64Array | null = null;
function leerLocal(id: number): Persona | null {
  const ruta = Netlify.env.get('PERSONAS_JSONL');
  if (!ruta) return null;
  if (!offsets) offsets = new BigUint64Array(fs.readFileSync(ruta.replace(/\.jsonl$/, '.offsets')).buffer.slice(0));
  if (id + 1 >= offsets.length) return null;
  const ini = Number(offsets[id]), fin = Number(offsets[id + 1]);
  const fd = fs.openSync(ruta, 'r'); const buf = Buffer.alloc(fin - ini);
  fs.readSync(fd, buf, 0, fin - ini, ini); fs.closeSync(fd);
  return JSON.parse(buf.toString('utf8')) as Persona;
}

export async function leerPersonas(ids: number[]): Promise<Persona[]> {
  if (Netlify.env.get('PERSONAS_JSONL')) return ids.map(leerLocal).filter((p): p is Persona => !!p);
  const store = getStore('personas');
  const out = await Promise.all(ids.map(async (id) => {
    const buf = await store.get(`p/${id}`, { type: 'arrayBuffer' });
    if (!buf) return null;
    try { return JSON.parse(gunzipSync(Buffer.from(buf)).toString('utf8')) as Persona; }
    catch { return null; }
  }));
  const ok = out.filter((p): p is Persona => !!p);
  if (!ok.length) throw new ErrorApi(503, 'La sala no tiene cargadas las personas (falta subir el dataset a Blobs).');
  return ok;
}

const EDU: Record<string, string> = { ninguno: 'sin escolaridad', primaria: 'primaria', secundaria: 'secundaria', bachillerato: 'bachillerato', tecnico: 'técnico', universitario: 'universitario', posgrado: 'posgrado' };
const CIVIL: Record<string, string> = { casado: 'casado/a', soltero: 'soltero/a', union_libre: 'en unión libre', separado: 'separado/a', viudo: 'viudo/a', divorciado: 'divorciado/a' };
const HOGAR: Record<string, string> = { extendido: 'hogar extendido', nuclear: 'hogar nuclear', monoparental: 'hogar monoparental', pareja: 'vive en pareja sin hijos en casa', unipersonal: 'vive solo/a' };

export function fichaCorta(p: Persona): string {
  return `${p.nombre}, ${p.edad} años, ${p.sexo.toLowerCase()}, zona ${p.zona}, ${p.muni} (${p.depto}), ${EDU[p.edu] || p.edu}, ${CIVIL[p.civil] || p.civil}, ${HOGAR[p.hogar] || p.hogar}, habla ${p.idiomas}. Ocupación: ${p.ocup}.`;
}

/** Ficha que se muestra en la interfaz (sin textos largos). */
export function fichaPublica(p: Persona) {
  return { id: p.id, nombre: p.nombre, edad: p.edad, sexo: p.sexo, zona: p.zona, muni: p.muni, depto: p.depto, edu: p.edu, ocup: p.ocup, civil: p.civil, hogar: p.hogar };
}
