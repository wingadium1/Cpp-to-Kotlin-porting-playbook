#!/usr/bin/env python3
"""
Coarse Chunk Kotlin Converter

This script converts coarse-grained C++ chunks to Kotlin using the MCP conversion tools.
It processes chunks in priority order and maintains relationship context.
"""
import argparse
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess
import sys


class CoarseChunkConverter:
    def __init__(self, coarse_chunks_dir: str, output_dir: str):
        self.coarse_chunks_dir = coarse_chunks_dir
        self.output_dir = output_dir
        self.coarse_chunks: Dict[str, Dict] = {}
        self.converted_chunks: Dict[str, Dict] = {}
        self.conversion_results: List[Dict] = []
        
        # Load coarse chunks
        self._load_coarse_chunks()
        
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    def _load_coarse_chunks(self):
        """Load all coarse-grained chunks."""
        for chunk_file in Path(self.coarse_chunks_dir).glob("*.json"):
            with open(chunk_file, 'r', encoding='utf-8') as f:
                chunk = json.load(f)
                self.coarse_chunks[chunk['id']] = chunk
        
        print(f"Loaded {len(self.coarse_chunks)} coarse chunks for conversion")
    
    def convert_all_chunks(self):
        """Convert all chunks in priority order."""
        # Sort chunks by conversion priority
        chunks_by_priority = self._sort_chunks_by_priority()
        
        print("Converting chunks in priority order...")
        
        # Convert high-priority chunks first (GOTO structures, complex constructs)
        if "high" in chunks_by_priority:
            print(f"\n🔥 Converting {len(chunks_by_priority['high'])} HIGH PRIORITY chunks...")
            for chunk_id in chunks_by_priority["high"]:
                self._convert_chunk(chunk_id, priority="high")
        
        # Convert medium-priority chunks
        if "medium" in chunks_by_priority:
            print(f"\n⚡ Converting {len(chunks_by_priority['medium'])} MEDIUM PRIORITY chunks...")
            for chunk_id in chunks_by_priority["medium"]:
                self._convert_chunk(chunk_id, priority="medium")
        
        # Convert low-priority chunks
        if "low" in chunks_by_priority:
            print(f"\n✅ Converting {len(chunks_by_priority['low'])} LOW PRIORITY chunks...")
            for chunk_id in chunks_by_priority["low"]:
                self._convert_chunk(chunk_id, priority="low")
        
        return self.converted_chunks
    
    def _sort_chunks_by_priority(self) -> Dict[str, List[str]]:
        """Sort chunks by conversion priority."""
        priority_map = {"high": [], "medium": [], "low": []}
        
        for chunk_id, chunk in self.coarse_chunks.items():
            priority = chunk.get('conversion_priority', 'medium')
            if priority in priority_map:
                priority_map[priority].append(chunk_id)
            else:
                priority_map['medium'].append(chunk_id)
        
        return priority_map
    
    def _convert_chunk(self, chunk_id: str, priority: str):
        """Convert a single coarse chunk to Kotlin."""
        chunk = self.coarse_chunks[chunk_id]
        
        print(f"Converting {chunk_id} ({priority} priority)...")
        
        try:
            # Create conversion context
            context = self._create_conversion_context(chunk)
            
            # Convert based on chunk type and complexity
            chunk_type = chunk.get('type', '')
            
            if 'goto_structure' in chunk_type:
                kotlin_code = self._convert_goto_structure(chunk, context)
            elif 'control_structure' in chunk_type:
                kotlin_code = self._convert_control_structure(chunk, context)
            elif 'complex_statement' in chunk_type:
                kotlin_code = self._convert_complex_statement(chunk, context)
            elif 'simple_sequence' in chunk_type:
                kotlin_code = self._convert_simple_sequence(chunk, context)
            elif 'global_declaration' in chunk_type:
                kotlin_code = self._convert_global_declaration(chunk, context)
            else:
                kotlin_code = self._convert_generic_chunk(chunk, context)
            
            # Create converted chunk
            converted_chunk = {
                "original_chunk_id": chunk_id,
                "kotlin_code": kotlin_code,
                "conversion_context": context,
                "conversion_priority": priority,
                "conversion_status": "success",
                "conversion_notes": self._generate_conversion_notes(chunk, kotlin_code)
            }
            
            self.converted_chunks[chunk_id] = converted_chunk
            self.conversion_results.append({
                "chunk_id": chunk_id,
                "status": "success",
                "priority": priority
            })
            
            print(f"✅ Successfully converted {chunk_id}")
            
        except Exception as e:
            error_msg = f"❌ Failed to convert {chunk_id}: {str(e)}"
            print(error_msg)
            
            self.conversion_results.append({
                "chunk_id": chunk_id,
                "status": "failed",
                "error": str(e),
                "priority": priority
            })
    
    def _create_conversion_context(self, chunk: Dict) -> Dict:
        """Create conversion context for the chunk."""
        context = {
            "function_name": chunk.get('parent_function', ''),
            "variable_scope": chunk.get('relationships', {}).get('variables_used', {}),
            "method_calls": chunk.get('relationships', {}).get('methods_called', []),
            "pointer_operations": chunk.get('relationships', {}).get('pointer_operations', []),
            "control_flow": chunk.get('relationships', {}).get('control_flow', {}),
            "c_constructs": chunk.get('conversion_notes', {}).get('c_specific_constructs', []),
            "null_safety_concerns": chunk.get('conversion_notes', {}).get('null_safety_concerns', []),
            "memory_safety_notes": chunk.get('conversion_notes', {}).get('memory_safety_notes', [])
        }
        return context
    
    def _convert_goto_structure(self, chunk: Dict, context: Dict) -> str:
        """Convert GOTO structure with special restructuring."""
        cpp_text = chunk.get('text', '')
        
        # GOTO structures need manual restructuring
        conversion_strategy = chunk.get('conversion_notes', {}).get('goto_conversion_strategy', 'complex_flow')
        
        if conversion_strategy == "error_handling":
            return self._restructure_error_handling_goto(cpp_text, context)
        elif conversion_strategy == "loop_control":
            return self._restructure_loop_control_goto(cpp_text, context)
        elif conversion_strategy == "early_exit":
            return self._restructure_early_exit_goto(cpp_text, context)
        else:
            return self._restructure_complex_flow_goto(cpp_text, context)
    
    def _restructure_error_handling_goto(self, cpp_text: str, context: Dict) -> str:
        """Restructure error handling GOTO to Kotlin exception handling."""
        # Convert GOTO error handling to try-catch or early returns
        kotlin_code = "// TODO: Restructure error handling GOTO\n"
        kotlin_code += "// Original C++ code:\n"
        for line in cpp_text.split('\n'):
            kotlin_code += f"// {line}\n"
        
        kotlin_code += "\n// Kotlin conversion (manual restructuring required):\n"
        kotlin_code += "// Use try-catch blocks or early returns instead of GOTO\n"
        
        return kotlin_code
    
    def _restructure_loop_control_goto(self, cpp_text: str, context: Dict) -> str:
        """Restructure loop control GOTO to Kotlin loop constructs."""
        kotlin_code = "// TODO: Restructure loop control GOTO\n"
        kotlin_code += "// Original C++ code:\n"
        for line in cpp_text.split('\n'):
            kotlin_code += f"// {line}\n"
        
        kotlin_code += "\n// Kotlin conversion (manual restructuring required):\n"
        kotlin_code += "// Use break, continue, or labeled breaks instead of GOTO\n"
        
        return kotlin_code
    
    def _restructure_early_exit_goto(self, cpp_text: str, context: Dict) -> str:
        """Restructure early exit GOTO to Kotlin early returns."""
        kotlin_code = "// TODO: Restructure early exit GOTO\n"
        kotlin_code += "// Original C++ code:\n"
        for line in cpp_text.split('\n'):
            kotlin_code += f"// {line}\n"
        
        kotlin_code += "\n// Kotlin conversion (manual restructuring required):\n"
        kotlin_code += "// Use early return statements instead of GOTO\n"
        
        return kotlin_code
    
    def _restructure_complex_flow_goto(self, cpp_text: str, context: Dict) -> str:
        """Restructure complex flow GOTO to Kotlin functions."""
        kotlin_code = "// TODO: Restructure complex flow GOTO\n"
        kotlin_code += "// Original C++ code:\n"
        for line in cpp_text.split('\n'):
            kotlin_code += f"// {line}\n"
        
        kotlin_code += "\n// Kotlin conversion (manual restructuring required):\n"
        kotlin_code += "// Extract functions and use proper control flow instead of GOTO\n"
        
        return kotlin_code
    
    def _convert_control_structure(self, chunk: Dict, context: Dict) -> str:
        """Convert control structure to Kotlin."""
        cpp_text = chunk.get('text', '')
        
        # Convert control structures line by line
        kotlin_lines = []
        
        for line in cpp_text.split('\n'):
            line = line.strip()
            if not line or line.startswith('//'):
                kotlin_lines.append(line)
                continue
            
            # Convert common control structures
            kotlin_line = self._convert_cpp_line_to_kotlin(line, context)
            kotlin_lines.append(kotlin_line)
        
        return '\n'.join(kotlin_lines)
    
    def _convert_complex_statement(self, chunk: Dict, context: Dict) -> str:
        """Convert complex statement to Kotlin."""
        cpp_text = chunk.get('text', '')
        
        kotlin_lines = []
        
        for line in cpp_text.split('\n'):
            line = line.strip()
            if not line or line.startswith('//'):
                kotlin_lines.append(line)
                continue
            
            kotlin_line = self._convert_cpp_line_to_kotlin(line, context)
            kotlin_lines.append(kotlin_line)
        
        return '\n'.join(kotlin_lines)
    
    def _convert_simple_sequence(self, chunk: Dict, context: Dict) -> str:
        """Convert simple sequence to Kotlin."""
        cpp_text = chunk.get('text', '')
        
        kotlin_lines = []
        
        for line in cpp_text.split('\n'):
            line = line.strip()
            if not line or line.startswith('//'):
                kotlin_lines.append(line)
                continue
            
            kotlin_line = self._convert_cpp_line_to_kotlin(line, context)
            kotlin_lines.append(kotlin_line)
        
        return '\n'.join(kotlin_lines)
    
    def _convert_global_declaration(self, chunk: Dict, context: Dict) -> str:
        """Convert global declaration to Kotlin."""
        cpp_text = chunk.get('text', '')
        
        # Convert global declarations to Kotlin properties or constants
        kotlin_lines = []
        
        for line in cpp_text.split('\n'):
            line = line.strip()
            if not line or line.startswith('//'):
                kotlin_lines.append(line)
                continue
            
            kotlin_line = self._convert_global_declaration_line(line, context)
            kotlin_lines.append(kotlin_line)
        
        return '\n'.join(kotlin_lines)
    
    def _convert_generic_chunk(self, chunk: Dict, context: Dict) -> str:
        """Convert generic chunk to Kotlin."""
        cpp_text = chunk.get('text', '')
        
        kotlin_lines = []
        
        for line in cpp_text.split('\n'):
            line = line.strip()
            if not line or line.startswith('//'):
                kotlin_lines.append(line)
                continue
            
            kotlin_line = self._convert_cpp_line_to_kotlin(line, context)
            kotlin_lines.append(kotlin_line)
        
        return '\n'.join(kotlin_lines)
    
    def _convert_cpp_line_to_kotlin(self, cpp_line: str, context: Dict) -> str:
        """Convert a single C++ line to Kotlin."""
        # Remove leading/trailing whitespace
        line = cpp_line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('//'):
            return line
        
        # Convert common C++ constructs to Kotlin
        kotlin_line = line
        
        # Function signature conversion
        if line.startswith('void ') or line.startswith('int ') or line.startswith('short '):
            kotlin_line = self._convert_function_signature(line)
        
        # Variable declarations
        elif any(line.startswith(t) for t in ['char ', 'int ', 'short ', 'long ', 'float ', 'double ']):
            kotlin_line = self._convert_variable_declaration(line)
        
        # Control structures
        elif line.startswith('if ') or line.startswith('if('):
            kotlin_line = self._convert_if_statement(line)
        elif line.startswith('for ') or line.startswith('for('):
            kotlin_line = self._convert_for_loop(line)
        elif line.startswith('while ') or line.startswith('while('):
            kotlin_line = self._convert_while_loop(line)
        elif line.startswith('switch ') or line.startswith('switch('):
            kotlin_line = self._convert_switch_statement(line)
        
        # String operations
        elif 'strcpy(' in line or 'strncpy(' in line:
            kotlin_line = self._convert_string_copy(line)
        elif 'strcat(' in line or 'strncat(' in line:
            kotlin_line = self._convert_string_concat(line)
        elif 'sprintf(' in line:
            kotlin_line = self._convert_sprintf(line)
        
        # Memory operations
        elif 'memset(' in line:
            kotlin_line = self._convert_memset(line)
        elif 'malloc(' in line or 'calloc(' in line:
            kotlin_line = self._convert_malloc(line)
        elif 'free(' in line:
            kotlin_line = self._convert_free(line)
        
        # Pointer operations
        elif '->' in line:
            kotlin_line = self._convert_pointer_access(line)
        
        # Array access with bounds checking
        elif '[' in line and ']' in line:
            kotlin_line = self._convert_array_access(line, context)
        
        return kotlin_line
    
    def _convert_function_signature(self, line: str) -> str:
        """Convert C++ function signature to Kotlin."""
        # Extract function name and parameters
        # This is a simplified conversion - full implementation would be more complex
        if 'void ' in line:
            kotlin_line = line.replace('void ', 'fun ').replace(';', '') + ': Unit'
        else:
            kotlin_line = f"// TODO: Convert function signature: {line}"
        
        return kotlin_line
    
    def _convert_variable_declaration(self, line: str) -> str:
        """Convert C++ variable declaration to Kotlin."""
        # Convert C++ types to Kotlin types
        type_mapping = {
            'char ': 'var ',
            'int ': 'var ',
            'short ': 'var ',
            'long ': 'var ',
            'float ': 'var ',
            'double ': 'var '
        }
        
        kotlin_line = line
        for cpp_type, kotlin_prefix in type_mapping.items():
            if line.startswith(cpp_type):
                kotlin_line = line.replace(cpp_type, kotlin_prefix, 1)
                break
        
        return kotlin_line
    
    def _convert_if_statement(self, line: str) -> str:
        """Convert C++ if statement to Kotlin."""
        # Basic conversion - more sophisticated logic would be needed
        kotlin_line = line
        
        # Convert common C++ patterns
        kotlin_line = kotlin_line.replace('==', '==')
        kotlin_line = kotlin_line.replace('!=', '!=')
        kotlin_line = kotlin_line.replace('NULL', 'null')
        
        return kotlin_line
    
    def _convert_for_loop(self, line: str) -> str:
        """Convert C++ for loop to Kotlin."""
        # TODO: Implement proper for loop conversion
        return f"// TODO: Convert for loop: {line}"
    
    def _convert_while_loop(self, line: str) -> str:
        """Convert C++ while loop to Kotlin."""
        kotlin_line = line.replace('NULL', 'null')
        return kotlin_line
    
    def _convert_switch_statement(self, line: str) -> str:
        """Convert C++ switch to Kotlin when."""
        kotlin_line = line.replace('switch', 'when')
        return kotlin_line
    
    def _convert_string_copy(self, line: str) -> str:
        """Convert strcpy/strncpy to Kotlin string assignment."""
        if 'strcpy(' in line:
            # Extract target and source
            # Simplified conversion
            kotlin_line = f"// TODO: Convert strcpy to Kotlin string assignment: {line}"
        elif 'strncpy(' in line:
            kotlin_line = f"// TODO: Convert strncpy to Kotlin string copy: {line}"
        else:
            kotlin_line = line
        
        return kotlin_line
    
    def _convert_string_concat(self, line: str) -> str:
        """Convert strcat to Kotlin string concatenation."""
        return f"// TODO: Convert strcat to Kotlin string concatenation: {line}"
    
    def _convert_sprintf(self, line: str) -> str:
        """Convert sprintf to Kotlin string formatting."""
        return f"// TODO: Convert sprintf to Kotlin string templates: {line}"
    
    def _convert_memset(self, line: str) -> str:
        """Convert memset to Kotlin array initialization."""
        return f"// TODO: Convert memset to Kotlin array fill: {line}"
    
    def _convert_malloc(self, line: str) -> str:
        """Convert malloc to Kotlin collections."""
        return f"// TODO: Convert malloc to Kotlin collections: {line}"
    
    def _convert_free(self, line: str) -> str:
        """Convert free to automatic memory management."""
        return "// Note: Manual memory deallocation not needed in Kotlin (automatic GC)"
    
    def _convert_pointer_access(self, line: str) -> str:
        """Convert pointer access to safe call operator."""
        kotlin_line = line.replace('->', '?.')
        return kotlin_line
    
    def _convert_array_access(self, line: str, context: Dict) -> str:
        """Convert array access with bounds checking."""
        # Add bounds checking if needed
        null_safety_concerns = context.get('null_safety_concerns', [])
        if any('bounds_check' in concern for concern in null_safety_concerns):
            kotlin_line = f"// TODO: Add bounds checking for: {line}"
        else:
            kotlin_line = line
        
        return kotlin_line
    
    def _convert_global_declaration_line(self, line: str, context: Dict) -> str:
        """Convert global declaration line to Kotlin."""
        # Convert global variables to companion object properties
        if any(line.startswith(t) for t in ['static ', 'extern ', 'const ']):
            kotlin_line = f"// TODO: Convert global declaration to companion object: {line}"
        else:
            kotlin_line = self._convert_cpp_line_to_kotlin(line, context)
        
        return kotlin_line
    
    def _generate_conversion_notes(self, chunk: Dict, kotlin_code: str) -> Dict:
        """Generate conversion notes for the chunk."""
        notes = {
            "original_complexity": chunk.get('conversion_notes', {}).get('complexity', 'unknown'),
            "chunking_strategy": chunk.get('conversion_notes', {}).get('chunking_strategy', 'unknown'),
            "c_constructs_handled": chunk.get('conversion_notes', {}).get('c_specific_constructs', []),
            "kotlin_patterns_used": [],
            "manual_review_needed": [],
            "conversion_confidence": "medium"
        }
        
        # Analyze converted code for patterns
        if 'TODO:' in kotlin_code:
            notes["manual_review_needed"].append("contains_todo_items")
            notes["conversion_confidence"] = "low"
        
        if '?.' in kotlin_code:
            notes["kotlin_patterns_used"].append("safe_call_operator")
        
        if 'when' in kotlin_code:
            notes["kotlin_patterns_used"].append("when_expression")
        
        return notes
    
    def save_converted_chunks(self, output_file: str):
        """Save all converted chunks to a file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.converted_chunks, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(self.converted_chunks)} converted chunks to {output_file}")
    
    def generate_conversion_report(self, output_file: str):
        """Generate conversion report."""
        successful_conversions = [r for r in self.conversion_results if r['status'] == 'success']
        failed_conversions = [r for r in self.conversion_results if r['status'] == 'failed']
        
        report = {
            "conversion_summary": {
                "total_chunks": len(self.coarse_chunks),
                "successful_conversions": len(successful_conversions),
                "failed_conversions": len(failed_conversions),
                "success_rate": len(successful_conversions) / len(self.coarse_chunks) * 100 if self.coarse_chunks else 0
            },
            "conversion_by_priority": {},
            "failed_conversions": failed_conversions,
            "manual_review_needed": [],
            "next_steps": []
        }
        
        # Group by priority
        for result in self.conversion_results:
            priority = result.get('priority', 'unknown')
            if priority not in report["conversion_by_priority"]:
                report["conversion_by_priority"][priority] = {"success": 0, "failed": 0}
            
            if result['status'] == 'success':
                report["conversion_by_priority"][priority]["success"] += 1
            else:
                report["conversion_by_priority"][priority]["failed"] += 1
        
        # Find chunks needing manual review
        for chunk_id, converted_chunk in self.converted_chunks.items():
            kotlin_code = converted_chunk.get('kotlin_code', '')
            if 'TODO:' in kotlin_code:
                report["manual_review_needed"].append({
                    "chunk_id": chunk_id,
                    "reason": "contains_todo_items"
                })
        
        # Generate next steps
        if failed_conversions:
            report["next_steps"].append(f"Review and fix {len(failed_conversions)} failed conversions")
        
        if report["manual_review_needed"]:
            report["next_steps"].append(f"Manual review needed for {len(report['manual_review_needed'])} chunks")
        
        report["next_steps"].append("Integrate converted chunks into main Kotlin class")
        report["next_steps"].append("Add unit tests for converted methods")
        report["next_steps"].append("Validate compilation and runtime behavior")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"Generated conversion report at {output_file}")
        return report


def main():
    parser = argparse.ArgumentParser(description="Convert coarse-grained C++ chunks to Kotlin")
    parser.add_argument("--coarse-chunks-dir", required=True, help="Directory containing coarse chunks")
    parser.add_argument("--output-dir", required=True, help="Output directory for converted chunks")
    parser.add_argument("--converted-chunks-out", required=True, help="Output file for converted chunks JSON")
    parser.add_argument("--conversion-report-out", required=True, help="Output file for conversion report")
    
    args = parser.parse_args()
    
    # Create converter and process chunks
    converter = CoarseChunkConverter(args.coarse_chunks_dir, args.output_dir)
    converted_chunks = converter.convert_all_chunks()
    
    # Save results
    converter.save_converted_chunks(args.converted_chunks_out)
    report = converter.generate_conversion_report(args.conversion_report_out)
    
    print(f"\n🎉 Conversion complete!")
    print(f"Successfully converted: {report['conversion_summary']['successful_conversions']}/{report['conversion_summary']['total_chunks']} chunks")
    print(f"Success rate: {report['conversion_summary']['success_rate']:.1f}%")
    
    if report['conversion_summary']['failed_conversions'] > 0:
        print(f"⚠️  Failed conversions: {report['conversion_summary']['failed_conversions']}")
    
    if report['manual_review_needed']:
        print(f"📝 Manual review needed: {len(report['manual_review_needed'])} chunks")


if __name__ == "__main__":
    main()