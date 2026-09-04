// Tokens de ensayo firmados (HMAC-SHA256). No se guardan: el servidor solo verifica la firma.
import { createHmac, createHash, timingSafeEqual } from 'node:crypto';
import { ErrorApi, env } from './comun.mts';

export interface TokenEnsayo {
  e: string;   // id del ensayo (aleatorio, generado en el servidor)
  x: number;   // expiración (epoch ms)
  c: number;   // máximo de llamadas al modelo permitidas en este ensayo
  h: string;   // hash de la IP que abrió el ensayo
  p?: 1;       // 1 = ensayo con clave propia del usuario (sin cuota)
}

function secreto(): Buffer {
  // ENSAYO_SECRET es opcional: si no está, se deriva de la API key (que nunca sale del servidor).
  const explicito = Netlify.env.get('ENSAYO_SECRET');
  const base = explicito || (Netlify.env.get('MODELO_MOCK') === '1' ? 'solo-desarrollo' : env('ANTHROPIC_API_KEY'));
  return Buffer.from(createHash('sha256').update('ensayo|' + base).digest('hex'), 'utf8');
}

const b64u = (b: Buffer) => b.toString('base64url');

export function hashIP(ip: string): string {
  return createHash('sha256').update(secreto()).update('|ip|').update(ip || 'sin-ip').digest('base64url').slice(0, 22);
}

export function firmar(t: TokenEnsayo): string {
  const cuerpo = b64u(Buffer.from(JSON.stringify(t), 'utf8'));
  const sig = b64u(createHmac('sha256', secreto()).update(cuerpo).digest());
  return cuerpo + '.' + sig;
}

export function verificar(token: unknown): TokenEnsayo {
  if (typeof token !== 'string' || !token.includes('.')) throw new ErrorApi(401, 'Token de ensayo inválido');
  const [cuerpo, sig] = token.split('.');
  const esperada = b64u(createHmac('sha256', secreto()).update(cuerpo).digest());
  const a = Buffer.from(sig || '', 'utf8'), b = Buffer.from(esperada, 'utf8');
  if (a.length !== b.length || !timingSafeEqual(a, b)) throw new ErrorApi(401, 'Token de ensayo inválido');
  let t: TokenEnsayo;
  try { t = JSON.parse(Buffer.from(cuerpo, 'base64url').toString('utf8')); } catch { throw new ErrorApi(401, 'Token de ensayo inválido'); }
  if (!t || typeof t.x !== 'number' || Date.now() > t.x) throw new ErrorApi(401, 'El ensayo expiró. Vuelve a ejecutarlo desde el plan.');
  return t;
}
