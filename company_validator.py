#!/usr/bin/env python3
"""
Company Validator - Automatically test and validate all company scrapers.

This tool provides an easy way to:
1. Test all company scrapers automatically
2. Show which ones are working/failing
3. Test individual companies
4. Get a health check dashboard
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.companies import get_company_configs
from scrapers.base_scraper import BaseScraper
from scrapers.greenhouse_scraper import GreenhouseScraper
from scrapers.lever_scraper import LeverScraper
from scrapers.ashby_scraper import AshbyScraper
from scrapers.workday_scraper import WorkdayScraper


class CompanyValidator:
    """Validates company scrapers and provides health checks."""
    
    def __init__(self):
        self.companies = get_company_configs()
        self.scraper_classes = {
            'greenhouse': GreenhouseScraper,
            'lever': LeverScraper,
            'ashby': AshbyScraper,
            'workday': WorkdayScraper,
        }
    
    async def test_company(self, company_name: str, timeout: int = 30) -> Dict:
        """Test a single company's scraper."""
        print(f"🔍 Testing {company_name}...")
        
        # Find company config
        company_config = None
        for company in self.companies:
            if company.name == company_name:
                company_config = company
                break
        
        if not company_config:
            return {
                'name': company_name,
                'status': 'error',
                'error': 'Company config not found',
                'jobs_count': 0,
                'duration': 0
            }
        
        # Get scraper class
        scraper_class = self.scraper_classes.get(company_config.source.value.lower())
        if not scraper_class:
            return {
                'name': company_name,
                'status': 'error',
                'error': f'No scraper for source: {company_config.source.value}',
                'jobs_count': 0,
                'duration': 0
            }
        
        start_time = datetime.now()
        
        try:
            # Create scraper instance
            if scraper_class == GreenhouseScraper:
                scraper = scraper_class(
                    company_name=company_config.name,
                    company_display_name=company_config.display_name,
                    job_board_url=company_config.job_board_url
                )
            elif scraper_class == LeverScraper:
                scraper = scraper_class(
                    company_name=company_config.name,
                    company_display_name=company_config.display_name,
                    job_board_url=company_config.job_board_url
                )
            elif scraper_class == AshbyScraper:
                scraper = scraper_class(
                    company_name=company_config.name,
                    company_display_name=company_config.display_name,
                    job_board_url=company_config.job_board_url
                )
            elif scraper_class == WorkdayScraper:
                scraper = scraper_class(
                    company_name=company_config.name,
                    company_display_name=company_config.display_name,
                    job_board_url=company_config.job_board_url
                )
            else:
                return {
                    'name': company_name,
                    'status': 'error',
                    'error': f'Unsupported scraper class: {scraper_class.__name__}',
                    'jobs_count': 0,
                    'duration': 0
                }
            
            # Test scraper with timeout
            async with scraper:
                jobs = await asyncio.wait_for(scraper.scrape_jobs(), timeout=timeout)
                
                duration = (datetime.now() - start_time).total_seconds()
                
                return {
                    'name': company_name,
                    'status': 'success',
                    'error': None,
                    'jobs_count': len(jobs),
                    'duration': duration,
                    'sample_jobs': jobs[:3] if jobs else []
                }
                
        except asyncio.TimeoutError:
            duration = (datetime.now() - start_time).total_seconds()
            return {
                'name': company_name,
                'status': 'timeout',
                'error': f'Scraper timed out after {timeout}s',
                'jobs_count': 0,
                'duration': duration
            }
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            return {
                'name': company_name,
                'status': 'error',
                'error': str(e),
                'jobs_count': 0,
                'duration': duration
            }
    
    async def test_all_companies(self, timeout: int = 30) -> List[Dict]:
        """Test all companies and return results."""
        print("🚀 Testing all company scrapers...")
        print("=" * 60)
        
        results = []
        
        for company in self.companies:
            result = await self.test_company(company.name, timeout)
            results.append(result)
            
            # Show immediate feedback
            if result['status'] == 'success':
                print(f"✅ {result['name']}: {result['jobs_count']} jobs in {result['duration']:.1f}s")
            elif result['status'] == 'timeout':
                print(f"⏰ {result['name']}: TIMEOUT after {result['duration']:.1f}s")
            else:
                print(f"❌ {result['name']}: {result['error']}")
        
        return results
    
    def print_health_dashboard(self, results: List[Dict]):
        """Print a nice health dashboard."""
        print("\n" + "=" * 80)
        print("🏥 COMPANY SCRAPER HEALTH DASHBOARD")
        print("=" * 80)
        
        # Summary stats
        total_companies = len(results)
        working = len([r for r in results if r['status'] == 'success'])
        failing = len([r for r in results if r['status'] != 'success'])
        total_jobs = sum([r['jobs_count'] for r in results if r['status'] == 'success'])
        
        print(f"📊 SUMMARY:")
        print(f"   Total Companies: {total_companies}")
        print(f"   ✅ Working: {working}")
        print(f"   ❌ Failing: {failing}")
        print(f"   📋 Total Jobs: {total_jobs:,}")
        print()
        
        # Working companies
        if working > 0:
            print("✅ WORKING COMPANIES:")
            working_results = [r for r in results if r['status'] == 'success']
            working_results.sort(key=lambda x: x['jobs_count'], reverse=True)
            
            for result in working_results:
                print(f"   {result['name']:20} | {result['jobs_count']:4} jobs | {result['duration']:5.1f}s")
            print()
        
        # Failing companies
        if failing > 0:
            print("❌ FAILING COMPANIES:")
            failing_results = [r for r in results if r['status'] != 'success']
            
            for result in failing_results:
                status_icon = "⏰" if result['status'] == 'timeout' else "❌"
                print(f"   {status_icon} {result['name']:20} | {result['error']}")
            print()
        
        # Recommendations
        if failing > 0:
            print("💡 RECOMMENDATIONS:")
            for result in failing_results:
                if result['status'] == 'timeout':
                    print(f"   • {result['name']}: Increase timeout or check for rate limiting")
                else:
                    print(f"   • {result['name']}: Investigate error: {result['error']}")
        
        print("=" * 80)
    
    async def quick_test(self, company_name: str):
        """Quick test of a single company with detailed output."""
        print(f"🧪 QUICK TEST: {company_name.upper()}")
        print("=" * 50)
        
        result = await self.test_company(company_name)
        
        if result['status'] == 'success':
            print(f"✅ SUCCESS! {result['jobs_count']} jobs scraped in {result['duration']:.1f}s")
            
            if result['sample_jobs']:
                print(f"\n🎯 Sample Jobs:")
                for i, job in enumerate(result['sample_jobs']):
                    print(f"   {i+1}. {job.title}")
                    print(f"      Location: {job.location or 'N/A'}")
                    print(f"      Team: {job.team or 'N/A'}")
                    print(f"      URL: {job.job_url}")
                    print()
        else:
            print(f"❌ FAILED: {result['error']}")
            print(f"   Duration: {result['duration']:.1f}s")


async def main():
    """Main function with command line interface."""
    validator = CompanyValidator()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "test" and len(sys.argv) > 2:
            # Test specific company: python company_validator.py test openai
            company_name = sys.argv[2]
            await validator.quick_test(company_name)
            
        elif command == "all":
            # Test all companies: python company_validator.py all
            results = await validator.test_all_companies()
            validator.print_health_dashboard(results)
            
        elif command == "help":
            print("Company Validator - Usage:")
            print("  python company_validator.py test <company_name>  - Test specific company")
            print("  python company_validator.py all                  - Test all companies")
            print("  python company_validator.py help                 - Show this help")
            print()
            print("Available companies:")
            for company in validator.companies:
                print(f"  - {company.name}")
        else:
            print(f"Unknown command: {command}")
            print("Use 'python company_validator.py help' for usage info")
    else:
        # Default: test all companies
        results = await validator.test_all_companies()
        validator.print_health_dashboard(results)


if __name__ == "__main__":
    asyncio.run(main())
