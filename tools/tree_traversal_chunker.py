#!/usr/bin/env python3
"""
Tree Traversal Chunker for LST-based code porting
Ensures no chunks are missed by using systematic tree traversal
"""
import json
import os
from typing import Dict, List, Any, Set
from dataclasses import dataclass

@dataclass
class ChunkNode:
    """Represents a chunk with its LST tree context"""
    chunk_id: str
    kind: str
    name: str
    span: Dict
    header_span: Dict
    body_span: Dict
    header: str
    text: str
    parent_id: str
    children_ids: List[str]
    depth: int
    tree_path: str  # e.g., "root.class.function.1"

class TreeTraversalChunker:
    def __init__(self, lst_file_path: str):
        self.lst_file_path = lst_file_path
        self.lst_data = None
        self.chunks: Dict[str, ChunkNode] = {}
        self.chunk_tree: Dict[str, List[str]] = {}  # parent -> children mapping
        self.visited_nodes: Set[str] = set()
        self.load_lst()
    
    def load_lst(self):
        """Load LST JSON data"""
        with open(self.lst_file_path, 'r', encoding='utf-8') as f:
            self.lst_data = json.load(f)
        print(f"Loaded LST with {len(self.lst_data.get('nodes', []))} nodes")
    
    def generate_chunk_id(self, node_index: int, kind: str, name: str) -> str:
        """Generate unique chunk ID"""
        clean_name = name.replace('::', '_').replace(' ', '_') if name else 'unnamed'
        return f"chunk_{node_index:03d}_{kind}_{clean_name}"
    
    def traverse_depth_first(self) -> Dict[str, ChunkNode]:
        """
        Perform depth-first traversal of LST tree to create chunks
        Ensures no nodes are missed
        """
        if not self.lst_data or 'nodes' not in self.lst_data:
            raise ValueError("Invalid LST data")
        
        nodes = self.lst_data['nodes']
        print(f"Starting DFS traversal of {len(nodes)} nodes...")
        
        # Create root level chunks
        for i, node in enumerate(nodes):
            self._traverse_node(node, i, parent_id="root", depth=0, tree_path=f"root.{i}")
        
        print(f"Created {len(self.chunks)} chunks from tree traversal")
        self._verify_complete_coverage()
        return self.chunks
    
    def _traverse_node(self, node: Dict, node_index: int, parent_id: str, depth: int, tree_path: str):
        """Recursively traverse a node and its children"""
        kind = node.get('kind', 'unknown')
        name = node.get('name', '')
        chunk_id = self.generate_chunk_id(node_index, kind, name)
        
        # Skip if already visited (shouldn't happen with proper tree traversal)
        if chunk_id in self.visited_nodes:
            print(f"Warning: Node {chunk_id} already visited")
            return
        
        # Create chunk for this node
        chunk = ChunkNode(
            chunk_id=chunk_id,
            kind=kind,
            name=name or f"unnamed_{kind}_{node_index}",
            span=node.get('span', {}),
            header_span=node.get('header_span', {}),
            body_span=node.get('body_span', {}),
            header=node.get('header', ''),
            text=node.get('text', ''),
            parent_id=parent_id,
            children_ids=[],
            depth=depth,
            tree_path=tree_path
        )
        
        self.chunks[chunk_id] = chunk
        self.visited_nodes.add(chunk_id)
        
        # Add to parent's children list
        if parent_id != "root" and parent_id in self.chunks:
            self.chunks[parent_id].children_ids.append(chunk_id)
        
        # Update tree mapping
        if parent_id not in self.chunk_tree:
            self.chunk_tree[parent_id] = []
        self.chunk_tree[parent_id].append(chunk_id)
        
        # Recursively process children
        children = node.get('children', [])
        if children:
            print(f"Processing {len(children)} children of {chunk_id} at depth {depth}")
            for j, child in enumerate(children):
                child_tree_path = f"{tree_path}.{j}"
                self._traverse_node(child, f"{node_index}_{j}", chunk_id, depth + 1, child_tree_path)
    
    def _verify_complete_coverage(self):
        """Verify that all LST nodes are covered by chunks"""
        total_nodes = self._count_total_nodes(self.lst_data['nodes'])
        chunk_count = len(self.chunks)
        
        print(f"Coverage verification:")
        print(f"  Total LST nodes: {total_nodes}")
        print(f"  Generated chunks: {chunk_count}")
        
        if chunk_count != total_nodes:
            print(f"WARNING: Coverage mismatch! {total_nodes - chunk_count} nodes may be missing")
        else:
            print("✅ Complete coverage verified - all nodes chunked")
    
    def _count_total_nodes(self, nodes: List[Dict]) -> int:
        """Recursively count all nodes in the tree"""
        count = len(nodes)
        for node in nodes:
            children = node.get('children', [])
            if children:
                count += self._count_total_nodes(children)
        return count
    
    def get_function_chunks(self) -> Dict[str, ChunkNode]:
        """Get only function chunks for focused conversion"""
        return {cid: chunk for cid, chunk in self.chunks.items() 
                if chunk.kind == 'function'}
    
    def get_chunk_by_tree_path(self, tree_path: str) -> ChunkNode:
        """Get chunk by its tree path"""
        for chunk in self.chunks.values():
            if chunk.tree_path == tree_path:
                return chunk
        return None
    
    def export_chunk_manifest(self, output_file: str):
        """Export chunk manifest for tracking during conversion"""
        manifest = {
            'lst_file': self.lst_file_path,
            'total_chunks': len(self.chunks),
            'chunk_tree': self.chunk_tree,
            'chunks': {
                cid: {
                    'kind': chunk.kind,
                    'name': chunk.name,
                    'tree_path': chunk.tree_path,
                    'depth': chunk.depth,
                    'span': chunk.span,
                    'has_children': len(chunk.children_ids) > 0,
                    'children_count': len(chunk.children_ids)
                }
                for cid, chunk in self.chunks.items()
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        print(f"Chunk manifest exported to: {output_file}")
    
    def export_chunks_for_conversion(self, output_dir: str):
        """Export individual chunk files for conversion"""
        os.makedirs(output_dir, exist_ok=True)
        
        for chunk_id, chunk in self.chunks.items():
            # Only export chunks with meaningful content
            if chunk.text.strip() and chunk.kind in ['function', 'class', 'method']:
                chunk_file = os.path.join(output_dir, f"{chunk_id}.json")
                chunk_data = {
                    'chunk_id': chunk_id,
                    'kind': chunk.kind,
                    'name': chunk.name,
                    'header': chunk.header,
                    'text': chunk.text,
                    'tree_path': chunk.tree_path,
                    'span': chunk.span,
                    'context': {
                        'parent_id': chunk.parent_id,
                        'children_ids': chunk.children_ids,
                        'depth': chunk.depth
                    }
                }
                
                with open(chunk_file, 'w', encoding='utf-8') as f:
                    json.dump(chunk_data, f, indent=2, ensure_ascii=False)
        
        print(f"Exported {len([c for c in self.chunks.values() if c.text.strip() and c.kind in ['function', 'class', 'method']])} conversion-ready chunks to: {output_dir}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Tree Traversal Chunker for LST-based porting')
    parser.add_argument('lst_file', help='Path to LST JSON file')
    parser.add_argument('--output-dir', default='chunks_output', help='Output directory for chunks')
    parser.add_argument('--manifest', default='chunk_manifest.json', help='Chunk manifest file')
    
    args = parser.parse_args()
    
    # Create chunker and perform traversal
    chunker = TreeTraversalChunker(args.lst_file)
    chunks = chunker.traverse_depth_first()
    
    # Export results
    chunker.export_chunk_manifest(args.manifest)
    chunker.export_chunks_for_conversion(args.output_dir)
    
    # Print summary
    function_chunks = chunker.get_function_chunks()
    print(f"\n=== Tree Traversal Summary ===")
    print(f"Total chunks: {len(chunks)}")
    print(f"Function chunks: {len(function_chunks)}")
    print(f"Function names: {[chunk.name for chunk in function_chunks.values()]}")

if __name__ == "__main__":
    main()