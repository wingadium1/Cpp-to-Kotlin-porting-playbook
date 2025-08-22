#!/usr/bin/env python3
"""
Coarse Chunk Assembler for C++ to Kotlin Conversion

This script assembles the converted coarse chunks into a complete Kotlin class file,
maintaining the original structure and organizing the chunks by function/method.
"""

import json
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict


def load_converted_chunks(converted_chunks_path: str) -> Dict[str, Any]:
    """Load the converted chunks from JSON file."""
    try:
        with open(converted_chunks_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading converted chunks: {e}")
        sys.exit(1)


def load_skeleton(skeleton_path: str) -> Dict[str, Any]:
    """Load the skeleton structure from JSON file."""
    try:
        with open(skeleton_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading skeleton: {e}")
        sys.exit(1)


def organize_chunks_by_function(converted_chunks: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """Organize chunks by function name."""
    function_chunks = defaultdict(list)
    
    for chunk_id, chunk_data in converted_chunks.items():
        function_name = chunk_data.get('conversion_context', {}).get('function_name', 'unknown')
        
        # Clean up function name (remove CTest:: prefix if present)
        if function_name.startswith('CTest::'):
            function_name = function_name[7:]
        
        function_chunks[function_name].append({
            'chunk_id': chunk_id,
            'kotlin_code': chunk_data.get('kotlin_code', ''),
            'original_chunk_id': chunk_data.get('original_chunk_id', chunk_id),
            'context': chunk_data.get('conversion_context', {})
        })
    
    # Sort chunks within each function by chunk ID (maintains order)
    for function_name in function_chunks:
        function_chunks[function_name].sort(key=lambda x: int(x['chunk_id'].split('_')[1]))
    
    return function_chunks


def generate_kotlin_class(function_chunks: Dict[str, List[Dict[str, Any]]], 
                         skeleton: Dict[str, Any], 
                         class_name: str = "Test") -> str:
    """Generate the complete Kotlin class from organized chunks."""
    
    kotlin_code = []
    
    # Add package and imports
    kotlin_code.append("package com.example.gassystem")
    kotlin_code.append("")
    kotlin_code.append("import java.lang.StringBuilder")
    kotlin_code.append("import kotlin.math.*")
    kotlin_code.append("")
    
    # Start class definition
    kotlin_code.append(f"class {class_name} {{")
    kotlin_code.append("")
    
    # Add class properties (extracted from skeleton if available)
    if 'properties' in skeleton:
        kotlin_code.append("    // Class properties")
        for prop in skeleton['properties']:
            kotlin_code.append(f"    private var {prop['name']}: {prop['type']} = {prop.get('default', 'null')}")
        kotlin_code.append("")
    
    # Process each function
    processed_functions = set()
    for function_name, chunks in function_chunks.items():
        if function_name == 'unknown' or function_name in processed_functions:
            continue
        
        processed_functions.add(function_name)
        
        # Add function header
        kotlin_code.append(f"    /**")
        kotlin_code.append(f"     * {function_name} - Converted from C++")
        kotlin_code.append(f"     * Total chunks: {len(chunks)}")
        kotlin_code.append(f"     */")
        
        # Determine function signature
        first_chunk = chunks[0] if chunks else {}
        context = first_chunk.get('context', {})
        
        # For now, use a generic signature
        kotlin_code.append(f"    fun {function_name}(): Unit {{")
        kotlin_code.append("")
        
        # Add function body from chunks
        for i, chunk in enumerate(chunks):
            code = chunk['kotlin_code'].strip()
            if code:
                # Add comment with chunk info
                kotlin_code.append(f"        // Chunk {chunk['chunk_id']}")
                
                # Process the code - add proper indentation
                code_lines = code.split('\n')
                for line in code_lines:
                    if line.strip():
                        # Add base indentation for function body
                        kotlin_code.append(f"        {line}")
                    else:
                        kotlin_code.append("")
                
                # Add separator between chunks
                if i < len(chunks) - 1:
                    kotlin_code.append("")
        
        kotlin_code.append("    }")
        kotlin_code.append("")
    
    # Add unknown chunks as separate section
    if 'unknown' in function_chunks:
        kotlin_code.append("    /**")
        kotlin_code.append("     * Unknown/global chunks")
        kotlin_code.append("     */")
        kotlin_code.append("    private fun processUnknownChunks(): Unit {")
        
        for chunk in function_chunks['unknown']:
            code = chunk['kotlin_code'].strip()
            if code:
                kotlin_code.append(f"        // Chunk {chunk['chunk_id']}")
                code_lines = code.split('\n')
                for line in code_lines:
                    if line.strip():
                        kotlin_code.append(f"        {line}")
                kotlin_code.append("")
        
        kotlin_code.append("    }")
        kotlin_code.append("")
    
    # Close class
    kotlin_code.append("}")
    kotlin_code.append("")
    
    return '\n'.join(kotlin_code)


def create_assembly_report(function_chunks: Dict[str, List[Dict[str, Any]]], 
                          output_path: str) -> Dict[str, Any]:
    """Create a report of the assembly process."""
    
    report = {
        "assembly_summary": {
            "total_functions": len([f for f in function_chunks.keys() if f != 'unknown']),
            "total_chunks_assembled": sum(len(chunks) for chunks in function_chunks.values()),
            "unknown_chunks": len(function_chunks.get('unknown', []))
        },
        "function_breakdown": {}
    }
    
    for function_name, chunks in function_chunks.items():
        report["function_breakdown"][function_name] = {
            "chunk_count": len(chunks),
            "chunk_ids": [chunk['chunk_id'] for chunk in chunks],
            "has_code": any(chunk['kotlin_code'].strip() for chunk in chunks)
        }
    
    # Save report
    report_path = str(Path(output_path).parent / "assembly_report.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    return report


def main():
    parser = argparse.ArgumentParser(description='Assemble converted coarse chunks into Kotlin class')
    parser.add_argument('--converted-chunks', required=True, 
                       help='Path to converted chunks JSON file')
    parser.add_argument('--skeleton', 
                       help='Path to skeleton JSON file (optional)')
    parser.add_argument('--output', required=True,
                       help='Output Kotlin file path')
    parser.add_argument('--class-name', default='Test',
                       help='Name of the generated Kotlin class')
    
    args = parser.parse_args()
    
    print("🔧 Assembling converted chunks into Kotlin class...")
    
    # Load data
    converted_chunks = load_converted_chunks(args.converted_chunks)
    skeleton = {}
    if args.skeleton:
        skeleton = load_skeleton(args.skeleton)
    
    print(f"📦 Loaded {len(converted_chunks)} converted chunks")
    
    # Organize chunks by function
    function_chunks = organize_chunks_by_function(converted_chunks)
    print(f"🏗️  Organized into {len(function_chunks)} functions")
    
    # Generate Kotlin class
    kotlin_class = generate_kotlin_class(function_chunks, skeleton, args.class_name)
    
    # Write output
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(kotlin_class)
    
    # Create assembly report
    report = create_assembly_report(function_chunks, args.output)
    
    print(f"✅ Kotlin class assembled successfully!")
    print(f"📄 Output: {args.output}")
    print(f"📊 Functions: {report['assembly_summary']['total_functions']}")
    print(f"📦 Chunks: {report['assembly_summary']['total_chunks_assembled']}")
    print(f"❓ Unknown chunks: {report['assembly_summary']['unknown_chunks']}")


if __name__ == "__main__":
    main()