"""
Ollama HTTP client for LLM inference

Provides interface to communicate with Ollama service.
"""

import asyncio
import json
from typing import Optional
import httpx

from intelligence_analyzer.utils.logger import get_logger

logger = get_logger("intelligence.analyzer.llm")


class OllamaClient:
    """
    Client for communicating with Ollama LLM service.

    Handles request/response formatting, timeouts, and retries.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama3",
        timeout: int = 30,
        max_retries: int = 1,
    ):
        """
        Initialize Ollama client.

        Args:
            base_url: Ollama service URL
            model: Model name to use
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries on failure
        """
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries

    async def generate(
        self, system_prompt: str, user_prompt: str, attempt: int = 1
    ) -> Optional[str]:
        """
        Generate a response from the LLM.

        Args:
            system_prompt: System prompt for context
            user_prompt: User prompt with the task
            attempt: Current attempt number (for retry logic)

        Returns:
            Optional[str]: LLM response or None if failed

        Raises:
            Exception: If all retry attempts fail
        """
        logger.info(
            f"Sending request to Ollama",
            extra={
                "model": self.model,
                "timeout": self.timeout,
                "attempt": attempt,
                "prompt_length": len(user_prompt),
            },
        )

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Prepare request payload
                payload = {
                    "model": self.model,
                    "prompt": user_prompt,
                    "system": system_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,  # Low temperature for more deterministic output
                        "top_p": 0.9,
                    },
                }

                # Send request
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                )

                response.raise_for_status()

                # Parse response
                response_data = response.json()
                generated_text = response_data.get("response", "")

                logger.info(
                    f"Successfully received response from Ollama",
                    extra={
                        "response_length": len(generated_text),
                        "model": self.model,
                    },
                )

                return generated_text

        except httpx.TimeoutException as e:
            logger.warning(
                f"Ollama request timed out (attempt {attempt}/{self.max_retries + 1})",
                extra={"error": str(e), "timeout": self.timeout},
            )

            if attempt <= self.max_retries:
                logger.info(f"Retrying request (attempt {attempt + 1})...")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                return await self.generate(system_prompt, user_prompt, attempt + 1)
            else:
                logger.error(
                    f"All Ollama request attempts failed",
                    extra={"attempts": attempt, "error": "timeout"},
                )
                raise Exception(f"Ollama request timed out after {attempt} attempts")

        except httpx.HTTPStatusError as e:
            logger.error(
                f"Ollama HTTP error: {e}",
                extra={"status_code": e.response.status_code, "error": str(e)},
            )

            if attempt <= self.max_retries and e.response.status_code >= 500:
                logger.info(f"Retrying request (attempt {attempt + 1})...")
                await asyncio.sleep(2 ** attempt)
                return await self.generate(system_prompt, user_prompt, attempt + 1)
            else:
                raise Exception(f"Ollama HTTP error: {e.response.status_code}")

        except Exception as e:
            logger.error(
                f"Ollama request failed: {e}",
                extra={"error": str(e), "attempt": attempt},
            )

            if attempt <= self.max_retries:
                logger.info(f"Retrying request (attempt {attempt + 1})...")
                await asyncio.sleep(2 ** attempt)
                return await self.generate(system_prompt, user_prompt, attempt + 1)
            else:
                raise Exception(f"Ollama request failed after {attempt} attempts: {e}")

    async def health_check(self) -> bool:
        """
        Check if Ollama service is accessible.

        Returns:
            bool: True if service is healthy, False otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama health check failed: {e}")
            return False
