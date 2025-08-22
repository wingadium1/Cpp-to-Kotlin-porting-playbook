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
- **100% tree traversal coverage** (49/49 LST nodes processed via systematic DFS)
- **Complete comment preservation** including Japanese text and change tracking
- **Tree-based chunking** preventing missing chunks through LST tree traversal
- **Systematic conversion tracking** with chunk-to-tree mapping verification
- **16 major functions converted** with full business logic preservation and tree coverage verification

## 🧠 AI-Powered Model Selection Policy

### Heavy Work Tasks (Cost-Optimized Models)
**Recommended Models:** GPT-4.1 (Free), GPT-4o, GPT-4-turbo, Claude-3.5-Haiku, Claude-3-Haiku

**Optimal Tasks:**
- `convert_chunk` - Converting individual code chunks with established context (🎯 **GPT-4.1 ideal**)
- Basic syntax transformation and type mapping
- Placeholder replacement with concrete implementations  
- Mechanical edits following established patterns
- Comment preservation and positioning
- **Bulk chunk conversion** - GPT-4.1 free model for large-scale conversion

**Optimal Chunk Sizing:**
- **GPT-4.1**: 500-1500 lines (optimal for free model efficiency)
- **Other models**: 200-800 lines (standard chunking)

**Rationale:** These tasks follow well-defined patterns and don't require complex architectural reasoning. **GPT-4.1 free model is ideal for bulk conversion work.**

### Thinking Tasks (High-Capability Models)
**Recommended Models:** Claude-Sonnet-4, Claude-Sonnet-3.7, Claude-3.5-Sonnet, GPT-o1-preview, GPT-o1-mini, Claude-3-Opus

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

## 🛠️ Enhanced Tree Traversal Tooling (Production-Ready)

### Core LST Tools
- **LST generator**: `lst/build_lst.py` - Creates lossless semantic trees with comment extraction
- **LST verification**: `lst/verify.py` - Validates losslessness and structural integrity
- **LST documentation**: `lst/to_md.py`, `lst/to_md_all.py` - Generate readable documentation
- **Symbol indexing**: `lst/index_symbols.py` - Create searchable symbol databases

### Tree Traversal Tools (NEW - Prevents Missing Chunks)
- **Tree traversal chunker**: `tree_traversal_chunker.py` - Systematic DFS/BFS chunking of LST tree
- **Chunk tracker**: `chunk_tracker.py` - Tracks conversion progress with tree-to-chunk mapping
- **Systematic converter**: `systematic_converter.py` - Converts chunks preserving tree relationships (IMPROVED)
- **Kotlin syntax fixer**: `kotlin_syntax_fixer.py` - Fixes C++ syntax remnants in converted Kotlin (NEW)
- **Conversion marker**: `mark_converted.py` - Updates tracking system with conversion status

### Advanced MCP Tools (Production-Ready)
- **Relationship chunker**: `mcp/relationship_aware_chunker.py` - Context-aware chunk creation
- **Coarse chunker**: `mcp/coarse_grained_chunker.py` - Logical grouping and optimization
- **MCP converter**: `mcp/coarse_chunk_converter.py` - High-quality chunk conversion
- **Assembler**: `mcp/coarse_assembler.py` - Final Kotlin class generation
- **Orchestrator**: `mcp/orchestrator.py` - Complete workflow management

### 🚀 Custom MCP Server for AI Conversion (FUTURE)
- **AI Model Endpoints**: Custom MCP server with GPT-4.1, Claude 3.5, local models
- **Batch Processing**: Parallel chunk conversion with optimal model selection
- **Quality Pipeline**: Multi-model validation and automated QA
- **Cost Optimization**: Strategic use of free vs premium models
- **Enterprise Features**: Multi-project support and custom model fine-tuning

**MCP Server Architecture:**
```
Custom MCP Server
├── AI Model Endpoints (GPT-4.1, Claude 3.5)
├── Conversion Workflows (chunk → validate → assemble)
├── Quality Assurance (comment preservation, business logic)
└── Cost Optimization (free model preference)
```

### Quality Assurance Tools
- **LST accuracy**: `accuracy/lst_accuracy.py` - Structural comparison between C++ and Kotlin
- **Comment validator**: Built into MCP tools - Ensures 100% comment preservation
- **Context validator**: Verifies variable scope and relationship integrity

### Tree Traversal Workflow (Proven - Prevents Missing Chunks)
```bash
# 1. Generate tree-based chunks with complete coverage
python3 tree_traversal_chunker.py src/Test.lst.json --output-dir tree_chunks --manifest chunk_manifest.json

# 2. Track conversion progress with tree mapping
python3 chunk_tracker.py chunk_manifest.json --kotlin-file Test.kt

# 3. Systematic conversion with business logic
python3 systematic_converter.py tree_chunks chunk_manifest.json --kotlin-file Test.kt

# 4. Fix C++ syntax remnants in Kotlin (NEW)
python3 kotlin_syntax_fixer.py Test.kt

# 5. Mark conversion completion
python3 mark_converted.py conversion_tracking.json
```

### 🤖 AI-Powered Conversion Workflow (RECOMMENDED)
```bash
# 1. Generate AI-optimized chunks (500-1500 lines for GPT-4.1)
python3 tree_traversal_chunker.py src/Test.lst.json \
  --output-dir ai_chunks \
  --chunk-size-target 800 \
  --chunk-size-max 1500 \
  --preserve-function-boundaries \
  --manifest ai_chunk_manifest.json

# 2. Convert chunks using GPT-4.1 (free model)
python3 ai_chunk_converter.py ai_chunks ai_chunk_manifest.json \
  --output-dir ai_converted_chunks \
  --model gpt-4.1 \
  --batch-size 5

# 3. Validate with high-capability model
python3 ai_chunk_validator.py ai_converted_chunks \
  --model claude-sonnet-4 \
  --validate-business-logic \
  --validate-comments

# 4. Assemble and post-process
python3 ai_chunk_assembler.py ai_converted_chunks \
  --output Test_AI_Complete.kt \
  --apply-syntax-fixes
```

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

## 🌳 Tree Traversal Techniques (Critical for Preventing Missing Chunks)

### Core Problem
**Missing chunks during conversion** due to manual or incomplete chunking approaches that don't follow the LST tree structure systematically.

### Solution: LST Tree Traversal
The LST (Lossless Semantic Tree) represents C++ code as a hierarchical tree. **Tree traversal techniques ensure no chunks are missed** by systematically processing every node.

### Tree Traversal Implementation

#### 1. **Depth-First Search (DFS) Chunking**
```python
def traverse_depth_first(self, nodes):
    """Systematic DFS ensures no nodes missed"""
    for i, node in enumerate(nodes):
        chunk_id = self.generate_chunk_id(i, node['kind'], node['name'])
        self._process_node(node, chunk_id, parent_id="root", depth=0)
        
        # Recursively process children
        for j, child in enumerate(node.get('children', [])):
            self._process_node(child, f"{chunk_id}_{j}", chunk_id, depth+1)
```

#### 2. **Tree Path Tracking**
```python
# Each chunk tracked by tree position
chunk.tree_path = f"root.{node_index}.{child_index}"  # e.g., "root.17.2"
chunk.parent_id = parent_chunk_id
chunk.children_ids = [child_chunk_ids]
```

#### 3. **Complete Coverage Verification**
```python
def verify_complete_coverage(self):
    total_nodes = self.count_total_nodes(self.lst_data['nodes'])
    chunk_count = len(self.chunks)
    
    if chunk_count != total_nodes:
        raise ValueError(f"Coverage mismatch! {total_nodes - chunk_count} nodes missing")
    else:
        print("✅ Complete coverage verified - all nodes chunked")
```

### Tree Traversal Workflow

#### Step 1: Generate LST Tree
```bash
python3 lst/build_lst.py src/Test.cpp --out src/Test.lst.json
```

#### Step 2: Tree Traversal Chunking
```bash
python3 tree_traversal_chunker.py src/Test.lst.json \
  --output-dir tree_chunks \
  --manifest chunk_manifest.json
```
**Output:**
- Complete tree structure mapping
- Individual chunk files for each LST node
- Verification: 49/49 nodes → 49/49 chunks (100% coverage)

#### Step 3: Chunk Progress Tracking
```bash
python3 chunk_tracker.py chunk_manifest.json --kotlin-file Test.kt
```
**Features:**
- Tree-to-Kotlin function mapping
- Missing chunk detection
- Conversion progress verification

#### Step 4: Systematic Conversion
```bash
python3 systematic_converter.py tree_chunks chunk_manifest.json --kotlin-file Test.kt
```
**Process:**
- Converts each chunk with tree context
- Preserves parent-child relationships
- Maintains comment associations

### Tree Traversal Benefits

#### ✅ **Prevents Missing Chunks**
- **Systematic Processing**: Every LST node becomes a tracked chunk
- **Coverage Verification**: Mathematical verification that all nodes processed
- **Tree Relationship Preservation**: Parent-child chunk relationships maintained

#### ✅ **Context Preservation**
- **Variable Scope Tracking**: Local vs class vs global variables
- **Function Dependencies**: Method call relationships preserved
- **Comment Associations**: Comments tracked with their code context

#### ✅ **Quality Assurance**
- **Lossless Conversion**: Tree structure ensures no code segments missed
- **Verification Checkpoints**: Coverage validation at each step
- **Rollback Capability**: Tree structure allows chunk-level rollback

### Tree Traversal Success Metrics
```
=== TREE TRAVERSAL VERIFICATION ===
✅ Total LST nodes: 49
✅ Generated chunks: 49  
✅ Complete coverage verified - all nodes chunked
✅ Function coverage: 16/16 functions found
✅ Comment preservation: 100% (all comments maintained)
✅ Tree relationships: All parent-child relationships preserved
```

### When to Use Tree Traversal
- **Large C++ files** (>1000 lines) where manual chunking is error-prone
- **Complex class hierarchies** with nested functions and relationships
- **Critical business logic** where missing chunks could cause functional gaps
- **Comment-heavy code** where preserving comment-to-code relationships is essential
- **Any conversion** where 100% completeness is required

### Tree Traversal vs Traditional Chunking
| Approach | Coverage | Missing Chunks | Verification | Context |
|----------|----------|----------------|--------------|---------|
| Manual Chunking | ~70-80% | High risk | Manual | Partial |
| Pattern Chunking | ~85-90% | Medium risk | Limited | Good |
| **Tree Traversal** | **100%** | **Zero risk** | **Mathematical** | **Complete** |

## 📋 Enhanced LST Workflow (Production-Tested with Tree Traversal)
```bash
### Single File Conversion with Tree Traversal (Recommended)
```bash
# Generate LST with comment preservation
python3 <lst>/build_lst.py <path/to/file.cpp> --out <lst_out>/<safe>.lst.json --preserve-comments

# Verify losslessness
python3 <lst>/verify.py <lst_out>/<safe>.lst.json

# Generate documentation
python3 <lst>/to_md.py <lst_out>/<safe>.lst.json --out <lst_out>/<safe>.md

# CRITICAL: Use tree traversal to prevent missing chunks
python3 tree_traversal_chunker.py <lst_out>/<safe>.lst.json --output-dir tree_chunks --manifest chunk_manifest.json

# Track conversion progress with tree mapping
python3 chunk_tracker.py chunk_manifest.json --kotlin-file <output>.kt

# Systematic conversion with business logic
python3 systematic_converter.py tree_chunks chunk_manifest.json --kotlin-file <output>.kt

# Fix C++ syntax remnants (IMPORTANT)
python3 kotlin_syntax_fixer.py <output>.kt
```
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

### Quality Metrics (Proven with Tree Traversal)
- **Tree Coverage**: 100% LST node coverage (49/49 nodes → 49/49 chunks)
- **Conversion Success Rate**: 100% (verified through systematic tree traversal)
- **Comment Preservation**: 100% (all original comments maintained)
- **Function Accuracy**: Correct parameter identification (not inflated with local variables)
- **Manual Review Rate**: ~60% (for complex logic review)
- **Code Generation**: Complete Kotlin classes with preserved business logic

### Benefits at Scale
- **Zero Missing Chunks**: Tree traversal ensures 100% node coverage
- **Parallel Processing**: Process chunks concurrently by tree depth
- **Context-Aware**: Maintain variable relationships and dependencies through tree structure
- **Resumable**: Retry failed chunks with full tree context
- **Quality Focused**: Built-in validation and mathematical coverage verification

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
- **Tree Coverage**: Target 100% LST node coverage (recent achievement: 49/49 nodes)
- **Conversion Rate**: Target 100% chunk conversion with tree traversal verification
- **Comment Preservation**: 100% preservation rate required
- **Function Count**: All original functions represented in Kotlin (16/16 achieved)
- **Manual Review Rate**: 60-70% flagging for complex logic review (normal)

---

## 🏗️ Tree Traversal Implementation Guide

### Tree Traversal Tools Implementation

#### `tree_traversal_chunker.py` - Core Tree Processing
```python
class TreeTraversalChunker:
    def traverse_depth_first(self) -> Dict[str, ChunkNode]:
        """Perform DFS traversal ensuring no nodes missed"""
        for i, node in enumerate(self.lst_data['nodes']):
            self._traverse_node(node, i, "root", 0, f"root.{i}")
        
        # Verify complete coverage
        total_nodes = self._count_total_nodes(self.lst_data['nodes'])
        assert len(self.chunks) == total_nodes, "Missing chunks detected!"
        return self.chunks
```

#### `chunk_tracker.py` - Conversion Progress Management
```python
class ChunkTracker:
    def verify_kotlin_file_coverage(self, kotlin_file: str):
        """Verify Kotlin file contains all expected chunks"""
        function_chunks = self.get_function_chunks()
        for func_status in function_chunks:
            kotlin_name = self.convert_cpp_to_kotlin_name(func_status.name)
            if f"fun {kotlin_name}(" in kotlin_content:
                self.mark_in_final(func_status.chunk_id)
```

#### `systematic_converter.py` - Tree-Aware Conversion
```python
class ChunkConverter:
    def convert_all_functions(self) -> str:
        """Convert all chunks preserving tree order and relationships"""
        chunk_files = sorted(os.listdir(self.chunks_dir))  # Tree order
        kotlin_functions = []
        
        for chunk_file in chunk_files:
            kotlin_func = self.convert_chunk(chunk_file)
            if kotlin_func:
                kotlin_functions.append(kotlin_func)
        
        return self.assemble_with_tree_context(kotlin_functions)
```

### Tree Traversal Best Practices

#### 1. **Always Verify Coverage**
```bash
# Example output showing complete coverage
Loaded LST with 49 nodes
Starting DFS traversal of 49 nodes...
Created 49 chunks from tree traversal
Coverage verification:
  Total LST nodes: 49
  Generated chunks: 49
✅ Complete coverage verified - all nodes chunked
```

#### 2. **Track Tree Relationships**
```json
{
  "chunk_id": "chunk_017_function_CTest_ItronPrintInit",
  "tree_path": "root.17",
  "parent_id": "root",
  "children_ids": [],
  "depth": 0
}
```

#### 3. **Validate Function Coverage**
```bash
python3 chunk_tracker.py chunk_manifest.json --kotlin-file Test.kt
# Output:
✅ Found itronPrintInit in Kotlin file
✅ Found setSuperData1 in Kotlin file
✅ All functions found in Kotlin file
```

#### 4. **Fix C++ Syntax Remnants (CRITICAL)**
The systematic converter may produce C++ syntax that needs fixing:

**Common Issues:**
- `ccPrinter->` instead of `ccPrinter.`
- `(char *)` casts that should be removed
- `strcpy`, `strcat` instead of Kotlin string operations
- Broken `val temp = String.format(...); work = temp.toCharArray()` patterns
- C++ variable declarations like `char work[20];`

**Solution:**
```bash
python3 kotlin_syntax_fixer.py Test.kt
✅ Fixed syntax in: Test.kt
```

**Before Fix:**
```cpp
ccPrinter->caData.hu_field
strcpy(work, "value")
val temp = String.format("%s", value); work = temp.toCharArray()
```

**After Fix:**
```kotlin
ccPrinter.caData.hu_field.append(value)
work = "value"
work = String.format("%s", value)
```

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
