#!/usr/bin/env python3
"""Compare measured FPS from manual/automated PS Vita test runs.

Expected CSV header: profile,scene,fps
Each row is a sampled displayed FPS value (not frame-time telemetry).
"""
import argparse
import csv
import json
import statistics
from collections import defaultdict


def summarize(rows):
    groups = defaultdict(list)
    for row in rows:
        try:
            fps = float(row['fps'])
            if not 0 < fps < 1000:
                raise ValueError()
        except (KeyError, ValueError, TypeError):
            raise ValueError('Every row must contain a valid positive fps')
        key = (row.get('profile', '').strip(), row.get('scene', '').strip())
        if not key[0] or not key[1]:
            raise ValueError('Missing profile/scene')
        groups[key].append(fps)
    summary = []
    for (profile, scene), values in sorted(groups.items()):
        values.sort()
        count = len(values)
        summary.append({'profile': profile, 'scene': scene, 'samples': count,
                        'mean_fps': round(statistics.mean(values), 2),
                        'median_fps': round(statistics.median(values), 2),
                        'min_fps': round(values[0], 2),
                        'p10_fps': round(values[max(0, int(.1 * (count - 1)))], 2),
                        'below_30_pct': round(100 * sum(v < 30 for v in values) / count, 1)})
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('csv_file')
    args = ap.parse_args(argv)
    with open(args.csv_file, encoding='utf-8-sig', newline='') as f:
        result = summarize(csv.DictReader(f))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
