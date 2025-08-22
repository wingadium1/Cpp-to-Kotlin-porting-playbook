#!/usr/bin/env python3
"""
Enhanced LST Chunker: Split C++ LST into fine-grained conversion chunks.

Creates detailed chunks for efficient conversion:
- Function signature chunks
- Function body logical blocks
- Variable declarations
- Control flow structures (if/else, loops, switch)
- Expression statements
- Class member chunks
- Maintains context dependencies for seamless conversion
"""
import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class LSTChunker:
    def __init__(self, lst_data: Dict[str, Any]):
        self.lst = lst_data
        self.chunks: List[Dict[str, Any]] = []
        self.skeleton_info: Dict[str, Any] = {}
        self.chunk_counter = 0
        self.context_stack: List[str] = []  # Track nested contexts (class, namespace, etc.)
        
    def chunk(self) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Split LST into fine-grained chunks and extract skeleton info."""
        self._extract_skeleton_info()
        self._create_detailed_chunks()
        return self.chunks, self.skeleton_info
    
    def _extract_skeleton_info(self):
        """Extract structure for skeleton generation."""
        self.skeleton_info = {
            "includes": self._find_includes(),
            "namespaces": self._find_namespaces(),
            "classes": self._find_class_declarations(),
            "functions": self._find_function_signatures(),
            "enums": self._find_enums(),
            "typedefs": self._find_typedefs()
        }
    
    def _create_detailed_chunks(self):
        """Create fine-grained logical chunks from LST."""
        nodes = self.lst.get("nodes", [])
        if nodes:
            for node in nodes:
                self._process_node_detailed(node)
    
    def _process_node_detailed(self, node: Dict[str, Any], parent_context: str = ""):
        """Process a node with fine-grained chunking strategy."""
        node_kind = node.get("kind", "")
        node_name = node.get("name", "")
        
        # Build context path
        current_context = f"{parent_context}::{node_name}" if parent_context else node_name
        
        if node_kind == "function":
            self._chunk_function_detailed(node, current_context)
        elif node_kind in ["class", "struct"]:
            self._chunk_class_detailed(node, current_context)
        elif node_kind == "namespace":
            self._chunk_namespace_detailed(node, current_context)
        elif node_kind == "other":
            # Parse other constructs based on text content
            self._chunk_other_detailed(node, current_context)
        else:
            # Process children if any
            children = node.get("children", [])
            for child in children:
                self._process_node_detailed(child, current_context)
    
    def _chunk_function_detailed(self, node: Dict[str, Any], context: str):
        """Break down function into multiple fine-grained chunks."""
        function_name = node.get("name", "unnamed_function")
        function_text = node.get("text", "")
        header = node.get("header", "")
        span = node.get("span", {})
        
        # 1. Function signature chunk
        sig_chunk = {
            "id": f"func_sig_{self.chunk_counter}",
            "type": "function_signature",
            "name": function_name,
            "context": context,
            "header": header,
            "signature": self._clean_signature(header),
            "return_type": self._extract_return_type_from_header(header),
            "parameters": self._extract_params_from_header(header),
            "class_name": self._extract_class_from_name(function_name),
            "span": span,
            "dependencies": self._find_function_dependencies(header),
            "conversion_priority": "high"  # Signatures are important
        }
        self.chunks.append(sig_chunk)
        self.chunk_counter += 1
        
        # 2. Function body chunks (break down by logical blocks)
        if function_text:
            body_chunks = self._chunk_function_body(function_text, function_name, context, span)
            self.chunks.extend(body_chunks)
    
    def _chunk_function_body(self, body_text: str, func_name: str, context: str, span: Dict) -> List[Dict[str, Any]]:
        """Break function body into logical chunks."""
        chunks = []
        lines = body_text.split('\n')
        
        # Parse body for logical blocks
        current_block = []
        current_block_type = "statement_block"
        block_start_line = span.get("start_line", 1)
        line_counter = 0
        
        for i, line in enumerate(lines):
            stripped_line = line.strip()
            line_counter += 1
            
            # Detect logical boundaries
            if self._is_control_structure_start(stripped_line):
                # Save previous block if exists
                if current_block:
                    chunk = self._create_body_chunk(
                        current_block, current_block_type, func_name, context,
                        block_start_line, block_start_line + len(current_block) - 1
                    )
                    chunks.append(chunk)
                
                # Start new control structure block
                current_block = [line]
                current_block_type = self._identify_control_structure(stripped_line)
                block_start_line = span.get("start_line", 1) + line_counter - 1
                
            elif self._is_variable_declaration(stripped_line):
                # Save previous block
                if current_block and current_block_type != "variable_declarations":
                    chunk = self._create_body_chunk(
                        current_block, current_block_type, func_name, context,
                        block_start_line, block_start_line + len(current_block) - 1
                    )
                    chunks.append(chunk)
                    current_block = []
                
                # Start or continue variable declaration block
                if current_block_type != "variable_declarations":
                    current_block_type = "variable_declarations"
                    block_start_line = span.get("start_line", 1) + line_counter - 1
                current_block.append(line)
                
            elif self._is_complex_statement(stripped_line):
                # Save previous block
                if current_block:
                    chunk = self._create_body_chunk(
                        current_block, current_block_type, func_name, context,
                        block_start_line, block_start_line + len(current_block) - 1
                    )
                    chunks.append(chunk)
                
                # Create single statement chunk
                chunk = self._create_body_chunk(
                    [line], "complex_statement", func_name, context,
                    span.get("start_line", 1) + line_counter - 1,
                    span.get("start_line", 1) + line_counter - 1
                )
                chunks.append(chunk)
                current_block = []
                block_start_line = span.get("start_line", 1) + line_counter
                current_block_type = "statement_block"
                
            else:
                # Regular statement
                current_block.append(line)
        
        # Save final block
        if current_block:
            chunk = self._create_body_chunk(
                current_block, current_block_type, func_name, context,
                block_start_line, block_start_line + len(current_block) - 1
            )
            chunks.append(chunk)
        
        return chunks
    
    def _create_body_chunk(self, lines: List[str], block_type: str, func_name: str, 
                          context: str, start_line: int, end_line: int) -> Dict[str, Any]:
        """Create a chunk for a function body block."""
        text = '\n'.join(lines)
        
        chunk = {
            "id": f"body_{self.chunk_counter}",
            "type": f"function_body_{block_type}",
            "parent_function": func_name,
            "context": context,
            "text": text,
            "line_range": {"start": start_line, "end": end_line},
            "dependencies": self._find_text_dependencies(text),
            "conversion_notes": self._analyze_conversion_complexity(text, block_type),
            "conversion_priority": self._get_conversion_priority(block_type)
        }
        self.chunk_counter += 1
        return chunk
    
    def _is_control_structure_start(self, line: str) -> bool:
        """Check if line starts a control structure."""
        control_keywords = [
            'if ', 'else', 'for ', 'while ', 'do ', 'switch ', 'case ', 'default:',
            'try ', 'catch ', 'throw '
        ]
        return any(line.startswith(keyword) for keyword in control_keywords)
    
    def _identify_control_structure(self, line: str) -> str:
        """Identify the type of control structure."""
        if line.startswith('if '):
            return "if_statement"
        elif line.startswith('else'):
            return "else_statement"
        elif line.startswith('for '):
            return "for_loop"
        elif line.startswith('while '):
            return "while_loop"
        elif line.startswith('do '):
            return "do_while_loop"
        elif line.startswith('switch '):
            return "switch_statement"
        elif line.startswith('case ') or line.startswith('default:'):
            return "case_statement"
        elif line.startswith('try '):
            return "try_block"
        elif line.startswith('catch '):
            return "catch_block"
        elif line.startswith('throw '):
            return "throw_statement"
        return "control_structure"
    
    def _is_variable_declaration(self, line: str) -> bool:
        """Check if line is a variable declaration."""
        # Simple heuristics for C++ variable declarations
        var_patterns = [
            'int ', 'char ', 'long ', 'short ', 'float ', 'double ', 'bool ', 'void ',
            'string ', 'String ', 'CString ', 'std::', 'BOOL ', 'WORD ', 'DWORD ',
            'auto ', 'const ', 'static ', 'extern '
        ]
        return any(line.startswith(pattern) for pattern in var_patterns)
    
    def _is_complex_statement(self, line: str) -> bool:
        """Check if line is a complex statement that should be its own chunk."""
        complex_patterns = [
            'strcat(', 'strcpy(', 'sprintf(', 'memset(', 'malloc(', 'free(',
            'new ', 'delete ', 'return ', '::',  # Method calls
            'printf(', 'fprintf(', '#define', '#include'
        ]
        return any(pattern in line for pattern in complex_patterns) and len(line.strip()) > 50
    
    def _analyze_conversion_complexity(self, text: str, block_type: str) -> Dict[str, Any]:
        """Analyze conversion complexity and provide notes."""
        notes = {
            "complexity": "medium",
            "c_specific_constructs": [],
            "kotlin_suggestions": [],
            "potential_issues": []
        }
        
        # Detect C-specific constructs
        if 'malloc(' in text or 'free(' in text:
            notes["c_specific_constructs"].append("manual_memory_management")
            notes["kotlin_suggestions"].append("use_kotlin_collections")
            notes["complexity"] = "high"
        
        if 'char*' in text or 'char ' in text:
            notes["c_specific_constructs"].append("c_strings")
            notes["kotlin_suggestions"].append("use_kotlin_string")
        
        if 'strcat(' in text or 'strcpy(' in text:
            notes["c_specific_constructs"].append("string_manipulation")
            notes["kotlin_suggestions"].append("use_string_interpolation")
        
        if '::' in text:
            notes["c_specific_constructs"].append("scope_resolution")
            notes["kotlin_suggestions"].append("use_kotlin_package_imports")
        
        if 'printf(' in text or 'sprintf(' in text:
            notes["c_specific_constructs"].append("c_io")
            notes["kotlin_suggestions"].append("use_kotlin_println")
        
        # Set complexity based on constructs found
        if len(notes["c_specific_constructs"]) > 2:
            notes["complexity"] = "high"
        elif len(notes["c_specific_constructs"]) > 0:
            notes["complexity"] = "medium"
        else:
            notes["complexity"] = "low"
        
        return notes
    
    def _get_conversion_priority(self, block_type: str) -> str:
        """Get conversion priority for block type."""
        high_priority = ["function_signature", "variable_declarations", "if_statement"]
        medium_priority = ["for_loop", "while_loop", "complex_statement"]
        
        if block_type in high_priority:
            return "high"
        elif block_type in medium_priority:
            return "medium"
        else:
            return "low"
    
    def _chunk_class_detailed(self, node: Dict[str, Any], context: str):
        """Break down class into fine-grained chunks."""
        class_name = node.get("name", "unnamed_class")
        
        # 1. Class declaration chunk (header only)
        class_chunk = {
            "id": f"class_decl_{self.chunk_counter}",
            "type": "class_declaration",
            "name": class_name,
            "context": context,
            "header": node.get("header", ""),
            "span": node.get("span", {}),
            "dependencies": [],
            "conversion_priority": "high"
        }
        self.chunks.append(class_chunk)
        self.chunk_counter += 1
        
        # 2. Process class members individually
        children = node.get("children", [])
        for child in children:
            self._process_node_detailed(child, context)
    
    def _chunk_namespace_detailed(self, node: Dict[str, Any], context: str):
        """Process namespace contents with detailed chunking."""
        children = node.get("children", [])
        for child in children:
            self._process_node_detailed(child, context)
    
    def _chunk_other_detailed(self, node: Dict[str, Any], context: str):
        """Process other constructs with text analysis."""
        text = node.get("text", "")
        if text and len(text.strip()) > 0:
            # Break down by meaningful sections
            sections = self._split_text_into_sections(text)
            for i, section in enumerate(sections):
                if section.strip():
                    chunk = {
                        "id": f"misc_{self.chunk_counter}",
                        "type": "miscellaneous",
                        "context": context,
                        "text": section,
                        "span": node.get("span", {}),
                        "dependencies": self._find_text_dependencies(section),
                        "conversion_notes": self._analyze_conversion_complexity(section, "miscellaneous"),
                        "conversion_priority": "low"
                    }
                    self.chunks.append(chunk)
                    self.chunk_counter += 1
    
    def _split_text_into_sections(self, text: str) -> List[str]:
        """Split text into logical sections."""
        lines = text.split('\n')
        sections = []
        current_section = []
        
        for line in lines:
            stripped = line.strip()
            
            # Section boundaries
            if (stripped.startswith('//') and len(stripped) > 20 or  # Long comments
                stripped.startswith('/*') or
                stripped.startswith('#define') or
                stripped.startswith('#include') or
                stripped == '' and len(current_section) > 5):  # Empty line after substantial content
                
                if current_section:
                    sections.append('\n'.join(current_section))
                    current_section = []
            
            if stripped:  # Don't add empty lines to start of sections
                current_section.append(line)
        
        # Add final section
        if current_section:
            sections.append('\n'.join(current_section))
        
        return sections
    
    def _find_function_dependencies(self, header: str) -> List[str]:
        """Find dependencies from function header."""
        deps = []
        
        # Extract types from parameters and return type
        if '(' in header and ')' in header:
            param_section = header[header.find('('):header.rfind(')')+1]
            
            # Common C++ types that need Kotlin equivalents
            cpp_types = ['char', 'int', 'long', 'short', 'float', 'double', 'void', 'bool',
                        'string', 'String', 'CString', 'BOOL', 'WORD', 'DWORD']
            
            for cpp_type in cpp_types:
                if cpp_type in param_section or cpp_type in header:
                    deps.append(f"type:{cpp_type}")
        
        return deps
    
    def _find_text_dependencies(self, text: str) -> List[str]:
        """Find dependencies in text content."""
        deps = []
        
        # Common function calls that need Kotlin equivalents
        c_functions = ['malloc', 'free', 'printf', 'sprintf', 'strcat', 'strcpy', 'strlen',
                      'memset', 'memcpy', 'strcmp', 'strncmp', 'fprintf']
        
        for func in c_functions:
            if f'{func}(' in text:
                deps.append(f"function:{func}")
        
        # Class/object references
        if '::' in text:
            # Extract class references
            import re
            class_refs = re.findall(r'(\w+)::\w+', text)
            for class_ref in class_refs:
                deps.append(f"class:{class_ref}")
        
        return list(set(deps))  # Remove duplicates
    
    def _extract_name(self, node: Dict[str, Any]) -> str:
        """Extract name from AST node."""
        # Look for common name fields
        for field in ["name", "identifier", "declName"]:
            if field in node and isinstance(node[field], str):
                return node[field]
        return "unnamed"
    
    def _extract_signature(self, node: Dict[str, Any]) -> str:
        """Extract function/method signature."""
        # Simplified signature extraction
        name = self._extract_name(node)
        params = self._extract_parameters(node)
        return_type = self._extract_return_type(node)
        return f"{return_type} {name}({params})"
    
    def _extract_parameters(self, node: Dict[str, Any]) -> str:
        """Extract parameter list."""
        # Simplified parameter extraction
        return "..."  # TODO: Implement proper parameter parsing
    
    def _extract_return_type(self, node: Dict[str, Any]) -> str:
        """Extract return type."""
        # Simplified return type extraction
        return "auto"  # TODO: Implement proper type parsing
    
    def _extract_line_range(self, node: Dict[str, Any], decl_only: bool = False) -> Tuple[int, int]:
        """Extract line range for chunk."""
        # Look for location information
        if "location" in node:
            loc = node["location"]
            start = loc.get("line", 1)
            end = loc.get("endLine", start)
            return (start, end)
        return (1, 1)
    
    def _extract_class_declaration(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Extract just the class declaration without methods."""
        # Return a copy with only declaration info
        decl = node.copy()
        decl.pop("children", None)  # Remove method implementations
        return decl
    
    def _find_dependencies(self, node: Dict[str, Any]) -> List[str]:
        """Find symbols this chunk depends on - enhanced version."""
        deps = []
        text = node.get("text", "")
        header = node.get("header", "")
        
        # Combine function and text dependency analysis
        if header:
            deps.extend(self._find_function_dependencies(header))
        if text:
            deps.extend(self._find_text_dependencies(text))
        
        # Traverse AST to find additional references
        self._collect_references(node, deps)
        return list(set(deps))  # Remove duplicates
    
    def _collect_references(self, node: Dict[str, Any], refs: List[str]):
        """Recursively collect symbol references."""
        if isinstance(node, dict):
            # Look for identifier references
            if node.get("kind") == "DeclRefExpr":
                name = self._extract_name(node)
                if name != "unnamed":
                    refs.append(name)
            
            # Recurse into children
            for value in node.values():
                if isinstance(value, (dict, list)):
                    self._collect_references(value, refs)
        elif isinstance(node, list):
            for item in node:
                self._collect_references(item, refs)
    
    def _find_includes(self) -> List[str]:
        """Find include directives."""
        return []  # TODO: Implement include extraction
    
    def _find_namespaces(self) -> List[str]:
        """Find namespace declarations."""
        return []  # TODO: Implement namespace extraction
    
    def _find_class_declarations(self) -> List[Dict[str, Any]]:
        """Find class/struct declarations."""
        return []  # TODO: Implement class extraction
    
    def _find_function_signatures(self) -> List[Dict[str, Any]]:
        """Find function signatures from LST with enhanced details."""
        functions = []
        if "nodes" in self.lst:
            self._extract_functions_from_nodes(self.lst["nodes"], functions)
        return functions
    
    def _extract_functions_from_nodes(self, nodes: List[Dict[str, Any]], functions: List[Dict[str, Any]]):
        """Recursively extract detailed function information from LST nodes."""
        for node in nodes:
            if node.get("kind") == "function":
                func_info = {
                    "name": node.get("name", "unknown"),
                    "header": node.get("header", ""),
                    "signature": self._clean_signature(node.get("header", "")),
                    "return_type": self._extract_return_type_from_header(node.get("header", "")),
                    "parameters": self._extract_params_from_header(node.get("header", "")),
                    "class_name": self._extract_class_from_name(node.get("name", "")),
                    "span": node.get("span", {}),
                    "body_text": node.get("text", "")[:2000] if node.get("text") else "",  # Increased for better analysis
                    "complexity_analysis": self._analyze_function_complexity(node.get("text", "")),
                    "conversion_hints": self._get_conversion_hints(node.get("name", ""), node.get("text", ""))
                }
                functions.append(func_info)
            
            # Recursively check children
            children = node.get("children", [])
            if children:
                self._extract_functions_from_nodes(children, functions)
    
    def _analyze_function_complexity(self, body: str) -> Dict[str, Any]:
        """Analyze function complexity for conversion planning."""
        if not body:
            return {"level": "simple", "issues": []}
        
        issues = []
        complexity_score = 0
        
        # Count complexity indicators
        control_structures = ['if', 'else', 'for', 'while', 'switch', 'case']
        for struct in control_structures:
            count = body.count(struct + ' ')
            complexity_score += count
            if count > 3:
                issues.append(f"many_{struct}_statements")
        
        # Check for C-specific constructs
        c_constructs = ['malloc', 'free', 'strcpy', 'strcat', 'sprintf', 'printf']
        for construct in c_constructs:
            if construct in body:
                complexity_score += 2
                issues.append(f"c_function_{construct}")
        
        # Determine complexity level
        if complexity_score < 5:
            level = "simple"
        elif complexity_score < 15:
            level = "moderate"
        else:
            level = "complex"
        
        return {
            "level": level,
            "score": complexity_score,
            "issues": issues,
            "line_count": len(body.split('\n'))
        }
    
    def _get_conversion_hints(self, func_name: str, body: str) -> List[str]:
        """Generate conversion hints for specific function patterns."""
        hints = []
        
        # Pattern-based hints
        if "Print" in func_name:
            hints.append("Consider using Kotlin's println() or string templates")
        
        if "Set" in func_name and "Data" in func_name:
            hints.append("Consider using Kotlin data classes and property setters")
        
        if body and "strcat" in body:
            hints.append("Replace strcat with Kotlin string concatenation or StringBuilder")
        
        if body and "malloc" in body:
            hints.append("Use Kotlin collections instead of manual memory management")
        
        if body and "::" in body:
            hints.append("Convert C++ scope resolution to Kotlin package/class access")
        
        return hints
    
    def _clean_signature(self, header: str) -> str:
        """Clean and format function signature."""
        if not header:
            return ""
        # Remove extra whitespace and normalize
        return " ".join(header.split())
    
    def _extract_return_type_from_header(self, header: str) -> str:
        """Extract return type from function header."""
        if not header:
            return "void"
        
        # Simple extraction - take everything before the function name
        parts = header.split()
        if len(parts) >= 2:
            # Find the function name (usually contains ::)
            for i, part in enumerate(parts):
                if "::" in part:
                    return " ".join(parts[:i])
        
        return "void"
    
    def _extract_params_from_header(self, header: str) -> str:
        """Extract parameters from function header."""
        if not header:
            return ""
        
        # Extract everything between parentheses
        start = header.find("(")
        end = header.rfind(")")
        if start != -1 and end != -1 and end > start:
            return header[start+1:end].strip()
        
        return ""
    
    def _extract_class_from_name(self, name: str) -> str:
        """Extract class name from function name."""
        if "::" in name:
            return name.split("::")[0]
        return ""
    
    def _find_enums(self) -> List[Dict[str, Any]]:
        """Find enum declarations."""
        return []  # TODO: Implement enum extraction
    
    def _find_typedefs(self) -> List[Dict[str, Any]]:
        """Find typedef declarations."""
        return []  # TODO: Implement typedef extraction
    
    def _create_chunks_recursive(self, node: Dict[str, Any], prefix: str):
        """Recursively create fine-grained chunks for nested structures."""
        self._process_node_detailed(node, prefix)


def main():
    parser = argparse.ArgumentParser(description="Chunk LST for conversion")
    parser.add_argument("--lst", required=True, help="Path to LST JSON file")
    parser.add_argument("--out-dir", required=True, help="Output directory for chunks")
    parser.add_argument("--skeleton-out", help="Output file for skeleton info")
    
    args = parser.parse_args()
    
    # Load LST
    with open(args.lst, 'r') as f:
        lst_data = json.load(f)
    
    # Create chunker and process
    chunker = LSTChunker(lst_data)
    chunks, skeleton_info = chunker.chunk()
    
    # Save chunks
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    for chunk in chunks:
        chunk_file = out_dir / f"{chunk['id']}.json"
        with open(chunk_file, 'w') as f:
            json.dump(chunk, f, indent=2)
    
    # Save skeleton info
    if args.skeleton_out:
        with open(args.skeleton_out, 'w') as f:
            json.dump(skeleton_info, f, indent=2)
    
    print(f"Created {len(chunks)} chunks in {out_dir}")
    if args.skeleton_out:
        print(f"Skeleton info saved to {args.skeleton_out}")


if __name__ == "__main__":
    main()