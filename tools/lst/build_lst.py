#!/usr/bin/env python3
import re
import json
import hashlib
import argparse
from dataclasses import dataclass, asdict
from typing import List, Optional, Tuple

# A very lightweight C++ structural slicer focused on this PoC file.
# It is NOT a full parser. It produces a Lossless Semantic Tree (LST)
# that preserves source slices and spans so we can reconstruct the file.

@dataclass
class Span:
    start_byte: int
    end_byte: int
    start_line: int
    end_line: int

@dataclass
class Node:
    kind: str  # include | namespace | class | struct | function | macro | comment | using | other
    name: Optional[str]
    span: Span
    header_span: Optional[Span]
    body_span: Optional[Span]
    header: Optional[str]
    text: str
    children: List['Node']

@dataclass
class LST:
    version: str
    file: str
    source_hash: str
    source_length: int
    nodes: List[Node]

# Utilities

def compute_lines_index(src: str) -> List[int]:
    idx = [0]
    for m in re.finditer(r"\n", src):
        idx.append(m.end())
    return idx

def byte_to_line(pos: int, line_index: List[int]) -> int:
    # 1-based lines
    lo, hi = 0, len(line_index)-1
    while lo <= hi:
        mid = (lo+hi)//2
        if line_index[mid] <= pos:
            lo = mid + 1
        else:
            hi = mid - 1
    return hi + 1

def make_span(start: int, end: int, line_index: List[int]) -> Span:
    return Span(start, end, byte_to_line(start, line_index), byte_to_line(end, line_index))

# Heuristics for json_writer.cpp
FUNC_RE = re.compile(r"(^|\n)\s*(?:static\s+)?(?:inline\s+)?(?:const\s+)?(?:Json::)?[A-Za-z_][\w:<>\s\*&]*\s+([A-Za-z_][\w:]*)\s*\(([^;{}]*)\)\s*(?:const\s*)?(?:->\s*[\w:<>]+\s*)?\{", re.M)
NAMESPACE_RE = re.compile(r"(^|\n)\s*namespace\s+([A-Za-z_][\w:]*)\s*\{", re.M)
CLASS_RE = re.compile(r"(^|\n)\s*(class|struct)\s+([A-Za-z_][\w:]*)[^;{]*\{", re.M)
INCLUDE_RE = re.compile(r"(^|\n)\s*#\s*include\s+([^\n]+)")
USING_RE = re.compile(r"(^|\n)\s*using\s+[\w:<>\s=,]+;", re.M)

# Brace matching to find body spans

def find_matching_brace(src: str, open_pos: int) -> Optional[int]:
    depth = 0
    i = open_pos
    n = len(src)
    while i < n:
        ch = src[i]
        if ch == '"' or ch == '\'':
            # skip string/char literals
            q = ch
            i += 1
            while i < n:
                if src[i] == '\\':
                    i += 2
                    continue
                if src[i] == q:
                    i += 1
                    break
                i += 1
            continue
        if ch == '/' and i+1 < n:
            if src[i+1] == '/':
                j = src.find('\n', i+2)
                i = n if j == -1 else j+1
                continue
            if src[i+1] == '*':
                j = src.find('*/', i+2)
                i = n if j == -1 else j+2
                continue
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return None


def slice_node(src: str, m: re.Match, name_group: int, kind: str, line_index: List[int]) -> Node:
    start = m.start() if m.start() == 0 else m.start()+1  # skip leading \n in group
    header_end = src.find('{', m.end()-1)
    if header_end == -1:
        header_end = m.end()
    body_start = header_end
    body_end = find_matching_brace(src, body_start)
    if body_end is None:
        body_end = m.end()
    text = src[start:body_end+1]
    name = m.group(name_group)
    span = make_span(start, body_end+1, line_index)
    header_span = make_span(start, header_end, line_index)
    body_span = make_span(body_start, body_end+1, line_index)
    return Node(kind, name, span, header_span, body_span, src[start:header_end], text, [])


def collect_toplevel(src: str, line_index: List[int]) -> List[Node]:
    nodes: List[Node] = []

    # includes
    for m in INCLUDE_RE.finditer(src):
        s = m.start(0) if m.start(0) == 0 else m.start(0)+1
        e = src.find('\n', m.end())
        if e == -1: e = len(src)
        nodes.append(Node('include', m.group(0).strip(), make_span(s, e, line_index), None, None, None, src[s:e], []))

    # namespaces
    for m in NAMESPACE_RE.finditer(src):
        node = slice_node(src, m, 2, 'namespace', line_index)
        nodes.append(node)

    # classes/structs
    for m in CLASS_RE.finditer(src):
        node = slice_node(src, m, 3, 'class' if m.group(2) == 'class' else 'struct', line_index)
        nodes.append(node)

    # functions (toplevel and nested; we will nest later)
    for m in FUNC_RE.finditer(src):
        node = slice_node(src, m, 2, 'function', line_index)
        nodes.append(node)

    # using declarations
    for m in USING_RE.finditer(src):
        s = m.start(0) if m.start(0) == 0 else m.start(0)+1
        e = m.end(0)
        nodes.append(Node('using', None, make_span(s, e, line_index), None, None, None, src[s:e], []))

    # macros (non-include)
    for m in re.finditer(r"(^|\n)\s*#.*", src):
        s = m.start(0) if m.start(0) == 0 else m.start(0)+1
        e = src.find('\n', m.end())
        if e == -1: e = len(src)
        text = src[s:e]
        if text.strip().startswith('#include'):
            continue
        nodes.append(Node('macro', None, make_span(s, e, line_index), None, None, None, text, []))

    # sort by start
    nodes.sort(key=lambda n: n.span.start_byte)
    return nodes


def nest_nodes(nodes: List[Node]) -> List[Node]:
    # Build parent-child relationships based on body span containment using index mapping
    idx_containers = [
        i for i, n in enumerate(nodes)
        if n.body_span is not None and n.kind in ('namespace', 'class', 'struct', 'function')
    ]
    # Sort containers by body size ascending to find nearest ancestor first
    idx_containers.sort(key=lambda i: (nodes[i].body_span.end_byte - nodes[i].body_span.start_byte))

    parent_idx: List[Optional[int]] = [None] * len(nodes)

    for i, n in enumerate(nodes):
        best: Optional[int] = None
        ns, ne = n.span.start_byte, n.span.end_byte
        for ci in idx_containers:
            if ci == i:
                continue
            c = nodes[ci]
            bs, be = c.body_span.start_byte, c.body_span.end_byte
            if bs <= ns and ne <= be:
                if best is None:
                    best = ci
                else:
                    b = nodes[best]
                    bbs, bbe = b.body_span.start_byte, b.body_span.end_byte
                    if (bbe - bbs) > (be - bs):
                        best = ci
        parent_idx[i] = best

    # assign children and filter roots
    for n in nodes:
        n.children = []
    for i, p in enumerate(parent_idx):
        if p is not None:
            nodes[p].children.append(nodes[i])

    roots = [nodes[i] for i, p in enumerate(parent_idx) if p is None]

    # For deterministic child order, sort children by start
    def sort_rec(n: Node):
        n.children.sort(key=lambda x: x.span.start_byte)
        for ch in n.children:
            sort_rec(ch)

    for r in roots:
        sort_rec(r)
    # Sort roots by start
    roots.sort(key=lambda x: x.span.start_byte)
    return roots


def add_gap_nodes(src: str, line_index: List[int], roots: List[Node]) -> List[Node]:
    # Fill gaps between root nodes with 'other' nodes so that concatenating all
    # root node texts reproduces the original source exactly.
    res: List[Node] = []
    pos = 0
    n = len(src)
    for node in roots:
        if pos < node.span.start_byte:
            s, e = pos, node.span.start_byte
            res.append(Node('other', None, make_span(s, e, line_index), None, None, None, src[s:e], []))
        res.append(node)
        pos = node.span.end_byte
    if pos < n:
        res.append(Node('other', None, make_span(pos, n, line_index), None, None, None, src[pos:n], []))
    return res


def build_lst_for_file(path: str) -> LST:
    with open(path, 'r', encoding='utf-8') as f:
        src = f.read()
    line_index = compute_lines_index(src)
    flat_nodes = collect_toplevel(src, line_index)
    roots = nest_nodes(flat_nodes)
    roots_with_gaps = add_gap_nodes(src, line_index, roots)
    h = hashlib.sha256(src.encode('utf-8')).hexdigest()
    return LST(version="0.1", file=path, source_hash=h, source_length=len(src), nodes=roots_with_gaps)


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (LST, Node, Span)):
            d = asdict(o)
            return d
        return super().default(o)


def main():
    ap = argparse.ArgumentParser(description="Build Lossless Semantic Tree (PoC) for a C++ file")
    ap.add_argument('file', help='C++ source file')
    ap.add_argument('--out', '-o', default=None, help='Output JSON path (default: print to stdout)')
    args = ap.parse_args()

    lst = build_lst_for_file(args.file)
    out = json.dumps(lst, cls=EnhancedJSONEncoder, indent=2, ensure_ascii=False)
    if args.out:
        with open(args.out, 'w', encoding='utf-8') as f:
            f.write(out)
    else:
        print(out)

if __name__ == '__main__':
    main()
