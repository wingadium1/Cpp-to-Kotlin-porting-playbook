#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from collections import Counter


def summarize_nodes(nodes):
    c = Counter()
    for n in nodes:
        c[n['kind']] += 1
    return c


def node_label(n):
    name = n.get('name')
    kind = n['kind']
    span = n['span']
    rng = f"L{span['start_line']}-{span['end_line']} B{span['start_byte']}-{span['end_byte']}"
    if kind == 'other':
        length = span['end_byte'] - span['start_byte']
        return f"other · {length} bytes ({rng})"
    if name:
        return f"{kind} {name} ({rng})"
    # fall back to first line of text trimmed
    text = (n.get('header') or n.get('text') or '').strip().splitlines()[:1]
    sample = (' ' + text[0]) if text else ''
    return f"{kind}{sample} ({rng})"


def node_detail_block(n):
    # Show compact header or single-line text for readability
    header = n.get('header')
    if header:
        body = header.strip()
    else:
        t = (n.get('text') or '').strip()
        body = t.splitlines()[0] if t else ''
    if not body:
        return ''
    return "\n".join(["", "```", body, "```", ""])  # fenced code block


def emit_tree(nodes, depth=0, lines=None):
    if lines is None:
        lines = []
    for n in nodes:
        if n['kind'] == 'other':
            # make tree concise; still indicate gaps compactly
            lbl = node_label(n)
            lines.append('  ' * depth + f"- {lbl}")
            continue
        lbl = node_label(n)
        lines.append('  ' * depth + f"- {lbl}")
        # Add small detail for key kinds
        if n['kind'] in ('namespace', 'class', 'struct', 'function', 'include', 'macro', 'using'):
            block = node_detail_block(n)
            if block:
                lines.append('' + '  ' * (depth) + block)
        if n.get('children'):
            emit_tree(n['children'], depth + 1, lines)
    return lines


def generate_markdown(lst_path: Path) -> str:
    data = json.load(open(lst_path, 'r'))
    title = f"LST Summary: {data['file']}"
    length = data['source_length']
    shash = data['source_hash']
    counts = summarize_nodes(data['nodes'])

    md = []
    md.append(f"# {title}")
    md.append("")
    md.append(f"- Version: `{data['version']}`")
    md.append(f"- Source length: `{length}` bytes")
    md.append(f"- Source hash (sha256): `{shash}`")
    if counts:
        md.append(f"- Node counts: " + ", ".join(f"{k}={counts[k]}" for k in sorted(counts)))
    md.append("")
    md.append("## Tree")
    md.append("")
    tree_lines = emit_tree(data['nodes'])
    md.extend(tree_lines)
    md.append("")
    return "\n".join(md)


def main():
    ap = argparse.ArgumentParser(description='Convert LST JSON to Markdown')
    ap.add_argument('lst_json', help='Path to .lst.json file')
    ap.add_argument('--out', '-o', help='Output .md path (default: alongside input)')
    args = ap.parse_args()

    in_path = Path(args.lst_json)
    out_path = Path(args.out) if args.out else in_path.with_suffix('').with_suffix('.md')

    md = generate_markdown(in_path)
    out_path.write_text(md, encoding='utf-8')
    print(f"Wrote {out_path}")

if __name__ == '__main__':
    main()
