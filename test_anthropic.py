#!/usr/bin/env python3
"""
Quick test to verify Anthropic's Greenhouse scraper is working.
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.greenhouse_scraper import GreenhouseScraper
from config.companies import get_company_configs

async def test_anthropic():
    """Test Anthropic's Greenhouse scraper."""
    print("🧪 Testing Anthropic Greenhouse Scraper")
    print("=" * 50)
    
    # Get Anthropic config
    companies = get_company_configs()
    anthropic_config = None
    
    for company in companies:
        if company.name == "anthropic":
            anthropic_config = company
            break
    
    if not anthropic_config:
        print("❌ Anthropic config not found!")
        return False
    
    print(f"✅ Found Anthropic config:")
    print(f"  Source: {anthropic_config.source}")
    print(f"  URL: {anthropic_config.job_board_url}")
    
    # Create scraper
    scraper = GreenhouseScraper(
        company_name=anthropic_config.name,
        company_display_name=anthropic_config.display_name,
        job_board_url=anthropic_config.job_board_url
    )
    
    print(f"\n🔍 Testing scraper...")
    
    try:
        # Use the scraper as an async context manager
        async with scraper:
            # Try to scrape jobs
            jobs = await scraper.scrape_jobs()
            
            if jobs:
                print(f"✅ SUCCESS! Scraped {len(jobs)} jobs from Anthropic!")
                print(f"\n🎯 Sample jobs:")
                for i, job in enumerate(jobs[:3]):
                    print(f"  {i+1}. {job.title}")
                    print(f"     Location: {job.location}")
                    print(f"     Team: {job.team}")
                    print(f"     URL: {job.job_url}")
                    print()
                
                print(f"🎉 Anthropic Greenhouse scraper is working properly!")
                return True
            else:
                print("❌ No jobs scraped")
                return False
                
    except Exception as e:
        print(f"❌ Scraper failed: {e}")
        return False

async def main():
    """Main test function."""
    success = await test_anthropic()
    
    if success:
        print("\n🎯 Anthropic is now working with Greenhouse!")
        print("We can proceed with confidence.")
    else:
        print("\n❌ Anthropic test failed - need to investigate further")

if __name__ == "__main__":
    asyncio.run(main())
