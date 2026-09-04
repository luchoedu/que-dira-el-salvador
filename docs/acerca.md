# Acerca de la sala de ensayo

**¿Qué dirá El Salvador?** es una sala de ensayo de ideas. Describes un negocio, una campaña o un producto y un panel de personas sintéticas, construido sobre las distribuciones del Censo 2024 de El Salvador, lo evalúa: qué tan bien se entiende, si resulta creíble y relevante, quién lo probaría y por qué no. En minutos, sin registro y sin que tu idea se guarde en ningún lado.

## Cómo funciona

1. **Eliges tu perfil.** Emprendedor, creativo, investigador o explorador. La medición es la misma; cambia el lente con el que se lee el reporte.
2. **Describes la idea.** Dos líneas bastan; más contexto, mejor ensayo.
3. **Defines quién opina.** El Salvador representativo, o una audiencia construida por departamento, zona, sexo, edad, educación, estado civil o tipo de hogar. Puedes guardar audiencias y comparar dos.
4. **Apruebas el plan y ejecutas.** La sala muestra exactamente qué va a correr antes de gastar una sola llamada al modelo.

Cada persona del panel responde un instrumento de cinco dimensiones (comprensión, atractivo, credibilidad, relevancia, intención) en elección forzada, más su objeción principal. Ocho personas, elegidas por polos de reacción, hablan en primera persona. Un pase adversarial busca por qué la idea fallaría. El reporte entrega un veredicto con intervalo de confianza, el mapa por segmento, la polarización, las objeciones rankeadas y una sección fija: dónde este ensayo probablemente se equivoca.

## Qué es y qué no es

Es un generador de hipótesis con base censal. No es una encuesta, no predice ventas y no sustituye a un panel humano. Las personas son sintéticas; las proporciones son reales. Por eso cada score sale con intervalo, y por eso el reporte termina con sus propios límites.

Quedan fuera por diseño la política, la religión y las afirmaciones de salud: una sala de ensayo no debe usarse para fabricar opinión sobre creencias ni para validar tratamientos.

## Tu idea no se almacena

- El texto de tu idea pasa por el servidor solo para construir las preguntas al modelo. No se guarda, no se registra y no se usa para nada más.
- El modelo se consulta a través de la API comercial de Anthropic. Según su política de datos, lo que se envía por la API no se usa para entrenar sus modelos, salvo que quien la usa lo autorice expresamente; en esta sala nunca se envía retroalimentación ni autorización de ese tipo.
- No hay cuentas ni correos. Lo único que persiste son las audiencias que decidas guardar, y quedan en tu dispositivo.
- Si usas tu propia clave de Anthropic, viaja en cada llamada y el servidor la usa para hablar con el modelo. No se guarda en ningún servidor; en el navegador vive solo en la pestaña abierta.

## Tres formas de usarla

- **Gratis, sin registro.** Un ensayo de muestra al día y hasta tres al mes por conexión, con un panel de 40 personas. La sala tiene un presupuesto diario para todos; si se agota, te avisa y puedes seguir con tu propia clave.
- **Con tu propia clave.** Con una API key de Anthropic no hay límite diario: paneles de hasta 140 personas, corridas de estabilidad y datos crudos. Cada ensayo cuesta alrededor de US$0.20 en tu cuenta. Se ingresa dentro de la sala, con el botón "Usar mi clave". [Cómo obtener una clave](https://console.anthropic.com/settings/keys).
- **Código abierto.** Puedes levantar tu propia sala, adaptarla a otro país o a tu equipo. El repositorio incluye el dataset preparado, los scripts y la configuración de despliegue. Repositorio en GitHub: pronto.

## Instala tu propia sala

En resumen, para quien quiera su propia instancia:

1. Clona el repositorio e instala las dependencias con `npm install`.
2. Descarga el dataset [Nemotron-Personas-El-Salvador](https://huggingface.co/datasets/nvidia/Nemotron-Personas-El-Salvador) y corre `python3 scripts/build_data.py` para generar el índice y los textos de las personas.
3. Crea un proyecto en Netlify, sube las personas a Netlify Blobs con `node scripts/upload-personas.mjs` y configura tu `ANTHROPIC_API_KEY` y las variables de cuota.
4. Despliega. Cualquier dominio propio se conecta con un registro CNAME apuntando a tu sitio de Netlify.

Los pasos detallados, las variables disponibles y el modo de desarrollo local están en el README del repositorio.

## Créditos y licencia

- Concepto, diseño y dirección: **Eduardo Aguilar (lucho)** · [lucho.cc](https://lucho.cc).
- Dataset: [nvidia/Nemotron-Personas-El-Salvador](https://huggingface.co/datasets/nvidia/Nemotron-Personas-El-Salvador) (NVIDIA · ANIA · WideLabs), licencia CC BY 4.0, fundamentado en el Censo 2024 de El Salvador.
- Modelo: Claude (Anthropic). Hospedaje: Netlify.

Proyecto independiente, sin afiliación con las instituciones que produjeron el dataset. Las personas son sintéticas; ninguna representa a un ciudadano real.
