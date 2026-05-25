"""AI interaction via Ollama."""
import requests
from typing import Optional


class OllamaClient:
    """Client for Ollama API."""
    
    def __init__(self, config: dict):
        """Initialize Ollama client with config."""
        self.ollama_config = config.get("ollama", {})
        self.base_url = self.ollama_config.get("base_url", "http://localhost:11434")
        self.model = self.ollama_config.get("model", "llama3.2:1b")
        self.timeout = self.ollama_config.get("timeout_seconds", 30)
    
    def is_available(self) -> bool:
        """Check if Ollama is available."""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Ollama not available: {e}")
            return False
    
    def generate(self, prompt: str) -> Optional[str]:
        """Generate a response from the model."""
        try:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "keep_alive": self.ollama_config.get("keep_alive", "30m")
            }
            
            response = requests.post(
                url,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "").strip()
            else:
                print(f"Ollama error: {response.status_code}")
                return None
        except requests.exceptions.Timeout:
            print("Ollama request timed out")
            return None
        except Exception as e:
            print(f"Error generating response: {e}")
            return None
