#!/usr/bin/env python3
"""
Systematic Chunk Converter
Converts each function chunk from C++ to Kotlin with full business logic
"""
import json
import os
import re
from typing import Dict, List

class ChunkConverter:
    def __init__(self, chunks_dir: str, manifest_file: str):
        self.chunks_dir = chunks_dir
        self.manifest_file = manifest_file
        self.manifest = None
        self.load_manifest()
    
    def load_manifest(self):
        """Load chunk manifest"""
        with open(self.manifest_file, 'r', encoding='utf-8') as f:
            self.manifest = json.load(f)
    
    def convert_cpp_to_kotlin_name(self, cpp_name: str) -> str:
        """Convert C++ function name to Kotlin camelCase"""
        if '::' in cpp_name:
            kotlin_name = cpp_name.split('::')[1]  # Remove CTest:: prefix
        else:
            kotlin_name = cpp_name
        
        # Convert to camelCase (first letter lowercase)
        if kotlin_name:
            kotlin_name = kotlin_name[0].lower() + kotlin_name[1:]
        
        return kotlin_name
    
    def convert_cpp_types(self, cpp_type: str) -> str:
        """Convert C++ types to Kotlin types"""
        type_mapping = {
            'void': 'Unit',
            'int': 'Int',
            'short': 'Short',
            'long': 'Long',
            'char': 'Char',
            'char*': 'String',
            'char[]': 'CharArray',
            'CString': 'String',
            'bool': 'Boolean'
        }
        
        for cpp, kotlin in type_mapping.items():
            cpp_type = cpp_type.replace(cpp, kotlin)
        
        return cpp_type
    
    def extract_function_signature(self, header: str) -> tuple:
        """Extract function name and parameters from C++ header"""
        # Parse C++ function header
        # Example: "void CTest::SetHaraRyosyu( void ) "
        
        # Extract return type
        parts = header.strip().split()
        if len(parts) >= 2:
            return_type = parts[0]
            remaining = ' '.join(parts[1:])
            
            # Extract function name and parameters
            if '::' in remaining:
                func_part = remaining.split('::')[1]
            else:
                func_part = remaining
            
            if '(' in func_part:
                func_name = func_part.split('(')[0].strip()
                params_part = func_part.split('(')[1].split(')')[0].strip()
                
                # Convert function name to camelCase
                kotlin_func_name = self.convert_cpp_to_kotlin_name(f"CTest::{func_name}")
                
                # Convert return type
                kotlin_return_type = self.convert_cpp_types(return_type)
                if kotlin_return_type == 'Unit':
                    kotlin_return_type = ''
                
                # Convert parameters
                kotlin_params = self.convert_parameters(params_part)
                
                return kotlin_func_name, kotlin_params, kotlin_return_type
        
        return "unknownFunction", "", ""
    
    def convert_parameters(self, cpp_params: str) -> str:
        """Convert C++ parameters to Kotlin"""
        if not cpp_params or cpp_params.strip() == 'void':
            return ""
        
        # This is a simplified parameter conversion
        # For complex parameters, manual review would be needed
        params = []
        for param in cpp_params.split(','):
            param = param.strip()
            if param:
                # Simple type conversion
                kotlin_param = self.convert_cpp_types(param)
                params.append(f"param: {kotlin_param}")
        
        return ", ".join(params)
    
    def convert_c_style_comments(self, text: str) -> str:
        """Convert C-style comments to Kotlin style"""
        # Convert // comments
        text = re.sub(r'//(.*)$', r'//\1', text, flags=re.MULTILINE)
        
        # Convert /* */ comments  
        text = re.sub(r'/\*(.*?)\*/', r'/*\1*/', text, flags=re.DOTALL)
        
        return text
    
    def convert_function_body(self, cpp_body: str) -> str:
        """Convert C++ function body to Kotlin"""
        kotlin_body = cpp_body
        
        # Preserve all comments exactly
        kotlin_body = self.convert_c_style_comments(kotlin_body)
        
        # Convert C++ specific constructs to proper Kotlin
        conversions = [
            # 1. C++ pointer syntax to Kotlin property access
            (r'ccPrinter->', r'ccPrinter.'),
            
            # 2. Remove C++ cast syntax
            (r'\(char \*\)', r''),
            
            # 3. Fix string formatting - convert broken pattern to proper Kotlin
            (r'val temp = String\.format\("([^"]*)",\s*([^)]+)\);\s*(\w+)\s*=\s*temp\.toCharArray\(\);?', 
             r'\3 = String.format("\1", \2)'),
            
            # 4. Variable declarations
            (r'\bchar\s+(\w+)\[(\d+)\]', r'var \1 = CharArray(\2)'),
            (r'\bchar\s+(\w+)\[([^\]]+)\]', r'var \1 = CharArray(\2)'),
            (r'\bchar\s+(\w+);', r'var \1: String = ""'),
            (r'\bint\s+(\w+);', r'var \1: Int = 0'),
            (r'\bshort\s+(\w+);', r'var \1: Short = 0'),
            (r'\blong\s+(\w+);', r'var \1: Long = 0L'),
            (r'\bCString\s+(\w+);', r'var \1: String = ""'),
            (r'\bunsigned\s+short\s+(\w+)', r'var \1: UShort = 0u'),
            
            # 5. String operations - convert to Kotlin equivalents
            (r'strcpy\(([^,]+),\s*([^)]+)\)', r'\1 = \2'),
            (r'strcat\(([^,]+),\s*([^)]+)\)', r'\1 += \2'),
            (r'sprintf\(([^,]+),\s*"([^"]*)",\s*([^)]+)\)', r'\1 = String.format("\2", \3)'),
            (r'strlen\(([^)]+)\)', r'\1.length'),
            
            # 6. Memory operations
            (r'memset\(([^,]+),\s*NULL,\s*sizeof\([^)]+\)\)', r'// memset equivalent: \1.fill(\'\\0\')'),
            (r'strncpy\(([^,]+),\s*([^,]+),\s*([^)]+)\)', r'System.arraycopy(\2.toCharArray(), 0, \1, 0, minOf(\3, \2.length))'),
            
            # 7. Control structures
            (r'if\s*\(\s*([^)]+)\s*\)\s*{', r'if (\1) {'),
            (r'}\s*else\s*{', r'} else {'),
            (r'for\s*\(\s*([^;]+);\s*([^;]+);\s*([^)]+)\s*\)', r'for (\1; \2; \3)'),
            
            # 8. Null/NULL conversion
            (r'\bNULL\b', r'null'),
            
            # 9. Increment/decrement operators
            (r'(\w+)\+\+', r'\1++'),
            (r'(\w+)--', r'\1--'),
            
            # 10. Array access with address operator
            (r'&([a-zA-Z_]\w*)\[(\d+)\]', r'\1[\2]'),
            
            # 11. Fix Macro calls to use proper Kotlin syntax
            (r'Macro\.strcat\(([^,]+),\s*([^)]+)\)', r'Macro.strcat(\1, \2)'),
            (r'Macro\.strnumber\(([^,]+),\s*([^,]+),\s*([^)]+)\)', r'Macro.strnumber(\1, \2, \3)'),
            
            # 12. Fix ccPrinter method calls
            (r'ccPrinter\.strnumber\(([^)]+)\)', r'ccPrinter.strnumber(\1)'),
            (r'ccPrinter\.SetOkyeu\(([^)]+)\)', r'ccPrinter.setOkyeu(\1)'),
            (r'ccPrinter\.SetEigyo\(([^)]+)\)', r'ccPrinter.setEigyo(\1)'),
        ]
        
        for pattern, replacement in conversions:
            kotlin_body = re.sub(pattern, replacement, kotlin_body)
        
        return kotlin_body
    
    def convert_chunk(self, chunk_file: str) -> str:
        """Convert a single chunk file to Kotlin"""
        with open(chunk_file, 'r', encoding='utf-8') as f:
            chunk_data = json.load(f)
        
        if chunk_data['kind'] != 'function':
            return ""
        
        header = chunk_data.get('header', '')
        text = chunk_data.get('text', '')
        
        # Extract function signature
        func_name, params, return_type = self.extract_function_signature(header)
        
        # Convert function body
        kotlin_body = self.convert_function_body(text)
        
        # Create Kotlin function
        if return_type:
            signature = f"fun {func_name}({params}): {return_type}"
        else:
            signature = f"fun {func_name}({params})"
        
        # Extract just the body part (remove C++ function declaration)
        body_lines = text.split('\n')[1:]  # Skip first line with function declaration
        if body_lines and body_lines[0].strip() == '{':
            body_lines = body_lines[1:]  # Skip opening brace
        if body_lines and body_lines[-1].strip() == '}':
            body_lines = body_lines[:-1]  # Skip closing brace
        
        kotlin_function_body = '\n'.join(body_lines)
        kotlin_function_body = self.convert_function_body(kotlin_function_body)
        
        kotlin_function = f"""    {signature} {{
{kotlin_function_body}
    }}"""
        
        return kotlin_function
    
    def convert_all_functions(self) -> str:
        """Convert all function chunks to Kotlin"""
        kotlin_functions = []
        
        chunk_files = [f for f in os.listdir(self.chunks_dir) if f.endswith('.json')]
        chunk_files.sort()  # Process in order
        
        for chunk_file in chunk_files:
            chunk_path = os.path.join(self.chunks_dir, chunk_file)
            kotlin_func = self.convert_chunk(chunk_path)
            if kotlin_func:
                kotlin_functions.append(kotlin_func)
        
        return '\n\n'.join(kotlin_functions)
    
    def update_kotlin_file(self, kotlin_file: str, functions_kotlin: str):
        """Update the Kotlin file with converted functions"""
        with open(kotlin_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the CTest class and replace function implementations
        class_start = content.find('class CTest')
        if class_start == -1:
            print("❌ Could not find CTest class in Kotlin file")
            return
        
        class_end = content.rfind('}')  # Last closing brace
        
        # Replace placeholder functions with actual implementations
        before_class = content[:class_start]
        after_class = content[class_end+1:]
        
        # Create new class content
        new_class_content = f"""class CTest {{
    // Printer instance for output operations
    private lateinit var ccPrinter: CPrinter

{functions_kotlin}
}}"""
        
        new_content = before_class + new_class_content + after_class
        
        with open(kotlin_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Updated {kotlin_file} with converted function implementations")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Systematic Chunk Converter')
    parser.add_argument('chunks_dir', help='Directory containing chunk JSON files')
    parser.add_argument('manifest_file', help='Path to chunk manifest JSON file')
    parser.add_argument('--kotlin-file', help='Kotlin file to update')
    parser.add_argument('--output', help='Output file for converted functions')
    
    args = parser.parse_args()
    
    # Create converter
    converter = ChunkConverter(args.chunks_dir, args.manifest_file)
    
    # Convert all functions
    print("Converting all function chunks...")
    kotlin_functions = converter.convert_all_functions()
    
    # Output results
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(kotlin_functions)
        print(f"Converted functions written to: {args.output}")
    
    # Update Kotlin file if specified
    if args.kotlin_file:
        converter.update_kotlin_file(args.kotlin_file, kotlin_functions)
    
    print("✅ Conversion complete!")

if __name__ == "__main__":
    main()