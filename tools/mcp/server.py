#!/usr/bin/env python3
"""
MCP Server for C++ to Kotlin Conversion

Provides tools for chunked conversion of C++ LST fragments to Kotlin code.
Implements the Model Context Protocol for integration with AI models.

Model Selection Strategy:
- Heavy work (convert_chunk): Use low-cost models (GPT-4o, Claude-3-Haiku)
- Thinking work (build_skeleton, validate_chunk, assemble_file): Use smart models (Claude-3.5-Sonnet, GPT-o1)
"""
import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from mcp.server import Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
import mcp.server.stdio


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cpp-kotlin-converter")

# Global state
server = Server("cpp-kotlin-converter")
chunks_dir: Optional[Path] = None
skeleton_dir: Optional[Path] = None
mapping_config: Dict[str, Any] = {}
model_config: Dict[str, Any] = {}


def load_model_config():
    """Load model selection configuration."""
    global model_config
    config_file = Path(__file__).parent / "mcp_config.json"
    if config_file.exists():
        with open(config_file) as f:
            model_config = json.load(f)
    else:
        # Default configuration
        model_config = {
            "model_selection": {
                "heavy_work": {
                    "recommended_models": ["gpt-4o", "claude-3-5-haiku"],
                    "tasks": ["convert_chunk"]
                },
                "thinking_work": {
                    "recommended_models": ["claude-3-5-sonnet", "gpt-o1-preview"],
                    "tasks": ["build_skeleton", "validate_chunk", "assemble_file"]
                }
            }
        }


def get_recommended_model(tool_name: str) -> Dict[str, Any]:
    """Get recommended model for a specific tool."""
    heavy_tasks = model_config.get("model_selection", {}).get("heavy_work", {}).get("tasks", [])
    thinking_tasks = model_config.get("model_selection", {}).get("thinking_work", {}).get("tasks", [])
    
    if tool_name in heavy_tasks:
        return {
            "category": "heavy_work",
            "models": model_config.get("model_selection", {}).get("heavy_work", {}).get("recommended_models", []),
            "priority": "low_cost"
        }
    elif tool_name in thinking_tasks:
        return {
            "category": "thinking_work", 
            "models": model_config.get("model_selection", {}).get("thinking_work", {}).get("recommended_models", []),
            "priority": "high_capability"
        }
    else:
        return {
            "category": "unknown",
            "models": ["gpt-4o"],
            "priority": "default"
        }


@server.list_resources()
async def list_resources() -> List[Resource]:
    """List available resources (chunks, skeletons, mappings)."""
    resources = []
    
    # LST chunks
    if chunks_dir and chunks_dir.exists():
        for chunk_file in chunks_dir.glob("*.json"):
            resources.append(
                Resource(
                    uri=f"lst://chunk/{chunk_file.stem}",
                    name=f"LST Chunk: {chunk_file.stem}",
                    mimeType="application/json",
                    description=f"C++ LST chunk for conversion"
                )
            )
    
    # Kotlin skeletons
    if skeleton_dir and skeleton_dir.exists():
        for skeleton_file in skeleton_dir.glob("*.kt"):
            resources.append(
                Resource(
                    uri=f"skeleton://kotlin/{skeleton_file.stem}",
                    name=f"Kotlin Skeleton: {skeleton_file.name}",
                    mimeType="text/kotlin",
                    description=f"Kotlin skeleton file"
                )
            )
    
    # Symbol mapping
    resources.append(
        Resource(
            uri="mapping://symbols",
            name="Symbol Mapping Configuration",
            mimeType="application/json",
            description="C++ to Kotlin symbol mapping rules"
        )
    )
    
    return resources


@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read a resource by URI."""
    if uri.startswith("lst://chunk/"):
        chunk_id = uri.split("/")[-1]
        chunk_file = chunks_dir / f"{chunk_id}.json"
        if chunk_file.exists():
            return chunk_file.read_text()
        else:
            raise ValueError(f"Chunk not found: {chunk_id}")
    
    elif uri.startswith("skeleton://kotlin/"):
        skeleton_name = uri.split("/")[-1]
        skeleton_file = skeleton_dir / f"{skeleton_name}.kt"
        if skeleton_file.exists():
            return skeleton_file.read_text()
        else:
            raise ValueError(f"Skeleton not found: {skeleton_name}")
    
    elif uri == "mapping://symbols":
        return json.dumps(mapping_config, indent=2)
    
    else:
        raise ValueError(f"Unknown resource URI: {uri}")


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available conversion tools."""
    return [
        Tool(
            name="convert_chunk",
            description="Convert a C++ LST chunk to Kotlin code",
            inputSchema={
                "type": "object",
                "properties": {
                    "chunk_id": {
                        "type": "string",
                        "description": "ID of the chunk to convert"
                    },
                    "context": {
                        "type": "object",
                        "description": "Additional context for conversion",
                        "properties": {
                            "class_name": {"type": "string"},
                            "namespace": {"type": "string"},
                            "dependencies": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    "style": {
                        "type": "object",
                        "description": "Kotlin style preferences",
                        "properties": {
                            "use_data_classes": {"type": "boolean", "default": True},
                            "use_extension_functions": {"type": "boolean", "default": True},
                            "null_safety": {"type": "boolean", "default": True}
                        }
                    }
                },
                "required": ["chunk_id"]
            }
        ),
        Tool(
            name="build_skeleton",
            description="Generate Kotlin skeleton from C++ LST structure",
            inputSchema={
                "type": "object",
                "properties": {
                    "lst_file": {
                        "type": "string",
                        "description": "Path to C++ LST file"
                    },
                    "output_file": {
                        "type": "string",
                        "description": "Output Kotlin file path"
                    },
                    "package_name": {
                        "type": "string",
                        "description": "Kotlin package name"
                    }
                },
                "required": ["lst_file", "output_file"]
            }
        ),
        Tool(
            name="validate_chunk",
            description="Validate that converted chunk fits skeleton",
            inputSchema={
                "type": "object",
                "properties": {
                    "chunk_id": {
                        "type": "string",
                        "description": "ID of the converted chunk"
                    },
                    "kotlin_code": {
                        "type": "string",
                        "description": "Converted Kotlin code"
                    },
                    "skeleton_file": {
                        "type": "string",
                        "description": "Skeleton file to validate against"
                    }
                },
                "required": ["chunk_id", "kotlin_code", "skeleton_file"]
            }
        ),
        Tool(
            name="assemble_file",
            description="Combine skeleton and converted chunks into complete Kotlin file",
            inputSchema={
                "type": "object",
                "properties": {
                    "skeleton_file": {
                        "type": "string",
                        "description": "Base skeleton file"
                    },
                    "chunk_mappings": {
                        "type": "object",
                        "description": "Map of chunk IDs to converted Kotlin code",
                        "additionalProperties": {"type": "string"}
                    },
                    "output_file": {
                        "type": "string",
                        "description": "Output assembled file"
                    }
                },
                "required": ["skeleton_file", "chunk_mappings", "output_file"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls with model recommendations."""
    try:
        # Get model recommendation for this tool
        model_info = get_recommended_model(name)
        
        logger.info(f"Tool {name} - Recommended: {model_info['category']} "
                   f"({model_info['priority']}) - Models: {model_info['models']}")
        
        result_content = []
        
        # Add model recommendation to response
        result_content.append(
            TextContent(
                type="text",
                text=f"🤖 MODEL RECOMMENDATION for {name}:\n"
                     f"Category: {model_info['category']}\n"
                     f"Priority: {model_info['priority']}\n"
                     f"Recommended models: {', '.join(model_info['models'])}\n\n"
            )
        )
        
        # Execute the actual tool
        if name == "convert_chunk":
            tool_result = await convert_chunk_tool(arguments)
        elif name == "build_skeleton":
            tool_result = await build_skeleton_tool(arguments)
        elif name == "validate_chunk":
            tool_result = await validate_chunk_tool(arguments)
        elif name == "assemble_file":
            tool_result = await assemble_file_tool(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
        
        result_content.extend(tool_result)
        return result_content
        
    except Exception as e:
        logger.error(f"Tool {name} failed: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def convert_chunk_tool(args: Dict[str, Any]) -> List[TextContent]:
    """Convert a C++ LST chunk to Kotlin."""
    chunk_id = args["chunk_id"]
    context = args.get("context", {})
    style = args.get("style", {})
    
    # Load chunk
    chunk_file = chunks_dir / f"{chunk_id}.json"
    if not chunk_file.exists():
        raise ValueError(f"Chunk not found: {chunk_id}")
    
    with open(chunk_file) as f:
        chunk_data = json.load(f)
    
    # Convert based on chunk type
    chunk_type = chunk_data.get("type", "unknown")
    
    if chunk_type == "function":
        kotlin_code = convert_function_chunk(chunk_data, context, style)
    elif chunk_type == "method":
        kotlin_code = convert_method_chunk(chunk_data, context, style)
    elif chunk_type == "class_declaration":
        kotlin_code = convert_class_declaration_chunk(chunk_data, context, style)
    else:
        kotlin_code = f"// TODO: Convert {chunk_type} chunk\n// Chunk ID: {chunk_id}"
    
    return [
        TextContent(
            type="text",
            text=f"Converted chunk {chunk_id}:\n\n{kotlin_code}"
        )
    ]


async def build_skeleton_tool(args: Dict[str, Any]) -> List[TextContent]:
    """Generate Kotlin skeleton from C++ LST."""
    lst_file = Path(args["lst_file"])
    output_file = Path(args["output_file"])
    package_name = args.get("package_name", "com.example")
    
    # Load LST
    with open(lst_file) as f:
        lst_data = json.load(f)
    
    # Generate skeleton
    skeleton = generate_kotlin_skeleton(lst_data, package_name)
    
    # Save skeleton
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(skeleton)
    
    return [
        TextContent(
            type="text",
            text=f"Generated skeleton: {output_file}\n\n{skeleton}"
        )
    ]


async def validate_chunk_tool(args: Dict[str, Any]) -> List[TextContent]:
    """Validate converted chunk against skeleton."""
    chunk_id = args["chunk_id"]
    kotlin_code = args["kotlin_code"]
    skeleton_file = Path(args["skeleton_file"])
    
    # Simple validation: check if code would fit in skeleton
    validation_result = validate_kotlin_chunk(kotlin_code, skeleton_file)
    
    return [
        TextContent(
            type="text",
            text=f"Validation result for {chunk_id}: {validation_result}"
        )
    ]


async def assemble_file_tool(args: Dict[str, Any]) -> List[TextContent]:
    """Assemble complete Kotlin file from skeleton and chunks."""
    skeleton_file = Path(args["skeleton_file"])
    chunk_mappings = args["chunk_mappings"]
    output_file = Path(args["output_file"])
    
    # Load skeleton
    skeleton = skeleton_file.read_text()
    
    # Replace placeholders with converted chunks
    assembled = assemble_kotlin_file(skeleton, chunk_mappings)
    
    # Save assembled file
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(assembled)
    
    return [
        TextContent(
            type="text",
            text=f"Assembled file: {output_file}\n\nFile size: {len(assembled)} characters"
        )
    ]


def convert_function_chunk(chunk: Dict[str, Any], context: Dict[str, Any], style: Dict[str, Any]) -> str:
    """Convert a function chunk to Kotlin."""
    name = chunk.get("name", "unknown")
    signature = chunk.get("signature", "")
    
    # Simple template-based conversion
    return f"""
fun {name}(): Unit {{
    // TODO: Convert function body
    // Original signature: {signature}
}}
""".strip()


def convert_method_chunk(chunk: Dict[str, Any], context: Dict[str, Any], style: Dict[str, Any]) -> str:
    """Convert a method chunk to Kotlin."""
    name = chunk.get("name", "unknown")
    class_name = chunk.get("class_name", context.get("class_name", "Unknown"))
    
    return f"""
    fun {name}(): Unit {{
        // TODO: Convert method body for {class_name}
    }}
""".strip()


def convert_class_declaration_chunk(chunk: Dict[str, Any], context: Dict[str, Any], style: Dict[str, Any]) -> str:
    """Convert a class declaration chunk to Kotlin."""
    name = chunk.get("name", "Unknown")
    
    if style.get("use_data_classes", True):
        return f"data class {name}()"
    else:
        return f"""
class {name} {{
    // TODO: Add class members
}}
""".strip()


def generate_kotlin_skeleton(lst_data: Dict[str, Any], package_name: str) -> str:
    """Generate Kotlin skeleton from LST."""
    skeleton = f"""package {package_name}

// Auto-generated Kotlin skeleton
// TODO: Add imports

"""
    
    # Add class declarations and method stubs
    skeleton += "// TODO: Add class and method declarations\n"
    skeleton += "// Use chunked conversion to fill in implementations\n"
    
    return skeleton


def validate_kotlin_chunk(kotlin_code: str, skeleton_file: Path) -> str:
    """Validate that Kotlin chunk is syntactically correct."""
    # Simple validation - in practice, would use Kotlin compiler
    if "TODO" in kotlin_code:
        return "WARNING: Contains TODO items"
    return "OK"


def assemble_kotlin_file(skeleton: str, chunk_mappings: Dict[str, str]) -> str:
    """Assemble complete Kotlin file from skeleton and chunks."""
    result = skeleton
    
    # Replace placeholders with actual implementations
    for chunk_id, kotlin_code in chunk_mappings.items():
        placeholder = f"// TODO: {chunk_id}"
        if placeholder in result:
            result = result.replace(placeholder, kotlin_code)
    
    return result


async def main():
    """Main server entry point."""
    global chunks_dir, skeleton_dir, mapping_config
    
    # Load model selection configuration
    load_model_config()
    logger.info(f"Loaded model configuration: {model_config.get('model_selection', {})}")
    
    # Initialize directories (could be passed as command line args)
    chunks_dir = Path("chunks")
    skeleton_dir = Path("skeletons")
    
    # Initialize mapping config
    mapping_config = {
        "symbol_renames": {
            "std::string": "String",
            "std::vector": "List",
            "std::map": "Map"
        },
        "type_mappings": {
            "int": "Int",
            "double": "Double",
            "bool": "Boolean"
        }
    }
    
    # Run the MCP server
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())