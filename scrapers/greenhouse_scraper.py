"""
Greenhouse job board scraper for AI Lab Jobs Tracker.

This module scrapes job postings from Greenhouse.io job boards, which are commonly
used by many AI labs and tech companies.
"""

import re
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from schemas.job_schema import JobPosting, JobSource, JobStatus
from scrapers.base_scraper import BaseScraper


class GreenhouseScraper(BaseScraper):
    """
    Scraper for Greenhouse job boards.

    Greenhouse provides both HTML pages and JSON API endpoints for job data.
    This scraper primarily uses the JSON API for reliability and completeness.
    """

    def __init__(self, company_name: str, company_display_name: str, job_board_url: str):
        # Extract the board identifier from the URL
        # URL format: https://boards.greenhouse.io/{board_id}
        match = re.search(r'boards\.greenhouse\.io/([^/]+)', job_board_url)
        if not match:
            raise ValueError(f"Invalid Greenhouse URL format: {job_board_url}")

        self.board_id = match.group(1)
        self.api_base_url = f"https://boards-api.greenhouse.io/v1/boards/{self.board_id}"

        super().__init__(
            source=JobSource.GREENHOUSE,
            company_name=company_name,
            base_url=job_board_url,
            delay_range=(2, 5)  # Higher delay for Greenhouse to be respectful
        )
        self.company_display_name = company_display_name

    async def scrape_jobs(self) -> List[JobPosting]:
        """
        Scrape all job postings from the Greenhouse board.

        Returns:
            List of JobPosting objects with normalized data
        """
        jobs = []

        try:
            # First, get the list of all jobs
            jobs_data = await self._get_jobs_list()

            # Then get detailed information for each job
            for job_data in jobs_data:
                try:
                    job_posting = await self._parse_job_data(job_data)
                    if job_posting:
                        jobs.append(job_posting)
                except Exception as e:
                    self.logger.warning(f"Failed to parse job {job_data.get('id')}: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"Failed to scrape Greenhouse jobs: {e}")
            raise

        self.logger.info(f"Successfully scraped {len(jobs)} jobs from Greenhouse")
        return jobs

    async def _get_jobs_list(self) -> List[Dict[str, Any]]:
        """
        Get the list of all jobs from Greenhouse API.

        Returns:
            List of job data dictionaries
        """
        api_url = f"{self.api_base_url}/jobs"

        try:
            data = await self.get_json(api_url)
            return data.get('jobs', [])
        except Exception as e:
            self.logger.error(f"Failed to fetch jobs list: {e}")
            raise

    async def _get_job_details(self, job_id: str) -> Dict[str, Any]:
        """
        Get detailed information for a specific job.

        Args:
            job_id: Greenhouse internal job ID

        Returns:
            Detailed job data dictionary
        """
        api_url = f"{self.api_base_url}/jobs/{job_id}"

        try:
            return await self.get_json(api_url)
        except Exception as e:
            self.logger.warning(f"Failed to fetch job details for {job_id}: {e}")
            raise

    async def _parse_job_data(self, job_data: Dict[str, Any]) -> Optional[JobPosting]:
        """
        Parse raw Greenhouse job data into normalized JobPosting object.

        Args:
            job_data: Raw job data from Greenhouse API

        Returns:
            Normalized JobPosting object or None if parsing fails
        """
        try:
            # Get detailed job information
            job_details = await self._get_job_details(job_data['id'])

            # Extract basic information
            external_id = str(job_data['id'])
            title = self.normalize_text(job_data.get('title', ''))

            if not title:
                return None

            # Extract team/department information
            team = None
            departments = job_data.get('departments', [])
            if departments:
                team = self.normalize_text(departments[0].get('name'))

            # Extract location information
            location = None
            locations = job_data.get('location', {}).get('name')
            if locations:
                location = self.normalize_text(locations)

            # Extract employment type
            employment_type = None
            if 'employment_type' in job_data:
                employment_type = self.normalize_text(job_data['employment_type'])

            # Build job URL
            job_url = f"https://boards.greenhouse.io/{self.board_id}/jobs/{external_id}"

            # Extract description and requirements
            description = None
            requirements = []

            if 'content' in job_details:
                content = job_details['content']
                if content:
                    # Parse HTML content for description
                    soup = self.parse_html(content)

                    # Try to extract main content sections
                    description_elem = soup.find(['div', 'p'], class_=lambda x: x and ('content' in x.lower() or 'description' in x.lower()))
                    if description_elem:
                        description = self.extract_text_from_html(description_elem)
                    else:
                        # Fallback to first paragraph or general content
                        first_p = soup.find('p')
                        if first_p:
                            description = self.extract_text_from_html(first_p)
                        else:
                            description = self.extract_text_from_html(soup)

            # Extract requirements if available in structured format
            if 'questions' in job_details:
                for question in job_details['questions']:
                    if 'required' in question.get('label', '').lower():
                        requirements.append(question.get('label', ''))

            # Create the job posting
            current_time = self.get_current_timestamp()

            job_posting = JobPosting(
                job_id=self.create_job_id(external_id),
                source=self.source,
                company_name=self.company_display_name,
                external_id=external_id,
                title=title,
                team=team,
                location=location,
                employment_type=employment_type,
                description=description,
                requirements=requirements if requirements else None,
                job_url=job_url,
                source_url=self.base_url,
                first_seen=current_time,
                last_seen=current_time,
                raw_data=job_data
            )

            return job_posting

        except Exception as e:
            self.logger.warning(f"Failed to parse job data: {e}")
            return None