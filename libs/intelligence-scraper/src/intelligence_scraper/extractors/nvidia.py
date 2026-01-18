"""
NVIDIA Newsroom scraper implementation

Scrapes articles from the NVIDIA Newsroom using trafilatura with Playwright fallback.
"""

import asyncio
from datetime import datetime
from typing import List, Optional
import httpx
import trafilatura
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

from intelligence_scraper.models import ScrapedArticle
from intelligence_scraper.extractors.base import BaseScraper
from intelligence_scraper.utils.cleaner import clean_text, extract_title_from_content
from intelligence_scraper.utils.logger import get_logger

logger = get_logger("intelligence.scraper.nvidia")


class NvidiaScraper(BaseScraper):
    """
    Scraper for NVIDIA Newsroom articles.

    Uses trafilatura as primary extraction method with Playwright fallback
    for JavaScript-rendered content.
    """

    NEWSROOM_URL = "https://nvidianews.nvidia.com/news"
    MAX_RETRIES = 2

    def get_source_name(self) -> str:
        """Get the source name."""
        return "NVIDIA Newsroom"

    async def scrape(self) -> List[ScrapedArticle]:
        """
        Scrape articles from NVIDIA Newsroom.

        Returns:
            List[ScrapedArticle]: List of successfully scraped articles

        Raises:
            Exception: If scraping fails completely
        """
        logger.info(
            f"Starting scrape of {self.get_source_name()}",
            extra={"max_articles": self.max_articles, "timeout": self.timeout},
        )

        try:
            # Step 1: Get list of article URLs
            article_urls = await self._get_article_urls()
            logger.info(
                f"Found {len(article_urls)} article URLs",
                extra={"url_count": len(article_urls)},
            )

            # Step 2: Scrape each article
            articles = []
            for i, url in enumerate(article_urls[: self.max_articles]):
                logger.info(
                    f"Scraping article {i + 1}/{min(len(article_urls), self.max_articles)}",
                    extra={"url": url, "progress": f"{i + 1}/{self.max_articles}"},
                )

                try:
                    article = await self._scrape_article_with_retry(url)
                    if article:
                        articles.append(article)
                        logger.info(
                            f"Successfully scraped article",
                            extra={"url": url, "title": article.title},
                        )
                except Exception as e:
                    logger.error(
                        f"Failed to scrape article: {e}",
                        extra={"url": url, "error": str(e)},
                    )
                    continue

            logger.info(
                f"Scraping complete: {len(articles)} articles scraped successfully",
                extra={"total_articles": len(articles), "failed": len(article_urls) - len(articles)},
            )

            return articles

        except Exception as e:
            logger.error(
                f"Scraping failed: {e}",
                extra={"error": str(e), "source": self.get_source_name()},
            )
            raise

    async def _get_article_urls(self) -> List[str]:
        """
        Get list of article URLs from the newsroom main page.

        Returns:
            List[str]: List of article URLs (limited to top 5)
        """
        logger.info("Fetching article URLs from newsroom")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(self.NEWSROOM_URL)
                response.raise_for_status()

                # Parse HTML with BeautifulSoup
                soup = BeautifulSoup(response.text, 'lxml')

                # Extract article URLs from <article> elements
                # Each article contains: <article><h3><a href="...">
                article_urls = []
                articles = soup.find_all('article', limit=5)  # Get first 5 articles

                for article in articles:
                    # Find the link within the h3 tag
                    h3 = article.find('h3')
                    if h3:
                        link = h3.find('a')
                        if link and link.get('href'):
                            url = link['href']
                            # Handle relative URLs
                            if url.startswith('/'):
                                url = f"https://nvidianews.nvidia.com{url}"
                            article_urls.append(url)
                            logger.info(
                                f"Found article URL",
                                extra={"url": url, "title": link.get_text(strip=True)[:50]},
                            )

                logger.info(
                    f"Extracted {len(article_urls)} article URLs",
                    extra={"count": len(article_urls)},
                )
                return article_urls

            except Exception as e:
                logger.warning(
                    f"Failed to fetch article URLs with httpx: {e}",
                    extra={"error": str(e)},
                )
                # Fallback to empty list
                return []

    async def _scrape_article_with_retry(
        self, url: str, attempt: int = 1
    ) -> Optional[ScrapedArticle]:
        """
        Scrape a single article with retry logic.

        Args:
            url: Article URL
            attempt: Current attempt number

        Returns:
            Optional[ScrapedArticle]: Scraped article or None if failed
        """
        try:
            # Try trafilatura first
            article = await self._scrape_with_trafilatura(url)
            if article:
                return article

            # Fallback to Playwright
            logger.info(
                f"Trafilatura extraction failed, trying Playwright fallback",
                extra={"url": url},
            )
            article = await self._scrape_with_playwright(url)
            if article:
                return article

            raise Exception("Both trafilatura and Playwright extraction failed")

        except Exception as e:
            if attempt < self.MAX_RETRIES:
                logger.warning(
                    f"Scraping attempt {attempt} failed, retrying...",
                    extra={"url": url, "error": str(e), "attempt": attempt},
                )
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                return await self._scrape_article_with_retry(url, attempt + 1)
            else:
                logger.error(
                    f"All scraping attempts failed for article",
                    extra={"url": url, "error": str(e), "attempts": self.MAX_RETRIES},
                )
                return None

    async def _scrape_with_trafilatura(self, url: str) -> Optional[ScrapedArticle]:
        """
        Scrape article using trafilatura.

        Args:
            url: Article URL

        Returns:
            Optional[ScrapedArticle]: Scraped article or None
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()

                # Extract content with trafilatura
                content = trafilatura.extract(
                    response.text,
                    include_comments=False,
                    include_tables=False,
                    no_fallback=False,
                )

                if not content:
                    logger.warning(
                        "Trafilatura extraction returned no content",
                        extra={"url": url},
                    )
                    return None

                # Extract metadata
                metadata_result = trafilatura.extract_metadata(response.text)
                title = metadata_result.title if metadata_result and metadata_result.title else None

                if not title:
                    title = extract_title_from_content(content)

                # Clean content
                cleaned_content = clean_text(content)

                # Get publish date (simplified - would parse from metadata in production)
                publish_date = datetime.utcnow()

                article = ScrapedArticle(
                    url=url,
                    title=title,
                    content=cleaned_content,
                    publishDate=publish_date,
                    source=self.get_source_name(),
                    metadata={"scraperMethod": "trafilatura", "contentTruncated": False},
                )

                return article

        except Exception as e:
            logger.warning(
                f"Trafilatura scraping failed: {e}",
                extra={"url": url, "error": str(e)},
            )
            return None

    async def _scrape_with_playwright(self, url: str) -> Optional[ScrapedArticle]:
        """
        Scrape article using Playwright (for JavaScript-rendered content).

        Args:
            url: Article URL

        Returns:
            Optional[ScrapedArticle]: Scraped article or None
        """
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()

                try:
                    await page.goto(url, timeout=self.timeout * 1000, wait_until="networkidle")

                    # Extract content
                    content = await page.inner_text("body")
                    title_element = await page.query_selector("h1")
                    title = await title_element.inner_text() if title_element else None

                    if not title:
                        title = extract_title_from_content(content)

                    # Clean content
                    cleaned_content = clean_text(content)

                    # Get publish date
                    publish_date = datetime.utcnow()

                    article = ScrapedArticle(
                        url=url,
                        title=title,
                        content=cleaned_content,
                        publishDate=publish_date,
                        source=self.get_source_name(),
                        metadata={"scraperMethod": "playwright", "contentTruncated": False},
                    )

                    return article

                except PlaywrightTimeout as e:
                    logger.warning(
                        f"Playwright timeout: {e}",
                        extra={"url": url, "timeout": self.timeout},
                    )
                    return None

                finally:
                    await browser.close()

        except Exception as e:
            logger.warning(
                f"Playwright scraping failed: {e}",
                extra={"url": url, "error": str(e)},
            )
            return None
