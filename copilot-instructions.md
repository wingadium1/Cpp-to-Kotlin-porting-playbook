gradle -q installDist
# Copilot Instructions: Reusable C++ → Kotlin Porting Playbook (LST + Accuracy)

Purpose: Provide a reusable, model-aware workflow for porting C++ codebases to Kotlin with guardrails for losslessness and behavioral accuracy. This guide is repo-agnostic and includes a mapping section to plug into any project; an example mapping for this repo is included at the end.

## Model Selection Policy
- Prefer GPT‑5 or Claude for:
  - Cross-file reasoning, public API changes, complex refactors, performance-sensitive logic.
  - Parser/AST/LST schema design or non-trivial multi-file code generation.
  - Ambiguous migration tradeoffs requiring exploration and justification.
- Allow GPT‑4.1 for:
  - Running/maintaining LST tools, batch conversions, Markdown summaries.
  - Mechanical edits with clear acceptance criteria and tests.
  - Docs/READMEs/scripts/simple CLIs and verifiers.
  - Small, locally testable bug fixes.
- If GPT‑5/Claude are unavailable (fallback mode with GPT‑4.1):
  - Reduce batch size; operate per-file or per-feature.
  - Always run verifiers/tests after edits; post concise diffs and results.
  - Ask confirmation before changing schemas or public APIs.
  - Avoid speculative refactors; preserve behavior; prefer minimal diffs.

## Ground Rules
- Losslessness: When slicing sources, ensure reconstructed output matches byte-for-byte.
- Accuracy: Validate Kotlin outputs against C++ using an accuracy harness (see below).
- Scope Control: Change only what’s required; do not reformat unrelated code.
- Observability: Before tool calls, state intent in 1 sentence; after, report result.
- Commands: Provide zsh-friendly commands in fenced blocks.

## Standard Tooling Interfaces (Abstract)
- LST generator: `lst/build_lst.py`
- LST batch + verify: `lst/run_all.py`, `lst/verify.py`
- LST → Markdown: `lst/to_md.py`, `lst/to_md_all.py`
- Symbol index: `lst/index_symbols.py`
- LST structural comparator: `accuracy/lst_accuracy.py`
- MCP chunked conversion orchestrator: `mcp/orchestrator.py`
- MCP C++→Kotlin conversion server: `convert-mcp`
    - `build_skeleton`: From LST, create a Kotlin file with method signatures.
    - `convert_chunk`: Convert a C++ code chunk (function body, etc.) to Kotlin.
    - `assemble_file`: Combine skeleton and converted chunks into a final Kotlin file.

Note: Projects may use different paths. Provide a mapping (see Project Mapping section) so these abstract commands resolve to real locations.

## LST Workflow
- One file
```sh
python3 <lst>/build_lst.py <path/to/file> --out <lst_out>/<safe>.lst.json
python3 <lst>/verify.py <lst_out>/<safe>.lst.json
python3 <lst>/to_md.py <lst_out>/<safe>.lst.json --out <lst_out>/<safe>.md
```
- Whole repo
```sh
python3 <lst>/run_all.py
python3 <lst>/verify.py <lst_out>/*.lst.json
python3 <lst>/to_md_all.py
python3 <lst>/index_symbols.py --out <lst_out>/symbols.index.json
```

## LST Accuracy (Structural Fidelity)
- Goal: the converted Kotlin source should mirror the C++ structure when both are represented as LSTs.
- Method: generate LSTs for source and ported files; compare with `accuracy/lst_accuracy.py`.
- Mapping: normalize known symbol renames and ignore non-semantic tokens via a mapping file.
- Signal: any structural diffs should be treated as regressions unless explicitly justified.

## MCP Chunked Conversion (For Large Files)
- Goal: handle large C++ files by converting in logical chunks (functions, methods, classes).
- Workflow:
  1.  **LST Generation**: `build_lst.py` creates an LST from the C++ source.
  2.  **Chunking**: `chunker.py` splits the LST into a skeleton and convertible chunks (functions, methods).
  3.  **Skeleton Build**: The `convert-mcp` server's `build_skeleton` tool generates a `.kt` file with method signatures.
  4.  **Chunk Conversion**: The `convert_chunk` tool is called for each chunk to translate the C++ code to Kotlin.
  5.  **Assembly**: The `assemble_file` tool combines the Kotlin skeleton with the converted code chunks.
- Orchestrator: `mcp/orchestrator.py` manages the complete workflow, calling the above tools.
- Benefits: scalable, parallel conversion; resumable on failures; maintains context.

## Kotlin Porting Guidance (Behavioral Parity)
- Builder options parity: indentation, YAML colon spacing, drop nulls, useSpecialFloats, emitUTF8, precision, precisionType.
- String escaping: control chars, UTF‑8 passthrough, `\uXXXX`, surrogate pairs.
- Doubles: locale-independent formatting, `.0` enforcement rules, trimming for decimalPlaces, exponent case/padding.
- Arrays/objects: multiline heuristic approximating C++ right-margin behavior; bracket and element indentation must match.
- Comments: If needed, add later with flags mirroring the C++ comment style.

## Change Strategy by Model
- GPT‑5/Claude:
  - May design/refine schema or multi-file refactors; still verify.
  - Can operate on many files if verifiers are fast and green.
- GPT‑4.1:
  - Limit scope; use existing schema/tools; avoid redesign.
  - Prefer incremental commits; keep diffs minimal and test-backed.

## Definition of Done
- LST tasks: Verified lossless; Markdown outline generated.
- Kotlin changes: Unit tests pass; comparator shows no diffs on cases.
- Documentation updated (README/usage) where relevant.

---

## Project Mapping (Fill for each repository)
- `<root>`: absolute path to repo root.
- `<lst>`: path to LST tools.
- `<lst_out>`: path for LST outputs.
- `<accuracy>`: path to accuracy tools.
- `<mcp>`: path to MCP tools.
- `<kotlin_module>`: path to Kotlin module/CLI.
- `<cpp_harness_bin>`: expected harness binary path.
- `<kotlin_bin>`: installed Kotlin binary path.

Example mapping (generic template)
- `<lst>` → `tools/lst`
- `<lst_out>` → `tools/lst/out`
- `<accuracy>` → `tools/accuracy`
- `<mcp>` → `tools/mcp`
- `<kotlin_module>` → `<path/to/your/kotlin/module>`

