#!/usr/bin/env python3
"""
Chunk Conversion Tracker
Tracks conversion progress and ensures no chunks are missed
"""
import json
import os
from typing import Dict, List, Set
from dataclasses import dataclass

@dataclass
class ConversionStatus:
    chunk_id: str
    kind: str
    name: str
    tree_path: str
    converted: bool = False
    in_skeleton: bool = False
    in_final_kotlin: bool = False
    conversion_notes: str = ""

class ChunkTracker:
    def __init__(self, manifest_file: str):
        self.manifest_file = manifest_file
        self.manifest = None
        self.conversion_status: Dict[str, ConversionStatus] = {}
        self.load_manifest()
        self.initialize_tracking()
    
    def load_manifest(self):
        """Load chunk manifest"""
        with open(self.manifest_file, 'r', encoding='utf-8') as f:
            self.manifest = json.load(f)
        print(f"Loaded manifest with {self.manifest['total_chunks']} chunks")
    
    def initialize_tracking(self):
        """Initialize conversion tracking for all chunks"""
        for chunk_id, chunk_info in self.manifest['chunks'].items():
            self.conversion_status[chunk_id] = ConversionStatus(
                chunk_id=chunk_id,
                kind=chunk_info['kind'],
                name=chunk_info['name'],
                tree_path=chunk_info['tree_path']
            )
    
    def mark_converted(self, chunk_id: str, notes: str = ""):
        """Mark a chunk as converted"""
        if chunk_id in self.conversion_status:
            self.conversion_status[chunk_id].converted = True
            self.conversion_status[chunk_id].conversion_notes = notes
            print(f"✅ Marked {chunk_id} as converted")
        else:
            print(f"❌ Unknown chunk_id: {chunk_id}")
    
    def mark_in_skeleton(self, chunk_id: str):
        """Mark a chunk as included in skeleton"""
        if chunk_id in self.conversion_status:
            self.conversion_status[chunk_id].in_skeleton = True
    
    def mark_in_final(self, chunk_id: str):
        """Mark a chunk as included in final Kotlin file"""
        if chunk_id in self.conversion_status:
            self.conversion_status[chunk_id].in_final_kotlin = True
    
    def get_unconverted_chunks(self) -> List[ConversionStatus]:
        """Get list of chunks not yet converted"""
        return [status for status in self.conversion_status.values() 
                if not status.converted]
    
    def get_function_chunks(self) -> List[ConversionStatus]:
        """Get all function chunks"""
        return [status for status in self.conversion_status.values() 
                if status.kind == 'function']
    
    def get_missing_from_skeleton(self) -> List[ConversionStatus]:
        """Get chunks missing from skeleton"""
        return [status for status in self.conversion_status.values() 
                if not status.in_skeleton and status.kind in ['function', 'class']]
    
    def get_missing_from_final(self) -> List[ConversionStatus]:
        """Get chunks missing from final Kotlin"""
        return [status for status in self.conversion_status.values() 
                if not status.in_final_kotlin and status.kind in ['function', 'class']]
    
    def verify_kotlin_file_coverage(self, kotlin_file: str):
        """Verify that Kotlin file contains all expected chunks"""
        with open(kotlin_file, 'r', encoding='utf-8') as f:
            kotlin_content = f.read()
        
        # Check function coverage
        function_chunks = self.get_function_chunks()
        missing_functions = []
        
        for func_status in function_chunks:
            # Convert C++ function name to expected Kotlin name
            cpp_name = func_status.name
            if '::' in cpp_name:
                kotlin_name = cpp_name.split('::')[1]  # Remove CTest:: prefix
                
                # Convert to camelCase (first letter lowercase)
                if kotlin_name:
                    kotlin_name = kotlin_name[0].lower() + kotlin_name[1:]
                
                # Check if function exists in Kotlin file
                if f"fun {kotlin_name}(" in kotlin_content:
                    self.mark_in_final(func_status.chunk_id)
                    print(f"✅ Found {kotlin_name} in Kotlin file")
                else:
                    missing_functions.append(func_status)
                    print(f"❌ Missing {kotlin_name} from Kotlin file")
        
        return missing_functions
    
    def generate_coverage_report(self) -> str:
        """Generate detailed coverage report"""
        total_chunks = len(self.conversion_status)
        converted_chunks = len([s for s in self.conversion_status.values() if s.converted])
        function_chunks = self.get_function_chunks()
        unconverted_functions = [f for f in function_chunks if not f.converted]
        
        report = f"""
=== CHUNK CONVERSION COVERAGE REPORT ===

Overall Coverage:
  Total chunks: {total_chunks}
  Converted chunks: {converted_chunks}
  Coverage percentage: {(converted_chunks/total_chunks)*100:.1f}%

Function Coverage:
  Total functions: {len(function_chunks)}
  Converted functions: {len(function_chunks) - len(unconverted_functions)}
  Unconverted functions: {len(unconverted_functions)}

Unconverted Functions:
"""
        for func in unconverted_functions:
            report += f"  - {func.name} ({func.chunk_id})\n"
        
        report += f"""
Missing from Skeleton: {len(self.get_missing_from_skeleton())}
Missing from Final: {len(self.get_missing_from_final())}

Function Names in Tree Order:
"""
        for func in function_chunks:
            status = "✅" if func.converted else "❌"
            report += f"  {status} {func.name} (path: {func.tree_path})\n"
        
        return report
    
    def export_tracking_status(self, output_file: str):
        """Export current tracking status"""
        status_data = {
            'manifest_file': self.manifest_file,
            'total_chunks': len(self.conversion_status),
            'converted_count': len([s for s in self.conversion_status.values() if s.converted]),
            'chunks': {
                cid: {
                    'kind': status.kind,
                    'name': status.name,
                    'tree_path': status.tree_path,
                    'converted': status.converted,
                    'in_skeleton': status.in_skeleton,
                    'in_final_kotlin': status.in_final_kotlin,
                    'conversion_notes': status.conversion_notes
                }
                for cid, status in self.conversion_status.items()
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, indent=2, ensure_ascii=False)
        
        print(f"Tracking status exported to: {output_file}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Chunk Conversion Tracker')
    parser.add_argument('manifest_file', help='Path to chunk manifest JSON file')
    parser.add_argument('--kotlin-file', help='Path to Kotlin file to verify coverage')
    parser.add_argument('--output', default='conversion_tracking.json', help='Output tracking file')
    
    args = parser.parse_args()
    
    # Create tracker
    tracker = ChunkTracker(args.manifest_file)
    
    # Verify Kotlin file coverage if provided
    if args.kotlin_file and os.path.exists(args.kotlin_file):
        print(f"Verifying coverage in: {args.kotlin_file}")
        missing = tracker.verify_kotlin_file_coverage(args.kotlin_file)
        if missing:
            print(f"❌ {len(missing)} functions missing from Kotlin file")
        else:
            print("✅ All functions found in Kotlin file")
    
    # Generate and print coverage report
    report = tracker.generate_coverage_report()
    print(report)
    
    # Export tracking status
    tracker.export_tracking_status(args.output)

if __name__ == "__main__":
    main()