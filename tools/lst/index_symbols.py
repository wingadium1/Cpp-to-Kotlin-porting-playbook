#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path
from collections import defaultdict

THIS = Path(__file__).resolve().parent
ROOT = THIS.parents[2]

SYMBOL_KINDS = {'namespace', 'class', 'struct', 'function', 'using'}


def find_lst_json():
    out = THIS / 'out'
    if not out.exists():
        return []
    paths = []
    for dirpath, _, filenames in os.walk(out):
        for fn in filenames:
            if fn.endswith('.lst.json'):
                paths.append(Path(dirpath) / fn)
    return sorted(paths)


def walk(nodes, acc, file):
    for n in nodes:
        kind = n['kind']
        if kind in SYMBOL_KINDS:
            name = n.get('name') or ''
            acc[(kind, name)].append({
                'file': file,
                'span': n['span'],
            })
        if n.get('children'):
            walk(n['children'], acc, file)


def main():
    ap = argparse.ArgumentParser(description='Index symbols from LSTs')
    ap.add_argument('--out', default=str(THIS / 'symbols.index.json'))
    args = ap.parse_args()

    acc = defaultdict(list)
    files = find_lst_json()
    for f in files:
        data = json.load(open(f, 'r'))
        walk(data['nodes'], acc, data['file'])

    # convert keys to objects
    out = []
    for (kind, name), locs in sorted(acc.items()):
        out.append({'kind': kind, 'name': name, 'locations': locs})

    Path(args.out).write_text(json.dumps(out, indent=2), encoding='utf-8')
    print(f"Wrote {args.out} with {len(out)} symbols")

if __name__ == '__main__':
    main()
