# LST PoC

This folder contains a quick Proof-of-Concept tool to build a Lossless Semantic Tree (LST) for a C++ source file. The LST captures structural nodes (includes, namespaces, classes/structs, and function definitions) with precise source spans, while preserving the original source for lossless reconstruction.

## One-file PoC

```sh
python3 tools/lst/build_lst.py src/lib_json/json_writer.cpp --out tools/lst/json_writer.lst.json
```

Outputs a JSON file with:
- version, file path, source hash/length
- top-level `nodes` containing nested namespaces/classes/functions
- each node includes `span` (byte/line ranges) and `header`/`text` slices so the original source can be reconstructed

## Batch over repo

```sh
python3 tools/lst/run_all.py
```
- Scans `src/`, `include/`, `example/`, and `test/` for C/C++-like files.
- Emits LST JSON files under `tools/lst/out/` (filenames are path-safe).

## Verify losslessness

```sh
# Verify a single LST (should print OK)
python3 tools/lst/verify.py tools/lst/json_writer.lst.json

# Or verify all generated LSTs
python3 tools/lst/verify.py tools/lst/out/*.lst.json
```
- The generator inserts `other` nodes between recognized nodes so that concatenating all top-level `nodes[*].text` exactly reproduces the original file.

## Convert to Markdown

```sh
# Single file
python3 tools/lst/to_md.py tools/lst/out/<file>.lst.json --out tools/lst/out/<file>.lst.md

# All under tools/lst/out
python3 tools/lst/to_md_all.py
```

## Build a symbol index

```sh
python3 tools/lst/index_symbols.py --out tools/lst/symbols.index.json
```
- Produces a project-wide index of `namespace`, `class`, `struct`, `function`, `using` occurrences with file and span references.

## Schema

A minimal JSON Schema for the LST is provided at `tools/lst/lst.schema.json`.

Key fields:
- `nodes[].kind`: include | namespace | class | struct | function | macro | using | other
- `nodes[].span`: `{start_byte,end_byte,start_line,end_line}` on original file
- `nodes[].header_span` / `nodes[].body_span`: present for containers/functions
- `nodes[].text`: exact source slice for lossless reconstruction
- `nodes[].children`: nested by lexical containment (e.g., functions inside `namespace Json`)

## Notes

- This is a lightweight, heuristic parser for the PoC. For the full project, we’ll replace it with a robust frontend (e.g., libclang or tree-sitter) emitting the same schema.
- The goal is to support a Kotlin conversion pipeline by providing a reliable, lossless structural view of the C++ sources.
