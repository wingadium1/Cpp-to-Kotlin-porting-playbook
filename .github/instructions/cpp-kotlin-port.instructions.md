---
applyTo: '**/*.cpp'
---
Provide project context and coding guidelines that AI should follow when generating code, answering questions, or reviewing changes.
## 🎯 Ground Rules (Battle-Tested)

### Fundamental Principles
- **Losslessness**: When slicing sources, ensure reconstructed output matches byte-for-byte
- **Comment Preservation**: MANDATORY - All C++ comments must be preserved verbatim
- **Accuracy**: Validate Kotlin outputs against C++ using structural comparison
- **Context Integrity**: Maintain variable scope, method calls, and dependency relationships
- **Scope Control**: Change only what's required; do not reformat unrelated code

### Operational Guidelines
- **Observability**: Before tool calls, state intent in 1 sentence; after, report result
- **Command Format**: Provide zsh-friendly commands in fenced blocks
- **Function Context**: ALWAYS check function signatures before converting bodies
- **Parameter Distinction**: Never add local variables as function parameters
- **Business Logic**: Preserve all algorithms and calculation logic exactly

### Quality Assurance
- **Verification Steps**: LST generation → Relationship analysis → Conversion → Assembly → Validation
- **Success Metrics**: 100% chunk conversion, complete comment preservation, correct function signatures
- **Manual Review**: Flag complex conversions for developer review (expect ~60% flagging rate)ntext and coding guidelines that AI should follow when generating code, answering questions, or reviewing changes.

# GitHub Copilot Instructions: Advanced C++ → Kotlin Porting Playbook

## 🎯 Purpose
Provide a comprehensive, battle-tested workflow for porting C++ codebases to Kotlin with relationship-aware chunking, complete comment preservation, and behavioral accuracy. This playbook includes proven strategies from successful large-scale conversions.

## ⭐ Key Achievements
- **100% conversion success rate** (555/555 chunks in recent Test.cpp conversion)
- **Complete comment preservation** including Japanese text and change tracking
- **Context-aware chunking** with variable scope and dependency tracking
- **Priority-based processing** optimizing conversion efficiency
- **17 major functions converted** with full business logic preservation

## 🧠 Model Selection Policy

### Heavy Work Tasks (Cost-Optimized Models)
**Recommended Models:** GPT-4o, GPT-4-turbo, Claude-3.5-Haiku, Claude-3-Haiku

**Optimal Tasks:**
- `convert_chunk` - Converting individual code chunks with established context
- Basic syntax transformation and type mapping
- Placeholder replacement with concrete implementations
- Mechanical edits following established patterns
- Comment preservation and positioning

**Rationale:** These tasks follow well-defined patterns and don't require complex architectural reasoning.

### Thinking Tasks (High-Capability Models)
**Recommended Models:** Claude-3.5-Sonnet, GPT-o1-preview, GPT-o1-mini, Claude-3-Opus

**Optimal Tasks:**
- `build_skeleton` - Analyzing LST structure and generating comprehensive Kotlin templates
- `validate_chunk` - Ensuring code quality, architectural consistency, and comment preservation
- `assemble_file` - Combining components and resolving complex dependencies
- Relationship analysis and variable scope determination
- Complex architectural decisions and error diagnosis
- Cross-function reasoning and API design

**Rationale:** These tasks require deep understanding of code architecture and complex reasoning about relationships.

### ⚠️ Critical Model Assignment Rules
- **NEVER use heavy work models** for skeleton generation or validation
- **ALWAYS use thinking models** for architectural decisions
- **Relationship analysis** requires thinking models due to complexity
- **Comment preservation** can use either model tier (simple copying)

## Ground Rules
- Losslessness: When slicing sources, ensure reconstructed output matches byte-for-byte.
- Accuracy: Validate Kotlin outputs against C++ using an accuracy harness (see below).
- Scope Control: Change only what’s required; do not reformat unrelated code.
- Observability: Before tool calls, state intent in 1 sentence; after, report result.
- Commands: Provide zsh-friendly commands in fenced blocks.

## 🛠️ Standard Tooling Interfaces (Proven Implementation)

### Core LST Tools
- **LST generator**: `lst/build_lst.py` - Creates lossless semantic trees with comment extraction
- **LST verification**: `lst/verify.py` - Validates losslessness and structural integrity
- **LST documentation**: `lst/to_md.py`, `lst/to_md_all.py` - Generate readable documentation
- **Symbol indexing**: `lst/index_symbols.py` - Create searchable symbol databases

### Advanced MCP Tools (Production-Ready)
- **Relationship chunker**: `mcp/relationship_aware_chunker.py` - Context-aware chunk creation
- **Coarse chunker**: `mcp/coarse_grained_chunker.py` - Logical grouping and optimization
- **MCP converter**: `mcp/coarse_chunk_converter.py` - High-quality chunk conversion
- **Assembler**: `mcp/coarse_assembler.py` - Final Kotlin class generation
- **Orchestrator**: `mcp/orchestrator.py` - Complete workflow management

### Quality Assurance Tools
- **LST accuracy**: `accuracy/lst_accuracy.py` - Structural comparison between C++ and Kotlin
- **Comment validator**: Built into MCP tools - Ensures 100% comment preservation
- **Context validator**: Verifies variable scope and relationship integrity

### Production Workflow (Proven)
```bash
# 1. Generate relationship-aware chunks
python3 mcp/relationship_aware_chunker.py --lst src/Test.lst.json --preserve-comments

# 2. Create optimized coarse chunks  
python3 mcp/coarse_grained_chunker.py --chunks-dir chunks --goto-detection

# 3. Convert with context preservation
python3 mcp/coarse_chunk_converter.py --coarse-chunks-dir coarse_chunks

# 4. Assemble final Kotlin class
python3 mcp/coarse_assembler.py --converted-chunks converted_chunks.json
```

## 📋 Enhanced LST Workflow (Production-Tested)

### Single File Conversion (Recommended)
```bash
# Generate LST with comment preservation
python3 <lst>/build_lst.py <path/to/file.cpp> --out <lst_out>/<safe>.lst.json --preserve-comments

# Verify losslessness
python3 <lst>/verify.py <lst_out>/<safe>.lst.json

# Generate documentation
python3 <lst>/to_md.py <lst_out>/<safe>.lst.json --out <lst_out>/<safe>.md

# Create relationship-aware chunks
python3 <mcp>/relationship_aware_chunker.py --lst <lst_out>/<safe>.lst.json --preserve-comments
```

### Batch Processing (Large Codebases)
```bash
# Process entire repository
python3 <lst>/run_all.py --preserve-comments

# Verify all LSTs
python3 <lst>/verify.py <lst_out>/*.lst.json

# Generate comprehensive documentation
python3 <lst>/to_md_all.py

# Build symbol index
python3 <lst>/index_symbols.py --out <lst_out>/symbols.index.json
```

### Quality Validation
```bash
# Structural accuracy comparison
python3 <accuracy>/lst_accuracy.py <cpp_lst> <kotlin_lst> --mapping <symbol_mapping>

# Comment preservation verification
grep -c '//' <original.cpp> && grep -c '//' <converted.kt>  # Should match
```

## LST Accuracy (Structural Fidelity)
- Goal: the converted Kotlin source should mirror the C++ structure when both are represented as LSTs.
- Method: generate LSTs for source and ported files; compare with `accuracy/lst_accuracy.py`.
- Mapping: normalize known symbol renames and ignore non-semantic tokens via a mapping file.
- Signal: any structural diffs should be treated as regressions unless explicitly justified.

## 🚀 Advanced MCP Chunked Conversion (Production System)

### Core Concept
Handle large C++ files through intelligent, relationship-aware chunking with complete context preservation and comment maintenance.

### Production Workflow (Proven at Scale)

#### 1. **Enhanced LST Generation**
```bash
python3 build_lst.py src/Test.cpp --preserve-comments --extract-relationships
```
**Output:** LST with embedded comment data and structural relationships

#### 2. **Relationship-Aware Chunking** 
```bash
python3 relationship_aware_chunker.py \
  --lst src/Test.lst.json \
  --out-dir chunks \
  --relationships-out relationships.json \
  --preserve-comments
```
**Features:**
- Variable scope tracking (local/class/global)
- Method call dependency mapping
- Comment-to-code associations
- Function signature extraction

#### 3. **Coarse-Grained Optimization**
```bash
python3 coarse_grained_chunker.py \
  --chunks-dir chunks \
  --output-dir coarse_chunks \
  --goto-detection \
  --priority-assignment
```
**Optimization Results:** Typically 3:1 chunk reduction (1,863 → 555 chunks)

#### 4. **Context-Aware Conversion** 
```bash
python3 coarse_chunk_converter.py \
  --coarse-chunks-dir coarse_chunks \
  --converted-chunks-out converted_chunks.json \
  --preserve-all-comments
```
**Process:** Priority-based conversion (high/medium/low) with full context preservation

#### 5. **Intelligent Assembly**
```bash
python3 coarse_assembler.py \
  --converted-chunks converted_chunks.json \
  --output Test_Complete.kt \
  --verify-comments
```
**Output:** Complete Kotlin class with organized functions and preserved comments

### Quality Metrics (Proven)
- **Conversion Success Rate**: 100% (555/555 chunks in recent conversion)
- **Comment Preservation**: 100% (all original comments maintained)
- **Function Accuracy**: Correct parameter identification (not inflated with local variables)
- **Manual Review Rate**: ~60% (355/555 chunks flagged for complex logic review)
- **Code Generation**: 6,771 lines of production-ready Kotlin

### Benefits at Scale
- **Scalable**: Handle files of any size through intelligent chunking
- **Parallel**: Process chunks concurrently by priority
- **Context-Aware**: Maintain variable relationships and dependencies  
- **Resumable**: Retry failed chunks with full context
- **Quality Focused**: Built-in validation and manual review flagging

## ⚠️ CRITICAL: Function Context Preservation Rules

### MANDATORY Pre-Conversion Validation
**ALWAYS perform these checks before converting any function:**

1. **Function Signature First**: Locate and read the corresponding `func_sig_*.json` chunk BEFORE processing any `body_*.json` chunks
2. **Parameter Validation**: Extract the EXACT parameter list from the function signature, not from body chunks
3. **Local Variable Identification**: Variables declared inside function bodies are LOCAL VARIABLES, NOT PARAMETERS
4. **Scope Awareness**: Maintain clear distinction between function parameters vs local variables vs class members

### Common Error Pattern to Avoid
```cpp
// C++ function signature shows:
void CTest::SetSuperData1( YahuzazFlag Yahuzazf )

// Body chunks contain local variables:
char work[20], work2[40];
long siyoryo, mryo, cryo;

// ❌ WRONG: Adding locals as parameters
fun setSuperData1(yahuzazf: YahuzazFlag, work: CharArray, work2: CharArray, siyoryo: Long, ...)

// ✅ CORRECT: Only actual parameters
fun setSuperData1(yahuzazf: YahuzazFlag) {
    var work = CharArray(20)  // Local variable
    var work2 = CharArray(40) // Local variable
    var siyoryo: Long = 0     // Local variable
}
```

### Validation Checklist for Every Function
- [ ] Function signature chunk identified and parsed
- [ ] Parameter count matches between C++ and Kotlin
- [ ] No local variables treated as parameters  
- [ ] Return type correctly converted
- [ ] Function name follows Kotlin naming conventions
- [ ] All business logic preserved within function scope

## Conversion Placeholder System
**Unique placeholders prevent conflicts with existing TODO comments:**

### Core Placeholders
- `CONVERSION_IMPORTS_PLACEHOLDER` - Add necessary imports based on converted chunks
- `CONVERSION_CONSTANTS_PLACEHOLDER` - C++ #defines and const values
- `CONVERSION_CLASS_DOC_PLACEHOLDER` - Class-level documentation
- `CONVERSION_MEMBER_VARS_PLACEHOLDER` - C++ member variables → Kotlin properties
- `CONVERSION_CONSTRUCTOR_IMPL_PLACEHOLDER` - Constructor implementation
- `CONVERSION_METHOD_DOC_PLACEHOLDER` - Method documentation  
- `CONVERSION_VARS_PLACEHOLDER` - Local variable declarations
- `CONVERSION_LOGIC_PLACEHOLDER` - Main method/function logic
- `CONVERSION_RETURN_PLACEHOLDER` - Return statement implementation
- `CONVERSION_FUNCTION_DOC_PLACEHOLDER` - Function documentation

### Chunk Markers
- `CONVERSION_CHUNK_START_<id>` - Beginning of conversion chunk
- `CONVERSION_CHUNK_END_<id>` - End of conversion chunk

### Conversion Strategy
1. **Skeleton Generation** (Thinking Model): Creates structure with placeholders
2. **Chunk Conversion** (Heavy Work Model): Replaces placeholders with actual Kotlin code **INCLUDING ALL ORIGINAL COMMENTS**
3. **Comment Preservation** (All Models): **MANDATORY** - Preserve ALL C++ comments verbatim
4. **Validation** (Thinking Model): Ensures code quality, architectural consistency, **AND COMMENT PRESERVATION**
5. **Assembly** (Thinking Model): Combines all components into final file with comments intact

## Kotlin Porting Guidance (Behavioral Parity)
- Builder options parity: indentation, YAML colon spacing, drop nulls, useSpecialFloats, emitUTF8, precision, precisionType.
- String escaping: control chars, UTF‑8 passthrough, `\uXXXX`, surrogate pairs.
- Doubles: locale-independent formatting, `.0` enforcement rules, trimming for decimalPlaces, exponent case/padding.
- Arrays/objects: multiline heuristic approximating C++ right-margin behavior; bracket and element indentation must match.
- **Comments: MANDATORY preservation of ALL C++ comments including business logic, change tracking, and historical annotations.**

## 🔤 Comment Preservation Requirements

### Critical Rule: Preserve ALL Original Comments
**ALWAYS preserve C++ comments during conversion:**

1. **Business Logic Comments**: Technical explanations of algorithms and calculations
2. **Change Tracking Comments**: Historical change markers (e.g., "20120130 201301-01 新CIS対応")
3. **Development Notes**: TODO items, bug fix references, and developer annotations
4. **Conditional Code Comments**: Commented-out code that may be relevant for future reference
5. **Section Headers**: Comments that organize code sections

### Comment Conversion Strategy
```cpp
// C++ comment style
/* Multi-line C++ comments */
// 20120130 201301-01 新CIS対応 ADD ↓↓↓ H.X
```

```kotlin
// Kotlin comment style (preserve content exactly)
/* Multi-line Kotlin comments */
// 20120130 201301-01 新CIS対応 ADD ↓↓↓ H.X
```

### Implementation Guidelines
- **Maintain Original Comment Text**: Do not translate or modify comment content
- **Preserve Comment Placement**: Keep comments in the same relative position to code
- **Include Japanese Comments**: Preserve all Japanese text and special characters
- **Keep Change Tracking**: Maintain all version control and change tracking information
- **Preserve Code Context**: Comments often provide essential business context

### Comment Processing in MCP Workflow
- **LST Generation**: Ensure comments are captured in the LST structure
- **Chunking**: Include comments with their associated code chunks
- **Conversion**: Copy comments verbatim to Kotlin output
- **Assembly**: Maintain comment positioning during file assembly

## Change Strategy by Model
- GPT‑5/Claude:
  - May design/refine schema or multi-file refactors; still verify.
  - Can operate on many files if verifiers are fast and green.
- GPT‑4.1:
  - Limit scope; use existing schema/tools; avoid redesign.
  - Prefer incremental commits; keep diffs minimal and test-backed.

## ✅ Definition of Done (Production Standards)

### Technical Completion Criteria
- **LST Verification**: Verified lossless; Markdown outline generated successfully
- **Structural Integrity**: LST structural comparator shows no semantic diffs
- **Conversion Completeness**: All chunks converted with 100% success rate
- **Placeholder Resolution**: All CONVERSION_* placeholders replaced with actual implementation

### Quality Assurance Requirements  
- **Comment Preservation**: 100% of C++ comments preserved verbatim in Kotlin output
- **Function Accuracy**: Correct parameter identification (no local variables as parameters)
- **Context Integrity**: Variable scope and method relationships maintained
- **Business Logic**: All algorithms and calculations preserved exactly

### Code Quality Standards
- **Kotlin Syntax**: Proper Kotlin syntax, idioms, and conventions
- **Type Safety**: Appropriate null safety and type conversions
- **Error Handling**: Proper exception handling and error propagation
- **Performance**: No unnecessary performance degradation from conversion

### Documentation and Validation
- **Comment Verification**: Manual review confirms no comments lost or modified
- **Manual Review**: Complex conversions flagged and reviewed by developers
- **Unit Testing**: Conversion accuracy validated through testing
- **Documentation**: README and usage documentation updated where relevant

### Success Metrics Benchmark
- **Conversion Rate**: Target 100% (recent achievement: 555/555 chunks)
- **Comment Preservation**: 100% preservation rate required
- **Function Count**: All original functions represented in Kotlin
- **Manual Review Rate**: 60-70% flagging for complex logic review (normal)

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
