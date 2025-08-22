#!/usr/bin/env python3
"""
Coarse-Grained Relationship-Aware Chunker

This chunker creates larger, more logical chunks by:
1. Grouping sequential simple statements together
2. Keeping control structures (if/else, loops) as complete blocks
3. Special handling for GOTO statements (restructuring required)
4. Creating chunks based on logical complexity rather than line count
"""
import argparse
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple


class CoarseGrainedChunker:
    def __init__(self, fine_chunks_dir: str):
        self.fine_chunks_dir = fine_chunks_dir
        self.fine_chunks: Dict[str, Dict] = {}
        self.coarse_chunks: List[Dict] = []
        self.chunk_counter = 0
        
        # Load fine-grained chunks
        self._load_fine_chunks()
        
        # Group chunks by function
        self.function_chunks: Dict[str, List[Dict]] = {}
        self._group_chunks_by_function()
        
    def _load_fine_chunks(self):
        """Load all fine-grained chunks."""
        for chunk_file in Path(self.fine_chunks_dir).glob("*.json"):
            with open(chunk_file, 'r', encoding='utf-8') as f:
                chunk = json.load(f)
                self.fine_chunks[chunk['id']] = chunk
        
        print(f"Loaded {len(self.fine_chunks)} fine-grained chunks")
    
    def _group_chunks_by_function(self):
        """Group chunks by their parent function."""
        for chunk in self.fine_chunks.values():
            parent_func = chunk.get('parent_function', 'global')
            if parent_func not in self.function_chunks:
                self.function_chunks[parent_func] = []
            self.function_chunks[parent_func].append(chunk)
        
        # Sort chunks within each function by line number
        for func_name, chunks in self.function_chunks.items():
            chunks.sort(key=lambda c: c.get('line_range', {}).get('start', 0))
        
        print(f"Grouped chunks into {len(self.function_chunks)} functions")
    
    def create_coarse_chunks(self):
        """Create coarse-grained chunks from fine-grained ones."""
        for func_name, chunks in self.function_chunks.items():
            if func_name == 'global':
                # Handle global chunks individually
                for chunk in chunks:
                    self._create_coarse_chunk([chunk], "global_declaration")
            else:
                # Process function chunks with coarse-grained logic
                self._process_function_chunks(func_name, chunks)
        
        return self.coarse_chunks
    
    def _process_function_chunks(self, func_name: str, chunks: List[Dict]):
        """Process chunks for a single function, creating coarse-grained logical blocks."""
        i = 0
        while i < len(chunks):
            # Analyze the chunk group starting at position i
            chunk_group, complexity = self._analyze_chunk_group(chunks, i)
            
            if complexity == "simple_sequence":
                # Group multiple simple consecutive chunks
                group_end = self._find_simple_sequence_end(chunks, i)
                coarse_chunk = self._create_coarse_chunk(
                    chunks[i:group_end + 1], 
                    "simple_sequence"
                )
                i = group_end + 1
            
            elif complexity == "control_structure":
                # Keep control structures as complete logical blocks
                group_end = self._find_control_structure_end(chunks, i)
                coarse_chunk = self._create_coarse_chunk(
                    chunks[i:group_end + 1], 
                    "control_structure"
                )
                i = group_end + 1
            
            elif complexity == "goto_structure":
                # Special handling for GOTO - needs restructuring
                group_end = self._find_goto_structure_end(chunks, i)
                coarse_chunk = self._create_coarse_chunk(
                    chunks[i:group_end + 1], 
                    "goto_structure"
                )
                # Add special conversion notes for GOTO restructuring
                coarse_chunk['conversion_notes']['requires_restructuring'] = True
                coarse_chunk['conversion_notes']['goto_conversion_strategy'] = self._analyze_goto_pattern(chunks[i:group_end + 1])
                i = group_end + 1
            
            elif complexity == "complex_statement":
                # Keep complex statements as individual chunks
                coarse_chunk = self._create_coarse_chunk([chunks[i]], "complex_statement")
                i += 1
            
            else:
                # Default: keep as individual chunk
                coarse_chunk = self._create_coarse_chunk([chunks[i]], "unknown")
                i += 1
    
    def _analyze_chunk_group(self, chunks: List[Dict], start_idx: int) -> Tuple[List[Dict], str]:
        """Analyze a group of chunks to determine complexity level."""
        if start_idx >= len(chunks):
            return [], "empty"
        
        chunk = chunks[start_idx]
        text = chunk.get('text', '')
        chunk_type = chunk.get('type', '')
        
        # Check for GOTO statements
        if re.search(r'\bgoto\b|\blabel\b|^\s*\w+\s*:', text, re.IGNORECASE):
            return [chunk], "goto_structure"
        
        # Check for control structures
        if any(keyword in chunk_type for keyword in ['if_statement', 'for_loop', 'while_loop', 'switch_statement']):
            return [chunk], "control_structure"
        
        # Check for complex statements
        if self._is_complex_statement(text):
            return [chunk], "complex_statement"
        
        # Default to simple sequence
        return [chunk], "simple_sequence"
    
    def _is_complex_statement(self, text: str) -> bool:
        """Determine if a statement is complex enough to warrant its own chunk."""
        complexity_indicators = [
            r'->',  # Pointer dereference
            r'::', # Namespace/class access
            r'\bmalloc\b|\bfree\b|\bnew\b|\bdelete\b',  # Memory management
            r'\bsizeof\b|\bstatic_cast\b|\bconst_cast\b',  # C++ specific
            r'\btemplate\b|\btypename\b',  # Templates
            r'\bunion\b|\bvolatile\b|\bregister\b',  # Complex types
            r'\.\.\.',  # Variable arguments
            r'\([^)]*\*[^)]*\)\s*\(',  # Function pointers
        ]
        
        complexity_score = 0
        for pattern in complexity_indicators:
            if re.search(pattern, text, re.IGNORECASE):
                complexity_score += 1
        
        # Also consider line count and nested structures
        line_count = text.count('\n') + 1
        if line_count > 10:
            complexity_score += 2
        
        nested_braces = text.count('{') + text.count('}')
        if nested_braces > 4:
            complexity_score += 1
        
        return complexity_score >= 2
    
    def _find_simple_sequence_end(self, chunks: List[Dict], start_idx: int) -> int:
        """Find the end of a simple sequence of statements."""
        max_group_size = 15  # Maximum statements to group together
        max_lines = 50       # Maximum total lines in a group
        
        end_idx = start_idx
        total_lines = 0
        
        for i in range(start_idx, min(start_idx + max_group_size, len(chunks))):
            chunk = chunks[i]
            text = chunk.get('text', '')
            
            # Stop if we hit a control structure
            if self._analyze_chunk_group(chunks, i)[1] != "simple_sequence":
                break
            
            # Stop if we exceed line limit
            chunk_lines = text.count('\n') + 1
            if total_lines + chunk_lines > max_lines:
                break
            
            # Stop if chunk is too complex
            if self._is_complex_statement(text):
                break
            
            total_lines += chunk_lines
            end_idx = i
        
        return end_idx
    
    def _find_control_structure_end(self, chunks: List[Dict], start_idx: int) -> int:
        """Find the end of a control structure block."""
        # For now, keep control structures as individual chunks
        # In a more sophisticated implementation, we could parse
        # matching braces to group entire if/else blocks
        return start_idx
    
    def _find_goto_structure_end(self, chunks: List[Dict], start_idx: int) -> int:
        """Find the end of a GOTO structure that needs restructuring."""
        # Find related GOTO and label chunks
        end_idx = start_idx
        
        # Look ahead for related labels or gotos
        for i in range(start_idx + 1, min(start_idx + 20, len(chunks))):
            chunk = chunks[i]
            text = chunk.get('text', '')
            
            if re.search(r'\bgoto\b|\blabel\b|^\s*\w+\s*:', text, re.IGNORECASE):
                end_idx = i
            else:
                break
        
        return end_idx
    
    def _analyze_goto_pattern(self, chunks: List[Dict]) -> str:
        """Analyze GOTO pattern to suggest restructuring strategy."""
        goto_pattern = "unknown"
        
        # Combine all text to analyze pattern
        combined_text = '\n'.join(chunk.get('text', '') for chunk in chunks)
        
        if re.search(r'goto.*error|goto.*cleanup|goto.*exit', combined_text, re.IGNORECASE):
            goto_pattern = "error_handling"
        elif re.search(r'goto.*loop|goto.*continue', combined_text, re.IGNORECASE):
            goto_pattern = "loop_control"
        elif re.search(r'goto.*end|goto.*done', combined_text, re.IGNORECASE):
            goto_pattern = "early_exit"
        else:
            goto_pattern = "complex_flow"
        
        return goto_pattern
    
    def _create_coarse_chunk(self, fine_chunks: List[Dict], chunk_type: str) -> Dict:
        """Create a coarse-grained chunk from multiple fine-grained chunks."""
        if not fine_chunks:
            return {}
        
        first_chunk = fine_chunks[0]
        last_chunk = fine_chunks[-1]
        
        # Combine text from all chunks
        combined_text = '\n'.join(chunk.get('text', '') for chunk in fine_chunks)
        
        # Calculate line range
        start_line = first_chunk.get('line_range', {}).get('start', 0)
        end_line = last_chunk.get('line_range', {}).get('end', 0)
        
        # Collect all relationships
        all_variables_used = {}
        all_methods_called = []
        all_pointer_operations = []
        
        for chunk in fine_chunks:
            relationships = chunk.get('relationships', {})
            
            # Merge variables used
            variables_used = relationships.get('variables_used', {})
            for scope_type, var_list in variables_used.items():
                if scope_type not in all_variables_used:
                    all_variables_used[scope_type] = []
                all_variables_used[scope_type].extend(var_list)
            
            # Merge method calls
            all_methods_called.extend(relationships.get('methods_called', []))
            
            # Merge pointer operations
            all_pointer_operations.extend(relationships.get('pointer_operations', []))
        
        # Remove duplicates
        for scope_type, var_list in all_variables_used.items():
            seen = set()
            unique_vars = []
            for var in var_list:
                var_key = var.get('name', '')
                if var_key not in seen:
                    seen.add(var_key)
                    unique_vars.append(var)
            all_variables_used[scope_type] = unique_vars
        
        # Remove duplicate method calls
        seen_methods = set()
        unique_methods = []
        for method in all_methods_called:
            method_key = f"{method.get('object', '')}.{method.get('method', '')}"
            if method_key not in seen_methods:
                seen_methods.add(method_key)
                unique_methods.append(method)
        
        # Assess complexity of the combined chunk
        complexity = self._assess_combined_complexity(combined_text, len(fine_chunks))
        
        # Create coarse chunk
        coarse_chunk = {
            "id": f"coarse_{self.chunk_counter}",
            "type": f"coarse_{chunk_type}",
            "parent_function": first_chunk.get('parent_function', ''),
            "context": first_chunk.get('context', ''),
            "text": combined_text,
            "line_range": {
                "start": start_line,
                "end": end_line
            },
            "fine_chunk_ids": [chunk['id'] for chunk in fine_chunks],
            "chunk_count": len(fine_chunks),
            "relationships": {
                "variables_used": all_variables_used,
                "methods_called": unique_methods,
                "pointer_operations": all_pointer_operations,
                "scope_dependencies": self._analyze_combined_scope_dependencies(fine_chunks),
                "data_flow": self._analyze_combined_data_flow(combined_text),
                "control_flow": self._analyze_combined_control_flow(combined_text)
            },
            "conversion_notes": {
                "complexity": complexity,
                "chunking_strategy": chunk_type,
                "c_specific_constructs": self._identify_combined_c_constructs(combined_text),
                "kotlin_suggestions": self._suggest_combined_kotlin_patterns(combined_text),
                "potential_issues": self._identify_combined_potential_issues(combined_text),
                "null_safety_concerns": self._identify_combined_null_safety_concerns(all_pointer_operations),
                "memory_safety_notes": self._identify_combined_memory_safety_notes(combined_text),
                "logical_cohesion": self._assess_logical_cohesion(fine_chunks)
            },
            "conversion_priority": self._assess_coarse_conversion_priority(chunk_type, complexity),
            "related_chunks": self._find_coarse_related_chunks(fine_chunks)
        }
        
        self.coarse_chunks.append(coarse_chunk)
        self.chunk_counter += 1
        
        return coarse_chunk
    
    def _assess_combined_complexity(self, combined_text: str, chunk_count: int) -> str:
        """Assess complexity of combined chunk."""
        # Base complexity from individual assessment
        base_complexity = self._assess_text_complexity(combined_text)
        
        # Adjust based on chunk count and logical cohesion
        if chunk_count > 10:
            if base_complexity == "low":
                base_complexity = "medium"
            elif base_complexity == "medium":
                base_complexity = "high"
        
        return base_complexity
    
    def _assess_text_complexity(self, text: str) -> str:
        """Assess text complexity based on content."""
        complexity_indicators = [
            (r'\bgoto\b', 3), (r'->', 2), (r'::', 2), (r'\btemplate\b', 3),
            (r'\bunion\b', 3), (r'\bsizeof\b', 2), (r'#define', 3), 
            (r'\bmalloc\b|\bfree\b', 2), (r'\bvolatile\b|\bregister\b', 3),
            (r'\.\.\.|#ifdef|#ifndef', 3), (r'static_cast|const_cast', 2)
        ]
        
        score = 0
        for pattern, weight in complexity_indicators:
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            score += matches * weight
        
        # Consider line count and nesting
        line_count = text.count('\n') + 1
        if line_count > 50:
            score += 3
        elif line_count > 20:
            score += 1
        
        nested_braces = text.count('{') + text.count('}')
        score += nested_braces // 4
        
        if score >= 8:
            return "high"
        elif score >= 3:
            return "medium"
        else:
            return "low"
    
    def _analyze_combined_scope_dependencies(self, fine_chunks: List[Dict]) -> Dict[str, Any]:
        """Analyze combined scope dependencies."""
        requires_local = any(chunk.get('relationships', {}).get('scope_dependencies', {}).get('requires_local_scope', False) for chunk in fine_chunks)
        requires_global = any(chunk.get('relationships', {}).get('scope_dependencies', {}).get('requires_global_scope', False) for chunk in fine_chunks)
        requires_class = any(chunk.get('relationships', {}).get('scope_dependencies', {}).get('requires_class_scope', False) for chunk in fine_chunks)
        
        return {
            "requires_local_scope": requires_local,
            "requires_global_scope": requires_global,
            "requires_class_scope": requires_class,
            "function_context": fine_chunks[0].get('parent_function', '') if fine_chunks else ''
        }
    
    def _analyze_combined_data_flow(self, combined_text: str) -> Dict[str, Any]:
        """Analyze combined data flow."""
        reads = set(re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*[^=]', combined_text))
        writes = set(re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=', combined_text))
        
        side_effect_functions = ['printf', 'strcpy', 'strcat', 'malloc', 'free']
        has_side_effects = any(func in combined_text for func in side_effect_functions)
        
        return {
            "reads_variables": list(reads),
            "writes_variables": list(writes),
            "has_side_effects": has_side_effects,
            "data_dependencies": len(reads & writes) > 0
        }
    
    def _analyze_combined_control_flow(self, combined_text: str) -> Dict[str, Any]:
        """Analyze combined control flow."""
        return {
            "is_conditional": any(keyword in combined_text for keyword in ['if', 'else', 'switch', 'case']),
            "is_loop": any(keyword in combined_text for keyword in ['for', 'while', 'do']),
            "has_return": 'return' in combined_text,
            "has_break": 'break' in combined_text,
            "has_continue": 'continue' in combined_text,
            "has_goto": 'goto' in combined_text.lower(),
            "control_complexity": self._assess_control_complexity(combined_text)
        }
    
    def _assess_control_complexity(self, text: str) -> str:
        """Assess control flow complexity."""
        control_keywords = ['if', 'else', 'for', 'while', 'switch', 'case', 'goto']
        control_count = sum(text.lower().count(keyword) for keyword in control_keywords)
        
        nesting_level = max(text.count('{'), text.count('}')) // 2
        
        if control_count > 5 or nesting_level > 3:
            return "high"
        elif control_count > 2 or nesting_level > 1:
            return "medium"
        else:
            return "low"
    
    def _identify_combined_c_constructs(self, combined_text: str) -> List[str]:
        """Identify C-specific constructs in combined text."""
        constructs = []
        
        construct_patterns = {
            "pointer_arithmetic": r'\*\s*\([^)]+\)\s*[+-]',
            "pointer_access": r'->',
            "manual_memory_management": r'\b(malloc|free|calloc|realloc)\b',
            "c_string_functions": r'\b(strcat|strcpy|strlen|strcmp|sprintf)\b',
            "goto_statement": r'\bgoto\b',
            "macro_usage": r'#\s*(define|ifdef|ifndef|endif)',
            "union_usage": r'\bunion\b',
            "bit_operations": r'[&|^~]',
            "type_casting": r'\([a-zA-Z_][a-zA-Z0-9_]*\s*\*?\)',
            "variable_arguments": r'\.\.\.',
            "function_pointers": r'\(\s*\*[^)]+\)\s*\('
        }
        
        for construct_name, pattern in construct_patterns.items():
            if re.search(pattern, combined_text):
                constructs.append(construct_name)
        
        return constructs
    
    def _suggest_combined_kotlin_patterns(self, combined_text: str) -> List[str]:
        """Suggest Kotlin patterns for combined C++ constructs."""
        suggestions = []
        
        if 'sprintf' in combined_text:
            suggestions.append("use_string_templates_for_formatting")
        if re.search(r'\bmalloc\b|\bnew\b', combined_text):
            suggestions.append("use_kotlin_collections_and_objects")
        if '->' in combined_text:
            suggestions.append("use_safe_call_operators")
        if re.search(r'\bstrcat\b|\bstrcpy\b', combined_text):
            suggestions.append("use_string_builder_or_concatenation")
        if 'goto' in combined_text.lower():
            suggestions.append("restructure_with_functions_and_early_returns")
        if re.search(r'\bfor\b.*\+\+', combined_text):
            suggestions.append("use_kotlin_ranges_and_iterators")
        
        return suggestions
    
    def _identify_combined_potential_issues(self, combined_text: str) -> List[str]:
        """Identify potential conversion issues in combined text."""
        issues = []
        
        if 'goto' in combined_text.lower():
            issues.append("goto_statements_need_restructuring")
        if '#define' in combined_text:
            issues.append("macros_need_manual_conversion")
        if 'union' in combined_text:
            issues.append("unions_have_no_direct_kotlin_equivalent")
        if re.search(r'\b(volatile|register)\b', combined_text):
            issues.append("storage_classes_not_applicable")
        if '...' in combined_text:
            issues.append("variable_arguments_need_special_handling")
        if re.search(r'\(\s*\*[^)]+\)\s*\(', combined_text):
            issues.append("function_pointers_need_lambda_conversion")
        if combined_text.count('\n') > 100:
            issues.append("large_block_may_need_further_decomposition")
        
        return issues
    
    def _identify_combined_null_safety_concerns(self, pointer_operations: List[Dict]) -> List[str]:
        """Identify null safety concerns from combined pointer operations."""
        concerns = []
        
        for op in pointer_operations:
            if op.get('operation') == 'dereference':
                concerns.append(f"null_check_needed_for_{op.get('variable', 'unknown')}")
            elif op.get('operation') == 'array_access':
                concerns.append(f"bounds_check_needed_for_{op.get('variable', 'unknown')}")
        
        # Remove duplicates
        return list(set(concerns))
    
    def _identify_combined_memory_safety_notes(self, combined_text: str) -> List[str]:
        """Identify memory safety notes for combined text."""
        notes = []
        
        if 'malloc' in combined_text:
            notes.append("manual_memory_allocation_converted_to_automatic")
        if 'free' in combined_text:
            notes.append("manual_deallocation_removed_automatic_gc")
        if '[' in combined_text and ']' in combined_text:
            notes.append("array_access_needs_bounds_checking")
        if '->' in combined_text:
            notes.append("pointer_dereference_needs_null_safety")
        if combined_text.count('*') > 5:  # Many pointer operations
            notes.append("heavy_pointer_usage_needs_careful_conversion")
        
        return notes
    
    def _assess_logical_cohesion(self, fine_chunks: List[Dict]) -> str:
        """Assess how logically cohesive the grouped chunks are."""
        if len(fine_chunks) <= 1:
            return "high"
        
        # Check if all chunks are in the same function
        functions = set(chunk.get('parent_function', '') for chunk in fine_chunks)
        if len(functions) > 1:
            return "low"
        
        # Check if chunks are sequential (no gaps in line numbers)
        line_numbers = []
        for chunk in fine_chunks:
            line_range = chunk.get('line_range', {})
            if 'start' in line_range and 'end' in line_range:
                line_numbers.extend(range(line_range['start'], line_range['end'] + 1))
        
        if line_numbers:
            line_numbers.sort()
            gaps = sum(1 for i in range(1, len(line_numbers)) if line_numbers[i] - line_numbers[i-1] > 1)
            if gaps > len(fine_chunks) // 3:  # Too many gaps
                return "medium"
        
        # Check if chunks share variables or method calls
        shared_elements = 0
        all_variables = set()
        all_methods = set()
        
        for chunk in fine_chunks:
            relationships = chunk.get('relationships', {})
            variables = relationships.get('variables_used', {})
            methods = relationships.get('methods_called', [])
            
            chunk_vars = set()
            for var_list in variables.values():
                chunk_vars.update(var.get('name', '') for var in var_list)
            
            chunk_methods = set(method.get('method', '') for method in methods)
            
            shared_elements += len(all_variables & chunk_vars)
            shared_elements += len(all_methods & chunk_methods)
            
            all_variables.update(chunk_vars)
            all_methods.update(chunk_methods)
        
        if shared_elements > len(fine_chunks):
            return "high"
        elif shared_elements > 0:
            return "medium"
        else:
            return "low"
    
    def _assess_coarse_conversion_priority(self, chunk_type: str, complexity: str) -> str:
        """Assess conversion priority for coarse chunk."""
        if chunk_type == "goto_structure":
            return "high"  # Requires immediate attention
        elif complexity == "high":
            return "high"
        elif chunk_type in ["control_structure", "complex_statement"]:
            return "medium"
        else:
            return "low"
    
    def _find_coarse_related_chunks(self, fine_chunks: List[Dict]) -> List[str]:
        """Find related chunks for coarse chunk."""
        related = set()
        
        for chunk in fine_chunks:
            related.update(chunk.get('related_chunks', []))
        
        # Remove chunks that are already part of this coarse chunk
        chunk_ids = set(chunk['id'] for chunk in fine_chunks)
        related -= chunk_ids
        
        return list(related)
    
    def save_coarse_chunks(self, output_dir: str):
        """Save coarse-grained chunks to output directory."""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        for chunk in self.coarse_chunks:
            output_file = Path(output_dir) / f"{chunk['id']}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(chunk, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(self.coarse_chunks)} coarse-grained chunks to {output_dir}")
    
    def create_coarse_summary(self, output_file: str):
        """Create summary of coarse chunking results."""
        summary = {
            "chunking_summary": {
                "total_fine_chunks": len(self.fine_chunks),
                "total_coarse_chunks": len(self.coarse_chunks),
                "compression_ratio": len(self.fine_chunks) / len(self.coarse_chunks) if self.coarse_chunks else 0,
                "functions_processed": len(self.function_chunks)
            },
            "chunk_type_distribution": {},
            "complexity_distribution": {},
            "chunking_strategy_distribution": {},
            "conversion_priority_distribution": {},
            "potential_issues_summary": {},
            "goto_structures_found": []
        }
        
        # Analyze chunk distributions
        for chunk in self.coarse_chunks:
            chunk_type = chunk.get('type', 'unknown')
            complexity = chunk.get('conversion_notes', {}).get('complexity', 'unknown')
            strategy = chunk.get('conversion_notes', {}).get('chunking_strategy', 'unknown')
            priority = chunk.get('conversion_priority', 'unknown')
            
            # Update distributions
            summary["chunk_type_distribution"][chunk_type] = summary["chunk_type_distribution"].get(chunk_type, 0) + 1
            summary["complexity_distribution"][complexity] = summary["complexity_distribution"].get(complexity, 0) + 1
            summary["chunking_strategy_distribution"][strategy] = summary["chunking_strategy_distribution"].get(strategy, 0) + 1
            summary["conversion_priority_distribution"][priority] = summary["conversion_priority_distribution"].get(priority, 0) + 1
            
            # Collect potential issues
            issues = chunk.get('conversion_notes', {}).get('potential_issues', [])
            for issue in issues:
                summary["potential_issues_summary"][issue] = summary["potential_issues_summary"].get(issue, 0) + 1
            
            # Collect GOTO structures
            if 'goto' in chunk_type.lower() or any('goto' in issue for issue in issues):
                summary["goto_structures_found"].append({
                    "chunk_id": chunk['id'],
                    "function": chunk.get('parent_function', ''),
                    "strategy": chunk.get('conversion_notes', {}).get('goto_conversion_strategy', 'unknown')
                })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"Created coarse chunking summary at {output_file}")
        return summary


def main():
    parser = argparse.ArgumentParser(description="Create coarse-grained chunks from fine-grained ones")
    parser.add_argument("--fine-chunks-dir", required=True, help="Directory containing fine-grained chunks")
    parser.add_argument("--output-dir", required=True, help="Output directory for coarse-grained chunks")
    parser.add_argument("--summary-out", required=True, help="Output file for chunking summary")
    
    args = parser.parse_args()
    
    # Create coarse-grained chunker
    chunker = CoarseGrainedChunker(args.fine_chunks_dir)
    coarse_chunks = chunker.create_coarse_chunks()
    
    # Save results
    chunker.save_coarse_chunks(args.output_dir)
    summary = chunker.create_coarse_summary(args.summary_out)
    
    print(f"\nCoarse chunking complete!")
    print(f"Converted {summary['chunking_summary']['total_fine_chunks']} fine chunks into {summary['chunking_summary']['total_coarse_chunks']} coarse chunks")
    print(f"Compression ratio: {summary['chunking_summary']['compression_ratio']:.2f}x")
    print(f"Functions processed: {summary['chunking_summary']['functions_processed']}")
    
    if summary['goto_structures_found']:
        print(f"\nFound {len(summary['goto_structures_found'])} GOTO structures requiring special handling")
    
    print(f"\nComplexity distribution:")
    for complexity, count in summary['complexity_distribution'].items():
        print(f"  {complexity}: {count} chunks")


if __name__ == "__main__":
    main()