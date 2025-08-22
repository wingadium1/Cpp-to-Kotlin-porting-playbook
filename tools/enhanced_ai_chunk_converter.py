#!/usr/bin/env python3
"""
Enhanced AI Chunk Converter with Configurable Providers
Supports MCP, OpenAI, Anthropic, Ollama, LMStudio with intelligent provider selection
"""
import os
import json
import argparse
import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from ai_provider_manager import AIProviderManager, AIRequest, TaskType

@dataclass
class EnhancedChunkContext:
    """Enhanced chunk context with provider flexibility"""
    chunk_id: str
    cpp_code: str
    chunk_type: str
    dependencies: List[str]
    comments: List[str]
    function_signature: Optional[str] = None
    parent_context: Optional[str] = None
    tree_path: str = ""
    
class EnhancedAIChunkConverter:
    """Enhanced AI chunk converter with multiple provider support"""
    
    def __init__(self, config_file: str = "ai_conversion_config.json"):
        self.config_file = config_file
        self.provider_manager = None
        self.conversion_stats = {
            "total_chunks": 0,
            "successful_conversions": 0,
            "failed_conversions": 0,
            "manual_review_flagged": 0,
            "providers_used": {},
            "total_cost": 0.0
        }
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.provider_manager = AIProviderManager(self.config_file)
        await self.provider_manager.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.provider_manager:
            await self.provider_manager.__aexit__(exc_type, exc_val, exc_tb)
    
    def create_conversion_prompt(self, context: EnhancedChunkContext) -> str:
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
    
    async def convert_chunk_with_ai(self, context: EnhancedChunkContext) -> Tuple[bool, str]:
        """Convert chunk using optimal AI provider"""
        try:
            prompt = self.create_conversion_prompt(context)
            
            request = AIRequest(
                task_type=TaskType.CONVERSION,
                prompt=prompt,
                context={
                    "chunk_id": context.chunk_id,
                    "chunk_type": context.chunk_type,
                    "tree_path": context.tree_path
                }
            )
            
            response = await self.provider_manager.make_ai_request(request)
            
            if response.success:
                # Validate conversion
                if self._validate_conversion(context.cpp_code, response.content):
                    self.conversion_stats["successful_conversions"] += 1
                    self._update_provider_stats(response.provider, response.cost)
                    return True, response.content
                else:
                    self.conversion_stats["failed_conversions"] += 1
                    return False, f"// CONVERSION_VALIDATION_FAILED: {context.chunk_id}\n// Original C++:\n{context.cpp_code}"
            else:
                self.conversion_stats["failed_conversions"] += 1
                return False, f"// CONVERSION_FAILED: {response.error}\n// Original C++:\n{context.cpp_code}"
                
        except Exception as e:
            self.conversion_stats["failed_conversions"] += 1
            return False, f"// ERROR: {e}\n// Original C++:\n{context.cpp_code}"
    
    def _validate_conversion(self, cpp_code: str, kotlin_code: str) -> bool:
        """Validate AI conversion quality"""
        # Check for obvious errors
        if any(marker in kotlin_code for marker in ["CONVERSION_FAILED", "ERROR:", "PLACEHOLDER"]):
            return False
            
        # Check comment preservation
        cpp_comment_lines = [line.strip() for line in cpp_code.split('\n') 
                           if line.strip().startswith('//')]
        kotlin_comment_lines = [line.strip() for line in kotlin_code.split('\n') 
                              if line.strip().startswith('//')]
        
        # Should have similar number of comments
        if len(cpp_comment_lines) > 0 and len(kotlin_comment_lines) == 0:
            print(f"⚠️ Warning: Comments may have been lost in conversion")
            return False
            
        return True
    
    def _update_provider_stats(self, provider: str, cost: float):
        """Update provider usage statistics"""
        if provider not in self.conversion_stats["providers_used"]:
            self.conversion_stats["providers_used"][provider] = {
                "count": 0,
                "total_cost": 0.0
            }
        
        self.conversion_stats["providers_used"][provider]["count"] += 1
        self.conversion_stats["providers_used"][provider]["total_cost"] += cost
        self.conversion_stats["total_cost"] += cost
    
    async def process_chunk_directory(self, chunks_dir: str, output_dir: str, manifest_file: str):
        """Process all chunks in directory with configurable AI providers"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Load chunk manifest
        with open(manifest_file, 'r') as f:
            manifest = json.load(f)
        
        converted_chunks = {}
        
        # Get chunk list from manifest
        chunk_list = []
        if 'chunk_tree' in manifest and 'root' in manifest['chunk_tree']:
            chunk_list = manifest['chunk_tree']['root']
        elif 'chunks' in manifest:
            chunk_list = [chunk['chunk_id'] if isinstance(chunk, dict) else chunk 
                         for chunk in manifest['chunks']]
        else:
            chunk_list = [f.replace('.json', '') for f in os.listdir(chunks_dir) 
                         if f.endswith('.json')]
        
        print(f"Processing {len(chunk_list)} chunks with configurable AI providers...")
        print(f"Available providers: {self.provider_manager.get_available_providers()}")
        
        for chunk_id in chunk_list:
            if isinstance(chunk_id, str):
                chunk_file = os.path.join(chunks_dir, f"{chunk_id}.json")
                
                if os.path.exists(chunk_file):
                    print(f"🔄 Converting chunk: {chunk_id}")
                    
                    # Load chunk content
                    with open(chunk_file, 'r') as f:
                        chunk_data = json.load(f)
                    
                    # Create conversion context
                    context = EnhancedChunkContext(
                        chunk_id=chunk_id,
                        cpp_code=chunk_data.get('text', ''),
                        chunk_type=self._infer_chunk_type(chunk_id),
                        dependencies=[],
                        comments=self._extract_comments(chunk_data.get('text', '')),
                        function_signature=chunk_data.get('header'),
                        tree_path=chunk_data.get('tree_path', f"root.{chunk_id}")
                    )
                    
                    # Convert with AI
                    success, kotlin_code = await self.convert_chunk_with_ai(context)
                    
                    # Save converted chunk
                    output_file = os.path.join(output_dir, f"{chunk_id}.kt")
                    with open(output_file, 'w') as f:
                        f.write(kotlin_code)
                    
                    converted_chunks[chunk_id] = {
                        "success": success,
                        "output_file": output_file,
                        "chunk_type": context.chunk_type,
                        "original_code_lines": len(context.cpp_code.split('\n')),
                        "converted_code_lines": len(kotlin_code.split('\n'))
                    }
                    
                    if not success:
                        self.conversion_stats["manual_review_flagged"] += 1
                        print(f"⚠️ Chunk {chunk_id} needs manual review")
                    else:
                        print(f"✅ Chunk {chunk_id} converted successfully")
        
        self.conversion_stats["total_chunks"] = len(chunk_list)
        
        # Save conversion results
        results_file = os.path.join(output_dir, "enhanced_conversion_results.json")
        with open(results_file, 'w') as f:
            json.dump({
                "converted_chunks": converted_chunks,
                "stats": self.conversion_stats,
                "provider_stats": self.provider_manager.get_stats()
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
    
    def _print_conversion_summary(self):
        """Print comprehensive conversion statistics"""
        print("\n" + "="*60)
        print("ENHANCED AI CHUNK CONVERSION SUMMARY")
        print("="*60)
        print(f"Total Chunks: {self.conversion_stats['total_chunks']}")
        print(f"Successful: {self.conversion_stats['successful_conversions']}")
        print(f"Failed: {self.conversion_stats['failed_conversions']}")
        print(f"Manual Review Needed: {self.conversion_stats['manual_review_flagged']}")
        print(f"Total Cost: ${self.conversion_stats['total_cost']:.3f}")
        
        if self.conversion_stats['total_chunks'] > 0:
            success_rate = (self.conversion_stats['successful_conversions'] / 
                          self.conversion_stats['total_chunks']) * 100
            print(f"Success Rate: {success_rate:.1f}%")
        
        print("\nProvider Usage:")
        for provider, stats in self.conversion_stats['providers_used'].items():
            print(f"  {provider}: {stats['count']} chunks, ${stats['total_cost']:.3f}")
        
        print("="*60)

async def main():
    parser = argparse.ArgumentParser(description="Enhanced AI-powered C++ to Kotlin chunk converter")
    parser.add_argument("chunks_dir", help="Directory containing C++ chunks")
    parser.add_argument("manifest_file", help="Chunk manifest JSON file")
    parser.add_argument("--output-dir", default="enhanced_converted_chunks", 
                       help="Output directory for converted Kotlin chunks")
    parser.add_argument("--config", default="ai_conversion_config.json",
                       help="AI provider configuration file")
    parser.add_argument("--provider-override", 
                       help="Force specific provider (mcp, openai, anthropic, ollama, lmstudio)")
    parser.add_argument("--model-override",
                       help="Force specific model for conversion")
    
    args = parser.parse_args()
    
    print(f"🚀 Starting Enhanced AI-powered chunk conversion")
    print(f"📁 Input: {args.chunks_dir}")
    print(f"📁 Output: {args.output_dir}")
    print(f"⚙️ Config: {args.config}")
    
    async with EnhancedAIChunkConverter(args.config) as converter:
        # Apply overrides if specified
        if args.provider_override and args.model_override:
            for task_type in [TaskType.CONVERSION, TaskType.VALIDATION, TaskType.ASSEMBLY]:
                converter.provider_manager.set_provider_override(
                    task_type, args.provider_override, args.model_override
                )
            print(f"🔧 Using provider override: {args.provider_override} ({args.model_override})")
        
        # Process chunks
        await converter.process_chunk_directory(
            args.chunks_dir, 
            args.output_dir, 
            args.manifest_file
        )
    
    print("✅ Enhanced AI chunk conversion completed!")

if __name__ == "__main__":
    asyncio.run(main())