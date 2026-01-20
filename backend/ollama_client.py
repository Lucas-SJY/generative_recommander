"""Ollama API client for LLM and embeddings"""
import requests
import json
import logging
from typing import List, Optional
from backend.config import settings

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for Ollama API"""
    
    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.llm_model = settings.llm_model
        self.embed_model = settings.embed_model
        self.timeout = settings.ollama_timeout_s
    
    def generate_text(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7) -> str:
        """Generate text using LLM"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            url = f"{self.base_url}/api/chat"
            payload = {
                "model": self.llm_model,
                "messages": messages,
                "temperature": temperature,
                "stream": False
            }
            
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            
            result = response.json()
            return result.get("message", {}).get("content", "")
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise
    
    def embed_text(self, text: str) -> List[float]:
        """Get embedding for text"""
        try:
            url = f"{self.base_url}/api/embed"
            payload = {
                "model": self.embed_model,
                "input": text
            }
            
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            
            result = response.json()
            embeddings = result.get("embeddings", [])
            if embeddings:
                return embeddings[0]
            return []
        except Exception as e:
            logger.error(f"Error embedding text: {e}")
            raise
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts"""
        try:
            url = f"{self.base_url}/api/embed"
            payload = {
                "model": self.embed_model,
                "input": texts
            }
            
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            
            result = response.json()
            return result.get("embeddings", [])
        except Exception as e:
            logger.error(f"Error batch embedding: {e}")
            raise


# Global client instance
ollama_client = OllamaClient()
