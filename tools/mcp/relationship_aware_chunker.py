#!/usr/bin/env python3
"""
Enhanced Relationship-Aware LST Chunker for C++ to Kotlin Conversion

This chunker maintains crucial relationships between code chunks including:
- Local vs global variable scope
- Method call relationships
- Class member access patterns
- Pointer and reference relationships
- Cross-chunk dependencies
"""
import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Set
import re


class RelationshipAwareLSTChunker:
    def __init__(self, lst_data: Dict[str, Any]):
        self.lst = lst_data
        self.chunks: List[Dict[str, Any]] = []
        self.skeleton_info: Dict[str, Any] = {}
        self.chunk_counter = 0
        
        # Relationship tracking
        self.global_variables: Dict[str, Dict] = {}      # name -> {type, scope, definition_chunk}
        self.class_members: Dict[str, Dict] = {}         # name -> {type, class, access, definition_chunk}
        self.local_variables: Dict[str, Dict] = {}       # name -> {type, function, definition_chunk}
        self.function_signatures: Dict[str, Dict] = {}   # name -> {return_type, parameters, definition_chunk}
        self.method_calls: List[Dict] = []               # [{caller_chunk, callee, relationship}]
        self.variable_usages: List[Dict] = []            # [{chunk, variable, usage_type, scope}]
        self.pointer_relationships: List[Dict] = []      # [{chunk, pointer, target, operation}]
        self.include_dependencies: List[str] = []        # Include files needed
        
        # Context tracking
        self.current_class: Optional[str] = None
        self.current_function: Optional[str] = None
        self.current_namespace: Optional[str] = None
        self.scope_stack: List[Dict] = []                # Stack of nested scopes
        
    def chunk(self) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Split LST into relationship-aware chunks."""
        # Phase 1: Extract skeleton and build symbol tables
        self._extract_skeleton_info()
        self._build_symbol_tables()
        
        # Phase 2: Create chunks with relationship context
        self._create_relationship_aware_chunks()
        
        # Phase 3: Resolve and link relationships
        self._resolve_relationships()
        
        return self.chunks, self.skeleton_info
    
    def _extract_skeleton_info(self):
        """Extract structural information for skeleton generation."""
        self.skeleton_info = {
            "includes": self._find_includes(),
            "namespaces": self._find_namespaces(),
            "classes": self._find_class_declarations(),
            "functions": self._find_function_signatures(),
            "enums": self._find_enums(),
            "typedefs": self._find_typedefs(),
            "global_variables": self._find_global_variables(),
            "relationships": {
                "variable_scopes": {},
                "method_dependencies": {},
                "class_hierarchies": {}
            }
        }
    
    def _build_symbol_tables(self):
        """Build comprehensive symbol tables for relationship tracking."""
        nodes = self.lst.get("nodes", [])
        if nodes:
            for node in nodes:
                self._analyze_node_for_symbols(node)
    
    def _analyze_node_for_symbols(self, node: Dict[str, Any]):
        """Analyze a node to extract symbol information."""
        node_type = node.get("type", "")
        
        if node_type == "class_declaration":
            self._process_class_declaration(node)
        elif node_type == "function_declaration":
            self._process_function_declaration(node)
        elif node_type == "variable_declaration":
            self._process_variable_declaration(node)
        elif node_type == "member_variable_declaration":
            self._process_member_variable_declaration(node)
            
        # Recursively process children
        for child in node.get("children", []):
            self._analyze_node_for_symbols(child)
    
    def _process_class_declaration(self, node: Dict[str, Any]):
        """Process class declaration and extract member information."""
        class_name = node.get("name", "")
        if class_name:
            self.current_class = class_name
            
            # Extract class members
            for child in node.get("children", []):
                if child.get("type") == "member_variable_declaration":
                    self._process_member_variable_declaration(child)
                elif child.get("type") == "method_declaration":
                    self._process_method_declaration(child)
    
    def _process_function_declaration(self, node: Dict[str, Any]):
        """Process function declaration and extract signature."""
        func_name = node.get("name", "")
        if func_name:
            self.function_signatures[func_name] = {
                "return_type": node.get("return_type", "void"),
                "parameters": node.get("parameters", []),
                "class": self.current_class,
                "namespace": self.current_namespace,
                "definition_chunk": None  # Will be set when chunk is created
            }
    
    def _process_variable_declaration(self, node: Dict[str, Any]):
        """Process variable declaration and determine scope."""
        var_name = node.get("name", "")
        var_type = node.get("type", "")
        
        if var_name and var_type:
            if self.current_function:
                # Local variable
                self.local_variables[var_name] = {
                    "type": var_type,
                    "function": self.current_function,
                    "class": self.current_class,
                    "definition_chunk": None
                }
            else:
                # Global variable
                self.global_variables[var_name] = {
                    "type": var_type,
                    "namespace": self.current_namespace,
                    "definition_chunk": None
                }
    
    def _process_member_variable_declaration(self, node: Dict[str, Any]):
        """Process class member variable declaration."""
        var_name = node.get("name", "")
        var_type = node.get("type", "")
        access = node.get("access", "private")
        
        if var_name and var_type and self.current_class:
            self.class_members[f"{self.current_class}::{var_name}"] = {
                "type": var_type,
                "class": self.current_class,
                "access": access,
                "definition_chunk": None
            }
    
    def _process_method_declaration(self, node: Dict[str, Any]):
        """Process class method declaration."""
        method_name = node.get("name", "")
        if method_name and self.current_class:
            full_method_name = f"{self.current_class}::{method_name}"
            self.function_signatures[full_method_name] = {
                "return_type": node.get("return_type", "void"),
                "parameters": node.get("parameters", []),
                "class": self.current_class,
                "access": node.get("access", "private"),
                "definition_chunk": None
            }
    
    def _create_relationship_aware_chunks(self):
        """Create chunks with comprehensive relationship tracking."""
        nodes = self.lst.get("nodes", [])
        if nodes:
            for node in nodes:
                self._process_node_with_relationships(node)
    
    def _process_node_with_relationships(self, node: Dict[str, Any]):
        """Process node and create chunks with relationship information."""
        node_type = node.get("type", "")
        
        if node_type == "function_declaration":
            self._create_function_signature_chunk(node)
        elif node_type in ["function_body", "method_body"]:
            self._create_function_body_chunks(node)
        elif node_type == "class_declaration":
            self._create_class_chunks(node)
        elif node_type == "variable_declaration":
            self._create_variable_declaration_chunk(node)
            
        # Recursively process children
        for child in node.get("children", []):
            self._process_node_with_relationships(child)
    
    def _create_function_signature_chunk(self, node: Dict[str, Any]):
        """Create function signature chunk with parameter relationships."""
        func_name = node.get("name", "")
        parameters = node.get("parameters", [])
        
        chunk = {
            "id": f"func_sig_{self.chunk_counter}",
            "type": "function_signature",
            "name": func_name,
            "context": self._get_current_context(),
            "signature": node.get("signature", ""),
            "return_type": node.get("return_type", "void"),
            "parameters": parameters,
            "class_name": self.current_class,
            "namespace": self.current_namespace,
            "span": node.get("span", {}),
            "relationships": {
                "parameter_types": [p.get("type") for p in parameters],
                "parameter_names": [p.get("name") for p in parameters],
                "requires_includes": self._extract_required_includes(node),
                "class_dependencies": self._extract_class_dependencies(node),
                "template_dependencies": self._extract_template_dependencies(node)
            },
            "conversion_priority": "high"
        }
        
        self.chunks.append(chunk)
        
        # Update function signature registry
        if func_name in self.function_signatures:
            self.function_signatures[func_name]["definition_chunk"] = chunk["id"]
        
        self.chunk_counter += 1
    
    def _create_function_body_chunks(self, node: Dict[str, Any]):
        """Create function body chunks with variable and method call relationships."""
        func_name = node.get("parent_function", "")
        self.current_function = func_name
        
        # Extract statements and create detailed chunks
        statements = node.get("statements", [])
        for i, stmt in enumerate(statements):
            self._create_statement_chunk(stmt, i)
    
    def _create_statement_chunk(self, stmt: Dict[str, Any], index: int):
        """Create a statement chunk with comprehensive relationship tracking."""
        stmt_text = stmt.get("text", "")
        stmt_type = self._classify_statement(stmt_text)
        
        # Analyze statement for relationships
        variables_used = self._extract_variables_from_statement(stmt_text)
        methods_called = self._extract_method_calls_from_statement(stmt_text)
        pointers_used = self._extract_pointer_operations_from_statement(stmt_text)
        
        chunk = {
            "id": f"body_{self.chunk_counter}",
            "type": f"function_body_{stmt_type}",
            "parent_function": self.current_function,
            "context": self._get_current_context(),
            "text": stmt_text,
            "line_range": stmt.get("line_range", {}),
            "statement_index": index,
            "relationships": {
                "variables_used": self._classify_variable_usage(variables_used),
                "methods_called": methods_called,
                "pointer_operations": pointers_used,
                "scope_dependencies": self._analyze_scope_dependencies(stmt_text),
                "data_flow": self._analyze_data_flow(stmt_text),
                "control_flow": self._analyze_control_flow(stmt_text)
            },
            "dependencies": self._extract_dependencies(stmt_text),
            "conversion_notes": {
                "complexity": self._assess_complexity(stmt_text),
                "c_specific_constructs": self._identify_c_constructs(stmt_text),
                "kotlin_suggestions": self._suggest_kotlin_patterns(stmt_text),
                "potential_issues": self._identify_potential_issues(stmt_text)
            },
            "conversion_priority": self._assess_conversion_priority(stmt_type, stmt_text)
        }
        
        self.chunks.append(chunk)
        
        # Record relationships for resolution phase
        self._record_chunk_relationships(chunk, variables_used, methods_called, pointers_used)
        
        self.chunk_counter += 1
    
    def _classify_variable_usage(self, variables: List[str]) -> Dict[str, Dict]:
        """Classify variables by scope and usage type."""
        classified = {
            "local_variables": [],
            "class_members": [],
            "global_variables": [],
            "parameters": [],
            "unknown": []
        }
        
        for var in variables:
            if var in self.local_variables:
                classified["local_variables"].append({
                    "name": var,
                    "type": self.local_variables[var]["type"],
                    "definition_scope": self.local_variables[var]["function"]
                })
            elif f"{self.current_class}::{var}" in self.class_members:
                classified["class_members"].append({
                    "name": var,
                    "type": self.class_members[f"{self.current_class}::{var}"]["type"],
                    "access": self.class_members[f"{self.current_class}::{var}"]["access"]
                })
            elif var in self.global_variables:
                classified["global_variables"].append({
                    "name": var,
                    "type": self.global_variables[var]["type"],
                    "namespace": self.global_variables[var].get("namespace")
                })
            elif self._is_parameter(var):
                classified["parameters"].append({
                    "name": var,
                    "type": self._get_parameter_type(var)
                })
            else:
                classified["unknown"].append({"name": var})
        
        return classified
    
    def _extract_variables_from_statement(self, stmt: str) -> List[str]:
        """Extract variable names from a statement."""
        # This is a simplified implementation - would need more sophisticated parsing
        variables = []
        
        # Look for common variable patterns
        var_patterns = [
            r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*=',  # Assignment
            r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\[',  # Array access
            r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\.',  # Member access
            r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*->', # Pointer access
            r'\s([a-zA-Z_][a-zA-Z0-9_]*)\s*[,;)]',  # Variable usage
        ]
        
        for pattern in var_patterns:
            matches = re.findall(pattern, stmt)
            variables.extend(matches)
        
        # Remove duplicates and filter out keywords
        cpp_keywords = {'if', 'else', 'for', 'while', 'return', 'int', 'char', 'void', 'const'}
        return list(set(var for var in variables if var not in cpp_keywords))
    
    def _extract_method_calls_from_statement(self, stmt: str) -> List[Dict]:
        """Extract method calls from a statement."""
        method_calls = []
        
        # Pattern for function/method calls
        call_patterns = [
            r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',  # Simple function call
            r'([a-zA-Z_][a-zA-Z0-9_]*)->([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',  # Pointer method call
            r'([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',  # Object method call
            r'::([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',  # Namespace function call
        ]
        
        for pattern in call_patterns:
            matches = re.findall(pattern, stmt)
            for match in matches:
                if isinstance(match, tuple):
                    if len(match) == 2:  # Object.method or pointer->method
                        method_calls.append({
                            "object": match[0],
                            "method": match[1],
                            "call_type": "member_call"
                        })
                    else:
                        method_calls.append({
                            "method": match[0],
                            "call_type": "function_call"
                        })
                else:
                    method_calls.append({
                        "method": match,
                        "call_type": "function_call"
                    })
        
        return method_calls
    
    def _extract_pointer_operations_from_statement(self, stmt: str) -> List[Dict]:
        """Extract pointer operations from a statement."""
        pointer_ops = []
        
        # Pattern for pointer operations
        pointer_patterns = [
            (r'([a-zA-Z_][a-zA-Z0-9_]*)\s*->', "dereference"),
            (r'\*\s*([a-zA-Z_][a-zA-Z0-9_]*)', "dereference"),
            (r'&\s*([a-zA-Z_][a-zA-Z0-9_]*)', "address_of"),
            (r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\[\s*([^\]]+)\s*\]', "array_access"),
        ]
        
        for pattern, op_type in pointer_patterns:
            matches = re.findall(pattern, stmt)
            for match in matches:
                if isinstance(match, tuple):
                    pointer_ops.append({
                        "variable": match[0],
                        "operation": op_type,
                        "index": match[1] if len(match) > 1 else None
                    })
                else:
                    pointer_ops.append({
                        "variable": match,
                        "operation": op_type
                    })
        
        return pointer_ops
    
    def _resolve_relationships(self):
        """Resolve and cross-link relationships between chunks."""
        for chunk in self.chunks:
            self._resolve_chunk_relationships(chunk)
    
    def _resolve_chunk_relationships(self, chunk: Dict[str, Any]):
        """Resolve relationships for a specific chunk."""
        chunk_id = chunk["id"]
        relationships = chunk.get("relationships", {})
        
        # Resolve variable dependencies
        if "variables_used" in relationships:
            self._resolve_variable_dependencies(chunk_id, relationships["variables_used"])
        
        # Resolve method call dependencies
        if "methods_called" in relationships:
            self._resolve_method_dependencies(chunk_id, relationships["methods_called"])
        
        # Add cross-references to related chunks
        chunk["related_chunks"] = self._find_related_chunks(chunk)
    
    def _resolve_variable_dependencies(self, chunk_id: str, variables: Dict[str, List]):
        """Resolve variable dependencies and add definition references."""
        for scope_type, var_list in variables.items():
            for var_info in var_list:
                var_name = var_info["name"]
                
                # Find definition chunk
                definition_chunk = None
                if scope_type == "local_variables" and var_name in self.local_variables:
                    definition_chunk = self.local_variables[var_name].get("definition_chunk")
                elif scope_type == "class_members":
                    member_key = f"{self.current_class}::{var_name}"
                    if member_key in self.class_members:
                        definition_chunk = self.class_members[member_key].get("definition_chunk")
                elif scope_type == "global_variables" and var_name in self.global_variables:
                    definition_chunk = self.global_variables[var_name].get("definition_chunk")
                
                if definition_chunk:
                    var_info["definition_chunk"] = definition_chunk
                    
                    # Record usage relationship
                    self.variable_usages.append({
                        "chunk": chunk_id,
                        "variable": var_name,
                        "definition_chunk": definition_chunk,
                        "scope": scope_type
                    })
    
    def _resolve_method_dependencies(self, chunk_id: str, methods: List[Dict]):
        """Resolve method call dependencies."""
        for method_info in methods:
            method_name = method_info["method"]
            
            # Find method definition
            definition_chunk = None
            if method_name in self.function_signatures:
                definition_chunk = self.function_signatures[method_name].get("definition_chunk")
            elif self.current_class:
                full_method_name = f"{self.current_class}::{method_name}"
                if full_method_name in self.function_signatures:
                    definition_chunk = self.function_signatures[full_method_name].get("definition_chunk")
            
            if definition_chunk:
                method_info["definition_chunk"] = definition_chunk
                
                # Record call relationship
                self.method_calls.append({
                    "caller_chunk": chunk_id,
                    "callee": method_name,
                    "callee_chunk": definition_chunk,
                    "call_type": method_info["call_type"]
                })
    
    def _find_related_chunks(self, chunk: Dict[str, Any]) -> List[str]:
        """Find chunks related to this chunk through various relationships."""
        related = []
        chunk_id = chunk["id"]
        
        # Find chunks that use variables defined in this chunk
        # Find chunks that call methods defined in this chunk
        # Find chunks in the same function/class
        # etc.
        
        return related
    
    # Helper methods for analysis
    def _get_current_context(self) -> str:
        """Get current context string."""
        context_parts = []
        if self.current_namespace:
            context_parts.append(self.current_namespace)
        if self.current_class:
            context_parts.append(self.current_class)
        if self.current_function:
            context_parts.append(self.current_function)
        return "::".join(context_parts)
    
    def _classify_statement(self, stmt: str) -> str:
        """Classify statement type for chunking."""
        stmt = stmt.strip()
        
        if stmt.startswith('if '):
            return "if_statement"
        elif stmt.startswith('else'):
            return "else_statement"
        elif stmt.startswith('for '):
            return "for_loop"
        elif stmt.startswith('while '):
            return "while_loop"
        elif stmt.startswith('switch '):
            return "switch_statement"
        elif stmt.startswith('case ') or stmt.startswith('default:'):
            return "case_statement"
        elif 'return ' in stmt:
            return "return_statement"
        elif '=' in stmt and not any(op in stmt for op in ['==', '!=', '<=', '>=']):
            return "assignment"
        elif any(func in stmt for func in ['strcat', 'strcpy', 'sprintf', 'printf']):
            return "string_operation"
        elif '->' in stmt or '.' in stmt:
            return "member_access"
        elif any(func in stmt for func in ['malloc', 'free', 'new', 'delete']):
            return "memory_operation"
        else:
            return "statement"
    
    def _is_parameter(self, var_name: str) -> bool:
        """Check if variable is a parameter of current function."""
        if self.current_function and self.current_function in self.function_signatures:
            params = self.function_signatures[self.current_function].get("parameters", [])
            return any(p.get("name") == var_name for p in params)
        return False
    
    def _get_parameter_type(self, var_name: str) -> str:
        """Get parameter type."""
        if self.current_function and self.current_function in self.function_signatures:
            params = self.function_signatures[self.current_function].get("parameters", [])
            for p in params:
                if p.get("name") == var_name:
                    return p.get("type", "unknown")
        return "unknown"
    
    def _extract_required_includes(self, node: Dict[str, Any]) -> List[str]:
        """Extract include dependencies from node."""
        # Implementation would analyze types and return required includes
        return []
    
    def _extract_class_dependencies(self, node: Dict[str, Any]) -> List[str]:
        """Extract class dependencies from node."""
        # Implementation would analyze used classes
        return []
    
    def _extract_template_dependencies(self, node: Dict[str, Any]) -> List[str]:
        """Extract template dependencies from node."""
        # Implementation would analyze template usage
        return []
    
    def _analyze_scope_dependencies(self, stmt: str) -> Dict[str, Any]:
        """Analyze scope dependencies in statement."""
        return {"local_scope": True, "global_scope": False}
    
    def _analyze_data_flow(self, stmt: str) -> Dict[str, Any]:
        """Analyze data flow in statement."""
        return {"reads": [], "writes": [], "modifies": []}
    
    def _analyze_control_flow(self, stmt: str) -> Dict[str, Any]:
        """Analyze control flow in statement."""
        return {"branching": False, "looping": False, "jumping": False}
    
    def _extract_dependencies(self, stmt: str) -> List[str]:
        """Extract function/library dependencies."""
        deps = []
        if 'strcat' in stmt or 'strcpy' in stmt:
            deps.append("function:string_h")
        if 'printf' in stmt or 'sprintf' in stmt:
            deps.append("function:stdio_h")
        # Add more dependency detection
        return deps
    
    def _assess_complexity(self, stmt: str) -> str:
        """Assess statement complexity."""
        if any(keyword in stmt for keyword in ['if', 'for', 'while', 'switch']):
            return "high"
        elif any(op in stmt for op in ['->', '.', '::', 'new', 'delete']):
            return "medium"
        else:
            return "low"
    
    def _identify_c_constructs(self, stmt: str) -> List[str]:
        """Identify C-specific constructs."""
        constructs = []
        if '->' in stmt:
            constructs.append("pointer_access")
        if any(func in stmt for func in ['malloc', 'free']):
            constructs.append("manual_memory_management")
        if any(func in stmt for func in ['strcat', 'strcpy', 'sprintf']):
            constructs.append("c_string_functions")
        return constructs
    
    def _suggest_kotlin_patterns(self, stmt: str) -> List[str]:
        """Suggest Kotlin patterns for C++ constructs."""
        suggestions = []
        if 'sprintf' in stmt:
            suggestions.append("use_string_interpolation")
        if 'malloc' in stmt or 'new' in stmt:
            suggestions.append("use_kotlin_collections")
        if '->' in stmt:
            suggestions.append("use_safe_call_operator")
        return suggestions
    
    def _identify_potential_issues(self, stmt: str) -> List[str]:
        """Identify potential conversion issues."""
        issues = []
        if 'goto' in stmt:
            issues.append("goto_statement")
        if '#define' in stmt:
            issues.append("macro_usage")
        return issues
    
    def _assess_conversion_priority(self, stmt_type: str, stmt: str) -> str:
        """Assess conversion priority."""
        if stmt_type in ["if_statement", "for_loop", "return_statement"]:
            return "high"
        elif stmt_type in ["assignment", "member_access"]:
            return "medium"
        else:
            return "low"
    
    def _record_chunk_relationships(self, chunk: Dict, variables: List[str], 
                                  methods: List[Dict], pointers: List[Dict]):
        """Record relationships for later resolution."""
        # This would update the global relationship tracking structures
        pass
    
    # Skeleton extraction methods (simplified versions of original methods)
    def _find_includes(self) -> List[str]:
        """Find include statements."""
        return []
    
    def _find_namespaces(self) -> List[str]:
        """Find namespace declarations."""
        return []
    
    def _find_class_declarations(self) -> List[Dict]:
        """Find class declarations."""
        return []
    
    def _find_function_signatures(self) -> List[Dict]:
        """Find function signatures."""
        return []
    
    def _find_enums(self) -> List[Dict]:
        """Find enum declarations."""
        return []
    
    def _find_typedefs(self) -> List[Dict]:
        """Find typedef declarations."""
        return []
    
    def _find_global_variables(self) -> List[Dict]:
        """Find global variable declarations."""
        return []


def main():
    parser = argparse.ArgumentParser(description="Enhanced Relationship-Aware LST Chunker")
    parser.add_argument("--lst", required=True, help="Input LST JSON file")
    parser.add_argument("--out-dir", required=True, help="Output directory for chunks")
    parser.add_argument("--skeleton-out", required=True, help="Output skeleton JSON file")
    parser.add_argument("--relationships-out", help="Output relationships JSON file")
    
    args = parser.parse_args()
    
    # Read LST file
    with open(args.lst, 'r', encoding='utf-8') as f:
        lst_data = json.load(f)
    
    # Create chunker and process
    chunker = RelationshipAwareLSTChunker(lst_data)
    chunks, skeleton_info = chunker.chunk()
    
    # Create output directory
    Path(args.out_dir).mkdir(parents=True, exist_ok=True)
    
    # Write chunks
    for chunk in chunks:
        chunk_file = Path(args.out_dir) / f"{chunk['id']}.json"
        with open(chunk_file, 'w', encoding='utf-8') as f:
            json.dump(chunk, f, indent=2, ensure_ascii=False)
    
    # Write skeleton
    with open(args.skeleton_out, 'w', encoding='utf-8') as f:
        json.dump(skeleton_info, f, indent=2, ensure_ascii=False)
    
    # Write relationships if requested
    if args.relationships_out:
        relationships = {
            "global_variables": chunker.global_variables,
            "class_members": chunker.class_members,
            "local_variables": chunker.local_variables,
            "function_signatures": chunker.function_signatures,
            "method_calls": chunker.method_calls,
            "variable_usages": chunker.variable_usages,
            "pointer_relationships": chunker.pointer_relationships
        }
        with open(args.relationships_out, 'w', encoding='utf-8') as f:
            json.dump(relationships, f, indent=2, ensure_ascii=False)
    
    print(f"Created {len(chunks)} relationship-aware chunks")
    print(f"Skeleton written to {args.skeleton_out}")
    if args.relationships_out:
        print(f"Relationships written to {args.relationships_out}")


if __name__ == "__main__":
    main()