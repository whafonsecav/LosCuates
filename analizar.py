"""Resume las respuestas de la encuesta Los Cuates.

Uso:
    python analizar.py respuestas.csv            (CSV descargado de Google Sheets: Archivo > Descargar > .csv)

Genera "resultados.md" junto al CSV: conteos y porcentajes por pregunta, separados por ruta
(A = la probó, B = no la ha probado), más unos cruces que responden a las hipótesis del deck.
Solo usa la biblioteca estándar de Python.
"""
import csv
import sys
from collections import Counter
from pathlib import Path

PREGUNTAS = [
    # (columna, título, ruta: 'A', 'B' o None para todas)
    ('edad', 'Edad', None),
    ('probado', '¿Ya probaste Los Cuates?', None),
    ('sabores', 'Sabores probados (múltiple)', 'A'),
    ('favorito', 'Sabor favorito', 'A'),
    ('gusta', 'Lo que más gusta (hasta 3)', None),
    ('mejorar', 'Qué le mejorarían (hasta 2)', 'A'),
    ('tequila', '¿Sienten el tequila?', 'A'),
    ('plan', 'Planes en que la toman (múltiple)', None),
    ('precio', 'Percepción del precio (~$5.000)', 'A'),
    ('sustituto', 'Si no hay Los Cuates, se llevan…', 'A'),
    ('entero', 'Dónde supieron de la marca (múltiple)', 'A'),
    ('persona', 'Si Los Cuates fuera una persona', 'A'),
    ('recomienda', 'Recomendación (1 a 5)', 'A'),
    ('frena', 'Qué frena la prueba (vio, no probó)', 'B'),
    ('conoce', 'Bebidas que conocen (múltiple)', 'B'),
    ('conoce_otro', 'Otras bebidas escritas a mano', 'B'),
    ('toma_normal', 'Qué toman si no conocen ninguna', 'B'),
    ('favorita', 'Bebida favorita', 'B'),
    ('paga', 'Cuánto pagan por su favorita', 'B'),
    ('cambiaria', 'Qué les haría probar algo nuevo (hasta 2)', 'B'),
    ('probaria', '¿Probarían Los Cuates? (prueba de concepto)', 'B'),
    ('sabor_primero', 'Sabor con el que arrancarían', 'B'),
    ('nuevo_sabor', 'Sabor nuevo que quieren', None),
    ('genero', 'Género', None),
    ('ciudad', 'Ciudad', None),
    ('estrato', 'Estrato', None),
    ('fuente', 'De dónde llegaron', None),
    ('dispositivo', 'Dispositivo', None),
]
MULTI = {'sabores', 'gusta', 'mejorar', 'plan', 'entero', 'frena', 'conoce', 'toma_normal', 'cambiaria'}


def ruta(r):
    return 'A' if r.get('probado') == 'si' else 'B'


def tabla(filas, col):
    c = Counter()
    base = 0
    for r in filas:
        v = (r.get(col) or '').strip()
        if not v:
            continue
        base += 1
        for x in (v.split(' | ') if col in MULTI else [v]):
            c[x.strip()] += 1
    if not base:
        return '_Sin respuestas todavía._\n'
    out = [f'Base: {base} personas' + (' (puede sumar más de 100 %: es de selección múltiple)' if col in MULTI else ''), '',
           '| Respuesta | n | % |', '|---|---:|---:|']
    for k, n in c.most_common():
        out.append(f'| {k} | {n} | {n / base * 100:.0f} % |')
    return '\n'.join(out) + '\n'


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    src = Path(sys.argv[1])
    with src.open(encoding='utf-8-sig', newline='') as f:
        filas = [r for r in csv.DictReader(f) if r.get('edad') and r.get('edad') != 'menor']
    a = [r for r in filas if ruta(r) == 'A']
    b = [r for r in filas if ruta(r) == 'B']
    md = [f'# Resultados de la encuesta Los Cuates', '',
          f'Fuente: `{src.name}` · {len(filas)} respuestas válidas (mayores de 18): **{len(a)} la probaron** (ruta A) y **{len(b)} no** (ruta B).',
          'Encuesta propia, muestra por conveniencia difundida en Instagram: sirve para orientar decisiones, no es representativa de Colombia.', '']
    for col, titulo, r in PREGUNTAS:
        grupo = a if r == 'A' else b if r == 'B' else filas
        md += [f'## {titulo}' + (f' · ruta {r}' if r else ''), '', tabla(grupo, col)]
        if r is None and col in ('gusta', 'plan', 'nuevo_sabor'):
            md += ['**Ruta A (la probaron):**', '', tabla(a, col), '**Ruta B (sobre su bebida favorita o sin probarla):**', '', tabla(b, col)]
    # recomendación neta: (4 y 5) − (1 y 2)
    notas = [int(r['recomienda']) for r in a if (r.get('recomienda') or '').isdigit()]
    if notas:
        pro, det = sum(n >= 4 for n in notas), sum(n <= 2 for n in notas)
        md += ['## Índice de recomendación neto', '',
               f'Promotores (4 y 5) − detractores (1 y 2) = {pro} − {det} sobre {len(notas)} = **{(pro - det) / len(notas) * 100:.0f} puntos**.',
               'Cálculo inspirado en el NPS, adaptado a una escala de 5 caritas.', '']
    out = src.with_name('resultados.md')
    out.write_text('\n'.join(md), encoding='utf-8')
    print(f'Listo: {out}')


if __name__ == '__main__':
    main()
