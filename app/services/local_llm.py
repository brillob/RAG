"""Local Language Model service for running LLMs locally without API calls."""
import logging
import httpx
from typing import Optional, Dict, Any
import asyncio

logger = logging.getLogger(__name__)

# Try to import transformers for fallback
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


class LocalLLMService:
    """
    Local LLM service using Ollama (preferred) or transformers (fallback).
    
    Supports very small models optimized for RAG/QA tasks on laptops:
    - Ollama: tinyllama (1.1B, ~637MB), qwen2.5:0.5b (500M, ~376MB) - smallest options
    - Transformers: google/flan-t5-small (80M params, best for RAG/instruction following)
    """
    
    def __init__(
        self,
        provider: str = "ollama",
        model_name: str = "tinyllama",
        base_url: str = "http://localhost:11434",
        use_gpu: bool = False
    ):
        """
        Initialize local LLM service.
        
        Args:
            provider: "ollama" or "transformers"
            model_name: Model name/identifier
            base_url: Ollama API base URL (only for Ollama provider)
            use_gpu: Whether to use GPU for transformers (if available)
        """
        self.provider = provider.lower()
        self.model_name = model_name
        self.base_url = base_url
        if TRANSFORMERS_AVAILABLE:
            import torch
            self.use_gpu = use_gpu and torch.cuda.is_available()
        else:
            self.use_gpu = False
        
        # Initialize based on provider
        if self.provider == "ollama":
            self._init_ollama()
        elif self.provider == "transformers":
            self._init_transformers()
        else:
            raise ValueError(f"Unknown provider: {provider}. Use 'ollama' or 'transformers'")
    
    def _init_ollama(self):
        """Initialize Ollama client."""
        from app.config import settings
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=settings.ollama_timeout  # Configurable timeout for model inference
        )
        logger.info(f"Local LLM Service initialized with Ollama (model: {self.model_name})")
        logger.info(f"Ollama base URL: {self.base_url}")
        logger.info("Make sure Ollama is running: ollama serve")
        logger.info(f"Make sure model is pulled: ollama pull {self.model_name}")
    
    def _init_transformers(self):
        """Initialize transformers pipeline."""
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "transformers library not available. Install with: pip install transformers torch"
            )
        
        import torch
        device = 0 if self.use_gpu else -1  # -1 for CPU, 0+ for GPU
        logger.info(f"Loading transformers model: {self.model_name} (device: {'GPU' if self.use_gpu else 'CPU'})")
        
        try:
            # Use text generation pipeline for causal models
            self.pipeline = pipeline(
                "text-generation",
                model=self.model_name,
                tokenizer=self.model_name,
                device=device,
                torch_dtype=torch.float16 if self.use_gpu else torch.float32,
                model_kwargs={
                    "low_cpu_mem_usage": True,
                    "trust_remote_code": True
                }
            )
            logger.info(f"Transformers model loaded successfully: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to load transformers model: {e}")
            raise
    
    async def generate_response(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.3,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate response using local LLM.
        
        Args:
            prompt: The prompt to generate a response for
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
            system_prompt: Optional system prompt
            
        Returns:
            Generated response text
        """
        if self.provider == "ollama":
            return await self._generate_ollama(prompt, max_tokens, temperature, system_prompt)
        else:
            return await self._generate_transformers(prompt, max_tokens, temperature, system_prompt)
    
    async def _generate_ollama(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
        system_prompt: Optional[str]
    ) -> str:
        """Generate response using Ollama API."""
        try:
            # Build messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            # Call Ollama API
            response = await self.client.post(
                "/api/chat",
                json={
                    "model": self.model_name,
                    "messages": messages,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    },
                    "stream": False
                }
            )
            response.raise_for_status()
            result = response.json()
            
            # Extract response
            if "message" in result and "content" in result["message"]:
                return result["message"]["content"].strip()
            else:
                logger.error(f"Unexpected Ollama response format: {result}")
                return "I encountered an error generating a response."
                
        except httpx.ConnectError:
            logger.error(
                f"Cannot connect to Ollama at {self.base_url}. "
                f"Make sure Ollama is running: ollama serve"
            )
            raise ConnectionError(
                f"Ollama is not running. Start it with: ollama serve"
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.error(
                    f"Model '{self.model_name}' not found. Pull it with: ollama pull {self.model_name}"
                )
                raise ValueError(
                    f"Model '{self.model_name}' not found. Run: ollama pull {self.model_name}"
                )
            else:
                logger.error(f"Ollama API error: {e}")
                raise
        except Exception as e:
            logger.error(f"Error generating response with Ollama: {e}")
            raise
    
    async def _generate_transformers(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
        system_prompt: Optional[str]
    ) -> str:
        """Generate response using transformers pipeline."""
        try:
            # Build full prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{full_prompt}"
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.pipeline(
                    full_prompt,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    do_sample=temperature > 0,
                    pad_token_id=self.pipeline.tokenizer.eos_token_id,
                    eos_token_id=self.pipeline.tokenizer.eos_token_id,
                    return_full_text=False,
                    num_return_sequences=1
                )
            )
            
            # Extract generated text
            if result and len(result) > 0:
                generated_text = result[0].get("generated_text", "").strip()
                return generated_text
            else:
                return "I encountered an error generating a response."
                
        except Exception as e:
            logger.error(f"Error generating response with transformers: {e}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if the LLM service is available."""
        if self.provider == "ollama":
            try:
                response = await self.client.get("/api/tags")
                response.raise_for_status()
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                return {
                    "status": "healthy",
                    "provider": "ollama",
                    "model": self.model_name,
                    "available_models": model_names,
                    "model_available": self.model_name in model_names
                }
            except Exception as e:
                return {
                    "status": "unhealthy",
                    "provider": "ollama",
                    "error": str(e)
                }
        else:
            return {
                "status": "healthy" if hasattr(self, "pipeline") else "unhealthy",
                "provider": "transformers",
                "model": self.model_name
            }
    
    async def close(self):
        """Close connections and cleanup."""
        if self.provider == "ollama" and hasattr(self, "client"):
            await self.client.aclose()
        logger.info("Local LLM service closed")
