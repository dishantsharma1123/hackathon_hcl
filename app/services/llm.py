"""LLM service wrapper supporting multiple providers (Ollama, OpenRouter)."""

import httpx
from typing import Optional, Dict, Any, List
from app.config import settings
from app.utils.logger import app_logger


class LLMService:
    """Service for interacting with LLM APIs (Ollama or OpenRouter)."""

    def __init__(self):
        self.provider = settings.llm_provider
        self.timeout = 60.0
        
        # Configure based on provider
        if self.provider == "openrouter":
            self.base_url = settings.openrouter_base_url
            self.model = settings.openrouter_model
            self.fallback_model = settings.openrouter_fallback_model
            self.api_key = settings.openrouter_api_key
        else:  # ollama (default)
            self.base_url = settings.ollama_host
            self.model = settings.ollama_model
            self.fallback_model = settings.ollama_fallback_model
            self.api_key = None

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for the API request."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _build_payload(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> Dict[str, Any]:
        """Build the payload for the API request."""
        payload = {
            "model": model,
            "messages": messages,
        }
        
        # Add provider-specific parameters
        if self.provider == "openrouter":
            payload["max_tokens"] = max_tokens
            payload["temperature"] = temperature
        else:  # ollama
            payload["stream"] = False
            payload["options"] = {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        
        return payload

    def _get_endpoint(self) -> str:
        """Get the API endpoint based on provider."""
        if self.provider == "openrouter":
            # base_url already includes /v1, so just add /chat/completions
            return f"{self.base_url}/chat/completions"
        else:  # ollama
            return f"{self.base_url}/api/chat"

    def _extract_content(self, response_data: Dict[str, Any]) -> str:
        """Extract content from the API response."""
        if self.provider == "openrouter":
            # OpenRouter uses OpenAI-compatible format
            choices = response_data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "")
        else:  # ollama
            return response_data.get("message", {}).get("content", "")
        return ""

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

        payload = self._build_payload(model, messages, temperature, max_tokens)
        headers = self._get_headers()
        endpoint = self._get_endpoint()

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    endpoint,
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()
                return self._extract_content(data)
        except httpx.HTTPError as e:
            app_logger.error(f"{self.provider.upper()} API error: {e}")
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
            app_logger.error(f"Unexpected error in LLM service: {e}")
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

Respond with ONLY the category name and confidence score (0-1) in this format:
Category: [category name]
Confidence: [0.0-1.0]
"""
        
        response = await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3,  # Lower temperature for more deterministic classification
            max_tokens=100,
        )
        
        # Parse response
        category = "legitimate"
        confidence = 0.5
        
        for line in response.split("\n"):
            line = line.strip().lower()
            if line.startswith("category:"):
                category_name = line.split(":", 1)[1].strip()
                # Validate category
                for cat in categories:
                    if cat.lower() in category_name or category_name in cat.lower():
                        category = cat
                        break
            elif line.startswith("confidence:"):
                try:
                    confidence = float(line.split(":", 1)[1].strip())
                except (ValueError, IndexError):
                    pass
        
        return category, confidence

    async def extract_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Extract structured JSON data from text.

        Args:
            prompt: The prompt with text to extract from
            system_prompt: Optional system prompt

        Returns:
            Parsed JSON dictionary
        """
        full_prompt = f"""
{prompt}

Respond with valid JSON only. No other text or explanation.
"""
        
        response = await self.generate(
            prompt=full_prompt,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=500,
        )
        
        # Try to extract JSON from response
        import json
        import re
        
        # Try to find JSON in the response
        json_match = re.search(r'\{[^{}]*\}|\[[^\[\]]*\]', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # Try parsing entire response
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            app_logger.warning(f"Failed to parse JSON from response: {response}")
            return {}

    async def check_connection(self) -> bool:
        """
        Check if the LLM service is accessible.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Simple test request
            await self.generate(
                prompt="Respond with 'OK' only.",
                max_tokens=10,
            )
            return True
        except Exception as e:
            app_logger.error(f"LLM connection check failed: {e}")
            return False


# Singleton instance
llm_service = LLMService()
