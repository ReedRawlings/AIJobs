"""
Data schema definitions for AI Lab Jobs Tracker.

This module defines the standardized schema for job postings collected from various sources.
All scraped job data is normalized to this schema before being stored or processed.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum


class JobStatus(Enum):
    """Status of a job posting."""
    ACTIVE = "active"
    CLOSED = "closed"
    UPDATED = "updated"
    NEW = "new"


class JobSource(Enum):
    """Supported job posting platforms."""
    GREENHOUSE = "greenhouse"
    LEVER = "lever"
    WORKDAY = "workday"
    ASHBY = "ashby"
    CUSTOM = "custom"


@dataclass
class JobPosting:
    """
    Standardized job posting data structure.

    All job postings from different sources are normalized to this schema.
    """

    # Unique identifier for the job (combination of source + external_id)
    job_id: str

    # Source information
    source: JobSource
    company_name: str
    external_id: str  # ID from the source platform

    # Job details
    title: str

    # URLs and metadata (required fields first)
    job_url: str
    source_url: str  # URL where this job was scraped from

    # Dates (required fields)
    first_seen: datetime
    last_seen: datetime

    # Optional fields (all with defaults)
    team: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None  # Full-time, Part-time, Contract, etc.
    description: Optional[str] = None
    requirements: Optional[List[str]] = None
    apply_url: Optional[str] = None
    updated_at: Optional[datetime] = None

    # Status tracking
    status: JobStatus = JobStatus.ACTIVE

    # Additional metadata
    salary_range: Optional[str] = None
    remote_policy: Optional[str] = None  # Remote, Hybrid, On-site
    experience_level: Optional[str] = None  # Entry, Mid, Senior, etc.

    # Raw data for debugging/extensibility
    raw_data: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert job posting to dictionary for CSV/JSON serialization."""
        data = asdict(self)

        # Convert enums to strings
        data['source'] = self.source.value
        data['status'] = self.status.value

        # Convert datetimes to ISO format strings
        if self.first_seen:
            data['first_seen'] = self.first_seen.isoformat()
        if self.last_seen:
            data['last_seen'] = self.last_seen.isoformat()
        if self.updated_at:
            data['updated_at'] = self.updated_at.isoformat()

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'JobPosting':
        """Create job posting from dictionary (for loading from CSV/JSON)."""
        # Convert string values back to enums
        data['source'] = JobSource(data['source'])
        data['status'] = JobStatus(data['status'])

        # Convert ISO strings back to datetimes
        if data.get('first_seen'):
            data['first_seen'] = datetime.fromisoformat(data['first_seen'])
        if data.get('last_seen'):
            data['last_seen'] = datetime.fromisoformat(data['last_seen'])
        if data.get('updated_at'):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])

        return cls(**data)

    @property
    def is_active(self) -> bool:
        """Check if job posting is currently active."""
        return self.status == JobStatus.ACTIVE

    @property
    def days_active(self) -> int:
        """Calculate how many days this job has been active."""
        return (self.last_seen - self.first_seen).days


@dataclass
class JobEvent:
    """
    Represents a change event for a job posting.

    Used to track when jobs are added, updated, or removed.
    """

    event_type: str  # 'appeared', 'updated', 'closed'
    job_id: str
    timestamp: datetime
    previous_data: Optional[Dict[str, Any]] = None
    new_data: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data