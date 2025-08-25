"""
Ashby job board scraper for AI Lab Jobs Tracker.

This scraper fetches job postings from Ashby job boards used by some AI companies.
For companies that don't allow API access (like OpenAI), it falls back to JavaScript extraction.
"""

import re
import json
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
        # Try API first
        try:
            data = await self.get_json(self.api_url)
            if isinstance(data, dict) and "jobs" in data:
                jobs_data = data["jobs"]
                jobs: List[JobPosting] = []
                for item in jobs_data:
                    job = self._parse_job(item)
                    if job:
                        jobs.append(job)
                self.logger.info(f"Successfully scraped {len(jobs)} jobs from Ashby API")
                return jobs
        except Exception as e:
            self.logger.warning(f"Ashby API failed for {self.company_name}: {e}")
        
        # Fallback to JavaScript extraction for companies that block API access
        self.logger.info(f"Falling back to JavaScript extraction for {self.company_name}")
        return await self._scrape_from_javascript()

    async def _scrape_from_javascript(self) -> List[JobPosting]:
        """Extract jobs from embedded JavaScript when API is not accessible."""
        try:
            html = await self.get_page(self.base_url)
            if not html:
                self.logger.error(f"Failed to get HTML from {self.base_url}")
                return []
            
            # Find the main script containing job data
            script_pattern = r'<script[^>]*>([^<]*)</script>'
            scripts = re.findall(script_pattern, html, re.DOTALL)
            
            main_script = None
            for script in scripts:
                if len(script) > 100000:  # Look for the large script with job data
                    main_script = script
                    break
            
            if not main_script:
                self.logger.error("No large script found in HTML")
                return []
            
            # Extract job objects using the pattern we discovered
            job_object_pattern = r'\{[^{}]*"id"[^{}]*"title"[^{}]*\}'
            job_objects = re.findall(job_object_pattern, main_script, re.DOTALL)
            
            self.logger.info(f"Found {len(job_objects)} potential job objects in JavaScript")
            
            jobs: List[JobPosting] = []
            for job_text in job_objects:
                try:
                    # Clean the job text and parse as JSON
                    cleaned = re.sub(r',\s*}', '}', job_text)
                    cleaned = re.sub(r'[^\x20-\x7E]', '', cleaned)
                    
                    job_data = json.loads(cleaned)
                    if 'id' in job_data and 'title' in job_data:
                        job = self._parse_job_from_js(job_data)
                        if job:
                            jobs.append(job)
                            
                except (json.JSONDecodeError, Exception) as e:
                    self.logger.debug(f"Failed to parse job object: {e}")
                    continue
            
            self.logger.info(f"Successfully extracted {len(jobs)} jobs from JavaScript")
            return jobs
            
        except Exception as e:
            self.logger.error(f"JavaScript extraction failed: {e}")
            return []

    def _parse_job_from_js(self, data: Dict[str, Any]) -> Optional[JobPosting]:
        """Parse a job from JavaScript data into JobPosting schema."""
        external_id = str(data.get("id"))
        title = self.normalize_text(data.get("title"))
        if not external_id or not title:
            return None

        location = self.normalize_text(data.get("locationName"))
        team = self.normalize_text(data.get("teamName"))
        department = self.normalize_text(data.get("departmentName"))
        
        # Construct the job URL
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

    def _parse_job(self, data: Dict[str, Any]) -> Optional[JobPosting]:
        """Parse an Ashby job entry into JobPosting schema (API version)."""
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
