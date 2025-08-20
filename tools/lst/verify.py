#!/usr/bin/env python3
import sys
import json
from pathlib import Path


def concat_text(nodes):
    s = []
    for n in nodes:
        s.append(n['text'])
    return ''.join(s)


def verify(lst_path: Path, repo_root: Path):
    data = json.load(open(lst_path, 'r'))
    file_rel = data['file']
    src = (repo_root / file_rel).read_text(encoding='utf-8')
    rebuilt = concat_text(data['nodes'])
    ok = src == rebuilt
    print(f"{lst_path}: {'OK' if ok else 'MISMATCH'}  len(src)={len(src)} len(rebuilt)={len(rebuilt)}")
    return ok


def main():
    if len(sys.argv) < 2:
        print('Usage: verify.py <lst.json> [<lst.json> ...]')
        sys.exit(2)
    root = Path(__file__).resolve().parents[2]
    ok_all = True
    for p in sys.argv[1:]:
        ok_all &= verify(Path(p), root)
    sys.exit(0 if ok_all else 1)

if __name__ == '__main__':
    main()
