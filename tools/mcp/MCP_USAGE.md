# MCP C++ to Kotlin Conversion - Complete Usage Guide

## 🎯 Overview

This guide covers the complete workflow for converting C++ code to Kotlin using our advanced MCP (Model Context Protocol) system with relationship-aware chunking, comment preservation, and context-aware conversion.

## 🧠 Model Selection Strategy

### Heavy Work Tasks (Low-Cost Models)
- **Models**: GPT-4o, GPT-4-turbo, Claude-3.5-Haiku, Claude-3-Haiku
- **Tasks**: 
  - `convert_chunk` - Converting individual code chunks
  - Basic syntax transformation and placeholder filling
  - Mechanical edits with clear patterns
- **Rationale**: These are well-defined transformation tasks that don't require deep architectural reasoning

### Thinking Tasks (High-Capability Models)
- **Models**: Claude-3.5-Sonnet, GPT-o1-preview, GPT-o1-mini, Claude-3-Opus
- **Tasks**:
  - `build_skeleton` - Analyzing LST structure and generating comprehensive skeletons
  - `validate_chunk` - Ensuring code quality, fit, and architectural consistency
  - `assemble_file` - Combining components and resolving dependencies
  - Relationship analysis, architectural decisions, and error diagnosis
- **Rationale**: These require complex reasoning about code structure and relationships

## 🔧 Complete Conversion Workflow

### Phase 1: LST Generation and Analysis

#### 1.1 Generate LST from C++ Source
```bash
# Generate LST with comment extraction
cd tools/lst
python3 build_lst.py ../../src/Test.cpp --preserve-comments
```

#### 1.2 Create Relationship-Aware Chunks
```bash
cd tools/mcp
python3 relationship_aware_chunker.py \
  --lst ../../src/Test.lst.json \
  --out-dir ../../conversion_work/chunks \
  --skeleton-out ../../conversion_work/skeleton_with_relationships.json \
  --relationships-out ../../conversion_work/relationships.json \
  --preserve-comments
```

**Output:**
- Fine-grained chunks with variable scope information
- Skeleton structure with placeholders
- Comprehensive relationship mapping
- Comment associations

### Phase 2: Coarse-Grained Optimization

#### 2.1 Create Logical Chunk Groups
```bash
python3 coarse_grained_chunker.py \
  --chunks-dir ../../conversion_work/chunks \
  --output-dir ../../conversion_work/coarse_chunks \
  --summary-out ../../conversion_work/coarse_chunking_summary.json \
  --goto-detection
```

**Features:**
- Groups related statements into logical units
- Assigns priority levels (high/medium/low)
- Detects GOTO statements for special handling
- Compresses chunk count (typically 3:1 ratio)

### Phase 3: MCP Conversion

#### 3.1 Convert Chunks with Context
```bash
python3 coarse_chunk_converter.py \
  --coarse-chunks-dir ../../conversion_work/coarse_chunks \
  --output-dir ../../conversion_work/kotlin_chunks \
  --converted-chunks-out ../../conversion_work/converted_chunks.json \
  --conversion-report-out ../../conversion_work/conversion_report.json
```

**Process:**
- Processes chunks by priority order
- Preserves all original comments
- Maintains variable scope context
- Generates comprehensive conversion report

### Phase 4: Assembly and Validation

#### 4.1 Assemble Final Kotlin Class
```bash
python3 coarse_assembler.py \
  --converted-chunks ../../conversion_work/converted_chunks.json \
  --skeleton ../../conversion_work/skeleton_with_relationships.json \
  --output ../../conversion_work/Test_Complete.kt \
  --class-name Test
```

**Output:**
- Complete Kotlin class with proper structure
- All functions organized by logical grouping
- Comments preserved in correct positions
- Assembly report with statistics

## 🏷️ Enhanced Placeholder System

Our system uses context-aware placeholders that preserve business logic:

### Core Placeholders
```kotlin
// CONVERSION_IMPORTS_PLACEHOLDER - Required imports based on code analysis
// CONVERSION_CONSTANTS_PLACEHOLDER - C++ #defines and const values  
// CONVERSION_CLASS_DOC_PLACEHOLDER - Class-level documentation
// CONVERSION_MEMBER_VARS_PLACEHOLDER - C++ member variables → Kotlin properties
// CONVERSION_CONSTRUCTOR_IMPL_PLACEHOLDER - Constructor with proper initialization
```

### Function-Level Placeholders
```kotlin
// CONVERSION_FUNCTION_DOC_PLACEHOLDER - Function documentation and comments
// CONVERSION_PARAMS_PLACEHOLDER - Function parameters (NOT local variables)
// CONVERSION_VARS_PLACEHOLDER - Local variable declarations with proper types
// CONVERSION_LOGIC_PLACEHOLDER - Main method logic with preserved comments
// CONVERSION_RETURN_PLACEHOLDER - Return statement with type safety
```

### Comment Preservation Markers
```kotlin
// CONVERSION_COMMENTS_START - Begin preserved comment block
// 20120130 201301-01 新CIS対応 ADD ↓↓↓ H.X (preserved exactly)
// 単価コメント１(フィールドNo.275) (preserved exactly)
// CONVERSION_COMMENTS_END - End preserved comment block
```

## 📊 Quality Assurance and Validation

### Automatic Quality Checks
- **Comment Preservation**: Verify all C++ comments are preserved
- **Function Context**: Ensure parameters vs local variables are correct
- **Type Safety**: Validate all type conversions
- **Relationship Integrity**: Check variable scope and method calls
- **Business Logic**: Confirm algorithm preservation

### Manual Review Indicators
```json
{
  "manual_review_needed": [
    {
      "chunk_id": "coarse_145",
      "reason": "contains_todo_items",
      "priority": "high"
    }
  ]
}
```

### Success Metrics
- **Conversion Rate**: Target 100% (recent: 555/555 chunks)
- **Comment Preservation**: 100% of original comments maintained
- **Function Accuracy**: Correct parameter identification (not 103 parameters!)
- **Context Integrity**: Variable scope and relationships preserved

## 🛠️ Advanced Configuration

### Model Selection Configuration (`mcp_config.json`)
```json
{
  "model_selection": {
    "heavy_work": {
      "recommended_models": ["gpt-4o", "claude-3-5-haiku"],
      "tasks": ["convert_chunk"],
      "cost_optimization": true
    },
    "thinking_work": {
      "recommended_models": ["claude-3-5-sonnet", "gpt-o1-preview"],
      "tasks": ["build_skeleton", "validate_chunk", "assemble_file"],
      "quality_focus": true
    }
  },
  "comment_preservation": {
    "mandatory": true,
    "preserve_japanese": true,
    "preserve_change_tracking": true,
    "preserve_business_logic": true
  }
}
```

### Chunking Configuration
```json
{
  "coarse_chunking": {
    "min_chunk_size": 3,
    "max_chunk_size": 15,
    "priority_assignment": {
      "high": ["function_signature", "main_logic", "error_handling"],
      "medium": ["variable_declarations", "simple_operations"],
      "low": ["comments_only", "includes", "constants"]
    },
    "goto_detection": true,
    "relationship_tracking": true
  }
}
```

## 🐛 Troubleshooting Guide

### Common Issues and Solutions

#### Issue: Comments Lost During Conversion
```bash
# Solution: Verify comment extraction
grep -c "//" src/Test.cpp  # Count original comments
grep -c "//" conversion_work/Test_Complete.kt  # Count preserved comments
# Numbers should match!
```

#### Issue: Too Many Function Parameters
```bash
# Solution: Check function signature chunks first
grep -A 5 "func_sig_" conversion_work/chunks/*.json
# Verify only actual parameters, not local variables
```

#### Issue: Lost Business Context
```bash
# Solution: Verify relationship preservation
python3 -c "import json; print(json.load(open('conversion_work/relationships.json'))['variable_scope'])"
```

### Debug Commands
```bash
# Verify LST losslessness
python3 tools/lst/verify.py src/Test.lst.json

# Check chunk relationship integrity
python3 tools/mcp/relationship_aware_chunker.py --debug --validate-only

# Validate comment preservation
python3 tools/mcp/coarse_assembler.py --verify-comments

# Check conversion statistics
cat conversion_work/conversion_report.json | jq '.conversion_summary'
```

## 📈 Success Examples

### Recent Conversion Results
- **Source**: Test.cpp (Gas billing system)
- **Output**: Test_Complete.kt (6,771 lines)
- **Functions**: 17 major functions converted
- **Chunks**: 555 logical chunks (from 1,863 fine-grained)
- **Success Rate**: 100% (555/555)
- **Comments**: 100% preserved
- **Manual Review**: 355 chunks flagged for developer verification

### Function Breakdown
| Function | Chunks | Status | Comments Preserved |
|----------|--------|--------|-----------------|
| SetSuperData1 | 184 | ✅ Complete | ✅ All |
| Setzumita | 95 | ✅ Complete | ✅ All |
| SetSuperData2 | 44 | ✅ Complete | ✅ All |
| SetTRyohyo | 31 | ✅ Complete | ✅ All |
| ... | ... | ✅ Complete | ✅ All |

## 🎓 Best Practices

### DO:
- ✅ Always run relationship analysis before conversion
- ✅ Verify comment preservation at each step
- ✅ Use coarse-grained chunking for efficiency
- ✅ Check function signatures before converting bodies
- ✅ Validate business logic preservation

### DON'T:
- ❌ Convert chunks without context
- ❌ Modify or translate comment content
- ❌ Add local variables as function parameters
- ❌ Skip manual review of flagged chunks
- ❌ Ignore relationship validation

This comprehensive approach ensures high-quality, maintainable Kotlin code that preserves all the business logic and historical context from the original C++ implementation.