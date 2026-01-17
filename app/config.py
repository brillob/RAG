"""Configuration management for the RAG system."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Mode: 'local' for vector DB testing, 'azure' for production
    mode: str = "local"  # 'local' or 'azure'
    
    # Local vector database settings
    vector_db_path: str = "./chroma_db"
    embedding_model: str = "all-MiniLM-L6-v2"  # or "paraphrase-multilingual-MiniLM-L12-v2" for multilingual
    
    # Local LLM settings (for local mode)
    local_llm_provider: str = "ollama"  # "ollama" or "transformers"
    # Very small models optimized for RAG/QA tasks:
    # Ollama: "tinyllama" (1.1B params, ~637MB), "qwen2.5:0.5b" (500M params, ~376MB) - smallest options
    # Transformers: "google/flan-t5-small" (80M params, best for RAG/instruction following)
    local_llm_model: str = "tinyllama:latest"  # Very small model (1.1B params) - perfect for RAG on laptops
    local_llm_base_url: str = "http://localhost:11434"  # Ollama API URL
    local_llm_use_gpu: bool = False  # Use GPU for transformers (if available)
    
    # Chunking strategy
    chunking_strategy: str = "sentence"  # Options: sentence, semantic, section, recursive
    chunk_size: int = 500
    chunk_overlap: int = 50
    
    # Conversation memory settings
    enable_conversation_memory: bool = True
    max_conversation_history: int = 10  # Maximum number of previous messages to keep
    conversation_ttl_hours: int = 24  # Time to live for conversation memory
    
    # Azure AI Search (required only in 'azure' mode)
    azure_search_endpoint: Optional[str] = None
    azure_search_key: Optional[str] = None
    azure_search_index_name: Optional[str] = None
    
    # Azure OpenAI (required only in 'azure' mode)
    azure_openai_endpoint: Optional[str] = None
    azure_openai_api_key: Optional[str] = None
    azure_openai_deployment_name: str = "gpt-4"
    azure_openai_api_version: str = "2024-02-15-preview"
    
    # API Security
    api_key: Optional[str] = None
    
    # Application Settings
    log_level: str = "INFO"
    max_response_length: int = 1000
    min_confidence_score: float = 0.7
    enable_multilingual: bool = True
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Timeout Settings
    api_timeout: int = 300  # API request timeout in seconds (5 minutes for LLM inference)
    ollama_timeout: float = 120.0  # Ollama client timeout in seconds (2 minutes for debug mode)
    debug_timeout: int = 120  # Timeout for debug/test scripts in seconds
    
    def is_local_mode(self) -> bool:
        """Check if running in local mode."""
        return self.mode.lower() == "local"
    
    def is_azure_mode(self) -> bool:
        """Check if running in Azure mode."""
        return self.mode.lower() == "azure"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
