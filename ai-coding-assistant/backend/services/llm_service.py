"""
LLM Service - Abstraction layer for language model interactions.
Now using Ollama (FREE local LLM instead of OpenAI).
"""

import logging
import requests

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class LLMService:
    """
    Centralized service for all LLM calls (Ollama).
    """

    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.model = "mistral"  # change to "codellama" for coding

        logger.info(f"✅ LLMService using Ollama model: {self.model}")

    def chat(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> str:
        """
        Single-turn chat
        """
        try:
            logger.info("📡 Sending request to Ollama")

            prompt = f"{system_prompt}\n\nUser: {user_message}\nAssistant:"

            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )

            response.raise_for_status()
            result = response.json().get("response", "")

            if not result:
                raise ValueError("Empty response from Ollama")

            logger.info("✅ Response received")
            return result.strip()

        except Exception as e:
            logger.error(f"❌ Ollama error: {e}")
            return f"ERROR: {str(e)}"

    def chat_with_history(
        self,
        messages: list,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> str:
        """
        Multi-turn chat
        """
        try:
            logger.info("📡 Sending multi-turn request")

            prompt = ""
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                prompt += f"{role.capitalize()}: {content}\n"

            prompt += "Assistant:"

            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )

            response.raise_for_status()
            result = response.json().get("response", "")

            if not result:
                raise ValueError("Empty response from Ollama")

            return result.strip()

        except Exception as e:
            logger.error(f"❌ Multi-turn error: {e}")
            return f"ERROR: {str(e)}"


# Singleton instance
llm_service = LLMService()