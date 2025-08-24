#!/usr/bin/env python3
"""
AI Lab Jobs Tracker - Main Pipeline

This is the main entry point for the AI Lab Jobs Tracker pipeline.
It orchestrates the scraping, change detection, and output generation process.
"""

import asyncio
import logging
import argparse
from datetime import datetime, date
from typing import List

from config.companies import get_company_configs, get_companies_by_source
from scrapers.base_scraper import ScraperRegistry
from scrapers.greenhouse_scraper import GreenhouseScraper
from scrapers.lever_scraper import LeverScraper
from schemas.job_schema import JobPosting, JobSource
from schemas.change_tracker import ChangeTracker, OutputGenerator


def setup_logging(verbose: bool = False):
    """Set up logging configuration."""
    level = logging.INFO if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def create_scrapers_for_companies() -> ScraperRegistry:
    """
    Create scrapers for all configured companies.

    Returns:
        ScraperRegistry with all configured scrapers
    """
    registry = ScraperRegistry()
    companies = get_company_configs()

    for company in companies:
        try:
            if company.source == JobSource.GREENHOUSE:
                scraper = GreenhouseScraper(
                    company_name=company.name,
                    company_display_name=company.display_name,
                    job_board_url=company.job_board_url
                )
                registry.register(scraper)
                logging.info(f"Created Greenhouse scraper for {company.display_name}")

            elif company.source == JobSource.LEVER:
                scraper = LeverScraper(
                    company_name=company.name,
                    company_display_name=company.display_name,
                    job_board_url=company.job_board_url
                )
                registry.register(scraper)
                logging.info(f"Created Lever scraper for {company.display_name}")

            else:
                logging.warning(f"No scraper available for {company.source.value} platform")
                continue

        except Exception as e:
            logging.error(f"Failed to create scraper for {company.name}: {e}")
            continue

    return registry


async def run_scraping(registry: ScraperRegistry) -> List[JobPosting]:
    """
    Run all scrapers and collect job postings.

    Args:
        registry: ScraperRegistry with configured scrapers

    Returns:
        List of all scraped job postings
    """
    print(f"Starting scraping with {len(registry.scrapers)} scrapers...")
    start_time = datetime.utcnow()

    all_jobs = await registry.run_all()

    end_time = datetime.utcnow()
    duration = (end_time - start_time).total_seconds()

    print(f"Scraping completed in {duration:.1f} seconds")
    print(f"Total jobs collected: {len(all_jobs)}")

    return all_jobs


def process_changes(new_jobs: List[JobPosting]) -> ChangeTracker:
    """
    Process the scraped jobs and detect changes.

    Args:
        new_jobs: List of newly scraped job postings

    Returns:
        ChangeTracker with processed data and events
    """
    print("\nProcessing changes...")

    tracker = ChangeTracker()
    events = tracker.process_new_scraping(new_jobs)

    return tracker


def generate_outputs(tracker: ChangeTracker, run_date: date):
    """
    Generate all output files.

    Args:
        tracker: ChangeTracker with processed data
        run_date: Date for the output files
    """
    print("\nGenerating output files...")

    generator = OutputGenerator()
    generator.generate_daily_outputs(tracker, run_date)

    print("Output generation completed")


async def main_async(args):
    """Main async function that orchestrates the entire pipeline."""
    setup_logging(args.verbose)

    print("🤖 AI Lab Jobs Tracker")
    print("=" * 50)

    # Step 1: Create scrapers
    registry = create_scrapers_for_companies()
    if not registry.scrapers:
        print("❌ No scrapers were successfully created. Exiting.")
        return

    # Step 2: Run scraping
    try:
        new_jobs = await run_scraping(registry)
    except Exception as e:
        print(f"❌ Scraping failed: {e}")
        return

    if not new_jobs:
        print("⚠️  No jobs were scraped. Exiting.")
        return

    # Step 3: Process changes
    try:
        tracker = process_changes(new_jobs)
    except Exception as e:
        print(f"❌ Change processing failed: {e}")
        return

    # Step 4: Generate outputs
    try:
        run_date = args.date or date.today()
        generate_outputs(tracker, run_date)
    except Exception as e:
        print(f"❌ Output generation failed: {e}")
        return

    # Step 5: Summary
    print("\n✅ Pipeline completed successfully!")
    print(f"📊 Summary:")
    print(f"   • Scrapers run: {len(registry.scrapers)}")
    print(f"   • Jobs collected: {len(new_jobs)}")
    print(f"   • Active jobs: {len(tracker.get_current_active_jobs())}")
    print(f"   • Events detected: {len(tracker.events)}")

    if tracker.events:
        event_counts = {}
        for event in tracker.events:
            event_counts[event.event_type] = event_counts.get(event.event_type, 0) + 1

        print(f"   • New jobs: {event_counts.get('appeared', 0)}")
        print(f"   • Updated jobs: {event_counts.get('updated', 0)}")
        print(f"   • Closed jobs: {event_counts.get('closed', 0)}")


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="AI Lab Jobs Tracker - Scrape and track job postings from AI companies"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--date",
        type=lambda x: date.fromisoformat(x),
        help="Run date in YYYY-MM-DD format (defaults to today)"
    )

    args = parser.parse_args()

    # Run the async main function
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()