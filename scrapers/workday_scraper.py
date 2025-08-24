"""
Workday job board scraper for AI Lab Jobs Tracker.

This scraper fetches job postings from Workday-powered career sites
used by many AI companies.
"""

from typing import List, Dict, Any, Optional

from schemas.job_schema import JobPosting, JobSource
from scrapers.base_scraper import BaseScraper


class WorkdayScraper(BaseScraper):
    """Scraper for Workday job boards."""

    def __init__(
        self,
        company_name: str,
        company_display_name: str,
        base_url: str,
        job_board_url: str,
        company_id: str,
    ):
        self.company_display_name = company_display_name
        self.company_id = company_id
        self.job_board_url = job_board_url.rstrip("/")
        self.api_base_url = f"{base_url.rstrip('/')}/wday/cxs/{company_id}/{self.job_board_url.split('/')[-1]}"
        super().__init__(
            source=JobSource.WORKDAY,
            company_name=company_name,
            base_url=self.job_board_url,
            delay_range=(1, 3),
        )

    async def scrape_jobs(self) -> List[JobPosting]:
        """Scrape all job postings from the Workday board."""
        jobs: List[JobPosting] = []
        offset = 0
        limit = 50
        while True:
            data = await self._fetch_jobs_batch(offset, limit)
            postings = data.get("jobPostings", [])
            for posting in postings:
                job = self._parse_job(posting)
                if job:
                    jobs.append(job)
            total = data.get("total", 0)
            offset += limit
            if offset >= total:
                break
        self.logger.info(f"Successfully scraped {len(jobs)} jobs from Workday")
        return jobs

    async def _fetch_jobs_batch(self, offset: int, limit: int) -> Dict[str, Any]:
        """Fetch a batch of jobs from Workday API."""
        if not self.session:
            raise RuntimeError("Scraper must be used as async context manager")
        url = f"{self.api_base_url}/jobs"
        payload = {"limit": limit, "offset": offset, "searchText": ""}
        async with self.session.post(url, json=payload) as resp:
            resp.raise_for_status()
            return await resp.json()

    def _parse_job(self, data: Dict[str, Any]) -> Optional[JobPosting]:
        """Parse a Workday job posting into JobPosting schema."""
        external_id = str(data.get("id") or data.get("jobPostingId"))
        title = self.normalize_text(data.get("title"))
        if not external_id or not title:
            return None

        location = None
        for field in data.get("bulletFields", []):
            if field.get("label") == "locations":
                location = self.normalize_text(field.get("text"))
                break

        job_url = f"{self.job_board_url}/job/{external_id}"
        current_time = self.get_current_timestamp()
        return JobPosting(
            job_id=self.create_job_id(external_id),
            source=self.source,
            company_name=self.company_display_name,
            external_id=external_id,
            title=title,
            location=location,
            job_url=job_url,
            source_url=self.base_url,
            first_seen=current_time,
            last_seen=current_time,
            raw_data=data,
        )
