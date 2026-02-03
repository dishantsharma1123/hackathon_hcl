"""Ollama service wrapper for LLM interactions."""

import httpx
from typing import Optional, Dict, Any, List
from app.config import settings
from app.utils.logger import app_logger


class OllamaService:
    """Service for interacting with Ollama LLM API."""

    def __init__(self):
        self.base_url = settings.ollama_host
        self.model = settings.ollama_model
        self.fallback_model = settings.ollama_fallback_model
        self.timeout = 60.0

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
        use_fallback: bool = False,
    ) -> str:
        """
        Generate a response from the LLM.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            use_fallback: Whether to use fallback model

        Returns:
            Generated text response
        """
        model = self.fallback_model if use_fallback else self.model
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                return data.get("message", {}).get("content", "")
        except httpx.HTTPError as e:
            app_logger.error(f"Ollama API error: {e}")
            if not use_fallback:
                app_logger.warning(f"Retrying with fallback model: {self.fallback_model}")
                return await self.generate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    use_fallback=True,
                )
            raise
        except Exception as e:
            app_logger.error(f"Unexpected error in Ollama service: {e}")
            raise

    async def classify(
        self,
        text: str,
        categories: List[str],
        system_prompt: Optional[str] = None,
    ) -> tuple[str, float]:
        """
        Classify text into one of the categories.

        Args:
            text: Text to classify
            categories: List of possible categories
            system_prompt: Optional system prompt

        Returns:
            Tuple of (category, confidence)
        """
        categories_str = ", ".join(categories)
        prompt = f"""
Classify the following message into one of these categories: {categories_str}

Message: {text}

Respond with only the category name and a confidence score (0-1) in this format:
CATEGORY: [category_name]
CONFIDENCE: [score]
"""
        
        response = await self.generate(
            prompt=prompt,
            system_prompt=system_prompt or "You are a text classification expert. Respond only in the specified format.",
            temperature=0.3,
            max_tokens=100,
        )

        # Parse response
        category = "unknown"
        confidence = 0.0
        
        for line in response.split("\n"):
            line = line.strip()
            if line.startswith("CATEGORY:"):
                category = line.split(":", 1)[1].strip().lower()
            elif line.startswith("CONFIDENCE:"):
                try:
                    confidence = float(line.split(":", 1)[1].strip())
                except ValueError:
                    pass

        return category, min(max(confidence, 0.0), 1.0)

    async def extract_json(
        self,
        text: str,
        schema_description: str,
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Extract structured data from text in JSON format.

        Args:
            text: Text to extract from
            schema_description: Description of the JSON schema
            system_prompt: Optional system prompt

        Returns:
            Parsed JSON dictionary
        """
        prompt = f"""
Extract structured information from the following message according to this schema:
{schema_description}

Message: {text}

Respond with valid JSON only, no additional text.
"""
        
        response = await self.generate(
            prompt=prompt,
            system_prompt=system_prompt or "You are a data extraction expert. Always respond with valid JSON only.",
            temperature=0.3,
            max_tokens=500,
        )

        # Try to parse JSON
        import json
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
            return {}

    async def check_connection(self) -> bool:
        """Check if Ollama service is available."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                return True
        except Exception as e:
            app_logger.error(f"Ollama connection check failed: {e}")
            return False


# Global service instance
ollama_service = OllamaService()
