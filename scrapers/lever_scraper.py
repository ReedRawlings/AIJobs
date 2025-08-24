"""
Lever job board scraper for AI Lab Jobs Tracker.

This module scrapes job postings from Lever.co job boards, which are commonly
used by many AI labs and tech companies like Anthropic and Cohere.
"""

import re
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from schemas.job_schema import JobPosting, JobSource, JobStatus
from scrapers.base_scraper import BaseScraper


class LeverScraper(BaseScraper):
    """
    Scraper for Lever job boards.

    Lever provides job data through their API and embedded JSON in their pages.
    This scraper extracts job data from both sources.
    """

    def __init__(self, company_name: str, company_display_name: str, job_board_url: str):
        # Extract the site identifier from the URL
        # URL format: https://jobs.lever.co/{site_id}
        match = re.search(r'jobs\.lever\.co/([^/]+)', job_board_url)
        if not match:
            raise ValueError(f"Invalid Lever URL format: {job_board_url}")

        self.site_id = match.group(1)

        super().__init__(
            source=JobSource.LEVER,
            company_name=company_name,
            base_url=job_board_url,
            delay_range=(1.5, 4)  # Respectful delay for Lever
        )
        self.company_display_name = company_display_name

    async def scrape_jobs(self) -> List[JobPosting]:
        """
        Scrape all job postings from the Lever board.

        Returns:
            List of JobPosting objects with normalized data
        """
        jobs = []

        try:
            # Get the main job board page to extract embedded job data
            html = await self.get_page(self.base_url)

            # Extract job data from embedded JSON
            jobs_data = self._extract_jobs_from_html(html)

            # Parse each job
            for job_data in jobs_data:
                try:
                    job_posting = self._parse_job_data(job_data)
                    if job_posting:
                        jobs.append(job_posting)
                except Exception as e:
                    self.logger.warning(f"Failed to parse job {job_data.get('id')}: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"Failed to scrape Lever jobs: {e}")
            raise

        self.logger.info(f"Successfully scraped {len(jobs)} jobs from Lever")
        return jobs

    def _extract_jobs_from_html(self, html: str) -> List[Dict[str, Any]]:
        """
        Extract job data from the embedded JSON in the Lever job board HTML.

        Args:
            html: HTML content of the job board page

        Returns:
            List of job data dictionaries
        """
        jobs = []

        try:
            # Look for the embedded JSON data in script tags
            soup = self.parse_html(html)

            # Find script tags that contain job data
            script_tags = soup.find_all('script', type='application/json')

            for script in script_tags:
                try:
                    data = json.loads(script.string)
                    # Look for job data in various possible structures
                    if isinstance(data, dict):
                        # Check common locations where job data might be stored
                        if 'jobs' in data:
                            jobs.extend(data['jobs'])
                        elif 'postings' in data:
                            jobs.extend(data['postings'])
                        elif isinstance(data.get('data'), list):
                            jobs.extend(data['data'])
                        elif isinstance(data.get('props'), dict) and 'jobs' in data['props']:
                            jobs.extend(data['props']['jobs'])
                except json.JSONDecodeError:
                    continue

            # Alternative: look for window.STATE or similar global variables
            if not jobs:
                script_content = soup.find('script', string=re.compile(r'window\.'))
                if script_content:
                    # Extract JSON from JavaScript variable assignments
                    matches = re.findall(r'window\.\w+\s*=\s*({.+?});', script_content.string, re.DOTALL)
                    for match in matches:
                        try:
                            data = json.loads(match)
                            if 'jobs' in data:
                                jobs.extend(data['jobs'])
                                break
                        except json.JSONDecodeError:
                            continue

        except Exception as e:
            self.logger.warning(f"Failed to extract jobs from HTML: {e}")

        return jobs

    def _parse_job_data(self, job_data: Dict[str, Any]) -> Optional[JobPosting]:
        """
        Parse raw Lever job data into normalized JobPosting object.

        Args:
            job_data: Raw job data from Lever

        Returns:
            Normalized JobPosting object or None if parsing fails
        """
        try:
            # Extract basic information
            external_id = str(job_data.get('id', ''))
            title = self.normalize_text(job_data.get('text', ''))

            if not title:
                return None

            # Build job URL
            if 'hostedUrl' in job_data:
                job_url = job_data['hostedUrl']
            elif 'applyUrl' in job_data:
                job_url = job_data['applyUrl']
            else:
                # Construct URL from known pattern
                job_url = f"{self.base_url}/{external_id}"

            # Extract team/department information
            team = None
            categories = job_data.get('categories', {})
            if 'team' in categories:
                team = self.normalize_text(categories['team'])
            elif 'department' in categories:
                team = self.normalize_text(categories['department'])

            # Extract location information
            location = None
            if 'location' in job_data:
                location = self.normalize_text(job_data['location'])
            elif 'locationText' in job_data:
                location = self.normalize_text(job_data['locationText'])
            elif 'workplaceAddress' in job_data:
                # Extract city/country from address
                address = job_data['workplaceAddress']
                if isinstance(address, dict):
                    city = address.get('city', '')
                    country = address.get('country', '')
                    location = ', '.join(filter(None, [city, country]))

            # Extract employment type
            employment_type = None
            if 'commitment' in categories:
                employment_type = self.normalize_text(categories['commitment'])
            elif 'type' in job_data:
                employment_type = self.normalize_text(job_data['type'])

            # Extract description
            description = None
            if 'description' in job_data:
                description = self.normalize_text(job_data['description'])
            elif 'descriptionPlain' in job_data:
                description = self.normalize_text(job_data['descriptionPlain'])

            # Extract additional metadata
            additional = job_data.get('additional', '')

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
                job_url=job_url,
                apply_url=job_url,  # Lever typically uses the same URL for viewing and applying
                source_url=self.base_url,
                first_seen=current_time,
                last_seen=current_time,
                raw_data=job_data
            )

            return job_posting

        except Exception as e:
            self.logger.warning(f"Failed to parse job data: {e}")
            return None