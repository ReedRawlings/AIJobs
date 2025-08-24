"""
Base scraper class for AI Lab Jobs Tracker.

This module provides a common interface and utilities for scraping job postings
from different platforms (Greenhouse, Lever, Workday, etc.).
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
import time
import random

import aiohttp
from bs4 import BeautifulSoup
import json

from schemas.job_schema import JobPosting, JobSource


class BaseScraper(ABC):
    """
    Abstract base class for job scrapers.

    Provides common functionality like HTTP requests, rate limiting, and error handling.
    """

    def __init__(
        self,
        source: JobSource,
        company_name: str,
        base_url: str,
        delay_range: tuple = (1, 3),
        max_retries: int = 3,
        timeout: int = 30
    ):
        self.source = source
        self.company_name = company_name
        self.base_url = base_url
        self.delay_range = delay_range
        self.max_retries = max_retries
        self.timeout = timeout

        # Set up logging
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self.logger.setLevel(logging.INFO)

        # Create session as None - will be initialized in context manager
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry."""
        connector = aiohttp.TCPConnector(limit=10)  # Connection pooling
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def get_page(self, url: str, headers: Optional[Dict[str, str]] = None) -> str:
        """
        Fetch a web page with retry logic and rate limiting.

        Args:
            url: URL to fetch
            headers: Optional HTTP headers

        Returns:
            HTML content of the page

        Raises:
            Exception: If all retries fail
        """
        if not self.session:
            raise RuntimeError("Scraper must be used as async context manager")

        default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        if headers:
            default_headers.update(headers)

        for attempt in range(self.max_retries):
            try:
                # Rate limiting
                delay = random.uniform(*self.delay_range)
                await asyncio.sleep(delay)

                self.logger.info(f"Fetching {url} (attempt {attempt + 1})")

                async with self.session.get(url, headers=default_headers) as response:
                    response.raise_for_status()
                    return await response.text()

            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

    async def get_json(self, url: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Fetch JSON data from an API endpoint.

        Args:
            url: API endpoint URL
            headers: Optional HTTP headers

        Returns:
            Parsed JSON data

        Raises:
            Exception: If request fails or JSON is invalid
        """
        html = await self.get_page(url, headers)
        try:
            return json.loads(html)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from {url}: {e}")

    def parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML content using BeautifulSoup."""
        return BeautifulSoup(html, 'html.parser')

    @abstractmethod
    async def scrape_jobs(self) -> List[JobPosting]:
        """
        Abstract method to scrape job postings from the platform.

        Must be implemented by each platform-specific scraper.

        Returns:
            List of normalized JobPosting objects
        """
        pass

    def create_job_id(self, external_id: str) -> str:
        """Create a unique job ID combining source and external ID."""
        return f"{self.source.value}_{self.company_name}_{external_id}"

    def normalize_text(self, text: Optional[str]) -> Optional[str]:
        """Normalize text by stripping whitespace and handling None values."""
        if text is None:
            return None
        return text.strip()

    def extract_text_from_html(self, html_element) -> Optional[str]:
        """Extract clean text from a BeautifulSoup HTML element."""
        if html_element is None:
            return None
        return self.normalize_text(html_element.get_text())

    def get_current_timestamp(self) -> datetime:
        """Get current UTC timestamp."""
        return datetime.utcnow()


class ScraperRegistry:
    """
    Registry to manage and run multiple scrapers.
    """

    def __init__(self):
        self.scrapers: Dict[str, BaseScraper] = {}

    def register(self, scraper: BaseScraper):
        """Register a scraper instance."""
        key = f"{scraper.company_name}_{scraper.source.value}"
        self.scrapers[key] = scraper
        logging.info(f"Registered scraper: {key}")

    async def run_all(self) -> List[JobPosting]:
        """
        Run all registered scrapers and collect results.

        Returns:
            Combined list of all job postings from all scrapers
        """
        all_jobs = []

        for key, scraper in self.scrapers.items():
            try:
                logging.info(f"Running scraper: {key}")
                async with scraper as s:
                    jobs = await s.scrape_jobs()
                    all_jobs.extend(jobs)
                    logging.info(f"Scraper {key} found {len(jobs)} jobs")
            except Exception as e:
                logging.error(f"Scraper {key} failed: {e}")
                continue

        return all_jobs