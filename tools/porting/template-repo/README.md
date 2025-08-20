# C++ → Kotlin Porting Template

This template provides a minimal structure to adopt the LST+Accuracy workflow in a new repository.

What’s included
- `tools/accuracy/`: comparator harness, C++ harness builder, sample cases
- `tools/kotlin-json-writer/`: placeholder Kotlin module (CLI) to wire your encoder/writer
- `tools/lst/`: placeholders for LST scripts (copy from your source repo if needed)
- `PROJECT_MAPPING.json`: path mapping for bootstrap
- `Makefile`: convenience targets

Quick start
```sh
# 1) Edit mapping to match your repo
cp PROJECT_MAPPING.template.json PROJECT_MAPPING.json
# 2) Implement Kotlin CLI to read JSON from stdin and print encoded output
# 3) Build and compare
make accuracy
```
