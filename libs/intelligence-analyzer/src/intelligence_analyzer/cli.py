"""
CLI entry point for intelligence-analyzer library

Provides command-line interface for running analysis.
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

from intelligence_analyzer.models import AnalysisInput, AnalysisResult
from intelligence_analyzer.llm.client import OllamaClient
from intelligence_analyzer.analyzers.unified import UnifiedAnalyzer
from intelligence_analyzer.utils.logger import get_logger

logger = get_logger("intelligence.analyzer.cli")


async def run_analyzer(
    input_file: str,
    output_file: str,
    llm_url: str,
    llm_model: str,
    timeout: int,
):
    """
    Run the analyzer on articles from input file and save results.

    Args:
        input_file: Path to input JSON file (array of articles)
        output_file: Path to output JSON file
        llm_url: Ollama service URL
        llm_model: LLM model name
        timeout: Request timeout in seconds
    """
    logger.info(
        f"Starting analyzer CLI",
        extra={
            "input_file": input_file,
            "output_file": output_file,
            "llm_url": llm_url,
            "llm_model": llm_model,
            "timeout": timeout,
        },
    )

    try:
        # Read input file
        input_path = Path(input_file)
        if not input_path.exists():
            logger.error(f"Input file not found: {input_file}")
            print(f"Error: Input file not found: {input_file}", file=sys.stderr)
            sys.exit(1)

        with open(input_path, "r", encoding="utf-8") as f:
            articles_data = json.load(f)

        if not isinstance(articles_data, list):
            logger.error("Input file must contain an array of articles")
            print("Error: Input file must contain an array of articles", file=sys.stderr)
            sys.exit(1)

        logger.info(f"Loaded {len(articles_data)} articles from input file")

        # Initialize LLM client and analyzer
        llm_client = OllamaClient(base_url=llm_url, model=llm_model, timeout=timeout)
        analyzer = UnifiedAnalyzer(llm_client=llm_client)

        # Check LLM service health
        is_healthy = await llm_client.health_check()
        if not is_healthy:
            logger.error(f"LLM service not accessible at {llm_url}")
            print(f"Error: LLM service not accessible at {llm_url}", file=sys.stderr)
            print("Make sure Ollama is running and accessible", file=sys.stderr)
            sys.exit(1)

        logger.info("LLM service is healthy")

        # Analyze each article
        results = []
        failed_count = 0

        for i, article_data in enumerate(articles_data):
            logger.info(
                f"Analyzing article {i + 1}/{len(articles_data)}",
                extra={"progress": f"{i + 1}/{len(articles_data)}"},
            )

            try:
                # Convert to AnalysisInput
                analysis_input = AnalysisInput(**article_data)

                # Analyze
                analysis_result = await analyzer.analyze(analysis_input)

                # Store result
                result_data = {
                    "url": str(article_data["url"]),
                    "title": article_data["title"],
                    "analysis": analysis_result.model_dump(mode="json"),
                }
                results.append(result_data)

                logger.info(
                    f"Successfully analyzed article",
                    extra={"url": article_data["url"]},
                )

            except Exception as e:
                logger.error(
                    f"Failed to analyze article: {e}",
                    extra={"url": article_data.get("url", "unknown"), "error": str(e)},
                )
                failed_count += 1
                print(
                    f"Warning: Failed to analyze article {i + 1}: {e}",
                    file=sys.stderr,
                )
                continue

        # Write results to output file
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        logger.info(
            f"Analysis complete: {len(results)} successful, {failed_count} failed",
            extra={
                "successful": len(results),
                "failed": failed_count,
                "output_file": output_file,
            },
        )

        print(f"Successfully analyzed {len(results)} articles")
        if failed_count > 0:
            print(f"Failed to analyze {failed_count} articles")
        print(f"Results saved to: {output_file}")

    except Exception as e:
        logger.error(f"Analysis failed: {e}", extra={"error": str(e)})
        print(f"Error: Analysis failed - {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """
    Main CLI entry point.

    Command usage:
        intelligence-analyzer <input-file> <output-file> [options]

    Examples:
        intelligence-analyzer articles.json analysis.json
        intelligence-analyzer articles.json analysis.json --llm-url http://localhost:11434
    """
    parser = argparse.ArgumentParser(
        description="Analyze articles using LLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s articles.json analysis.json
  %(prog)s articles.json analysis.json --llm-url http://localhost:11434
  %(prog)s articles.json analysis.json --llm-model llama3 --timeout 60
        """,
    )

    parser.add_argument(
        "input_file",
        type=str,
        help="Path to input JSON file (array of articles)",
    )

    parser.add_argument(
        "output_file",
        type=str,
        help="Path to output JSON file",
    )

    parser.add_argument(
        "--llm-url",
        type=str,
        default="http://localhost:11434",
        help="Ollama service URL (default: http://localhost:11434)",
    )

    parser.add_argument(
        "--llm-model",
        type=str,
        default="llama3",
        help="LLM model name (default: llama3)",
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="LLM request timeout in seconds (default: 30)",
    )

    args = parser.parse_args()

    # Run analyzer
    asyncio.run(
        run_analyzer(
            args.input_file,
            args.output_file,
            args.llm_url,
            args.llm_model,
            args.timeout,
        )
    )


if __name__ == "__main__":
    main()
