#!/usr/bin/env python3
"""
AI Provider Manager
Supports multiple AI providers (MCP, OpenAI, Anthropic, Ollama, LMStudio) with configurable models
"""
import json
import os
import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from enum import Enum
import time

class ProviderType(Enum):
    """Available AI providers"""
    MCP = "mcp"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    LMSTUDIO = "lmstudio"
    AZURE_OPENAI = "azure_openai"
    GOOGLE = "google"

class TaskType(Enum):
    """Types of AI tasks"""
    CONVERSION = "conversion"
    VALIDATION = "validation"
    ASSEMBLY = "assembly"

@dataclass
class AIRequest:
    """AI request with context"""
    task_type: TaskType
    prompt: str
    context: Dict[str, Any]
    max_tokens: int = 4000
    temperature: float = 0.1

@dataclass
class AIResponse:
    """AI response with metadata"""
    content: str
    provider: str
    model: str
    task_type: TaskType
    tokens_used: int = 0
    cost: float = 0.0
    response_time: float = 0.0
    success: bool = True
    error: Optional[str] = None

class AIProviderManager:
    """Manages multiple AI providers with configurable models"""
    
    def __init__(self, config_file: str = "ai_conversion_config.json"):
        self.config = self._load_config(config_file)
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = self._setup_logging()
        self.stats = {
            "requests": 0,
            "successful": 0,
            "failed": 0,
            "total_cost": 0.0,
            "total_tokens": 0
        }
        
    def _load_config(self, config_file: str) -> Dict:
        """Load AI provider configuration"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)["ai_conversion_config"]
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file {config_file} not found")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging based on configuration"""
        logger = logging.getLogger("ai_provider_manager")
        log_level = getattr(logging, self.config["logging"]["level"])
        logger.setLevel(log_level)
        
        if not logger.handlers:
            handler = logging.FileHandler(self.config["logging"]["log_file"])
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def get_optimal_provider_and_model(self, task_type: TaskType) -> tuple[str, str]:
        """Get optimal provider and model for task type based on strategy"""
        strategy = self.config["conversion_strategy"]["model_selection_strategy"]
        mode = strategy["mode"]
        
        if mode == "cost_optimized":
            return self._get_cost_optimized_provider(task_type)
        elif mode == "quality_first":
            return self._get_quality_first_provider(task_type)
        elif mode == "speed_first":
            return self._get_speed_first_provider(task_type)
        else:  # balanced
            return self._get_balanced_provider(task_type)
    
    def _get_cost_optimized_provider(self, task_type: TaskType) -> tuple[str, str]:
        """Get cheapest available provider for task"""
        # Priority: MCP (free) > Ollama (local) > others
        providers_by_cost = ["mcp", "ollama", "lmstudio", "openai", "anthropic"]
        
        for provider_name in providers_by_cost:
            if self._is_provider_available(provider_name):
                provider_config = self.config["providers"][provider_name]
                model = provider_config["models"][task_type.value]
                return provider_name, model
        
        raise RuntimeError("No available providers found")
    
    def _get_quality_first_provider(self, task_type: TaskType) -> tuple[str, str]:
        """Get highest quality provider for task"""
        # Priority: Anthropic > OpenAI > MCP > others
        providers_by_quality = ["anthropic", "openai", "mcp", "ollama", "lmstudio"]
        
        for provider_name in providers_by_quality:
            if self._is_provider_available(provider_name):
                provider_config = self.config["providers"][provider_name]
                model = provider_config["models"][task_type.value]
                return provider_name, model
        
        raise RuntimeError("No available providers found")
    
    def _get_speed_first_provider(self, task_type: TaskType) -> tuple[str, str]:
        """Get fastest provider for task"""
        # Priority: Local models > Cloud APIs
        providers_by_speed = ["ollama", "lmstudio", "mcp", "openai", "anthropic"]
        
        for provider_name in providers_by_speed:
            if self._is_provider_available(provider_name):
                provider_config = self.config["providers"][provider_name]
                model = provider_config["models"][task_type.value]
                return provider_name, model
        
        raise RuntimeError("No available providers found")
    
    def _get_balanced_provider(self, task_type: TaskType) -> tuple[str, str]:
        """Get balanced provider (quality vs cost) for task"""
        # Use different strategies for different tasks
        if task_type == TaskType.CONVERSION:
            return self._get_cost_optimized_provider(task_type)
        elif task_type == TaskType.VALIDATION:
            return self._get_quality_first_provider(task_type)
        else:  # ASSEMBLY
            return self._get_balanced_provider_internal(task_type)
    
    def _get_balanced_provider_internal(self, task_type: TaskType) -> tuple[str, str]:
        """Internal balanced provider selection"""
        providers_balanced = ["mcp", "openai", "anthropic", "ollama"]
        
        for provider_name in providers_balanced:
            if self._is_provider_available(provider_name):
                provider_config = self.config["providers"][provider_name]
                model = provider_config["models"][task_type.value]
                return provider_name, model
        
        raise RuntimeError("No available providers found")
    
    def _is_provider_available(self, provider_name: str) -> bool:
        """Check if provider is available and enabled"""
        if provider_name not in self.config["providers"]:
            return False
        
        provider_config = self.config["providers"][provider_name]
        if not provider_config.get("enabled", False):
            return False
        
        # Check API key for cloud providers
        if provider_name in ["openai", "anthropic", "azure_openai", "google"]:
            api_key_env = provider_config.get("api_key_env")
            if not api_key_env or not os.getenv(api_key_env):
                self.logger.warning(f"API key not found for {provider_name}")
                return False
        
        return True
    
    async def make_ai_request(self, request: AIRequest) -> AIResponse:
        """Make AI request using optimal provider"""
        start_time = time.time()
        
        try:
            provider_name, model = self.get_optimal_provider_and_model(request.task_type)
            self.logger.info(f"Using provider: {provider_name}, model: {model} for {request.task_type.value}")
            
            # Route to appropriate provider
            if provider_name == "mcp":
                response = await self._call_mcp_provider(request, model)
            elif provider_name == "openai":
                response = await self._call_openai_provider(request, model)
            elif provider_name == "anthropic":
                response = await self._call_anthropic_provider(request, model)
            elif provider_name == "ollama":
                response = await self._call_ollama_provider(request, model)
            elif provider_name == "lmstudio":
                response = await self._call_lmstudio_provider(request, model)
            else:
                raise ValueError(f"Unsupported provider: {provider_name}")
            
            response.response_time = time.time() - start_time
            response.provider = provider_name
            response.model = model
            response.task_type = request.task_type
            
            # Update stats
            self.stats["requests"] += 1
            if response.success:
                self.stats["successful"] += 1
                self.stats["total_cost"] += response.cost
                self.stats["total_tokens"] += response.tokens_used
            else:
                self.stats["failed"] += 1
            
            return response
            
        except Exception as e:
            self.logger.error(f"AI request failed: {e}")
            return AIResponse(
                content="",
                provider="unknown",
                model="unknown", 
                task_type=request.task_type,
                success=False,
                error=str(e),
                response_time=time.time() - start_time
            )
    
    async def _call_mcp_provider(self, request: AIRequest, model: str) -> AIResponse:
        """Call MCP provider"""
        # Use MCP server settings and models
        mcp_config = self.config["providers"]["mcp"]
        
        if mcp_config["settings"]["use_mcp_model_selection"]:
            # Let MCP server choose the model
            model = "auto"
        
        # Mock MCP call - in real implementation, call MCP server
        self.logger.info(f"Calling MCP server with model: {model}")
        await asyncio.sleep(0.1)  # Simulate API call
        
        return AIResponse(
            content=f"MCP_CONVERTED_CONTENT_{model}",
            provider="mcp",
            model=model,
            task_type=request.task_type,
            tokens_used=1000,
            cost=0.0,  # Free through MCP
            success=True
        )
    
    async def _call_openai_provider(self, request: AIRequest, model: str) -> AIResponse:
        """Call OpenAI API"""
        openai_config = self.config["providers"]["openai"]
        api_key = os.getenv(openai_config["api_key_env"])
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": request.prompt}],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens
        }
        
        # Mock OpenAI call - in real implementation, call OpenAI API
        self.logger.info(f"Calling OpenAI API with model: {model}")
        await asyncio.sleep(0.2)  # Simulate API call
        
        return AIResponse(
            content=f"OPENAI_CONVERTED_CONTENT_{model}",
            provider="openai",
            model=model,
            task_type=request.task_type,
            tokens_used=1200,
            cost=0.03,  # Estimated cost
            success=True
        )
    
    async def _call_anthropic_provider(self, request: AIRequest, model: str) -> AIResponse:
        """Call Anthropic API"""
        anthropic_config = self.config["providers"]["anthropic"]
        api_key = os.getenv(anthropic_config["api_key_env"])
        
        # Mock Anthropic call - in real implementation, call Anthropic API
        self.logger.info(f"Calling Anthropic API with model: {model}")
        await asyncio.sleep(0.3)  # Simulate API call
        
        return AIResponse(
            content=f"ANTHROPIC_CONVERTED_CONTENT_{model}",
            provider="anthropic",
            model=model,
            task_type=request.task_type,
            tokens_used=1100,
            cost=0.05,  # Estimated cost
            success=True
        )
    
    async def _call_ollama_provider(self, request: AIRequest, model: str) -> AIResponse:
        """Call Ollama local API"""
        ollama_config = self.config["providers"]["ollama"]
        base_url = ollama_config["base_url"]
        
        # Mock Ollama call - in real implementation, call Ollama API
        self.logger.info(f"Calling Ollama with model: {model}")
        await asyncio.sleep(0.5)  # Simulate local processing
        
        return AIResponse(
            content=f"OLLAMA_CONVERTED_CONTENT_{model}",
            provider="ollama",
            model=model,
            task_type=request.task_type,
            tokens_used=1000,
            cost=0.0,  # Free local model
            success=True
        )
    
    async def _call_lmstudio_provider(self, request: AIRequest, model: str) -> AIResponse:
        """Call LM Studio local API"""
        lmstudio_config = self.config["providers"]["lmstudio"]
        base_url = lmstudio_config["base_url"]
        
        # Mock LM Studio call - in real implementation, call LM Studio API
        self.logger.info(f"Calling LM Studio with model: {model}")
        await asyncio.sleep(0.4)  # Simulate local processing
        
        return AIResponse(
            content=f"LMSTUDIO_CONVERTED_CONTENT_{model}",
            provider="lmstudio",
            model=model,
            task_type=request.task_type,
            tokens_used=1000,
            cost=0.0,  # Free local model
            success=True
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get provider usage statistics"""
        return {
            **self.stats,
            "success_rate": self.stats["successful"] / max(1, self.stats["requests"]),
            "average_cost_per_request": self.stats["total_cost"] / max(1, self.stats["successful"]),
            "average_tokens_per_request": self.stats["total_tokens"] / max(1, self.stats["successful"])
        }
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return [name for name in self.config["providers"].keys() 
                if self._is_provider_available(name)]
    
    def set_provider_override(self, task_type: TaskType, provider: str, model: str):
        """Override provider for specific task type"""
        if not hasattr(self, '_overrides'):
            self._overrides = {}
        self._overrides[task_type] = (provider, model)
    
    def clear_provider_overrides(self):
        """Clear all provider overrides"""
        if hasattr(self, '_overrides'):
            delattr(self, '_overrides')

# Example usage and testing
async def demo_provider_manager():
    """Demonstrate AI provider manager capabilities"""
    async with AIProviderManager() as manager:
        print("🤖 AI PROVIDER MANAGER DEMONSTRATION")
        print("=" * 50)
        
        print(f"Available providers: {manager.get_available_providers()}")
        print()
        
        # Test different task types
        tasks = [
            (TaskType.CONVERSION, "Convert this C++ function to Kotlin"),
            (TaskType.VALIDATION, "Validate this conversion for accuracy"),
            (TaskType.ASSEMBLY, "Assemble these chunks into a complete file")
        ]
        
        for task_type, prompt in tasks:
            print(f"Testing {task_type.value}...")
            
            request = AIRequest(
                task_type=task_type,
                prompt=prompt,
                context={"chunk_id": "test_chunk"}
            )
            
            response = await manager.make_ai_request(request)
            
            if response.success:
                print(f"✅ {response.provider} ({response.model}) - "
                      f"Cost: ${response.cost:.3f}, "
                      f"Time: {response.response_time:.2f}s")
            else:
                print(f"❌ Failed: {response.error}")
            print()
        
        print("📊 Usage Statistics:")
        stats = manager.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")

if __name__ == "__main__":
    asyncio.run(demo_provider_manager())