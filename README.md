# C++ to Kotlin Porting Playbook

This document outlines a semi-automated workflow for porting C++ code to Kotlin, using a combination of custom-built tools for Lossless Semantic Tree (LST) generation and accuracy verification.

## Overview

The goal of this playbook is to provide a structured and repeatable process for porting C++ libraries to Kotlin, ensuring correctness and maintaining a high degree of fidelity to the original implementation. The process relies on:

1.  **Lossless Semantic Trees (LSTs)**: We generate a detailed, lossless representation of the C++ source code. This provides a structured, machine-readable format that is easier to work with than raw source text.
2.  **Accuracy-Checking Framework**: A testing harness that compares the output of the original C++ code and the ported Kotlin code to ensure they are functionally identical.
3.  **Porting Template**: A template repository that can be used to quickly bootstrap a new porting project.

## Directory Structure

The following directories and files have been added to the repository to support the porting workflow:

-   `tools/`: Contains all the tooling for the porting process.
    -   `lst/`: Tools for generating and working with Lossless Semantic Trees (LSTs).
        -   `build_lst.py`: Generates an LST for a given C++ file.
        -   `run_all.py`: A script to generate LSTs for all C++ files in the project.
        -   `to_md.py`: Converts an LST to a Markdown document for easier viewing.
        -   `verify.py`: Verifies that the LST can be perfectly reconstructed back to the original source code.
        -   `index_symbols.py`: Creates an index of all symbols in the codebase.
    -   `accuracy/`: Tools for verifying the correctness of the ported code.
        -   `compare.py`: Compares the output of the C++ and Kotlin implementations for a given set of inputs.
        -   `cases.json`: A set of test cases to be used by the comparator.
        -   `setup_cpp_ref.py`: A script to build the C++ reference implementation.
    -   `porting/`: Tools for managing the porting process itself.
        -   `bootstrap.py`: A script to initialize a new porting project from the template.
        -   `PROJECT_MAPPING.template.json`: A template for the project mapping file.
        -   `template-repo/`: A template repository for a new porting project.
-   `copilot-instructions.md`: Instructions for using GitHub Copilot to assist with the porting process.
-   `Makefile`: A Makefile with convenience targets for running the various tools.

## Workflow

The porting process is as follows:

1.  **Generate LSTs**:
    -   To generate an LST for a single file, run:
        ```bash
        python3 tools/lst/build_lst.py <path/to/file.cpp>
        ```
    -   To generate LSTs for all C++ files in the project, run:
        ```bash
        python3 tools/lst/run_all.py
        ```
2.  **Verify LSTs**:
    -   To verify that the LSTs are lossless, run:
        ```bash
        python3 tools/lst/verify.py
        ```
3.  **Port the code**:
    -   Use the generated LSTs and the `copilot-instructions.md` to guide the process of porting the C++ code to Kotlin.
4.  **Verify Accuracy**:
    -   Build the C++ reference implementation:
        ```bash
        python3 tools/accuracy/setup_cpp_ref.py
        ```
    -   Run the accuracy comparator:
        ```bash
        python3 tools/accuracy/compare.py --cases tools/accuracy/cases.json
        ```
5.  **Bootstrap a new project**:
    -   To start a new porting project, use the `porting` tools:
        ```bash
        python3 tools/porting/bootstrap.py --mapping <path/to/mapping.json>
        ```

## Dependencies

-   Python 3.6+
-   `clang`
