"""Configuration module"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    database_url: str = "postgresql+psycopg://postgres:postgres@0.0.0.0:5432/recsys?options=-csearch_path%3Dlmrc,public"
    
    # Ollama
    ollama_base_url: str = "http://0.0.0.0:11434"
    llm_model: str = "qwen2.5:14b"
    embed_model: str = "nomic-embed-text"
    ollama_timeout_s: int = 60
    
    # Recommendation
    retrieve_topk: int = 80
    return_topn: int = 8
    
    # Embedding
    embed_dim: int = 768

    # Performance & feature toggles
    enable_llm_intent: bool = True
    enable_llm_category_fallback: bool = True
    enable_embeddings: bool = True
    log_level: str = "WARNING"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
