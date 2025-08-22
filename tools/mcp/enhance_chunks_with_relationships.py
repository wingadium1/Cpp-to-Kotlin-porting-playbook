#!/usr/bin/env python3
"""
Enhance Existing Chunks with Relationship Information

This script takes existing basic chunks and enhances them with relationship tracking
including variable scope, method calls, and pointer operations.
"""
import argparse
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Any, Set


class ChunkRelationshipEnhancer:
    def __init__(self, chunks_dir: str):
        self.chunks_dir = chunks_dir
        self.chunks: Dict[str, Dict] = {}
        self.enhanced_chunks: Dict[str, Dict] = {}
        
        # Relationship tracking
        self.global_variables: Dict[str, Dict] = {}
        self.class_members: Dict[str, Dict] = {}
        self.local_variables: Dict[str, Dict] = {}
        self.function_signatures: Dict[str, Dict] = {}
        self.method_calls: List[Dict] = []
        self.variable_usages: List[Dict] = []
        self.pointer_relationships: List[Dict] = []
        
        # Load all chunks
        self._load_chunks()
        
    def _load_chunks(self):
        """Load all chunk files from the directory."""
        for chunk_file in Path(self.chunks_dir).glob("*.json"):
            with open(chunk_file, 'r', encoding='utf-8') as f:
                chunk = json.load(f)
                self.chunks[chunk['id']] = chunk
        
        print(f"Loaded {len(self.chunks)} chunks for enhancement")
    
    def enhance_all_chunks(self):
        """Enhance all chunks with relationship information."""
        print("Building symbol tables...")
        self._build_symbol_tables()
        
        print("Enhancing chunks with relationships...")
        for chunk_id, chunk in self.chunks.items():
            self._enhance_chunk(chunk_id, chunk)
        
        print("Resolving cross-chunk relationships...")
        self._resolve_relationships()
        
        return self.enhanced_chunks
    
    def _build_symbol_tables(self):
        """Build symbol tables by analyzing all chunks."""
        # Phase 1: Find all function signatures
        for chunk_id, chunk in self.chunks.items():
            if chunk.get('type') == 'function_signature':
                self._extract_function_signature(chunk)
            elif 'parent_function' in chunk:
                parent_func = chunk['parent_function']
                if parent_func not in self.function_signatures:
                    self.function_signatures[parent_func] = {
                        "return_type": "unknown",
                        "parameters": [],
                        "definition_chunk": None
                    }
        
        # Phase 2: Analyze variable declarations and usage patterns
        for chunk_id, chunk in self.chunks.items():
            self._analyze_chunk_for_symbols(chunk_id, chunk)
    
    def _extract_function_signature(self, chunk: Dict):
        """Extract function signature information."""
        func_name = chunk.get('name', '')
        if func_name:
            self.function_signatures[func_name] = {
                "return_type": chunk.get('return_type', 'unknown'),
                "parameters": chunk.get('parameters', []),
                "definition_chunk": chunk['id'],
                "class": chunk.get('class_name'),
                "namespace": chunk.get('namespace')
            }
    
    def _analyze_chunk_for_symbols(self, chunk_id: str, chunk: Dict):
        """Analyze chunk text for symbol information."""
        text = chunk.get('text', '')
        parent_function = chunk.get('parent_function', '')
        context = chunk.get('context', '')
        
        # Extract variable declarations
        var_declarations = self._find_variable_declarations(text)
        for var_name, var_type in var_declarations:
            if parent_function:
                # Local variable
                self.local_variables[f"{parent_function}::{var_name}"] = {
                    "name": var_name,
                    "type": var_type,
                    "function": parent_function,
                    "definition_chunk": chunk_id
                }
            elif 'class' in context.lower():
                # Class member (heuristic)
                class_name = self._extract_class_name_from_context(context)
                if class_name:
                    self.class_members[f"{class_name}::{var_name}"] = {
                        "name": var_name,
                        "type": var_type,
                        "class": class_name,
                        "access": "private",  # Default assumption
                        "definition_chunk": chunk_id
                    }
            else:
                # Global variable
                self.global_variables[var_name] = {
                    "name": var_name,
                    "type": var_type,
                    "definition_chunk": chunk_id
                }
    
    def _find_variable_declarations(self, text: str) -> List[tuple]:
        """Find variable declarations in text."""
        declarations = []
        
        # Common C++ variable declaration patterns
        patterns = [
            r'\b(int|short|long|char|float|double|bool)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[=;,\[]',
            r'\b([A-Z][a-zA-Z0-9_]*)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[=;,\[]',  # Custom types
            r'\b(const\s+)?([a-zA-Z_][a-zA-Z0-9_]*)\s*\*\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*[=;,]',  # Pointers
            r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\[',  # Arrays
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            for match in matches:
                if isinstance(match, tuple):
                    if len(match) == 2:
                        var_type, var_name = match
                        declarations.append((var_name, var_type))
                    elif len(match) == 3:
                        # Handle const and pointer patterns
                        if match[0]:  # const prefix
                            var_type = f"{match[0]}{match[1]}"
                            var_name = match[2]
                        else:
                            var_type = match[1]
                            var_name = match[2]
                        declarations.append((var_name, var_type))
        
        return declarations
    
    def _extract_class_name_from_context(self, context: str) -> str:
        """Extract class name from context string."""
        # Look for class name patterns
        if '::' in context:
            parts = context.split('::')
            if len(parts) >= 2:
                return parts[0]
        return ""
    
    def _enhance_chunk(self, chunk_id: str, chunk: Dict):
        """Enhance a single chunk with relationship information."""
        text = chunk.get('text', '')
        parent_function = chunk.get('parent_function', '')
        
        # Create enhanced chunk
        enhanced = chunk.copy()
        
        # Extract relationships
        variables_used = self._extract_variables_from_text(text, parent_function)
        methods_called = self._extract_method_calls_from_text(text)
        pointer_operations = self._extract_pointer_operations_from_text(text)
        
        # Classify variables by scope
        classified_variables = self._classify_variables(variables_used, parent_function)
        
        # Add comprehensive relationship information
        enhanced['relationships'] = {
            "variables_used": classified_variables,
            "methods_called": methods_called,
            "pointer_operations": pointer_operations,
            "scope_dependencies": self._analyze_scope_dependencies(text, parent_function),
            "data_flow": self._analyze_data_flow(text),
            "control_flow": self._analyze_control_flow(text)
        }
        
        # Enhanced conversion notes
        enhanced['conversion_notes'] = {
            "complexity": self._assess_complexity(text),
            "c_specific_constructs": self._identify_c_constructs(text),
            "kotlin_suggestions": self._suggest_kotlin_patterns(text),
            "potential_issues": self._identify_potential_issues(text),
            "null_safety_concerns": self._identify_null_safety_concerns(pointer_operations),
            "memory_safety_notes": self._identify_memory_safety_notes(text)
        }
        
        # Add related chunks (will be populated in resolution phase)
        enhanced['related_chunks'] = []
        
        self.enhanced_chunks[chunk_id] = enhanced
    
    def _extract_variables_from_text(self, text: str, parent_function: str) -> Set[str]:
        """Extract variable names from text."""
        variables = set()
        
        # Variable usage patterns
        patterns = [
            r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*=',  # Assignment target
            r'=\s*([a-zA-Z_][a-zA-Z0-9_]*)\b',  # Assignment source
            r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\[',  # Array access
            r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\.',  # Member access
            r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*->',  # Pointer access
            r'\(&([a-zA-Z_][a-zA-Z0-9_]*)\)',  # Address-of
            r'\*([a-zA-Z_][a-zA-Z0-9_]*)\b',   # Dereference
            r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*[,;)]',  # General usage
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            variables.update(matches)
        
        # Filter out C++ keywords and common functions
        cpp_keywords = {
            'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'default',
            'return', 'break', 'continue', 'goto', 'int', 'char', 'short',
            'long', 'float', 'double', 'bool', 'void', 'const', 'static',
            'extern', 'auto', 'register', 'volatile', 'signed', 'unsigned',
            'struct', 'union', 'enum', 'class', 'public', 'private', 'protected',
            'virtual', 'inline', 'template', 'typename', 'namespace', 'using',
            'try', 'catch', 'throw', 'new', 'delete', 'sizeof', 'sizeof',
            'true', 'false', 'nullptr', 'NULL'
        }
        
        return {var for var in variables if var not in cpp_keywords and len(var) > 1}
    
    def _extract_method_calls_from_text(self, text: str) -> List[Dict]:
        """Extract method calls from text."""
        method_calls = []
        
        # Method call patterns
        patterns = [
            (r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', "function_call"),
            (r'([a-zA-Z_][a-zA-Z0-9_]*)->([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', "pointer_method_call"),
            (r'([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', "object_method_call"),
            (r'::([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', "static_call"),
        ]
        
        for pattern, call_type in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple) and len(match) == 2:
                    method_calls.append({
                        "object": match[0],
                        "method": match[1],
                        "call_type": call_type,
                        "library": self._identify_library(match[1])
                    })
                else:
                    method_calls.append({
                        "method": match,
                        "call_type": call_type,
                        "library": self._identify_library(match)
                    })
        
        return method_calls
    
    def _extract_pointer_operations_from_text(self, text: str) -> List[Dict]:
        """Extract pointer operations from text."""
        pointer_ops = []
        
        # Pointer operation patterns
        patterns = [
            (r'([a-zA-Z_][a-zA-Z0-9_]*)\s*->', "dereference"),
            (r'\*\s*([a-zA-Z_][a-zA-Z0-9_]*)', "dereference"),
            (r'&\s*([a-zA-Z_][a-zA-Z0-9_]*)', "address_of"),
            (r'&\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\[\s*([^\]]+)\s*\]', "array_address"),
            (r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\[\s*([^\]]+)\s*\]', "array_access"),
        ]
        
        for pattern, op_type in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    op_info = {
                        "variable": match[0],
                        "operation": op_type,
                        "context": text.strip()
                    }
                    if len(match) > 1:
                        op_info["index"] = match[1]
                    
                    # Add safety notes
                    if op_type in ["array_access", "array_address"]:
                        op_info["safety_notes"] = "array_bounds_check_needed"
                    elif op_type == "dereference":
                        op_info["safety_notes"] = "null_check_needed"
                    
                    pointer_ops.append(op_info)
                else:
                    pointer_ops.append({
                        "variable": match,
                        "operation": op_type,
                        "context": text.strip(),
                        "safety_notes": "null_check_needed" if op_type == "dereference" else ""
                    })
        
        return pointer_ops
    
    def _classify_variables(self, variables: Set[str], parent_function: str) -> Dict[str, List[Dict]]:
        """Classify variables by scope."""
        classified = {
            "local_variables": [],
            "class_members": [],
            "global_variables": [],
            "parameters": [],
            "unknown": []
        }
        
        for var in variables:
            # Check local variables
            local_key = f"{parent_function}::{var}"
            if local_key in self.local_variables:
                classified["local_variables"].append({
                    "name": var,
                    "type": self.local_variables[local_key]["type"],
                    "definition_chunk": self.local_variables[local_key]["definition_chunk"],
                    "usage_type": "read_write"
                })
                continue
            
            # Check class members (try different class names)
            found_as_member = False
            for member_key, member_info in self.class_members.items():
                if member_key.endswith(f"::{var}"):
                    classified["class_members"].append({
                        "name": var,
                        "type": member_info["type"],
                        "class": member_info["class"],
                        "access": member_info["access"],
                        "definition_chunk": member_info["definition_chunk"],
                        "member_path": member_key
                    })
                    found_as_member = True
                    break
            
            if found_as_member:
                continue
            
            # Check global variables
            if var in self.global_variables:
                classified["global_variables"].append({
                    "name": var,
                    "type": self.global_variables[var]["type"],
                    "definition_chunk": self.global_variables[var]["definition_chunk"]
                })
                continue
            
            # Check parameters
            is_parameter = False
            if parent_function in self.function_signatures:
                params = self.function_signatures[parent_function].get("parameters", [])
                for param in params:
                    if isinstance(param, dict) and param.get("name") == var:
                        classified["parameters"].append({
                            "name": var,
                            "type": param.get("type", "unknown")
                        })
                        is_parameter = True
                        break
            
            if not is_parameter:
                classified["unknown"].append({"name": var})
        
        return classified
    
    def _identify_library(self, method_name: str) -> str:
        """Identify library for method call."""
        string_functions = ['strcat', 'strcpy', 'strcmp', 'strlen', 'sprintf', 'strstr']
        stdio_functions = ['printf', 'scanf', 'fprintf', 'fscanf', 'fopen', 'fclose']
        stdlib_functions = ['malloc', 'free', 'atoi', 'atof', 'exit']
        
        if method_name in string_functions:
            return "string.h"
        elif method_name in stdio_functions:
            return "stdio.h"
        elif method_name in stdlib_functions:
            return "stdlib.h"
        else:
            return "user_defined"
    
    def _analyze_scope_dependencies(self, text: str, parent_function: str) -> Dict[str, Any]:
        """Analyze scope dependencies."""
        return {
            "requires_local_scope": bool(parent_function),
            "requires_global_scope": any(gvar in text for gvar in self.global_variables.keys()),
            "requires_class_scope": ('->' in text or '.' in text),
            "function_context": parent_function
        }
    
    def _analyze_data_flow(self, text: str) -> Dict[str, Any]:
        """Analyze data flow."""
        reads = re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*[^=]', text)
        writes = re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=', text)
        
        return {
            "reads_variables": list(set(reads)),
            "writes_variables": list(set(writes)),
            "has_side_effects": bool(writes or any(func in text for func in ['printf', 'strcpy', 'strcat']))
        }
    
    def _analyze_control_flow(self, text: str) -> Dict[str, Any]:
        """Analyze control flow."""
        return {
            "is_conditional": any(keyword in text for keyword in ['if', 'else', 'switch', 'case']),
            "is_loop": any(keyword in text for keyword in ['for', 'while', 'do']),
            "has_return": 'return' in text,
            "has_break": 'break' in text,
            "has_continue": 'continue' in text
        }
    
    def _assess_complexity(self, text: str) -> str:
        """Assess conversion complexity."""
        complexity_indicators = [
            ('goto', 3), ('->',  2), ('::',  2), ('template', 3),
            ('union', 3), ('sizeof', 2), ('#define', 3), ('malloc', 2),
            ('free', 2), ('cast', 2), ('volatile', 3), ('register', 3)
        ]
        
        score = 0
        for indicator, weight in complexity_indicators:
            if indicator in text:
                score += weight
        
        if score >= 6:
            return "high"
        elif score >= 3:
            return "medium"
        else:
            return "low"
    
    def _identify_c_constructs(self, text: str) -> List[str]:
        """Identify C-specific constructs."""
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
            if re.search(pattern, text):
                constructs.append(construct_name)
        
        return constructs
    
    def _suggest_kotlin_patterns(self, text: str) -> List[str]:
        """Suggest Kotlin patterns for C++ constructs."""
        suggestions = []
        
        if 'sprintf' in text:
            suggestions.append("use_string_templates")
        if 'malloc' in text or 'new' in text:
            suggestions.append("use_kotlin_collections")
        if '->' in text:
            suggestions.append("use_safe_call_operator")
        if 'strcat' in text or 'strcpy' in text:
            suggestions.append("use_string_builder")
        if any(func in text for func in ['printf', 'fprintf']):
            suggestions.append("use_println_or_logging")
        if 'goto' in text:
            suggestions.append("restructure_with_functions")
        if re.search(r'\b(malloc|free)\b', text):
            suggestions.append("use_automatic_memory_management")
        
        return suggestions
    
    def _identify_potential_issues(self, text: str) -> List[str]:
        """Identify potential conversion issues."""
        issues = []
        
        if 'goto' in text:
            issues.append("goto_statement_needs_restructuring")
        if '#define' in text:
            issues.append("macro_needs_manual_conversion")
        if 'union' in text:
            issues.append("union_has_no_direct_kotlin_equivalent")
        if re.search(r'\b(volatile|register)\b', text):
            issues.append("storage_class_not_applicable")
        if '...' in text:
            issues.append("variable_arguments_need_special_handling")
        if re.search(r'\(\s*\*[^)]+\)\s*\(', text):
            issues.append("function_pointers_need_lambda_conversion")
        
        return issues
    
    def _identify_null_safety_concerns(self, pointer_operations: List[Dict]) -> List[str]:
        """Identify null safety concerns from pointer operations."""
        concerns = []
        
        for op in pointer_operations:
            if op['operation'] == 'dereference':
                concerns.append(f"null_check_needed_for_{op['variable']}")
            elif op['operation'] == 'array_access':
                concerns.append(f"bounds_check_needed_for_{op['variable']}")
        
        return concerns
    
    def _identify_memory_safety_notes(self, text: str) -> List[str]:
        """Identify memory safety notes."""
        notes = []
        
        if 'malloc' in text:
            notes.append("manual_memory_allocation_converted_to_automatic")
        if 'free' in text:
            notes.append("manual_deallocation_removed_automatic_gc")
        if '[' in text and ']' in text:
            notes.append("array_access_needs_bounds_checking")
        if '->' in text:
            notes.append("pointer_dereference_needs_null_safety")
        
        return notes
    
    def _resolve_relationships(self):
        """Resolve cross-chunk relationships."""
        for chunk_id, chunk in self.enhanced_chunks.items():
            related_chunks = []
            
            # Find chunks that define variables used in this chunk
            variables_used = chunk.get('relationships', {}).get('variables_used', {})
            for scope_type, var_list in variables_used.items():
                for var_info in var_list:
                    def_chunk = var_info.get('definition_chunk')
                    if def_chunk and def_chunk != chunk_id:
                        related_chunks.append(def_chunk)
            
            # Find chunks that call methods defined in this chunk
            # Find chunks in the same function
            parent_func = chunk.get('parent_function')
            if parent_func:
                for other_id, other_chunk in self.enhanced_chunks.items():
                    if (other_id != chunk_id and 
                        other_chunk.get('parent_function') == parent_func):
                        related_chunks.append(other_id)
            
            chunk['related_chunks'] = list(set(related_chunks))
    
    def save_enhanced_chunks(self, output_dir: str):
        """Save enhanced chunks to output directory."""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        for chunk_id, chunk in self.enhanced_chunks.items():
            output_file = Path(output_dir) / f"{chunk_id}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(chunk, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(self.enhanced_chunks)} enhanced chunks to {output_dir}")
    
    def save_relationships(self, output_file: str):
        """Save relationship information."""
        relationships = {
            "global_variables": self.global_variables,
            "class_members": self.class_members,
            "local_variables": self.local_variables,
            "function_signatures": self.function_signatures,
            "method_calls": self.method_calls,
            "variable_usages": self.variable_usages,
            "pointer_relationships": self.pointer_relationships,
            "summary": {
                "total_chunks": len(self.enhanced_chunks),
                "functions_found": len(self.function_signatures),
                "global_vars_found": len(self.global_variables),
                "class_members_found": len(self.class_members),
                "local_vars_found": len(self.local_variables)
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(relationships, f, indent=2, ensure_ascii=False)
        
        print(f"Saved relationship data to {output_file}")
    
    def create_enhanced_skeleton(self, output_file: str):
        """Create enhanced skeleton with relationship information."""
        skeleton = {
            "class_name": "Test",
            "package_name": "com.example.converted",
            "imports": [
                "kotlin.collections.*",
                "kotlin.text.*",
                "java.util.*"
            ],
            "methods": [],
            "properties": [],
            "conversion_metadata": {
                "total_chunks": len(self.enhanced_chunks),
                "relationships_tracked": True,
                "conversion_approach": "relationship_aware",
                "functions_identified": list(self.function_signatures.keys()),
                "global_variables": list(self.global_variables.keys()),
                "class_members": list(self.class_members.keys())
            }
        }
        
        # Add method stubs based on function signatures
        for func_name, func_info in self.function_signatures.items():
            if func_name and '::' in func_name:
                class_name, method_name = func_name.split('::', 1)
                skeleton["methods"].append({
                    "name": self._to_kotlin_name(method_name),
                    "original_name": method_name,
                    "return_type": self._to_kotlin_type(func_info.get("return_type", "Unit")),
                    "parameters": [
                        {
                            "name": self._to_kotlin_name(p.get("name", "") if isinstance(p, dict) else str(p)),
                            "type": self._to_kotlin_type(p.get("type", "Any") if isinstance(p, dict) else "Any")
                        } for p in func_info.get("parameters", [])
                    ],
                    "definition_chunk": func_info.get("definition_chunk"),
                    "conversion_status": "pending"
                })
        
        # Add property stubs based on class members
        for member_key, member_info in self.class_members.items():
            if '::' in member_key:
                skeleton["properties"].append({
                    "name": self._to_kotlin_name(member_info["name"]),
                    "original_name": member_info["name"],
                    "type": self._to_kotlin_type(member_info["type"]),
                    "access": "private",  # Kotlin default
                    "definition_chunk": member_info.get("definition_chunk"),
                    "conversion_status": "pending"
                })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(skeleton, f, indent=2, ensure_ascii=False)
        
        print(f"Created enhanced skeleton at {output_file}")
    
    def _to_kotlin_name(self, cpp_name: str) -> str:
        """Convert C++ name to Kotlin naming convention."""
        if not cpp_name:
            return ""
        
        # Convert from snake_case or PascalCase to camelCase
        if '_' in cpp_name:
            parts = cpp_name.split('_')
            return parts[0].lower() + ''.join(word.capitalize() for word in parts[1:])
        elif cpp_name[0].isupper():
            return cpp_name[0].lower() + cpp_name[1:]
        else:
            return cpp_name
    
    def _to_kotlin_type(self, cpp_type: str) -> str:
        """Convert C++ type to Kotlin type."""
        type_mapping = {
            'int': 'Int',
            'short': 'Short',
            'long': 'Long',
            'char': 'Char',
            'float': 'Float',
            'double': 'Double',
            'bool': 'Boolean',
            'void': 'Unit',
            'string': 'String',
            'char*': 'String',
            'const char*': 'String'
        }
        
        # Handle pointers and arrays
        if '*' in cpp_type:
            base_type = cpp_type.replace('*', '').replace('const', '').strip()
            kotlin_base = type_mapping.get(base_type, base_type.capitalize())
            return f"{kotlin_base}?"  # Nullable in Kotlin
        elif '[' in cpp_type:
            base_type = cpp_type.split('[')[0].strip()
            kotlin_base = type_mapping.get(base_type, base_type.capitalize())
            return f"Array<{kotlin_base}>"
        else:
            return type_mapping.get(cpp_type, cpp_type.capitalize())


def main():
    parser = argparse.ArgumentParser(description="Enhance existing chunks with relationship information")
    parser.add_argument("--chunks-dir", required=True, help="Directory containing existing chunks")
    parser.add_argument("--output-dir", required=True, help="Output directory for enhanced chunks")
    parser.add_argument("--relationships-out", required=True, help="Output relationships JSON file")
    parser.add_argument("--skeleton-out", required=True, help="Output enhanced skeleton JSON file")
    
    args = parser.parse_args()
    
    # Create enhancer and process chunks
    enhancer = ChunkRelationshipEnhancer(args.chunks_dir)
    enhanced_chunks = enhancer.enhance_all_chunks()
    
    # Save results
    enhancer.save_enhanced_chunks(args.output_dir)
    enhancer.save_relationships(args.relationships_out)
    enhancer.create_enhanced_skeleton(args.skeleton_out)
    
    print(f"\nEnhancement complete!")
    print(f"Enhanced {len(enhanced_chunks)} chunks")
    print(f"Found {len(enhancer.function_signatures)} function signatures")
    print(f"Found {len(enhancer.global_variables)} global variables")
    print(f"Found {len(enhancer.class_members)} class members")
    print(f"Found {len(enhancer.local_variables)} local variables")


if __name__ == "__main__":
    main()