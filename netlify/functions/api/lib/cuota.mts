// Cuotas: ensayos por día por IP, tope global diario y presupuesto de llamadas por ensayo.
// Se guardan en Netlify Blobs (consistencia fuerte). Solo contadores: nunca el texto de la idea.
import { getStore } from '@netlify/blobs';
import { ErrorApi, envInt, diaUTC } from './comun.mts';

const cuotas = () => getStore({ name: 'cuotas', consistency: 'strong' });

export function limites() {
  return {
    porIP: envInt('ENSAYOS_POR_DIA', 1),            // ensayos gratuitos por día por conexión
    porMes: envInt('ENSAYOS_POR_MES', 3),           // ensayos gratuitos por mes por conexión
    global: envInt('ENSAYOS_GLOBAL_DIA', 100),      // tope de ensayos gratuitos por día en toda la sala
    presupuesto: envInt('PRESUPUESTO_DIARIO_CENTAVOS', 500),   // gasto máximo diario del nivel gratuito (US$5)
    costoEstimado: envInt('COSTO_ENSAYO_GRATIS_CENTAVOS', 10), // reserva por ensayo en curso mientras no hay gasto real
    nGratis: envInt('ENSAYO_N_GRATIS', 40),
  };
}

const mesUTC = () => diaUTC().slice(0, 7);
const leerN = async (s: ReturnType<typeof cuotas>, k: string) => ((await s.get(k, { type: 'json' })) as { n: number } | null)?.n ?? 0;

const MSG_PRESUPUESTO = 'Hoy alcanzamos el límite diario de la sala gratuita. Puedes ingresar tu propia clave de Anthropic y seguir sin límite, o volver mañana.';

export interface EstadoCuota { usados: number; limite: number; usadosMes: number; limiteMes: number; presupuestoAgotado: boolean; gastadoCentavos: number; presupuestoCentavos: number }

export async function estadoCuota(ipHash: string): Promise<EstadoCuota> {
  const s = cuotas();
  const L = limites();
  const dia = diaUTC();
  const [nDia, nMes, gasto, nG] = await Promise.all([
    leerN(s, `dia/${dia}/${ipHash}`), leerN(s, `mes/${mesUTC()}/${ipHash}`), leerN(s, `gasto/${dia}`), leerN(s, `dia/${dia}/_global`),
  ]);
  // Gasto real si ya se registró; si no, la estimación por ensayos reservados (cubre los ensayos en curso).
  const comprometido = Math.max(gasto, nG * L.costoEstimado);
  return { usados: nDia, limite: L.porIP, usadosMes: nMes, limiteMes: L.porMes, presupuestoAgotado: comprometido >= L.presupuesto || nG >= L.global, gastadoCentavos: gasto, presupuestoCentavos: L.presupuesto };
}

export async function ensayosUsadosHoy(ipHash: string): Promise<{ usados: number; limite: number }> {
  const e = await estadoCuota(ipHash);
  return { usados: e.usados, limite: e.limite };
}

/** Reserva un ensayo gratuito para esta IP. Lanza 429 (con código) si se agotó la cuota diaria, mensual o el presupuesto. */
export async function reservarEnsayo(ipHash: string): Promise<{ restantes: number }> {
  const s = cuotas();
  const L = limites();
  const dia = diaUTC(), mes = mesUTC();
  const kIP = `dia/${dia}/${ipHash}`, kMes = `mes/${mes}/${ipHash}`, kG = `dia/${dia}/_global`;
  const [nIP, nMes, nG, gasto] = await Promise.all([leerN(s, kIP), leerN(s, kMes), leerN(s, kG), leerN(s, `gasto/${dia}`)]);
  if (nIP >= L.porIP) throw new ErrorApi(429, `Ya usaste tu ensayo de muestra de hoy (${L.porIP} por día). Mañana la sala vuelve a abrir, o puedes seguir con tu propia clave.`, 'cuota');
  if (nMes >= L.porMes) throw new ErrorApi(429, `Ya usaste los ${L.porMes} ensayos de muestra de este mes. Puedes seguir con tu propia clave de Anthropic.`, 'cuota');
  if (nG >= L.global || Math.max(gasto, nG * L.costoEstimado) >= L.presupuesto) throw new ErrorApi(429, MSG_PRESUPUESTO, 'presupuesto');
  await Promise.all([s.setJSON(kIP, { n: nIP + 1 }), s.setJSON(kMes, { n: nMes + 1 }), s.setJSON(kG, { n: nG + 1 })]);
  return { restantes: L.porIP - nIP - 1 };
}

/** Suma al gasto real del día (en centavos) de las llamadas hechas con la clave del servidor. */
export async function registrarGasto(centavos: number): Promise<void> {
  if (!(centavos > 0)) return;
  const s = cuotas();
  const k = `gasto/${diaUTC()}`;
  const n = await leerN(s, k);
  await s.setJSON(k, { n: n + centavos });
}

/** Consume una llamada del presupuesto del ensayo. Lanza 429 si el ensayo ya gastó su presupuesto. */
export async function consumirLlamada(ensayoId: string, maximo: number): Promise<number> {
  const s = cuotas();
  const k = `ensayo/${ensayoId}`;
  const v = (await s.get(k, { type: 'json' })) as { n: number } | null;
  const n = (v?.n ?? 0) + 1;
  if (n > maximo) throw new ErrorApi(429, 'Este ensayo agotó su presupuesto de llamadas al modelo.');
  await s.setJSON(k, { n });
  return n;
}

/** Cuántas llamadas al modelo puede necesitar un ensayo con este plan (con margen para reintentos). */
export function presupuestoLlamadas(plan: { n: number; k: number; adv: boolean; cmp: boolean }): number {
  const nEf = plan.cmp ? Math.floor(plan.n / 2) : plan.n;
  const lotes = Math.ceil(nEf / 10) * (plan.cmp ? 2 : 1) * plan.k;
  const voces = 4, extra = (plan.adv ? 1 : 0) + 1;
  return Math.ceil((lotes + voces + extra) * 1.5) + 4;
}
