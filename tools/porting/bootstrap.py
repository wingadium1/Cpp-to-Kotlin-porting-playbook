#!/usr/bin/env python3
"""
Bootstrap accuracy workflow for arbitrary C++→Kotlin repos using a mapping file.

Usage:
  python3 tools/porting/bootstrap.py --mapping <path/to/mapping.json> [--cases <path/to/cases.json>]

Mapping schema (JSON):
{
  "root": "/abs/repo/root",           # optional; auto-detected from mapping file if omitted
  "lst": "tools/lst",                  # optional
  "lst_out": "tools/lst/out",          # optional
  "accuracy": "tools/accuracy",        # required for accuracy run
  "kotlin_module": "tools/kotlin-json-writer",  # required for accuracy run
  "cpp_harness_bin": "tools/accuracy/cpp_ref/build/cpp_ref", # optional; will build if missing
  "kotlin_bin": "tools/kotlin-json-writer/build/install/kotlin-json-writer/bin/kotlin-json-writer" # optional; will build if missing
}
"""
import argparse, json, os, subprocess, sys
from pathlib import Path

def run(cmd, cwd=None):
    p = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return p.returncode, p.stdout

def ensure_cpp_harness(root: Path, accuracy: Path):
    cpp = accuracy / 'cpp_ref' / 'build' / 'cpp_ref'
    if cpp.exists():
        return cpp
    rc, out = run([sys.executable, str(accuracy / 'setup_cpp_ref.py')], cwd=str(root))
    if rc != 0:
        print(out)
        sys.exit(1)
    if not cpp.exists():
        print('C++ harness not found after build at', cpp)
        sys.exit(1)
    return cpp

def ensure_kotlin_bin(root: Path, kotlin_module: Path):
    binpath = kotlin_module / 'build' / 'install' / kotlin_module.name / 'bin' / kotlin_module.name
    if binpath.exists():
        return binpath
    rc, out = run(['gradle', '-q', 'installDist'], cwd=str(kotlin_module))
    if rc != 0:
        print(out)
        sys.exit(1)
    if not binpath.exists():
        print('Kotlin binary not found after build at', binpath)
        sys.exit(1)
    return binpath

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mapping', required=True)
    ap.add_argument('--cases', help='cases.json path; defaults to <accuracy>/cases.json')
    args = ap.parse_args()

    mapping = json.load(open(args.mapping))
    root = Path(mapping.get('root') or Path(args.mapping).resolve().parents[2])
    accuracy = root / mapping.get('accuracy', 'tools/accuracy')
    kotlin_module = root / mapping.get('kotlin_module', 'tools/kotlin-json-writer')

    cpp_bin = root / mapping.get('cpp_harness_bin') if mapping.get('cpp_harness_bin') else ensure_cpp_harness(root, accuracy)
    kotlin_bin = root / mapping.get('kotlin_bin') if mapping.get('kotlin_bin') else ensure_kotlin_bin(root, kotlin_module)

    cases = Path(args.cases) if args.cases else (accuracy / 'cases.json')
    if not cases.exists():
        print('Cases file not found:', cases)
        sys.exit(1)

    # Delegate to repo comparator if present, else run a simple echo check
    comparator = accuracy / 'compare.py'
    if comparator.exists():
        rc, out = run([sys.executable, str(comparator), '--cases', str(cases)], cwd=str(root))
        print(out)
        sys.exit(rc)
    else:
        print('Comparator not found; verify manually:')
        print('  C++:', cpp_bin)
        print('  Kotlin:', kotlin_bin)
        sys.exit(0)

if __name__ == '__main__':
    main()
