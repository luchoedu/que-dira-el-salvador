# ¿Qué dirá El Salvador? · sala de ensayo de ideas

Un proyecto de **Eduardo Aguilar (lucho)** · [lucho.cc](https://lucho.cc)

Panel sintético construido sobre las **148,000 personas** del dataset abierto
[nvidia/Nemotron-Personas-El-Salvador](https://huggingface.co/datasets/nvidia/Nemotron-Personas-El-Salvador)
(ANIA · NVIDIA · WideLabs, CC BY 4.0, base Censo 2024). Sitio estático + funciones de Netlify.

## Arquitectura

| Pieza | Dónde | Qué hace |
|---|---|---|
| `public/index.html` | CDN | La app. Carga el índice de las 148,000 personas (`/data/index.bin.gz`, ~420 KB) y hace filtros y muestreo en el navegador. |
| `public/data/` | CDN | `dict.json` (diccionarios), `index.bin.gz` (1 byte por persona por columna: sexo, edad, municipio, educación, estado civil, hogar, idiomas, zona), `sala.json` (desfile del landing). |
| Netlify Blobs `personas` | servidor | Una entrada por persona (`p/<id>`, JSON gzip) con todos los textos del dataset. Solo se leen las personas muestreadas. |
| `netlify/functions/api` | servidor | `/api/*`: construye los prompts, llama a Claude con la API key del servidor, aplica cuotas. |
| Netlify Blobs `cuotas` | servidor | Contadores de ensayos por día/IP y por ensayo. Nunca se guarda la idea. |

## Tres formas de usarla

1. **Gratis, sin registro.** Un ensayo de muestra al día (`ENSAYOS_POR_DIA`, 1) y tres al mes (`ENSAYOS_POR_MES`, 3) por
   conexión, con panel de 40 personas (`ENSAYO_N_GRATIS`). Para toda la sala hay un presupuesto diario en centavos
   (`PRESUPUESTO_DIARIO_CENTAVOS`, 500 = US$5) que se compara con el gasto real acumulado de las llamadas con la clave del
   servidor (calculado con los tokens de cada respuesta), más un tope de ensayos (`ENSAYOS_GLOBAL_DIA`, 100). Al agotarse,
   la sala avisa y ofrece continuar con clave propia.
2. **Con clave propia.** El usuario pega su API key de Anthropic en la pantalla Modo. Viaja en la cabecera
   `x-clave-propia` en cada llamada; el servidor la usa para hablar con el modelo y no la guarda ni la registra. En el
   navegador queda en `sessionStorage` (solo esa pestaña). Sin cuota, panel hasta 140 y corridas de estabilidad.
3. **Código abierto.** Este repositorio, con el dataset preparado y los scripts, para levantar una instancia propia.

Seguridad frente a abuso:
- La API key del servidor vive solo en Netlify (variable de entorno).
- Los prompts se arman en el servidor: `/api/*` no sirve como proxy genérico al modelo.
- Cuota por conexión y tope global diario (ver arriba); los ensayos con clave propia no consumen cuota.
- Cada ensayo recibe un token firmado (HMAC) con presupuesto de llamadas y expiración de 25 min.
- Temas excluidos (política, religión y afirmaciones de salud) filtrados en cliente y en servidor con la misma
  lista (`RE_TEMAS_EXCLUIDOS`); idea limitada a 700 caracteres.

## Puesta en marcha (una sola vez)

```bash
npm install
# 1) Dataset crudo (3 parquet, ~570 MB) en data/raw/  -> ver scripts/build_data.py
python3 -m pip install --user pyarrow pandas
python3 scripts/build_data.py          # genera public/data/* y data/build/personas.jsonl
# 2) Netlify
npx netlify login
npx netlify link                        # o: npx netlify sites:create
node scripts/upload-personas.mjs        # sube las 148,000 personas a Blobs (~10–20 min, reanudable con --desde=N)
# 3) Variables en Netlify (UI o CLI):
npx netlify env:set ANTHROPIC_API_KEY sk-ant-...
npx netlify env:set CLAUDE_MODEL claude-sonnet-5
npx netlify env:set ENSAYOS_POR_DIA 1
npx netlify env:set ENSAYOS_GLOBAL_DIA 100
npx netlify env:set ENSAYOS_POR_MES 3
npx netlify env:set PRESUPUESTO_DIARIO_CENTAVOS 500
# 4) Deploy
npx netlify deploy --prod
```

## Desarrollo local

`cp .env.example .env`, ajusta y luego `npm run dev` (abre http://localhost:8888).
Con `MODELO_MOCK=1` la sala responde con datos simulados (sin costo) y con
`PERSONAS_JSONL=./data/build/personas.jsonl` lee las personas del archivo local en vez de Blobs
(requiere `node scripts/index-jsonl.mjs` para generar `personas.offsets`).

## Dominio propio

En Netlify: *Domain management → Add domain* con tu subdominio. En el DNS de tu dominio, crea un registro `CNAME`
apuntando a `<nombre-del-sitio>.netlify.app`. Netlify emite el certificado TLS automáticamente al detectar el registro.

## Costos de referencia

Un ensayo estándar (80 personas, voces, pase adversarial y síntesis) hace ~15 llamadas al modelo,
~60K tokens de entrada y ~8K de salida: **≈ US$0.20 con `claude-sonnet-5`** (US$2/M entrada, US$10/M salida)
o **≈ US$0.50 con `claude-opus-5`** (US$5/M, US$25/M). Un ensayo de muestra (40 personas) cuesta la mitad. Con 1 ensayo/día/IP
y tope global de 100/día, el gasto máximo del nivel gratuito es ~US$10/día con Sonnet 5.

## Frontend

`public/index.html` es la fuente de verdad del frontend: edítalo directamente. `original/` conserva el artefacto
de claude.ai tal cual; `scripts/patch_frontend.py` y `scripts/redesign.py` documentan cómo se llegó de ese
original a la versión actual (adaptación a Netlify, dataset completo, rediseño sobrio, retiro de los votos),
pero ya no hace falta correrlos.

## Créditos

- Concepto, diseño y dirección: **Eduardo Aguilar (lucho)**.
- Dataset: [nvidia/Nemotron-Personas-El-Salvador](https://huggingface.co/datasets/nvidia/Nemotron-Personas-El-Salvador)
  (NVIDIA · ANIA · WideLabs), licencia CC BY 4.0, fundamentado en el Censo 2024 de El Salvador.
- Modelo: Claude (Anthropic). Hospedaje: Netlify.

Proyecto independiente, sin afiliación con las instituciones que produjeron el dataset. Las personas son sintéticas;
ninguna representa a un ciudadano real.
