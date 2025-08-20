# Porting Bootstrap

This folder contains reusable utilities for applying the C++ → Kotlin porting workflow to any repository.

- `PROJECT_MAPPING.template.json`: Copy to your repo and fill in path mappings.
- `bootstrap.py`: Validates the mapping and runs the accuracy workflow end-to-end.

Quick Start (this repo):
```sh
python3 tools/porting/bootstrap.py --mapping PROJECT_MAPPING.json --cases tools/accuracy/cases.json
```

For a new repo:
```sh
cp tools/porting/PROJECT_MAPPING.template.json PROJECT_MAPPING.json
# Edit the JSON fields to match your repo layout
python3 tools/porting/bootstrap.py --mapping PROJECT_MAPPING.json --cases <accuracy>/cases.json
```
