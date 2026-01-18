"""
Base scraper abstract class

Defines the interface that all scrapers must implement.
"""

from abc import ABC, abstractmethod
from typing import List
from intelligence_scraper.models import ScrapedArticle


class BaseScraper(ABC):
    """
    Abstract base class for all web scrapers.

    All scraper implementations must inherit from this class and implement
    the scrape method.
    """

    def __init__(self, max_articles: int = 100, timeout: int = 30):
        """
        Initialize the scraper with configuration.

        Args:
            max_articles: Maximum number of articles to scrape
            timeout: Request timeout in seconds
        """
        self.max_articles = max_articles
        self.timeout = timeout

    @abstractmethod
    async def scrape(self) -> List[ScrapedArticle]:
        """
        Scrape articles from the target source.

        Returns:
            List[ScrapedArticle]: List of scraped articles

        Raises:
            Exception: If scraping fails
        """
        pass

    @abstractmethod
    def get_source_name(self) -> str:
        """
        Get the name of the source being scraped.

        Returns:
            str: Source name (e.g., "NVIDIA Newsroom")
        """
        pass
