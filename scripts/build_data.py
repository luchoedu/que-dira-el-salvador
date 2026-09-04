#!/usr/bin/env python3
"""Construye los datos derivados del dataset Nemotron-Personas-El-Salvador.

Entrada:  data/raw/train-*.parquet  (148,000 personas, CC BY 4.0, NVIDIA/ANIA/WideLabs)
Salidas:
  public/data/dict.json      diccionarios (municipios, departamentos, educación, etc.) + stats
  public/data/index.bin.gz   índice binario por columnas (1 byte por persona por columna)
  public/data/sala.json      40 personas para el desfile del landing
  data/build/personas.jsonl  registro completo por persona (para subir a Netlify Blobs)

El id de cada persona es su posición (0..n-1) tras ordenar por uuid: estable y compacto.
"""
import glob, gzip, json, os, re, struct, sys, collections, random
import pyarrow.parquet as pq

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'data', 'raw')
OUT_PUB = os.path.join(ROOT, 'public', 'data')
OUT_BUILD = os.path.join(ROOT, 'data', 'build')
os.makedirs(OUT_PUB, exist_ok=True); os.makedirs(OUT_BUILD, exist_ok=True)

TEXT_COLS = ['persona','professional_persona','family_persona','culinary_persona','cultural_background',
             'skills_and_expertise','hobbies_and_interests','career_goals_and_ambitions',
             'sports_persona','arts_persona','travel_persona']
CAP = re.compile(r"[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+")
STOP = set("""En La El Con Desde Cada Aunque Los Las Todos Todas Para Al Un Una Su Sus Hoy Como Entre Tras Sin Por Durante
Mientras Después Antes Cuando Ya A De Es Este Esta Ese Esa Aquí Allí Hace Pese Gracias Junto Ahora Bajo Sobre Según Siendo Ser
Tal Muy Más Dentro Fuera Hasta Le Lo Se Si No Pero Ni Que Quien Aún Así También Tiene Lleva Trabaja Vive Nació Centro Norte Sur
Este Oeste Costa Enero Febrero Marzo Abril Mayo Junio Agosto Septiembre Octubre Noviembre Diciembre Dios Navidad Semana Santa
Lunes Martes Miércoles Jueves Viernes Sábado Salvadoreña Salvadoreño Salvadoreñas Salvadoreños Nada Nadie Siempre Nunca Luego
Además Sólo Solo Aquel Aquella Uno Dos Tres Cuatro Cinco Seis Siete Ocho Nueve Diez Actualmente Recientemente Finalmente Primero
Universidad Instituto Escuela Colegio Hospital Ministerio Alcaldía Iglesia Banco Empresa Cooperativa Municipalidad Porque Tanto
Toda Todo Otra Otro Otras Otros Ellos Ellas Ella Ahí Allá Sí Cómo Qué Dónde Han Ha Fue Era Está Están Son Hay Puede Debe Suele
Quiere Sabe Sigue Va Ve Vende Cultiva Atiende Abre Cierra Sale Entra Muchas Muchos Pocas Pocos Algunas Algunos Varios Varias
Ambos Ambas Ninguna Ninguno Todavía Apenas Casi Bien Mal Mejor Peor Mucho Poco Tan Jamás Quizá Quizás Acaso Vez Incluso Pues
Entonces Igual Mismo Misma Propio Propia Cual Cuál Cuales Cuáles Confiable Cumple Maneja Amante Fiel Orgullosa Orgulloso
Pupusas Pupusa Fiesta Fiestas Feria Ferias Selección Copa Liga Barrio Colonia Cantón Caserío Mercado Parque Playa Volcán Lago
Río Cerro Sierra Mar Sol Luna Estados Unidos Guatemala Honduras Nicaragua México Costa Rica Panamá""".split())

def load():
    files = sorted(glob.glob(os.path.join(RAW, 'train-*.parquet')))
    if not files: sys.exit('No hay parquet en data/raw')
    tables = [pq.read_table(f) for f in files]
    import pyarrow as pa
    t = pa.concat_tables(tables)
    return t

def main():
    t = load()
    n = t.num_rows
    print('filas', n)
    cols = {c: t.column(c).to_pylist() for c in t.column_names}
    order = sorted(range(n), key=lambda i: cols['uuid'][i])

    munis = sorted(set(cols['municipality']))
    deptos = sorted(set(cols['department']))
    muni_depto = {}
    for m, d in zip(cols['municipality'], cols['department']): muni_depto[m] = d
    EDU_ORDER = ['ninguno','primaria','secundaria','bachillerato','tecnico','universitario','posgrado']
    edus = [e for e in EDU_ORDER if e in set(cols['education_level'])] + sorted(set(cols['education_level']) - set(EDU_ORDER))
    civiles = sorted(set(cols['marital_status']))
    hogares = sorted(set(cols['household_type']))
    idiomas = sorted(set(cols['languages_spoken']))
    ocups = sorted(set(cols['occupation']))
    ix = lambda lst: {v: i for i, v in enumerate(lst)}
    I_M, I_D, I_E, I_C, I_H, I_L, I_O = ix(munis), ix(deptos), ix(edus), ix(civiles), ix(hogares), ix(idiomas), ix(ocups)
    assert len(ocups) < 256 and len(munis) < 256

    places = sorted(set(munis) | set(deptos) | {'El Salvador','San Salvador','Santa Ana','San Miguel','San Vicente','La Libertad','La Paz','La Unión'}, key=len, reverse=True)
    PLACE_RE = re.compile('|'.join(re.escape(p) for p in places))
    def clean(s): return PLACE_RE.sub(' ', (s or '').replace(' ', ' ').replace('\xa0', ' '))
    def nombre_de(i):
        prof = clean(cols['professional_persona'][i])
        textos = [clean(cols[c][i]) for c in TEXT_COLS]
        conteo = collections.Counter()
        for tx in textos:
            for w in set(CAP.findall(tx)):
                if w not in STOP: conteo[w] += 1
        if not conteo: return None
        # candidato: aparece en más textos; empate -> primero en professional_persona
        pos = {}
        for m in CAP.finditer(prof):
            pos.setdefault(m.group(0), m.start())
        mejor = max(conteo.items(), key=lambda kv: (kv[1], -pos.get(kv[0], 10**9)))
        if mejor[1] >= 3: return mejor[0]
        m2 = re.search(r"([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)(?:\s[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){0,3},?\s*(?:quien\s+a\s+sus\s+|de\s+|con\s+|a\s+sus\s+)?\d+\s*años", prof)
        if m2 and m2.group(1) not in STOP: return m2.group(1)
        return mejor[0] if mejor[1] >= 2 else None

    # columnas del índice (1 byte c/u): sexo, edad, muni, edu, civil, hogar, idiomas, zona
    sexo = bytearray(n); edad = bytearray(n); muni = bytearray(n); edu = bytearray(n)
    civil = bytearray(n); hogar = bytearray(n); idio = bytearray(n); zona = bytearray(n)
    sin_nombre = 0; nombres = collections.Counter()
    jsonl = open(os.path.join(OUT_BUILD, 'personas.jsonl'), 'w', encoding='utf-8')
    sala_pool = []
    rnd = random.Random(503)
    for new_id, i in enumerate(order):
        nom = nombre_de(i)
        if not nom:
            sin_nombre += 1
            nom = 'Vecina' if cols['sex'][i] == 'Femenino' else 'Vecino'
        nombres[nom] += 1
        sexo[new_id] = 1 if cols['sex'][i] == 'Femenino' else 0
        edad[new_id] = min(255, int(cols['age'][i]))
        muni[new_id] = I_M[cols['municipality'][i]]
        edu[new_id] = I_E[cols['education_level'][i]]
        civil[new_id] = I_C[cols['marital_status'][i]]
        hogar[new_id] = I_H[cols['household_type'][i]]
        idio[new_id] = I_L[cols['languages_spoken'][i]]
        zona[new_id] = 1 if cols['area'][i] == 'urbano' else 0
        def L(s):
            try: return json.loads(s) if s else []
            except Exception: return []
        rec = {
            'id': new_id, 'uuid': cols['uuid'][i], 'nombre': nom,
            'sexo': cols['sex'][i], 'edad': int(cols['age'][i]), 'edu': cols['education_level'][i],
            'ocup': cols['occupation'][i], 'zona': cols['area'][i], 'muni': cols['municipality'][i],
            'depto': cols['department'][i], 'civil': cols['marital_status'][i], 'hogar': cols['household_type'][i],
            'idiomas': cols['languages_spoken'][i],
            'persona': cols['persona'][i], 'profesional': cols['professional_persona'][i],
            'familia': cols['family_persona'][i], 'cultura': cols['cultural_background'][i],
            'culinaria': cols['culinary_persona'][i], 'deportes': cols['sports_persona'][i],
            'artes': cols['arts_persona'][i], 'viajes': cols['travel_persona'][i],
            'habilidades': cols['skills_and_expertise'][i], 'habilidades_list': L(cols['skills_and_expertise_list'][i]),
            'hobbies': cols['hobbies_and_interests'][i], 'hobbies_list': L(cols['hobbies_and_interests_list'][i]),
            'metas': cols['career_goals_and_ambitions'][i],
        }
        jsonl.write(json.dumps(rec, ensure_ascii=False) + '\n')
        if rnd.random() < 0.002 and nom not in ('Vecino','Vecina'):
            sala_pool.append({'id': new_id, 'nombre': nom, 'edad': rec['edad'], 'muni': rec['muni'], 'ocup': rec['ocup']})
        if new_id % 20000 == 0: print('...', new_id)
    jsonl.close()

    raw = bytes(sexo) + bytes(edad) + bytes(muni) + bytes(edu) + bytes(civil) + bytes(hogar) + bytes(idio) + bytes(zona)
    with gzip.open(os.path.join(OUT_PUB, 'index.bin.gz'), 'wb', compresslevel=9) as f: f.write(raw)
    stats = {
        'n': n, 'urbano': int(sum(zona)), 'edadMin': int(min(edad)), 'edadMax': int(max(edad)),
        'porDepto': {d: 0 for d in deptos}, 'porEdu': {e: 0 for e in edus},
    }
    for m_i in muni: stats['porDepto'][muni_depto[munis[m_i]]] += 1
    for e_i in edu: stats['porEdu'][edus[e_i]] += 1
    dic = {
        'version': 1, 'n': n,
        'columnas': ['sexo','edad','muni','edu','civil','hogar','idiomas','zona'],
        'sexo': ['Masculino','Femenino'], 'zona': ['rural','urbano'],
        'munis': munis, 'muniDepto': [I_D[muni_depto[m]] for m in munis], 'deptos': deptos,
        'edu': edus, 'civil': civiles, 'hogar': hogares, 'idiomas': idiomas,
        'stats': stats, 'sinNombre': sin_nombre,
        'fuente': 'nvidia/Nemotron-Personas-El-Salvador (ANIA · NVIDIA · WideLabs, CC BY 4.0, Censo 2024)'
    }
    json.dump(dic, open(os.path.join(OUT_PUB, 'dict.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    rnd.shuffle(sala_pool)
    json.dump(sala_pool[:40], open(os.path.join(OUT_PUB, 'sala.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print('sin nombre', sin_nombre, 'nombres distintos', len(nombres))
    print('top', nombres.most_common(12))
    print('raros', [k for k, v in nombres.items() if v == 1][:40])
    print('index.bin.gz', os.path.getsize(os.path.join(OUT_PUB, 'index.bin.gz')), 'bytes')
    print('personas.jsonl', os.path.getsize(os.path.join(OUT_BUILD, 'personas.jsonl')), 'bytes')

if __name__ == '__main__':
    main()
