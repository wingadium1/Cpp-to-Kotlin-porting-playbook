# Conversion Accuracy Playbook

Goal: Verify Kotlin port output matches C++ JsonCpp writer behavior across a corpus of inputs.

Components:
- `cpp_ref`: A tiny C++ harness that links JsonCpp from this repo and prints writer outputs for given JSON inputs and settings.
- `kotlin_cli`: A small Kotlin program that uses our Kotlin writer and prints outputs for the same inputs.
- `compare.py`: Runs both and diffs outputs. Reports mismatches with minimal repro.

## Quick Start

1) Build C++ harness (requires CMake or any C++17 compiler):
```sh
python3 tools/accuracy/setup_cpp_ref.py
```

2) Build Kotlin runner (Gradle):
```sh
cd tools/kotlin-json-writer
gradle -q installDist
```

3) Run comparator on sample cases:
```sh
python3 tools/accuracy/compare.py --cases tools/accuracy/cases.json
```

## Notes
- The comparator passes JSON strings via stdin to each runner and collects output. Settings (precision, emitUTF8, special floats, indentation) are case-configurable.
- For floating comparisons, string equality is required to ensure formatting parity.
