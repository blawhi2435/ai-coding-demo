"""
Unified analyzer for single-pass article analysis

Performs entity extraction, classification, sentiment analysis, and summarization
in a single LLM call.
"""

import json
from typing import Optional
from pydantic import ValidationError

from intelligence_analyzer.models import AnalysisInput, AnalysisResult
from intelligence_analyzer.llm.client import OllamaClient
from intelligence_analyzer.llm.prompts import get_system_prompt, create_analysis_prompt
from intelligence_analyzer.utils.truncate import truncate_content
from intelligence_analyzer.utils.logger import get_logger

logger = get_logger("intelligence.analyzer.unified")


class UnifiedAnalyzer:
    """
    Unified analyzer that performs all analysis in a single pass.

    Uses structured LLM prompts to extract:
    - Summary
    - Entities (companies, people, products, technologies)
    - Classification (competitive_news, personnel_change, product_launch, market_trend)
    - Sentiment score (1-10)
    """

    def __init__(
        self,
        llm_client: OllamaClient,
        max_content_chars: int = 16000,
    ):
        """
        Initialize unified analyzer.

        Args:
            llm_client: Ollama client for LLM inference
            max_content_chars: Maximum content characters (~4000 tokens)
        """
        self.llm_client = llm_client
        self.max_content_chars = max_content_chars

    async def analyze(self, article: AnalysisInput) -> AnalysisResult:
        """
        Analyze an article and extract structured information.

        Args:
            article: Article to analyze

        Returns:
            AnalysisResult: Analysis results

        Raises:
            Exception: If analysis fails or validation fails
        """
        logger.info(
            f"Starting analysis",
            extra={
                "url": str(article.url),
                "title": article.title,
                "content_length": len(article.content),
            },
        )

        try:
            # Step 1: Truncate content if needed
            truncated_content, was_truncated = truncate_content(
                article.content, self.max_content_chars
            )

            if was_truncated:
                logger.info(
                    f"Content truncated",
                    extra={
                        "original_length": len(article.content),
                        "truncated_length": len(truncated_content),
                    },
                )

            # Step 2: Create prompts
            system_prompt = get_system_prompt()
            user_prompt = create_analysis_prompt(article, truncated_content)

            # Step 3: Get LLM response
            logger.info("Sending request to LLM")
            llm_response = await self.llm_client.generate(system_prompt, user_prompt)

            if not llm_response:
                raise Exception("LLM returned empty response")

            logger.info(
                f"Received LLM response",
                extra={"response_length": len(llm_response)},
            )

            # Step 4: Parse and validate JSON response
            analysis_result = self._parse_and_validate_response(llm_response)

            logger.info(
                f"Analysis complete",
                extra={
                    "url": str(article.url),
                    "classification": analysis_result.classification,
                    "sentiment": analysis_result.sentimentScore,
                    "entities_count": len(analysis_result.entities),
                },
            )

            return analysis_result

        except Exception as e:
            logger.error(
                f"Analysis failed: {e}",
                extra={"url": str(article.url), "error": str(e)},
            )
            raise

    def _parse_and_validate_response(self, llm_response: str) -> AnalysisResult:
        """
        Parse LLM response and validate against schema.

        Args:
            llm_response: Raw LLM response (expected to be JSON)

        Returns:
            AnalysisResult: Validated analysis result

        Raises:
            Exception: If parsing or validation fails
        """
        try:
            # Extract JSON from response (in case there's extra text)
            json_str = self._extract_json(llm_response)

            # Parse JSON
            try:
                response_data = json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.error(
                    f"Failed to parse JSON response",
                    extra={"error": str(e), "response": llm_response[:500]},
                )
                raise Exception(f"Invalid JSON in LLM response: {e}")

            # Validate with Pydantic
            try:
                analysis_result = AnalysisResult(**response_data)
                return analysis_result
            except ValidationError as e:
                logger.error(
                    f"Response validation failed",
                    extra={"error": str(e), "response_data": response_data},
                )
                raise Exception(f"LLM response does not match schema: {e}")

        except Exception as e:
            logger.error(f"Failed to parse and validate response: {e}")
            raise

    def _extract_json(self, text: str) -> str:
        """
        Extract JSON object from text that may contain extra content.

        Args:
            text: Text that may contain JSON

        Returns:
            str: Extracted JSON string

        Raises:
            Exception: If no valid JSON found
        """
        # Try to find JSON object boundaries
        start_idx = text.find("{")
        end_idx = text.rfind("}")

        if start_idx == -1 or end_idx == -1:
            raise Exception("No JSON object found in response")

        json_str = text[start_idx : end_idx + 1]
        return json_str
