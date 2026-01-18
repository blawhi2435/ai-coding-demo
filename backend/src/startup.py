"""
Startup orchestration for scraping and analysis

Handles automatic scraping and analysis on backend startup.
"""

import asyncio
import subprocess
import json
import tempfile
from pathlib import Path
from typing import List, Dict, Any

from src.config import settings
from src.db.mongo import get_database
from src.services.article_service import ArticleService
from src.utils.logger import logger


async def run_startup_pipeline():
    """
    Run the complete startup pipeline: scrape → store → analyze → update.

    This function orchestrates the entire process of:
    1. Scraping articles from NVIDIA Newsroom
    2. Storing scraped articles in MongoDB
    3. Analyzing articles with LLM
    4. Updating MongoDB with analysis results

    Handles partial failures gracefully by marking failed articles.
    """
    logger.info(
        "Starting automatic scraping and analysis pipeline",
        extra={"event": "pipeline_start"},
    )

    try:
        # Get database instance
        db = get_database()

        # Initialize article service
        article_service = ArticleService(db)

        # Step 1: Run scraper
        logger.info("Step 1: Running scraper", extra={"step": "scraping"})
        scraped_articles = await run_scraper()

        if not scraped_articles:
            logger.warning("No articles were scraped", extra={"step": "scraping"})
            return

        logger.info(
            f"Scraped {len(scraped_articles)} articles",
            extra={"article_count": len(scraped_articles), "step": "scraping"},
        )

        # Step 2: Store scraped articles in MongoDB
        logger.info("Step 2: Storing articles in database", extra={"step": "storage"})
        stored_count = await store_articles(article_service, scraped_articles)
        logger.info(
            f"Stored {stored_count} articles in database",
            extra={"stored_count": stored_count, "step": "storage"},
        )

        # Step 3: Analyze articles
        logger.info("Step 3: Running analyzer", extra={"step": "analysis"})
        analyzed_results = await run_analyzer(scraped_articles)

        if not analyzed_results:
            logger.warning("No articles were analyzed", extra={"step": "analysis"})
            return

        logger.info(
            f"Analyzed {len(analyzed_results)} articles",
            extra={"analyzed_count": len(analyzed_results), "step": "analysis"},
        )

        # Step 4: Update database with analysis results
        logger.info(
            "Step 4: Updating database with analysis results",
            extra={"step": "update"},
        )
        updated_count = await update_with_analysis(article_service, analyzed_results)
        logger.info(
            f"Updated {updated_count} articles with analysis",
            extra={"updated_count": updated_count, "step": "update"},
        )

        # Log final stats
        stats = await article_service.get_stats()
        logger.info(
            f"Pipeline complete",
            extra={
                "event": "pipeline_complete",
                "stats": stats,
            },
        )

    except Exception as e:
        logger.error(
            f"Startup pipeline failed: {e}",
            extra={"event": "pipeline_failed", "error": str(e)},
        )
        # Don't raise - allow backend to continue running even if scraping fails


async def run_scraper() -> List[Dict[str, Any]]:
    """
    Run the scraper library CLI to scrape articles.

    Returns:
        List[Dict]: List of scraped articles

    Raises:
        Exception: If scraping fails
    """
    logger.info(
        "Invoking scraper library",
        extra={
            "max_articles": settings.SCRAPER_MAX_ARTICLES,
        },
    )

    try:
        # Create temporary file for scraper output
        with tempfile.NamedTemporaryFile(
            mode="w+", suffix=".json", delete=False
        ) as temp_file:
            temp_path = temp_file.name

        try:
            # Run scraper CLI
            cmd = [
                "intelligence-scraper",
                "nvidia",
                temp_path,
                "--max-articles",
                str(settings.SCRAPER_MAX_ARTICLES),
                "--timeout",
                str(settings.SCRAPER_TIMEOUT),
            ]

            logger.info(f"Running scraper command: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=settings.SCRAPER_TIMEOUT * settings.SCRAPER_MAX_ARTICLES,
            )

            if result.returncode != 0:
                logger.error(
                    f"Scraper command failed",
                    extra={
                        "returncode": result.returncode,
                        "stderr": result.stderr,
                    },
                )
                raise Exception(f"Scraper failed: {result.stderr}")

            # Read scraped articles
            with open(temp_path, "r", encoding="utf-8") as f:
                articles = json.load(f)

            logger.info(f"Scraper completed successfully")
            return articles

        finally:
            # Cleanup temp file
            Path(temp_path).unlink(missing_ok=True)

    except subprocess.TimeoutExpired as e:
        logger.error(f"Scraper timed out", extra={"timeout": e.timeout})
        raise Exception("Scraper timed out")
    except Exception as e:
        logger.error(f"Scraper execution failed: {e}")
        raise


async def store_articles(
    article_service: ArticleService, articles: List[Dict[str, Any]]
) -> int:
    """
    Store scraped articles in MongoDB.

    Args:
        article_service: Article service instance
        articles: List of scraped articles

    Returns:
        int: Number of articles stored

    Handles errors gracefully - continues even if some articles fail.
    """
    stored_count = 0

    for article in articles:
        try:
            await article_service.upsert_scraped_article(article)
            stored_count += 1
        except Exception as e:
            logger.error(
                f"Failed to store article: {e}",
                extra={"url": article.get("url"), "error": str(e)},
            )
            continue

    return stored_count


async def run_analyzer(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Run the analyzer library CLI to analyze articles.

    Args:
        articles: List of articles to analyze

    Returns:
        List[Dict]: List of analysis results

    Raises:
        Exception: If analysis fails
    """
    logger.info(
        "Invoking analyzer library",
        extra={"article_count": len(articles)},
    )

    try:
        # Create temporary files for input/output
        with tempfile.NamedTemporaryFile(
            mode="w+", suffix=".json", delete=False
        ) as input_file, tempfile.NamedTemporaryFile(
            mode="w+", suffix=".json", delete=False
        ) as output_file:
            input_path = input_file.name
            output_path = output_file.name

            # Write articles to input file
            json.dump(articles, input_file, ensure_ascii=False, default=str)
            input_file.flush()

        try:
            # Run analyzer CLI
            cmd = [
                "intelligence-analyzer",
                input_path,
                output_path,
                "--llm-url",
                settings.LLM_SERVICE_URL,
                "--llm-model",
                settings.LLM_MODEL,
                "--timeout",
                str(settings.ANALYZER_TIMEOUT),
            ]

            logger.info(f"Running analyzer command: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=settings.ANALYZER_TIMEOUT * len(articles) * 2,
            )

            if result.returncode != 0:
                logger.error(
                    f"Analyzer command failed",
                    extra={
                        "returncode": result.returncode,
                        "stderr": result.stderr,
                    },
                )
                raise Exception(f"Analyzer failed: {result.stderr}")

            # Read analysis results
            with open(output_path, "r", encoding="utf-8") as f:
                results = json.load(f)

            logger.info(f"Analyzer completed successfully")
            return results

        finally:
            # Cleanup temp files
            Path(input_path).unlink(missing_ok=True)
            Path(output_path).unlink(missing_ok=True)

    except subprocess.TimeoutExpired as e:
        logger.error(f"Analyzer timed out", extra={"timeout": e.timeout})
        raise Exception("Analyzer timed out")
    except Exception as e:
        logger.error(f"Analyzer execution failed: {e}")
        raise


async def update_with_analysis(
    article_service: ArticleService, analysis_results: List[Dict[str, Any]]
) -> int:
    """
    Update MongoDB articles with analysis results.

    Args:
        article_service: Article service instance
        analysis_results: List of analysis results

    Returns:
        int: Number of articles updated

    Handles errors gracefully - marks failed articles as failed.
    """
    updated_count = 0
    failed_count = 0

    for result in analysis_results:
        url = result.get("url")
        analysis = result.get("analysis")

        if not url or not analysis:
            logger.warning("Invalid analysis result", extra={"result": result})
            continue

        try:
            success = await article_service.update_with_analysis(url, analysis)
            if success:
                updated_count += 1
            else:
                failed_count += 1
        except Exception as e:
            logger.error(
                f"Failed to update article with analysis: {e}",
                extra={"url": url, "error": str(e)},
            )
            await article_service.mark_as_failed(url, str(e))
            failed_count += 1
            continue

    if failed_count > 0:
        logger.warning(
            f"{failed_count} articles failed to update",
            extra={"failed_count": failed_count},
        )

    return updated_count
