"""
LLM prompt templates for analysis

Defines structured prompts for article analysis.
"""

from intelligence_analyzer.models import AnalysisInput


ANALYSIS_SYSTEM_PROMPT = """You are an expert analyst for enterprise competitive intelligence.
Your task is to analyze news articles and extract key information in a structured format.

You must respond with ONLY valid JSON matching this exact schema:
{
  "summary": "string (20-500 characters)",
  "entities": [
    {
      "text": "string",
      "type": "company|person|product|technology",
      "mentions": number (>= 1)
    }
  ],
  "classification": "competitive_news|personnel_change|product_launch|market_trend",
  "sentimentScore": number (1-10)
}

Guidelines:
- summary: Concise 1-2 sentence summary of the article
- entities: Extract up to 10 most important entities (companies, people, products, technologies)
- classification: Choose ONE that best fits the article
- sentimentScore: 1=very negative, 5=neutral, 10=very positive

Respond with ONLY the JSON object, no additional text."""


def create_analysis_prompt(article: AnalysisInput, truncated_content: str) -> str:
    """
    Create the analysis prompt for an article.

    Args:
        article: Article to analyze
        truncated_content: Truncated article content

    Returns:
        str: Formatted prompt
    """
    user_prompt = f"""Analyze this article:

Title: {article.title}
URL: {article.url}
Published: {article.publishDate.isoformat()}

Content:
{truncated_content}

Provide your analysis as a JSON object following the schema provided."""

    return user_prompt


def get_system_prompt() -> str:
    """
    Get the system prompt for analysis.

    Returns:
        str: System prompt
    """
    return ANALYSIS_SYSTEM_PROMPT
