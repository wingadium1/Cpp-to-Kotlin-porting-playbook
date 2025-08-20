#!/usr/bin/env python3
import argparse, json, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DEF_CPP = ROOT / 'tools' / 'accuracy' / 'cpp_ref' / 'build' / 'cpp_ref'
DEF_KT = ROOT / 'tools' / 'kotlin-json-writer' / 'build' / 'install' / 'kotlin-json-writer' / 'bin' / 'kotlin-json-writer'


def to_args(cfg):
    indentation = cfg.get('indentation', '\t')
    precision = str(cfg.get('precision', 17))
    precisionType = cfg.get('precisionType', 'significant')
    emitUTF8 = '1' if cfg.get('emitUTF8', False) else '0'
    useSpecialFloats = '1' if cfg.get('useSpecialFloats', False) else '0'
    enableYAMLCompatibility = '1' if cfg.get('enableYAMLCompatibility', False) else '0'
    dropNullPlaceholders = '1' if cfg.get('dropNullPlaceholders', False) else '0'
    return [indentation, precision, precisionType, emitUTF8, useSpecialFloats, enableYAMLCompatibility, dropNullPlaceholders]


def run(binpath: Path, json_str: str, cfg: dict):
    args = [str(binpath)] + to_args(cfg)
    p = subprocess.run(args, input=json_str.encode('utf-8'), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.returncode, p.stdout.decode('utf-8'), p.stderr.decode('utf-8')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cases', required=True)
    ap.add_argument('--cpp', default=str(DEF_CPP))
    ap.add_argument('--kt', default=str(DEF_KT))
    args = ap.parse_args()
    cpp = Path(args.cpp)
    kt = Path(args.kt)

    cases = json.load(open(args.cases, 'r'))
    failures = 0
    for case in cases:
        name = case['name']
        obj = case['json']
        json_str = json.dumps(obj)
        cfg = case.get('cfg', {})
        rc_cpp, out_cpp, err_cpp = run(cpp, json_str, cfg)
        if rc_cpp != 0:
            print(f"[cpp] FAIL {name}: {err_cpp.strip()}")
            failures += 1
            continue
        rc_k, out_k, err_k = run(kt, json_str, cfg)
        if rc_k != 0:
            print(f"[kt ] FAIL {name}: {err_k.strip()}")
            failures += 1
            continue
        if out_cpp != out_k:
            print(f"[diff] {name}: outputs differ")
            print("--cpp--\n" + out_cpp)
            print("--kt --\n" + out_k)
            failures += 1
        else:
            print(f"[ok ] {name}")

    raise SystemExit(1 if failures else 0)

if __name__ == '__main__':
    main()
