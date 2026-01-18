"""
CLI entry point for intelligence-scraper library

Provides command-line interface for running scrapers.
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

from intelligence_scraper.extractors.nvidia import NvidiaScraper
from intelligence_scraper.utils.logger import get_logger

logger = get_logger("intelligence.scraper.cli")


async def run_scraper(source: str, output_file: str, max_articles: int, timeout: int):
    """
    Run the scraper and save results to a file.

    Args:
        source: Source to scrape (currently only 'nvidia' is supported)
        output_file: Path to output JSON file
        max_articles: Maximum number of articles to scrape
        timeout: Request timeout in seconds
    """
    logger.info(
        f"Starting scraper CLI",
        extra={
            "source": source,
            "output_file": output_file,
            "max_articles": max_articles,
            "timeout": timeout,
        },
    )

    # Select scraper based on source
    if source.lower() == "nvidia":
        scraper = NvidiaScraper(max_articles=max_articles, timeout=timeout)
    else:
        logger.error(f"Unsupported source: {source}")
        print(f"Error: Unsupported source '{source}'. Supported sources: nvidia", file=sys.stderr)
        sys.exit(1)

    try:
        # Run scraper
        articles = await scraper.scrape()

        if not articles:
            logger.warning("No articles were scraped")
            print("Warning: No articles were scraped", file=sys.stderr)

        # Convert articles to JSON
        articles_data = [article.model_dump(mode="json") for article in articles]

        # Write to output file
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(articles_data, f, indent=2, ensure_ascii=False, default=str)

        logger.info(
            f"Successfully scraped {len(articles)} articles to {output_file}",
            extra={"article_count": len(articles), "output_file": output_file},
        )

        print(f"Successfully scraped {len(articles)} articles")
        print(f"Output saved to: {output_file}")

    except Exception as e:
        logger.error(f"Scraping failed: {e}", extra={"error": str(e)})
        print(f"Error: Scraping failed - {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """
    Main CLI entry point.

    Command usage:
        intelligence-scraper <source> <output-file> [options]

    Examples:
        intelligence-scraper nvidia articles.json
        intelligence-scraper nvidia articles.json --max-articles 50 --timeout 60
    """
    parser = argparse.ArgumentParser(
        description="Scrape articles from various sources",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s nvidia articles.json
  %(prog)s nvidia articles.json --max-articles 50
  %(prog)s nvidia articles.json --max-articles 100 --timeout 60
        """,
    )

    parser.add_argument(
        "source",
        type=str,
        help="Source to scrape (e.g., 'nvidia')",
    )

    parser.add_argument(
        "output_file",
        type=str,
        help="Path to output JSON file",
    )

    parser.add_argument(
        "--max-articles",
        type=int,
        default=100,
        help="Maximum number of articles to scrape (default: 100)",
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Request timeout in seconds (default: 30)",
    )

    args = parser.parse_args()

    # Run scraper
    asyncio.run(run_scraper(args.source, args.output_file, args.max_articles, args.timeout))


if __name__ == "__main__":
    main()
