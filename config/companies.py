"""
Company configuration for AI Lab Jobs Tracker.

This module defines the companies to track and their career page configurations.
Each company specifies which platform they use and their specific URLs.
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from schemas.job_schema import JobSource


@dataclass
class CompanyConfig:
    """
    Configuration for a single company's job postings.
    """

    name: str
    display_name: str
    source: JobSource
    base_url: str
    job_board_url: str
    additional_config: Dict[str, Any] = None

    def __post_init__(self):
        if self.additional_config is None:
            self.additional_config = {}


# Configuration for major AI labs and companies
COMPANIES = [
    # OpenAI
    CompanyConfig(
        name="openai",
        display_name="OpenAI",
        source=JobSource.ASHBY,
        base_url="https://jobs.ashbyhq.com",
        job_board_url="https://jobs.ashbyhq.com/openai",
    ),

    # Anthropic
    CompanyConfig(
        name="anthropic",
        display_name="Anthropic",
        source=JobSource.LEVER,
        base_url="https://jobs.lever.co",
        job_board_url="https://jobs.lever.co/anthropic",
    ),

    # DeepMind (Google)
    CompanyConfig(
        name="deepmind",
        display_name="DeepMind",
        source=JobSource.GREENHOUSE,
        base_url="https://boards.greenhouse.io",
        job_board_url="https://boards.greenhouse.io/deepmind",
    ),

    # Cohere
    CompanyConfig(
        name="cohere",
        display_name="Cohere",
        source=JobSource.LEVER,
        base_url="https://jobs.lever.co",
        job_board_url="https://jobs.lever.co/cohere",
    ),

    # Hugging Face
    CompanyConfig(
        name="huggingface",
        display_name="Hugging Face",
        source=JobSource.WORKDAY,
        base_url="https://huggingface.wd1.myworkdayjobs.com",
        job_board_url="https://huggingface.wd1.myworkdayjobs.com/huggingface",
        additional_config={
            "company_id": "huggingface"
        }
    ),

    # Scale AI
    CompanyConfig(
        name="scaleai",
        display_name="Scale AI",
        source=JobSource.GREENHOUSE,
        base_url="https://boards.greenhouse.io",
        job_board_url="https://boards.greenhouse.io/scaleai",
    ),

    # Midjourney
    CompanyConfig(
        name="midjourney",
        display_name="Midjourney",
        source=JobSource.ASHBY,
        base_url="https://jobs.ashbyhq.com",
        job_board_url="https://jobs.ashbyhq.com/midjourney",
    ),

    # Stability AI
    CompanyConfig(
        name="stabilityai",
        display_name="Stability AI",
        source=JobSource.WORKDAY,
        base_url="https://stability.wd1.myworkdayjobs.com",
        job_board_url="https://stability.wd1.myworkdayjobs.com/Stability",
        additional_config={
            "company_id": "stability"
        }
    ),

    # Inflection AI
    CompanyConfig(
        name="inflectionai",
        display_name="Inflection AI",
        source=JobSource.GREENHOUSE,
        base_url="https://boards.greenhouse.io",
        job_board_url="https://boards.greenhouse.io/inflectionai",
    ),

    # Adept AI
    CompanyConfig(
        name="adept",
        display_name="Adept",
        source=JobSource.GREENHOUSE,
        base_url="https://boards.greenhouse.io",
        job_board_url="https://boards.greenhouse.io/adept",
    ),

    # Character.AI
    CompanyConfig(
        name="characterai",
        display_name="Character.AI",
        source=JobSource.GREENHOUSE,
        base_url="https://boards.greenhouse.io",
        job_board_url="https://boards.greenhouse.io/character",
    ),

    # Replit
    CompanyConfig(
        name="replit",
        display_name="Replit",
        source=JobSource.GREENHOUSE,
        base_url="https://boards.greenhouse.io",
        job_board_url="https://boards.greenhouse.io/replit",
    ),

    # Runway
    CompanyConfig(
        name="runway",
        display_name="Runway",
        source=JobSource.GREENHOUSE,
        base_url="https://boards.greenhouse.io",
        job_board_url="https://boards.greenhouse.io/runwayml",
    ),

    # Perplexity AI
    CompanyConfig(
        name="perplexity",
        display_name="Perplexity AI",
        source=JobSource.GREENHOUSE,
        base_url="https://boards.greenhouse.io",
        job_board_url="https://boards.greenhouse.io/perplexityai",
    ),
]


def get_company_configs() -> List[CompanyConfig]:
    """
    Get all company configurations.

    Returns:
        List of all configured companies
    """
    return COMPANIES


def get_company_by_name(name: str) -> CompanyConfig:
    """
    Get company configuration by name.

    Args:
        name: Company name identifier

    Returns:
        CompanyConfig for the specified company

    Raises:
        ValueError: If company not found
    """
    for company in COMPANIES:
        if company.name == name:
            return company
    raise ValueError(f"Company not found: {name}")


def get_companies_by_source(source: JobSource) -> List[CompanyConfig]:
    """
    Get all companies using a specific job platform.

    Args:
        source: Job platform to filter by

    Returns:
        List of companies using the specified platform
    """
    return [company for company in COMPANIES if company.source == source]