#!/usr/bin/env python3
"""
AI Chunk Assembler
Assembles AI-converted and validated chunks into final Kotlin file
"""
import os
import json
import argparse
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class AssemblyChunk:
    """Chunk for assembly"""
    chunk_id: str
    kotlin_code: str
    chunk_type: str
    validation_score: float
    needs_review: bool
    tree_path: str = ""

class AIChunkAssembler:
    """Assembles validated AI chunks into final Kotlin file"""
    
    def __init__(self):
        self.assembly_stats = {
            "total_chunks": 0,
            "assembled_chunks": 0,
            "skipped_chunks": 0,
            "review_flagged": 0
        }
        
    def load_validation_report(self, report_file: str) -> Dict:
        """Load validation report"""
        with open(report_file, 'r') as f:
            return json.load(f)
    
    def load_converted_chunks(self, chunks_dir: str, validation_report: Dict) -> List[AssemblyChunk]:
        """Load converted chunks with validation data"""
        chunks = []
        validation_details = {
            item['chunk_id']: item 
            for item in validation_report.get('validation_details', [])
        }
        
        for kt_file in sorted(os.listdir(chunks_dir)):
            if not kt_file.endswith('.kt'):
                continue
                
            chunk_id = kt_file.replace('.kt', '')
            chunk_path = os.path.join(chunks_dir, kt_file)
            
            # Load chunk content
            with open(chunk_path, 'r') as f:
                kotlin_code = f.read()
            
            # Get validation data
            validation_data = validation_details.get(chunk_id, {})
            
            chunk = AssemblyChunk(
                chunk_id=chunk_id,
                kotlin_code=kotlin_code,
                chunk_type=self._infer_chunk_type(chunk_id, kotlin_code),
                validation_score=validation_data.get('score', 0.0),
                needs_review=validation_data.get('needs_manual_review', True)
            )
            
            chunks.append(chunk)
            
        return chunks
    
    def _infer_chunk_type(self, chunk_id: str, kotlin_code: str) -> str:
        """Infer chunk type from ID and content"""
        if 'function' in chunk_id or 'fun ' in kotlin_code:
            return 'function'
        elif 'class' in chunk_id or 'class ' in kotlin_code:
            return 'class'
        elif 'constructor' in chunk_id or 'init' in kotlin_code:
            return 'constructor'
        elif 'property' in chunk_id or 'val ' in kotlin_code or 'var ' in kotlin_code:
            return 'property'
        else:
            return 'unknown'
    
    def assemble_kotlin_file(self, 
                           chunks: List[AssemblyChunk],
                           output_file: str,
                           class_name: str = "CTest",
                           package_name: str = "com.test.kotlin") -> str:
        """Assemble chunks into complete Kotlin file"""
        
        # Organize chunks by type
        organized_chunks = self._organize_chunks_by_type(chunks)
        
        # Generate file content
        kotlin_content = self._generate_kotlin_file(
            organized_chunks, class_name, package_name
        )
        
        # Apply post-processing
        kotlin_content = self._apply_post_processing(kotlin_content)
        
        # Save file
        with open(output_file, 'w') as f:
            f.write(kotlin_content)
        
        # Generate assembly report
        self._generate_assembly_report(chunks, output_file)
        
        return kotlin_content
    
    def _organize_chunks_by_type(self, chunks: List[AssemblyChunk]) -> Dict[str, List[AssemblyChunk]]:
        """Organize chunks by type for proper assembly"""
        organized = {
            'imports': [],
            'constants': [],
            'properties': [],
            'constructors': [],
            'functions': [],
            'unknown': []
        }
        
        for chunk in chunks:
            chunk_type = chunk.chunk_type
            if chunk_type in organized:
                organized[chunk_type].append(chunk)
            else:
                organized['unknown'].append(chunk)
        
        return organized
    
    def _generate_kotlin_file(self, 
                            organized_chunks: Dict[str, List[AssemblyChunk]],
                            class_name: str,
                            package_name: str) -> str:
        """Generate complete Kotlin file content"""
        
        content_parts = []
        
        # Package declaration
        content_parts.append(f"package {package_name}\n")
        
        # File header comment
        content_parts.append("""
///////////////////////////////////////////////////////////////////////////////
//
// file name  : Test.cpp -> {}.kt (AI Converted)
// class name : {}
// Copyright My Company Limited
// Generated by AI-powered conversion workflow
//
//////////////////////////////////////////////////////////////////////////////
""".format(class_name, class_name))
        
        # Imports (if any)
        if organized_chunks['imports']:
            content_parts.append("// Imports")
            for chunk in organized_chunks['imports']:
                content_parts.append(chunk.kotlin_code)
            content_parts.append("")
        
        # Constants (if any)
        if organized_chunks['constants']:
            content_parts.append("// Constants")
            for chunk in organized_chunks['constants']:
                content_parts.append(chunk.kotlin_code)
            content_parts.append("")
        
        # Class declaration
        content_parts.append(f"class {class_name} {{")
        
        # Properties
        if organized_chunks['properties']:
            content_parts.append("    // Properties")
            for chunk in organized_chunks['properties']:
                indented_code = self._indent_code(chunk.kotlin_code, 1)
                content_parts.append(indented_code)
            content_parts.append("")
        
        # Constructors
        if organized_chunks['constructors']:
            content_parts.append("    // Constructors")
            for chunk in organized_chunks['constructors']:
                indented_code = self._indent_code(chunk.kotlin_code, 1)
                content_parts.append(indented_code)
            content_parts.append("")
        
        # Functions
        if organized_chunks['functions']:
            content_parts.append("    // Functions")
            for chunk in organized_chunks['functions']:
                # Add review comment if needed
                if chunk.needs_review:
                    content_parts.append(f"    // TODO: Manual review required (Score: {chunk.validation_score:.2f})")
                
                indented_code = self._indent_code(chunk.kotlin_code, 1)
                content_parts.append(indented_code)
                content_parts.append("")
        
        # Unknown chunks
        if organized_chunks['unknown']:
            content_parts.append("    // Other code")
            for chunk in organized_chunks['unknown']:
                content_parts.append(f"    // Chunk: {chunk.chunk_id}")
                indented_code = self._indent_code(chunk.kotlin_code, 1)
                content_parts.append(indented_code)
                content_parts.append("")
        
        # Close class
        content_parts.append("}")
        
        return "\n".join(content_parts)
    
    def _indent_code(self, code: str, indent_level: int) -> str:
        """Indent code by specified level"""
        indent = "    " * indent_level
        lines = code.split('\n')
        indented_lines = [indent + line if line.strip() else line for line in lines]
        return '\n'.join(indented_lines)
    
    def _apply_post_processing(self, kotlin_content: str) -> str:
        """Apply post-processing fixes"""
        # Remove empty lines at beginning/end of functions
        lines = kotlin_content.split('\n')
        processed_lines = []
        
        in_function = False
        for i, line in enumerate(lines):
            if line.strip().startswith('fun ') or line.strip().startswith('private fun '):
                in_function = True
                processed_lines.append(line)
            elif in_function and line.strip() == '}':
                in_function = False
                processed_lines.append(line)
            elif in_function and not line.strip() and i > 0 and not lines[i-1].strip():
                # Skip duplicate empty lines in functions
                continue
            else:
                processed_lines.append(line)
        
        return '\n'.join(processed_lines)
    
    def _generate_assembly_report(self, chunks: List[AssemblyChunk], output_file: str):
        """Generate assembly report"""
        report = {
            "assembly_summary": {
                "total_chunks": len(chunks),
                "assembled_chunks": len([c for c in chunks if c.validation_score > 0.5]),
                "review_required": len([c for c in chunks if c.needs_review]),
                "average_validation_score": sum(c.validation_score for c in chunks) / len(chunks) if chunks else 0,
                "output_file": output_file
            },
            "chunk_details": [
                {
                    "chunk_id": c.chunk_id,
                    "chunk_type": c.chunk_type,
                    "validation_score": c.validation_score,
                    "needs_review": c.needs_review,
                    "code_lines": len(c.kotlin_code.split('\n'))
                }
                for c in chunks
            ],
            "review_required_chunks": [
                {
                    "chunk_id": c.chunk_id,
                    "chunk_type": c.chunk_type,
                    "validation_score": c.validation_score,
                    "reason": "Low validation score" if c.validation_score < 0.7 else "Flagged for review"
                }
                for c in chunks if c.needs_review
            ]
        }
        
        report_file = output_file.replace('.kt', '_assembly_report.json')
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📊 Assembly report saved to: {report_file}")
        
        # Update stats
        self.assembly_stats["total_chunks"] = len(chunks)
        self.assembly_stats["assembled_chunks"] = len([c for c in chunks if c.validation_score > 0.5])
        self.assembly_stats["review_flagged"] = len([c for c in chunks if c.needs_review])
    
    def print_assembly_summary(self):
        """Print assembly statistics"""
        print("\n" + "="*60)
        print("AI CHUNK ASSEMBLY SUMMARY")
        print("="*60)
        print(f"Total Chunks: {self.assembly_stats['total_chunks']}")
        print(f"Assembled: {self.assembly_stats['assembled_chunks']}")
        print(f"Review Required: {self.assembly_stats['review_flagged']}")
        
        if self.assembly_stats['total_chunks'] > 0:
            assembly_rate = (self.assembly_stats['assembled_chunks'] / 
                           self.assembly_stats['total_chunks']) * 100
            print(f"Assembly Rate: {assembly_rate:.1f}%")
            
            review_rate = (self.assembly_stats['review_flagged'] / 
                         self.assembly_stats['total_chunks']) * 100
            print(f"Review Rate: {review_rate:.1f}%")
        print("="*60)

def main():
    parser = argparse.ArgumentParser(description="AI chunk assembler")
    parser.add_argument("converted_chunks_dir", help="Directory with converted Kotlin chunks")
    parser.add_argument("--validation-report", required=True,
                       help="Validation report JSON file")
    parser.add_argument("--output", default="Test_AI_Complete.kt",
                       help="Output Kotlin file")
    parser.add_argument("--class-name", default="CTest",
                       help="Kotlin class name")
    parser.add_argument("--package-name", default="com.test.kotlin",
                       help="Kotlin package name")
    parser.add_argument("--apply-syntax-fixes", action="store_true",
                       help="Apply additional syntax fixes")
    
    args = parser.parse_args()
    
    # Create assembler
    assembler = AIChunkAssembler()
    
    print(f"🔧 Starting AI chunk assembly")
    print(f"📁 Input chunks: {args.converted_chunks_dir}")
    print(f"📊 Validation report: {args.validation_report}")
    print(f"📄 Output file: {args.output}")
    
    # Load validation report
    validation_report = assembler.load_validation_report(args.validation_report)
    
    # Load converted chunks
    chunks = assembler.load_converted_chunks(args.converted_chunks_dir, validation_report)
    print(f"📦 Loaded {len(chunks)} chunks for assembly")
    
    # Assemble Kotlin file
    kotlin_content = assembler.assemble_kotlin_file(
        chunks, args.output, args.class_name, args.package_name
    )
    
    # Apply additional syntax fixes if requested
    if args.apply_syntax_fixes:
        print("🔧 Applying additional syntax fixes...")
        # This would call the kotlin_syntax_fixer.py if available
        import subprocess
        try:
            result = subprocess.run([
                'python3', 'tools/kotlin_syntax_fixer.py', args.output
            ], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Syntax fixes applied successfully")
            else:
                print(f"⚠️ Syntax fixer warnings: {result.stderr}")
        except FileNotFoundError:
            print("⚠️ kotlin_syntax_fixer.py not found, skipping syntax fixes")
    
    # Print summary
    assembler.print_assembly_summary()
    
    print(f"✅ AI chunk assembly completed! Output: {args.output}")

if __name__ == "__main__":
    main()