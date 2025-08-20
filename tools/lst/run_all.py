#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # repo root
THIS = Path(__file__).resolve().parent
OUT_DIR = THIS / 'out'

EXTS = {'.cpp', '.cc', '.cxx', '.h', '.hpp', '.hh', '.inl'}


def find_source_files(root: Path):
    candidates = []
    for rel in ('src', 'include', 'example', 'test', 'src/lib_json', 'src/jsontestrunner'):
        p = root / rel
        if p.exists():
            for dirpath, _, filenames in os.walk(p):
                for fn in filenames:
                    if Path(fn).suffix in EXTS:
                        candidates.append(Path(dirpath) / fn)
    # Deduplicate and sort
    uniq = sorted({str(Path(f).resolve()): Path(f).resolve() for f in candidates}.values())
    return uniq


def run_build(file_path: Path, out_dir: Path):
    rel = file_path.relative_to(ROOT)
    out_path = out_dir / (str(rel).replace('/', '__') + '.lst.json')
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = ['python3', str(THIS / 'build_lst.py'), str(rel), '--out', str(out_path.relative_to(ROOT))]
    subprocess.run(cmd, cwd=ROOT, check=True)
    return out_path


def main():
    ap = argparse.ArgumentParser(description='Run LST generator across repo files')
    ap.add_argument('--root', default=str(ROOT), help='Repo root (default: repo)')
    ap.add_argument('--out', default=str(OUT_DIR), help='Output directory')
    args = ap.parse_args()

    root = Path(args.root).resolve()
    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    files = find_source_files(root)
    stats = []
    for f in files:
        try:
            outp = run_build(f, out_dir)
            stats.append((f, outp))
        except subprocess.CalledProcessError as e:
            print(f"Failed: {f}: {e}")
    print(f"Generated {len(stats)} LST files under {out_dir}")

if __name__ == '__main__':
    main()
