#!/usr/bin/env python3
"""Comparador de lecturas de FPS tomadas en PS Vita (CSV perfil,escena,fps)."""
import argparse
import csv
import math
import statistics
from pathlib import Path

def analyze(rows):
    data={}
    for row in rows:
        try:
            profile=row['perfil'].strip()
            scene=row['escena'].strip()
            fps=float(row['fps'])
            if not profile or not scene or not math.isfinite(fps) or fps<=0 or fps>120:
                raise ValueError('Valor inválido de perfil, escena o FPS')
        except (KeyError,TypeError) as exc:
            raise ValueError('CSV requiere las columnas perfil,escena,fps') from exc
        data.setdefault((scene,profile),[]).append(fps)
    result=[]
    for (scene,profile),fps_list in sorted(data.items()):
        fps_list.sort()
        n=len(fps_list)
        result.append(dict(escena=scene,perfil=profile,muestras=n,
                           promedio=round(statistics.fmean(fps_list),2),
                           mediana=round(statistics.median(fps_list),2),
                           minimo=round(fps_list[0],2),
                           p10=round(fps_list[max(0,math.ceil(n*.1)-1)],2),
                           bajo30=round(sum(fps <30 for fps in fps_list)*100/n,1)))
    return result

def to_markdown(stats):
    lines=['| Escena | Perfil | Lecturas | FPS promedio | Mín. | 10 % bajo | % < 30 FPS |',
           '|---|---|---:|---:|---:|---:|---:|']
    for s in stats:
        lines.append('| {escena} | {perfil} | {muestras} | {promedio:.2f} | {minimo:.2f} | {p10:.2f} | {bajo30:.1f}% |'.format(**s))
    lines.append('\nNota: Son lecturas de FPS, no tiempos por cuadro; p10 NO representa 1 % low de frametimes.')
    return '\n'.join(lines)+'\n'

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('csv_path',type=Path)
    p.add_argument('--salida',type=Path)
    opts=p.parse_args()
    with opts.csv_path.open(encoding='utf-8-sig',newline='') as fh:
        results=analyze(csv.DictReader(fh))
    if not results:
        p.error('El CSV no contiene lecturas')
    report=to_markdown(results)
    print(report)
    if opts.salida:
        opts.salida.write_text(report,encoding='utf-8')

if __name__=='__main__':
    main()
