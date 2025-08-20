#!/usr/bin/env python3
import argparse
import os
from pathlib import Path
import subprocess

THIS = Path(__file__).resolve().parent
ROOT = THIS.parents[2]


def find_lst_json(root: Path):
    out = THIS / 'out'
    if not out.exists():
        return []
    paths = []
    for dirpath, _, filenames in os.walk(out):
        for fn in filenames:
            if fn.endswith('.lst.json'):
                paths.append(Path(dirpath) / fn)
    return sorted(paths)


def main():
    ap = argparse.ArgumentParser(description='Convert all LST JSONs to Markdown')
    ap.add_argument('--out', default=None, help='Ignored; Markdown goes next to each JSON')
    args = ap.parse_args()

    files = find_lst_json(ROOT)
    count = 0
    for f in files:
        md_path = f.with_suffix('').with_suffix('.md')
        cmd = ['python3', str(THIS / 'to_md.py'), str(f), '--out', str(md_path)]
        subprocess.run(cmd, cwd=ROOT, check=True)
        count += 1
    print(f"Converted {count} LSTs to Markdown")

if __name__ == '__main__':
    main()
