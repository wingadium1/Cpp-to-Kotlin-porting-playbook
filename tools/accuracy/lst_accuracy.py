#!/usr/bin/env python3
"""
LST-based structural accuracy checker.

Compares a C++ LST JSON against a Kotlin LST JSON (or any other target-language
LST) to assess structural fidelity of a port. This is schema-light and attempts
to be tolerant by extracting generic tokens from common LST fields.

Inputs:
- --cpp-lst: path to source (C++) LST JSON
- --kotlin-lst: path to target (Kotlin) LST JSON
- --mapping: optional JSON mapping file with fields like:
  {
    "symbol_renames": {"OldName": "NewName"},
    "ignore_tokens": ["T:Comment"]
  }

Output: human-readable diff summary and non-zero exit code on mismatch.
"""
import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def token_stream(obj: Any, parent_key: str | None = None) -> Iterable[str]:
    # Schema-light tokenization from an arbitrary LST-like JSON
    if isinstance(obj, dict):
        for k, v in obj.items():
            # Key presence token
            yield f"K:{k}"
            # Common type/kind tags
            if k in ("kind", "type", "node", "tag") and isinstance(v, str):
                yield f"T:{v}"
            # Common identifier names
            if k in ("name", "identifier", "callee", "declName") and isinstance(v, str):
                if v:
                    yield f"ID:{v}"
            # Recurse
            yield from token_stream(v, k)
    elif isinstance(obj, list):
        # Length bucket to prevent overfitting exact sizes
        try:
            n = len(obj)
        except Exception:
            n = 0
        # Bucketize lengths to reduce noise while keeping structure signal
        if n == 0:
            yield "LEN:0"
        elif n <= 3:
            yield f"LEN:{n}"
        elif n <= 8:
            yield "LEN:4-8"
        else:
            yield "LEN:9+"
        for it in obj:
            yield from token_stream(it, parent_key)
    else:
        # Literals
        if isinstance(obj, bool):
            yield f"LIT:bool:{obj}"
        elif isinstance(obj, int):
            yield "LIT:int"
        elif isinstance(obj, float):
            yield "LIT:float"
        elif isinstance(obj, str):
            # Avoid including long strings; just mark presence
            if parent_key in ("string", "value", "literal", "text"):
                yield "LIT:string"


def apply_mapping(tokens: Counter, mapping: Dict[str, Any]) -> Counter:
    renames: Dict[str, str] = mapping.get("symbol_renames", {}) if mapping else {}
    ignore: set[str] = set(mapping.get("ignore_tokens", [])) if mapping else set()

    remapped: Counter = Counter()
    for tok, cnt in tokens.items():
        if tok in ignore:
            continue
        if tok.startswith("ID:"):
            ident = tok[3:]
            new_ident = renames.get(ident, ident)
            tok = f"ID:{new_ident}"
        remapped[tok] += cnt
    return remapped


def diff_counters(a: Counter, b: Counter) -> Tuple[Counter, Counter]:
    # Tokens in A more than B and vice versa
    only_a = Counter()
    only_b = Counter()
    all_keys = set(a.keys()) | set(b.keys())
    for k in all_keys:
        da = a.get(k, 0)
        db = b.get(k, 0)
        if da > db:
            only_a[k] = da - db
        elif db > da:
            only_b[k] = db - da
    return only_a, only_b


def main() -> None:
    ap = argparse.ArgumentParser(description="LST-based structural accuracy checker")
    ap.add_argument("--cpp-lst", required=True, help="Path to C++ LST JSON")
    ap.add_argument("--kotlin-lst", required=True, help="Path to Kotlin LST JSON")
    ap.add_argument("--mapping", default=None, help="Optional mapping JSON")
    ap.add_argument("--top", type=int, default=50, help="Show top-N token diffs")
    args = ap.parse_args()

    cpp_lst = Path(args.cpp_lst)
    kt_lst = Path(args.kotlin_lst)
    mapping = Path(args.mapping) if args.mapping else None

    cpp = load_json(cpp_lst)
    kt = load_json(kt_lst)
    mapping_obj = load_json(mapping) if mapping and mapping.exists() else {}

    toks_a = Counter(token_stream(cpp))
    toks_b = Counter(token_stream(kt))

    toks_a = apply_mapping(toks_a, mapping_obj)
    toks_b = apply_mapping(toks_b, mapping_obj)

    only_a, only_b = diff_counters(toks_a, toks_b)

    if not only_a and not only_b:
        print("[ok] Structural token multiset matches after mapping.")
        raise SystemExit(0)

    print("[diff] Structural discrepancies detected (top tokens):")
    if only_a:
        print("-- In C++ LST more than Kotlin LST --")
        for tok, cnt in only_a.most_common(args.top):
            print(f"{tok}\t+{cnt}")
    if only_b:
        print("-- In Kotlin LST more than C++ LST --")
        for tok, cnt in only_b.most_common(args.top):
            print(f"{tok}\t+{cnt}")

    raise SystemExit(1)


if __name__ == "__main__":
    main()
