"""
Change tracking system for AI Lab Jobs Tracker.

This module tracks changes in job postings over time, detecting when jobs are
added, updated, or removed. It maintains a registry of current jobs and generates
event logs for analysis.
"""

import json
import csv
import os
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, date
from dataclasses import asdict

from schemas.job_schema import JobPosting, JobEvent, JobStatus


class ChangeTracker:
    """
    Tracks changes in job postings across multiple runs.

    Maintains a registry of current jobs and detects:
    - New jobs (appeared)
    - Updated jobs (changed details)
    - Removed jobs (closed)
    """

    def __init__(self, registry_file: str = "outputs/registry/current_jobs.json"):
        self.registry_file = registry_file
        self.current_jobs: Dict[str, JobPosting] = {}
        self.previous_jobs: Dict[str, JobPosting] = {}
        self.events: List[JobEvent] = []

        # Ensure output directories exist
        os.makedirs(os.path.dirname(registry_file), exist_ok=True)

        # Load previous job registry if it exists
        self._load_registry()

    def _load_registry(self):
        """Load the previous job registry from disk."""
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for job_dict in data:
                        job = JobPosting.from_dict(job_dict)
                        self.previous_jobs[job.job_id] = job
                print(f"Loaded {len(self.previous_jobs)} previous jobs from registry")
            except Exception as e:
                print(f"Warning: Could not load previous registry: {e}")
                self.previous_jobs = {}

    def _save_registry(self):
        """Save the current job registry to disk."""
        try:
            job_dicts = [job.to_dict() for job in self.current_jobs.values()]
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                json.dump(job_dicts, f, indent=2, ensure_ascii=False)
            print(f"Saved {len(self.current_jobs)} jobs to registry")
        except Exception as e:
            print(f"Error saving registry: {e}")

    def process_new_scraping(self, new_jobs: List[JobPosting]) -> List[JobEvent]:
        """
        Process a new batch of scraped jobs and detect changes.

        Args:
            new_jobs: List of newly scraped job postings

        Returns:
            List of change events (appeared/updated/closed)
        """
        self.events = []
        self.current_jobs = {}

        # Index new jobs by job_id
        for job in new_jobs:
            self.current_jobs[job.job_id] = job

        # Detect new and updated jobs
        current_job_ids: Set[str] = set(self.current_jobs.keys())
        previous_job_ids: Set[str] = set(self.previous_jobs.keys())

        # Find new jobs
        new_job_ids = current_job_ids - previous_job_ids
        for job_id in new_job_ids:
            job = self.current_jobs[job_id]
            job.status = JobStatus.NEW
            job.first_seen = datetime.utcnow()
            job.last_seen = datetime.utcnow()
            event = JobEvent(
                event_type='appeared',
                job_id=job_id,
                timestamp=datetime.utcnow(),
                new_data=job.to_dict()
            )
            self.events.append(event)

        # Find updated jobs
        updated_job_ids = current_job_ids & previous_job_ids
        for job_id in updated_job_ids:
            current_job = self.current_jobs[job_id]
            previous_job = self.previous_jobs[job_id]

            # Check if job details have changed
            if self._jobs_differ(current_job, previous_job):
                current_job.status = JobStatus.UPDATED
                current_job.first_seen = previous_job.first_seen  # Preserve original first_seen
                current_job.last_seen = datetime.utcnow()
                current_job.updated_at = datetime.utcnow()

                event = JobEvent(
                    event_type='updated',
                    job_id=job_id,
                    timestamp=datetime.utcnow(),
                    previous_data=previous_job.to_dict(),
                    new_data=current_job.to_dict()
                )
                self.events.append(event)
            else:
                # Job exists but hasn't changed
                current_job.status = JobStatus.ACTIVE
                current_job.first_seen = previous_job.first_seen
                current_job.last_seen = datetime.utcnow()

        # Find closed/removed jobs
        closed_job_ids = previous_job_ids - current_job_ids
        for job_id in closed_job_ids:
            previous_job = self.previous_jobs[job_id]
            # Create a copy with closed status
            closed_job = JobPosting(
                job_id=previous_job.job_id,
                source=previous_job.source,
                company_name=previous_job.company_name,
                external_id=previous_job.external_id,
                title=previous_job.title,
                team=previous_job.team,
                location=previous_job.location,
                employment_type=previous_job.employment_type,
                description=previous_job.description,
                requirements=previous_job.requirements,
                job_url=previous_job.job_url,
                apply_url=previous_job.apply_url,
                source_url=previous_job.source_url,
                first_seen=previous_job.first_seen,
                last_seen=previous_job.last_seen,
                updated_at=previous_job.updated_at,
                status=JobStatus.CLOSED,
                raw_data=previous_job.raw_data
            )
            self.current_jobs[job_id] = closed_job

            event = JobEvent(
                event_type='closed',
                job_id=job_id,
                timestamp=datetime.utcnow(),
                previous_data=previous_job.to_dict()
            )
            self.events.append(event)

        # Save the updated registry
        self._save_registry()

        print(f"Change detection complete: {len(self.events)} events detected")
        print(f"  - New jobs: {len(new_job_ids)}")
        print(f"  - Updated jobs: {len([e for e in self.events if e.event_type == 'updated'])}")
        print(f"  - Closed jobs: {len(closed_job_ids)}")

        return self.events

    def _jobs_differ(self, job1: JobPosting, job2: JobPosting) -> bool:
        """
        Compare two job postings to see if they have meaningful differences.

        Args:
            job1: First job posting
            job2: Second job posting

        Returns:
            True if jobs differ in meaningful ways
        """
        # Compare key fields that would indicate a real change
        fields_to_compare = [
            'title', 'team', 'location', 'employment_type', 'description'
        ]

        for field in fields_to_compare:
            val1 = getattr(job1, field)
            val2 = getattr(job2, field)
            if val1 != val2:
                return True

        return False

    def get_current_active_jobs(self) -> List[JobPosting]:
        """Get all currently active job postings."""
        return [job for job in self.current_jobs.values() if job.is_active]

    def get_events_by_type(self, event_type: str) -> List[JobEvent]:
        """Get all events of a specific type."""
        return [event for event in self.events if event.event_type == event_type]

    def get_job_by_id(self, job_id: str) -> Optional[JobPosting]:
        """Get a specific job by its ID."""
        return self.current_jobs.get(job_id)


class OutputGenerator:
    """
    Generates various output files (CSV, NDJSON) for analysis.
    """

    def __init__(self, output_base_dir: str = "outputs"):
        self.output_base_dir = output_base_dir
        os.makedirs(output_base_dir, exist_ok=True)

    def generate_daily_outputs(self, tracker: ChangeTracker, run_date: Optional[date] = None):
        """
        Generate all output files for a daily run.

        Args:
            tracker: ChangeTracker instance with processed data
            run_date: Date of the run (defaults to today)
        """
        if run_date is None:
            run_date = date.today()

        date_str = run_date.isoformat()

        # Generate registry CSV (current active jobs)
        self._generate_registry_csv(tracker, run_date)

        # Generate daily snapshot
        self._generate_snapshot_csv(tracker, date_str)

        # Generate events log
        self._generate_events_csv(tracker, date_str)

    def _generate_registry_csv(self, tracker: ChangeTracker, run_date: date):
        """Generate current registry CSV with all active jobs."""
        registry_dir = os.path.join(self.output_base_dir, "registry")
        os.makedirs(registry_dir, exist_ok=True)

        filename = os.path.join(registry_dir, "current_jobs.csv")

        active_jobs = tracker.get_current_active_jobs()

        if active_jobs:
            self._write_jobs_to_csv(active_jobs, filename)
            print(f"Generated registry CSV: {filename} ({len(active_jobs)} jobs)")

    def _generate_snapshot_csv(self, tracker: ChangeTracker, date_str: str):
        """Generate daily snapshot CSV with all jobs from this run."""
        snapshot_dir = os.path.join(self.output_base_dir, "snapshots")
        os.makedirs(snapshot_dir, exist_ok=True)

        filename = os.path.join(snapshot_dir, f"{date_str}.csv")

        all_current_jobs = list(tracker.current_jobs.values())

        if all_current_jobs:
            self._write_jobs_to_csv(all_current_jobs, filename)
            print(f"Generated snapshot CSV: {filename} ({len(all_current_jobs)} jobs)")

    def _generate_events_csv(self, tracker: ChangeTracker, date_str: str):
        """Generate daily events CSV with all changes from this run."""
        events_dir = os.path.join(self.output_base_dir, "events")
        os.makedirs(events_dir, exist_ok=True)

        filename = os.path.join(events_dir, f"{date_str}.csv")

        if tracker.events:
            self._write_events_to_csv(tracker.events, filename)
            print(f"Generated events CSV: {filename} ({len(tracker.events)} events)")

    def _write_jobs_to_csv(self, jobs: List[JobPosting], filename: str):
        """Write job postings to CSV file."""
        if not jobs:
            return

        # Get all unique fields from job data
        fieldnames = set()
        job_dicts = []
        for job in jobs:
            job_dict = job.to_dict()
            job_dicts.append(job_dict)
            fieldnames.update(job_dict.keys())

        fieldnames = sorted(list(fieldnames))

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(job_dicts)

    def _write_events_to_csv(self, events: List[JobEvent], filename: str):
        """Write events to CSV file."""
        if not events:
            return

        fieldnames = ['event_type', 'job_id', 'timestamp', 'previous_data', 'new_data']

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for event in events:
                row = {
                    'event_type': event.event_type,
                    'job_id': event.job_id,
                    'timestamp': event.timestamp.isoformat(),
                    'previous_data': json.dumps(event.previous_data) if event.previous_data else None,
                    'new_data': json.dumps(event.new_data) if event.new_data else None
                }
                writer.writerow(row)