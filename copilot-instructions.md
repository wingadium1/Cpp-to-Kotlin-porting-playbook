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
- Accuracy (C++ vs Kotlin):
  - C++ reference harness builder: `accuracy/setup_cpp_ref.py` → builds `cpp_ref`
  - Kotlin CLI (writer/encoder under test): `kotlin-json-writer` (Gradle `installDist`)
  - Comparator: `accuracy/compare.py`

Note: Projects may use different paths. Provide a mapping (see Project Mapping section) so these abstract commands resolve to real locations.

## Accuracy Workflow (Required for Non-trivial Changes)
1) Build C++ reference
```sh
python3 <accuracy>/setup_cpp_ref.py
```
2) Build Kotlin CLI
```sh
cd <kotlin_module>
gradle -q installDist
```
3) Run comparator
```sh
python3 <accuracy>/compare.py --cases <accuracy>/cases.json
```
4) If diff found
- Minimize repro; post the smallest JSON + cfg showing divergence.
- Triage category: double formatting, string escaping (UTF‑8 vs \uXXXX), spacing, or structural.
- Patch with focused changes and re-run comparator + unit tests.

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
- `<kotlin_module>`: path to Kotlin module/CLI.
- `<cpp_harness_bin>`: expected harness binary path.
- `<kotlin_bin>`: installed Kotlin binary path.

Example mapping (this repository)
- `<lst>` → `tools/lst`
- `<lst_out>` → `tools/lst/out`
- `<accuracy>` → `tools/accuracy`
- `<kotlin_module>` → `tools/kotlin-json-writer`
- `<cpp_harness_bin>` → `tools/accuracy/cpp_ref/build/cpp_ref`
- `<kotlin_bin>` → `tools/kotlin-json-writer/build/install/kotlin-json-writer/bin/kotlin-json-writer`

Example quick start (this repository)
```sh
python3 tools/accuracy/setup_cpp_ref.py
cd tools/kotlin-json-writer && gradle -q installDist
python3 tools/accuracy/compare.py --cases tools/accuracy/cases.json
```
