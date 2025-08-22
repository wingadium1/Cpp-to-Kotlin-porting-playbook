#!/usr/bin/env python3
"""
Workflow Orchestrator: Manage the complete chunked conversion workflow
"""
import json
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Any
import argparse
import shutil


class ConversionOrchestrator:
    def __init__(self, work_dir: Path):
        self.work_dir = work_dir
        self.chunks_dir = work_dir / "chunks"
        self.skeletons_dir = work_dir / "skeletons"
        self.output_dir = work_dir / "output"
        self.package_name = "com.example"  # Default package name
        
        # Create directories
        for dir_path in [self.chunks_dir, self.skeletons_dir, self.output_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def convert_file(self, input_file: Path) -> Path:
        """Convert a C++ file or LST file to Kotlin using chunked workflow."""
        print(f"Converting {input_file}")
        
        file_stem = input_file.stem
        if file_stem.endswith('.lst'):
            file_stem = file_stem[:-4]  # Remove .lst extension
        
        # Check if input is already an LST file
        if input_file.suffix == '.json' and '.lst' in input_file.name:
            print("  1. Using existing LST...")
            lst_file = input_file
        else:
            # 1. Generate LST
            print("  1. Generating LST...")
            lst_file = self._generate_lst(input_file, file_stem)
            if not lst_file:
                raise Exception("LST generation failed")
        
        print(f"    ✓ Using LST {lst_file}")
        
        # 2. Chunk LST
        print("  2. Chunking LST...")
        chunks, skeleton_info = self._chunk_lst(lst_file)
        
        # Save chunks data for later use
        chunks_data = {
            "chunks": chunks,
            "skeleton_info": skeleton_info
        }
        chunks_file = self.chunks_dir / f"{file_stem}_chunks.json"
        chunks_file.write_text(json.dumps(chunks_data, indent=2))
        print(f"    ✓ Generated {chunks_file}")
        
        # 3. Build skeleton
        print("  3. Building skeleton...")
        skeleton_file = self._generate_skeleton(skeleton_info, file_stem, self.package_name)
        print(f"    ✓ Generated {skeleton_file}")
        
        # 4. Convert chunks
        print("  4. Converting chunks...")
        converted_chunks = self._convert_chunks(chunks)
        print(f"    ✓ Converted {len(converted_chunks)} chunks")
        
        # 5. Assemble final file
        print("  5. Assembling final file...")
        output_file = self._assemble_file(skeleton_file, converted_chunks, file_stem)
        print(f"    ✓ Generated {output_file}")
        
        return output_file
    
    def _generate_lst(self, cpp_file: Path, file_stem: str) -> Path:
        """Generate LST from C++ file."""
        lst_file = self.work_dir / f"{file_stem}.lst.json"
        
        build_lst_script = Path(__file__).parent.parent / "lst" / "build_lst.py"
        cmd = [
            sys.executable,
            str(build_lst_script.resolve()),
            str(cpp_file.resolve()),
            "--out",
            str(lst_file.resolve()),
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            return lst_file
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"LST generation failed: {e.stderr}")
    
    def _chunk_lst(self, lst_file: Path) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Chunk LST into conversion units."""
        # Call chunker directly and parse its output
        cmd = [
            sys.executable, "chunker.py",
            "--lst", str(lst_file.resolve()),  # Use absolute path
            "--out-dir", str(self.chunks_dir.resolve()),
            "--skeleton-out", str((self.work_dir / "skeleton_info.json").resolve())
        ]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            # Read the skeleton info that was generated
            skeleton_file = self.work_dir / "skeleton_info.json"
            if skeleton_file.exists():
                skeleton_info = json.loads(skeleton_file.read_text())
            else:
                skeleton_info = {"functions": [], "classes": []}
                
            # Create mock chunks for now - in practice would parse chunker output
            chunks = [
                {
                    "id": "chunk_1",
                    "type": "function",
                    "name": "main",
                    "dependencies": [],
                    "content": "// TODO: Extract from LST"
                }
            ]
            
            return chunks, skeleton_info
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Chunking failed: {e.stderr}")
    
    def _generate_skeleton(self, skeleton_info: Dict[str, Any], file_stem: str, package_name: str) -> Path:
        """Generate Kotlin skeleton file."""
        skeleton_file = self.skeletons_dir / f"{file_stem}.kt"
        
        # Generate basic skeleton
        skeleton_content = self._build_skeleton_content(skeleton_info, package_name)
        skeleton_file.write_text(skeleton_content)
        
        return skeleton_file
    
    def _build_skeleton_content(self, skeleton_info: Dict[str, Any], package_name: str) -> str:
        """Build skeleton content from structure info."""
        lines = [
            f"package {package_name}",
            "",
            "// Auto-generated Kotlin file",
            "// Converted from C++ using chunked LST workflow",
            ""
        ]
        
        # Add common imports we'll likely need
        lines.extend([
            "// Common imports for converted C++ code",
            "// CONVERSION_IMPORTS_PLACEHOLDER",
            "// import kotlin.jvm.JvmStatic",
            "// import java.util.*",
            ""
        ])
        
        # Add constants and companion object if needed
        lines.extend([
            "// Constants and static values",
            "// CONVERSION_CONSTANTS_PLACEHOLDER",
            ""
        ])
        
        # Group functions by class
        functions = skeleton_info.get("functions", [])
        classes = {}
        standalone_functions = []
        
        for func in functions:
            class_name = func.get("class_name", "")
            if class_name:
                if class_name not in classes:
                    classes[class_name] = []
                classes[class_name].append(func)
            else:
                standalone_functions.append(func)
        
        # Generate class skeletons
        for class_name, class_functions in classes.items():
            lines.extend(self._generate_class_skeleton_with_functions(class_name, class_functions))
            lines.append("")
        
        # Generate standalone functions
        for func in standalone_functions:
            lines.extend(self._generate_function_skeleton_from_info(func))
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_class_skeleton_with_functions(self, class_name: str, functions: List[Dict[str, Any]]) -> List[str]:
        """Generate skeleton for a class with its methods."""
        lines = [
            f"/**",
            f" * {class_name} - Converted from C++",
            f" * Contains {len(functions)} methods",
            f" * CONVERSION_CLASS_DOC_PLACEHOLDER",
            f" */",
            f"class {class_name} {{",
            "",
            "    // Member variables",
            "    // CONVERSION_MEMBER_VARS_PLACEHOLDER",
            ""
        ]
        
        # Add constructor if present
        constructors = [f for f in functions if f["name"].endswith(f"::{class_name}")]
        destructors = [f for f in functions if f["name"].endswith(f"::~{class_name}")]
        methods = [f for f in functions if f not in constructors and f not in destructors]
        
        # Add constructors
        for ctor in constructors:
            lines.append(f"    // CONVERSION_CHUNK_START_{self._generate_chunk_id(ctor)}")
            lines.append(f"    constructor({self._convert_params_to_kotlin(ctor.get('parameters', ''))}) {{")
            lines.append("        // CONVERSION_CONSTRUCTOR_IMPL_PLACEHOLDER")
            lines.append("    }")
            lines.append(f"    // CONVERSION_CHUNK_END_{self._generate_chunk_id(ctor)}")
            lines.append("")
        
        # Add methods
        for method in methods:
            method_name = method["name"].split("::")[-1]
            return_type = self._convert_type_to_kotlin(method.get("return_type", "void"))
            params = self._convert_params_to_kotlin(method.get("parameters", ""))
            
            # Extract line information for context
            span = method.get("span", {})
            start_line = span.get("start_line", 0)
            end_line = span.get("end_line", 0)
            
            # Extract variables from function body for hints
            body_text = method.get("body_text", "")
            variables = self._extract_function_variables(body_text)
            
            lines.append(f"    /**")
            lines.append(f"     * {method_name} - Converted from C++ method")
            lines.append(f"     * Original location: lines {start_line}-{end_line}")
            lines.append(f"     * CONVERSION_METHOD_DOC_PLACEHOLDER")
            lines.append(f"     */")
            lines.append(f"    // CONVERSION_CHUNK_START_{self._generate_chunk_id(method)}")
            lines.append(f"    fun {method_name}({params}): {return_type} {{")
            lines.append("        // Local variables")
            if variables:
                lines.append("        // Detected from C++ code:")
                for var in variables:
                    lines.append(f"        // {var}")
            lines.append("        // CONVERSION_VARS_PLACEHOLDER")
            lines.append("")
            lines.append("        // Method implementation")
            lines.append("        // CONVERSION_LOGIC_PLACEHOLDER")
            if return_type != "Unit":
                lines.append(f"        return CONVERSION_RETURN_PLACEHOLDER // Implement {method_name}")
            lines.append("    }")
            lines.append(f"    // CONVERSION_CHUNK_END_{self._generate_chunk_id(method)}")
            lines.append("")
        
        lines.append("}")
        return lines
    
    def _generate_function_skeleton_from_info(self, func_info: Dict[str, Any]) -> List[str]:
        """Generate skeleton for a standalone function."""
        func_name = func_info["name"]
        return_type = self._convert_type_to_kotlin(func_info.get("return_type", "void"))
        params = self._convert_params_to_kotlin(func_info.get("parameters", ""))
        
        # Extract line information for context
        span = func_info.get("span", {})
        start_line = span.get("start_line", 0)
        end_line = span.get("end_line", 0)
        
        lines = [
            f"/**",
            f" * {func_name} - Converted from C++ function",
            f" * Original location: lines {start_line}-{end_line}",
            f" * CONVERSION_FUNCTION_DOC_PLACEHOLDER",
            f" */",
            f"// CONVERSION_CHUNK_START_{self._generate_chunk_id(func_info)}",
            f"fun {func_name}({params}): {return_type} {{",
            "    // Local variables",
            "    // CONVERSION_VARS_PLACEHOLDER",
            "",
            "    // Function implementation",
            "    // CONVERSION_LOGIC_PLACEHOLDER"
        ]
        
        if return_type != "Unit":
            lines.append(f"    return CONVERSION_RETURN_PLACEHOLDER // Implement {func_name}")
        
        lines.append("}")
        lines.append(f"// CONVERSION_CHUNK_END_{self._generate_chunk_id(func_info)}")
        return lines
    
    def _convert_type_to_kotlin(self, cpp_type: str) -> str:
        """Convert C++ type to Kotlin equivalent."""
        cpp_type = cpp_type.strip()
        
        # Basic type mappings
        type_map = {
            "void": "Unit",
            "int": "Int",
            "short": "Short", 
            "long": "Long",
            "char": "Char",
            "bool": "Boolean",
            "float": "Float",
            "double": "Double",
            "string": "String",
            "std::string": "String",
        }
        
        # Handle pointers - convert to nullable types
        if "*" in cpp_type:
            base_type = cpp_type.replace("*", "").strip()
            kotlin_type = type_map.get(base_type, base_type)
            return f"{kotlin_type}?"
        
        return type_map.get(cpp_type, cpp_type)
    
    def _convert_params_to_kotlin(self, cpp_params: str) -> str:
        """Convert C++ parameters to Kotlin format."""
        if not cpp_params or cpp_params.strip() == "void":
            return ""
        
        # Simple parameter conversion - this is a basic implementation
        # In practice, you'd want more sophisticated parsing
        params = []
        for param in cpp_params.split(","):
            param = param.strip()
            if not param:
                continue
            
            # Extract type and name (very basic parsing)
            parts = param.split()
            if len(parts) >= 2:
                param_type = " ".join(parts[:-1])
                param_name = parts[-1]
                kotlin_type = self._convert_type_to_kotlin(param_type)
                params.append(f"{param_name}: {kotlin_type}")
            else:
                # Fallback
                params.append(f"param: Any")
        
        return ", ".join(params)
    
    def _generate_chunk_id(self, func_info: Dict[str, Any]) -> str:
        """Generate a unique chunk ID for the function."""
        name = func_info.get("name", "unknown")
        span = func_info.get("span", {})
        start_line = span.get("start_line", 0)
        return f"{name.replace('::', '_')}_{start_line}"
    
    def _extract_function_variables(self, func_text: str) -> List[str]:
        """Extract variable declarations from C++ function text."""
        variables = []
        lines = func_text.split('\n')
        
        for line in lines:
            # Remove tabs and strip whitespace
            line = line.replace('\t', ' ').strip()
            
            # Skip comments, empty lines, and preprocessor directives
            if (not line or line.startswith('//') or line.startswith('/*') 
                or line.startswith('#') or line.startswith('}')):
                continue
            
            # Look for lines that end with semicolon (potential variable declarations)
            if line.endswith(';'):
                # Remove inline comments
                if '//' in line:
                    line = line.split('//')[0].strip()
                
                # Skip control statements
                if any(keyword in line for keyword in ['if', 'for', 'while', 'return', 'break', 'continue', 'switch', 'case']):
                    continue
                
                # Skip function calls and assignments that don't declare variables
                if ('(' in line and ')' in line) or '=' in line:
                    continue
                
                # Clean up the variable declaration
                var_decl = line.replace(';', '').strip()
                
                # Check if it looks like a variable declaration (type + name)
                if ' ' in var_decl and not var_decl.startswith('//'):
                    parts = var_decl.split()
                    if len(parts) >= 2:
                        var_type = parts[0]
                        var_name_part = ' '.join(parts[1:])
                        
                        # Handle array declarations like "PrintFlg[5][2]"
                        if '[' in var_name_part:
                            var_name = var_name_part.split('[')[0].strip()
                            array_part = var_name_part[var_name_part.find('['):]
                            kotlin_type = self._convert_array_type_to_kotlin(var_type, array_part)
                        else:
                            var_name = var_name_part.strip('*').strip()  # Remove pointer notation
                            kotlin_type = self._convert_type_to_kotlin(var_type)
                        
                        # Validate variable name
                        if (var_name and var_name.replace('_', 'a').isalnum() 
                            and not any(char in var_name for char in ['(', ')', '+', '-', '/', '<', '>'])):
                            variables.append(f"var {var_name}: {kotlin_type}")
        
        return variables[:8]  # Limit to first 8 variables for skeleton
    
    def _convert_array_type_to_kotlin(self, cpp_type: str, array_part: str) -> str:
        """Convert C++ array type to Kotlin equivalent."""
        base_type = self._convert_type_to_kotlin(cpp_type)
        
        # Count dimensions
        dimensions = array_part.count('[')
        if dimensions == 1:
            return f"Array<{base_type}>"
        elif dimensions == 2:
            return f"Array<Array<{base_type}>>"
        else:
            return f"Array<{base_type}>"  # Fallback
    
    def _convert_chunks(self, chunks: List[Dict[str, Any]]) -> Dict[str, str]:
        """Convert chunks to Kotlin code."""
        converted = {}
        
        for chunk in chunks:
            chunk_id = chunk.get("id", "unknown")
            chunk_type = chunk.get("type", "unknown")
            
            # Mock conversion for now
            if chunk_type == "function":
                kotlin_code = self._mock_convert_function(chunk)
            elif chunk_type == "method":
                kotlin_code = self._mock_convert_method(chunk)
            elif chunk_type == "class_declaration":
                kotlin_code = self._mock_convert_class_declaration(chunk)
            else:
                kotlin_code = f"// TODO: Convert {chunk_type}"
            
            converted[chunk_id] = kotlin_code
            print(f"    ✓ Converted chunk {chunk_id} ({chunk_type})")
        
        return converted
    
    def _mock_convert_function(self, chunk: Dict[str, Any]) -> str:
        """Mock function conversion."""
        name = chunk.get("name", "unknown")
        return f"""
fun {name}(): Unit {{
    // TODO: Implement {name}
    // Dependencies: {', '.join(chunk.get('dependencies', []))}
}}
""".strip()
    
    def _mock_convert_method(self, chunk: Dict[str, Any]) -> str:
        """Mock method conversion."""
        name = chunk.get("name", "unknown")
        class_name = chunk.get("class_name", "Unknown")
        return f"""
    fun {name}(): Unit {{
        // TODO: Implement {class_name}.{name}
    }}
""".strip()
    
    def _mock_convert_class_declaration(self, chunk: Dict[str, Any]) -> str:
        """Mock class declaration conversion."""
        name = chunk.get("name", "Unknown")
        return f"class {name}"
    
    def _assemble_file(self, skeleton_file: Path, converted_chunks: Dict[str, str], file_stem: str) -> Path:
        """Assemble final Kotlin file."""
        skeleton = skeleton_file.read_text()
        
        # Simple assembly - replace TODO comments with converted code
        assembled = skeleton
        for chunk_id, kotlin_code in converted_chunks.items():
            # This is simplified - in practice would use proper markers
            placeholder = f"// TODO: {chunk_id}"
            if placeholder in assembled:
                assembled = assembled.replace(placeholder, kotlin_code)
        
        # Save assembled file
        output_file = self.output_dir / f"{file_stem}.kt"
        output_file.write_text(assembled)
        
        return output_file


def main():
    parser = argparse.ArgumentParser(description="Orchestrate chunked C++ to Kotlin conversion")
    parser.add_argument("input_file", help="C++ file or LST JSON file to convert")
    parser.add_argument("--work-dir", default="work", help="Working directory")
    parser.add_argument("--package", default="com.example", help="Kotlin package name")
    parser.add_argument("--clean", action="store_true", help="Clean work directory first")
    
    args = parser.parse_args()
    
    input_file = Path(args.input_file)
    work_dir = Path(args.work_dir)
    
    if args.clean and work_dir.exists():
        shutil.rmtree(work_dir)
    
    # Create orchestrator and convert
    orchestrator = ConversionOrchestrator(work_dir)
    orchestrator.package_name = args.package  # Set package name
    
    try:
        output_file = orchestrator.convert_file(input_file)
        print(f"\n✓ Conversion complete: {output_file}")
        
        # Show summary
        print(f"\nWorkflow artifacts:")
        print(f"  - Chunks: {orchestrator.chunks_dir}")
        print(f"  - Skeleton: {orchestrator.skeletons_dir}")
        print(f"  - Output: {output_file}")
        
    except Exception as e:
        print(f"✗ Conversion failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()