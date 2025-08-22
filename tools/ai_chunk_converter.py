#!/usr/bin/env python3
"""
AI-Powered Chunk Converter
Leverages external AI models (GPT-4.1, Claude, etc.) for intelligent C++ to Kotlin conversion
"""
import os
import json
import argparse
import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class ModelType(Enum):
    """Available AI models for chunk conversion"""
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_4_O = "gpt-4o"
    CLAUDE_3_5_SONNET = "claude-3-5-sonnet"
    CLAUDE_3_5_HAIKU = "claude-3-5-haiku"
    GPT_4_1 = "gpt-4.1"  # Free model as mentioned
    
@dataclass
class ChunkConversionContext:
    """Context for AI chunk conversion"""
    chunk_id: str
    cpp_code: str
    chunk_type: str  # function, class, namespace, etc.
    dependencies: List[str]
    comments: List[str]
    function_signature: Optional[str] = None
    parent_context: Optional[str] = None
    tree_path: str = ""
    
@dataclass 
class ConversionRequest:
    """AI model conversion request"""
    model: ModelType
    chunk_context: ChunkConversionContext
    conversion_rules: Dict[str, str]
    max_tokens: int = 4000
    temperature: float = 0.1  # Low for consistency
    
class AIChunkConverter:
    """AI-powered chunk converter using external models"""
    
    def __init__(self, model_type: ModelType = ModelType.GPT_4_1):
        self.model_type = model_type
        self.conversion_stats = {
            "total_chunks": 0,
            "successful_conversions": 0,
            "failed_conversions": 0,
            "manual_review_flagged": 0
        }
        
    def create_conversion_prompt(self, context: ChunkConversionContext) -> str:
        """Create AI prompt for chunk conversion"""
        prompt = f"""
Convert this C++ code chunk to idiomatic Kotlin, following these requirements:

**CRITICAL RULES:**
1. PRESERVE ALL COMMENTS EXACTLY (including Japanese text)
2. Maintain business logic and algorithms precisely
3. Use proper Kotlin syntax and conventions
4. Handle null safety appropriately
5. Convert C++ patterns to Kotlin equivalents

**Chunk Information:**
- Chunk ID: {context.chunk_id}
- Type: {context.chunk_type}
- Tree Path: {context.tree_path}

**Dependencies:** {', '.join(context.dependencies)}

**Function Signature (if applicable):**
{context.function_signature or 'N/A'}

**C++ Code to Convert:**
```cpp
{context.cpp_code}
```

**Conversion Guidelines:**
- char arrays → String or CharArray as appropriate
- Pointers → nullable types or direct references
- C-style casts → Kotlin type conversion
- strcpy/strcat → Kotlin string operations
- Manual memory management → Kotlin automatic memory management
- C++ member access (->) → Kotlin property access (.)

**Output Format:**
Provide ONLY the converted Kotlin code with preserved comments.
Do not include explanations or markdown formatting.
"""
        return prompt
        
    async def convert_chunk_with_ai(self, context: ChunkConversionContext) -> Tuple[bool, str]:
        """Convert chunk using AI model"""
        try:
            prompt = self.create_conversion_prompt(context)
            
            # This would integrate with actual AI APIs
            # For now, providing a mock implementation structure
            kotlin_code = await self._call_ai_model(prompt)
            
            # Validate conversion
            if self._validate_conversion(context.cpp_code, kotlin_code):
                self.conversion_stats["successful_conversions"] += 1
                return True, kotlin_code
            else:
                self.conversion_stats["failed_conversions"] += 1
                return False, f"// CONVERSION_FAILED: {context.chunk_id}\n// Original C++:\n{context.cpp_code}"
                
        except Exception as e:
            self.conversion_stats["failed_conversions"] += 1
            return False, f"// ERROR: {e}\n// Original C++:\n{context.cpp_code}"
    
    async def _call_ai_model(self, prompt: str) -> str:
        """Call external AI model API (to be implemented)"""
        # This is where you'd integrate with:
        # - OpenAI API for GPT models
        # - Anthropic API for Claude models  
        # - Local models via Ollama
        # - Custom MCP server endpoints
        
        # Mock implementation for now
        print(f"🤖 Calling {self.model_type.value} for conversion...")
        await asyncio.sleep(0.1)  # Simulate API call
        
        # In real implementation, return actual AI response
        return "// AI_CONVERSION_PLACEHOLDER"
    
    def _validate_conversion(self, cpp_code: str, kotlin_code: str) -> bool:
        """Validate AI conversion quality"""
        # Check for obvious errors
        if "CONVERSION_FAILED" in kotlin_code:
            return False
            
        if "AI_CONVERSION_PLACEHOLDER" in kotlin_code:
            return False
            
        # Check comment preservation
        cpp_comment_lines = [line.strip() for line in cpp_code.split('\n') if line.strip().startswith('//')]
        kotlin_comment_lines = [line.strip() for line in kotlin_code.split('\n') if line.strip().startswith('//')]
        
        # Should have similar number of comments
        if len(cpp_comment_lines) > 0 and len(kotlin_comment_lines) == 0:
            print(f"⚠️ Warning: Comments may have been lost in conversion")
            return False
            
        return True
    
    def process_chunk_directory(self, chunks_dir: str, output_dir: str, manifest_file: str):
        """Process all chunks in directory with AI conversion"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Load chunk manifest
        with open(manifest_file, 'r') as f:
            manifest = json.load(f)
        
        converted_chunks = {}
        
        # Get chunk list from the manifest structure
        chunk_list = []
        if 'chunk_tree' in manifest and 'root' in manifest['chunk_tree']:
            chunk_list = manifest['chunk_tree']['root']
        elif 'chunks' in manifest:
            chunk_list = [chunk['chunk_id'] if isinstance(chunk, dict) else chunk 
                         for chunk in manifest['chunks']]
        else:
            # Fallback: get all .cpp files in chunks directory
            chunk_list = [f.replace('.cpp', '') for f in os.listdir(chunks_dir) if f.endswith('.cpp')]
        
        print(f"Processing {len(chunk_list)} chunks for AI conversion...")
        
        for chunk_id in chunk_list:
            if isinstance(chunk_id, str):
                chunk_file = os.path.join(chunks_dir, f"{chunk_id}.cpp")
                
                if os.path.exists(chunk_file):
                    print(f"🔄 Converting chunk: {chunk_id}")
                    
                    # Load chunk content
                    with open(chunk_file, 'r') as f:
                        cpp_code = f.read()
                    
                    # Create conversion context
                    context = ChunkConversionContext(
                        chunk_id=chunk_id,
                        cpp_code=cpp_code,
                        chunk_type=self._infer_chunk_type(chunk_id),
                        dependencies=[],
                        comments=self._extract_comments(cpp_code),
                        function_signature=self._extract_function_signature(chunk_id, cpp_code),
                        tree_path=f"root.{chunk_id}"
                    )
                    
                    # Convert with AI
                    success, kotlin_code = asyncio.run(self.convert_chunk_with_ai(context))
                    
                    # Save converted chunk
                    output_file = os.path.join(output_dir, f"{chunk_id}.kt")
                    with open(output_file, 'w') as f:
                        f.write(kotlin_code)
                    
                    converted_chunks[chunk_id] = {
                        "success": success,
                        "output_file": output_file,
                        "chunk_type": context.chunk_type,
                        "model_used": self.model_type.value
                    }
                    
                    if not success:
                        self.conversion_stats["manual_review_flagged"] += 1
                        print(f"⚠️ Chunk {chunk_id} needs manual review")
                    else:
                        print(f"✅ Chunk {chunk_id} converted successfully")
        
        self.conversion_stats["total_chunks"] = len(chunk_list)
        
        # Save conversion results
        results_file = os.path.join(output_dir, "conversion_results.json")
        with open(results_file, 'w') as f:
            json.dump({
                "converted_chunks": converted_chunks,
                "stats": self.conversion_stats
            }, f, indent=2)
        
        self._print_conversion_summary()
    
    def _infer_chunk_type(self, chunk_id: str) -> str:
        """Infer chunk type from chunk ID"""
        if 'function' in chunk_id:
            return 'function'
        elif 'include' in chunk_id:
            return 'include'
        elif 'macro' in chunk_id:
            return 'macro'
        else:
            return 'other'
    
    def _extract_comments(self, cpp_code: str) -> List[str]:
        """Extract comments from C++ code"""
        comments = []
        lines = cpp_code.split('\n')
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('//') or stripped.startswith('/*'):
                comments.append(stripped)
        return comments
    
    def _extract_function_signature(self, chunk_id: str, cpp_code: str) -> Optional[str]:
        """Extract function signature if this is a function chunk"""
        if 'function' in chunk_id:
            lines = cpp_code.split('\n')
            for line in lines:
                if '::' in line and '(' in line and ')' in line:
                    return line.strip()
        return None
    
    def _print_conversion_summary(self):
        """Print conversion statistics"""
        print("\n" + "="*50)
        print("AI CHUNK CONVERSION SUMMARY")
        print("="*50)
        print(f"Model Used: {self.model_type.value}")
        print(f"Total Chunks: {self.conversion_stats['total_chunks']}")
        print(f"Successful: {self.conversion_stats['successful_conversions']}")
        print(f"Failed: {self.conversion_stats['failed_conversions']}")
        print(f"Manual Review Needed: {self.conversion_stats['manual_review_flagged']}")
        
        if self.conversion_stats['total_chunks'] > 0:
            success_rate = (self.conversion_stats['successful_conversions'] / 
                          self.conversion_stats['total_chunks']) * 100
            print(f"Success Rate: {success_rate:.1f}%")
        print("="*50)

class MCPServerIntegration:
    """Integration with MCP server for AI conversion"""
    
    def __init__(self, server_url: str = "http://localhost:3000"):
        self.server_url = server_url
        
    async def convert_via_mcp(self, context: ChunkConversionContext) -> str:
        """Convert chunk via MCP server"""
        # This would integrate with your custom MCP server
        # that has AI model endpoints for code conversion
        
        request_data = {
            "action": "convert_chunk",
            "model": "gpt-4.1",  # Free model
            "chunk_data": {
                "code": context.cpp_code,
                "type": context.chunk_type,
                "dependencies": context.dependencies,
                "function_signature": context.function_signature
            },
            "conversion_rules": {
                "preserve_comments": True,
                "target_language": "kotlin",
                "maintain_business_logic": True
            }
        }
        
        # Mock MCP server call
        print(f"📡 Calling MCP server for chunk conversion...")
        await asyncio.sleep(0.1)
        
        # In real implementation, make HTTP request to MCP server
        return "// MCP_CONVERTED_CODE_PLACEHOLDER"

def main():
    parser = argparse.ArgumentParser(description="AI-powered C++ to Kotlin chunk converter")
    parser.add_argument("chunks_dir", help="Directory containing C++ chunks")
    parser.add_argument("manifest_file", help="Chunk manifest JSON file")
    parser.add_argument("--output-dir", default="ai_converted_chunks", 
                       help="Output directory for converted Kotlin chunks")
    parser.add_argument("--model", choices=[m.value for m in ModelType], 
                       default=ModelType.GPT_4_1.value,
                       help="AI model to use for conversion")
    parser.add_argument("--mcp-server", help="Use MCP server for conversion")
    
    args = parser.parse_args()
    
    # Create converter
    model_type = ModelType(args.model)
    converter = AIChunkConverter(model_type)
    
    print(f"🚀 Starting AI-powered chunk conversion with {model_type.value}")
    print(f"📁 Input: {args.chunks_dir}")
    print(f"📁 Output: {args.output_dir}")
    
    # Process chunks
    converter.process_chunk_directory(
        args.chunks_dir, 
        args.output_dir, 
        args.manifest_file
    )
    
    print("✅ AI chunk conversion completed!")

if __name__ == "__main__":
    main()