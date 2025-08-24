"""
Ashby job board scraper for AI Lab Jobs Tracker.

This scraper fetches job postings from Ashby job boards used by some AI companies.
"""

from typing import List, Dict, Any, Optional

from schemas.job_schema import JobPosting, JobSource
from scrapers.base_scraper import BaseScraper


class AshbyScraper(BaseScraper):
    """Scraper for Ashby job boards."""

    def __init__(
        self,
        company_name: str,
        company_display_name: str,
        job_board_url: str,
    ):
        self.company_display_name = company_display_name
        self.company_slug = job_board_url.rstrip("/").split("/")[-1]
        self.api_url = f"https://api.ashbyhq.com/api/public/job-board?orgSlug={self.company_slug}"
        super().__init__(
            source=JobSource.ASHBY,
            company_name=company_name,
            base_url=job_board_url.rstrip("/"),
            delay_range=(1, 3),
        )

    async def scrape_jobs(self) -> List[JobPosting]:
        """Scrape all job postings from the Ashby board."""
        data = await self.get_json(self.api_url)
        jobs_data = []
        if isinstance(data, dict):
            if "jobs" in data:
                jobs_data = data["jobs"]
            elif "jobBoard" in data and isinstance(data["jobBoard"], dict):
                jobs_data = data["jobBoard"].get("jobs", [])
        jobs: List[JobPosting] = []
        for item in jobs_data:
            job = self._parse_job(item)
            if job:
                jobs.append(job)
        self.logger.info(f"Successfully scraped {len(jobs)} jobs from Ashby")
        return jobs

    def _parse_job(self, data: Dict[str, Any]) -> Optional[JobPosting]:
        """Parse an Ashby job entry into JobPosting schema."""
        external_id = str(data.get("id") or data.get("slug"))
        title = self.normalize_text(data.get("title"))
        if not external_id or not title:
            return None

        location = None
        locations = data.get("locations")
        if locations:
            first = locations[0]
            if isinstance(first, dict):
                location = self.normalize_text(first.get("name"))
            else:
                location = self.normalize_text(first)

        team = None
        departments = data.get("departments")
        if departments:
            first = departments[0]
            if isinstance(first, dict):
                team = self.normalize_text(first.get("name"))
            else:
                team = self.normalize_text(first)

        job_url = f"{self.base_url}/{external_id}"
        current_time = self.get_current_timestamp()
        return JobPosting(
            job_id=self.create_job_id(external_id),
            source=self.source,
            company_name=self.company_display_name,
            external_id=external_id,
            title=title,
            team=team,
            location=location,
            job_url=job_url,
            source_url=self.base_url,
            first_seen=current_time,
            last_seen=current_time,
            raw_data=data,
        )
