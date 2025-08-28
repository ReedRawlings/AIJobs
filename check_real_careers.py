#!/usr/bin/env python3
"""
Check the actual career pages of companies to see what platforms they use.
"""

import asyncio
import aiohttp
import re
from typing import Dict, Optional

async def check_company_careers(company_name: str, career_url: str) -> Dict:
    """Check what platform a company is actually using for careers."""
    print(f"🔍 Checking {company_name}: {career_url}")
    
    # Set up headers to avoid encoding issues
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',  # Avoid brotli encoding
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(career_url, headers=headers, timeout=15) as response:
                print(f"   Status: {response.status}")
                
                if response.status == 200:
                    html = await response.text()
                    
                    # Look for platform indicators
                    platform_hints = {
                        'greenhouse': ['greenhouse', 'boards.greenhouse.io'],
                        'lever': ['lever', 'jobs.lever.co', 'lever.co'],
                        'ashby': ['ashby', 'jobs.ashbyhq.com', 'ashbyhq.com'],
                        'workday': ['workday', 'wd1.myworkdayjobs.com'],
                        'bamboo': ['bamboo', 'bamboohr.com'],
                        'smartrecruiters': ['smartrecruiters', 'smartrecruiters.com'],
                        'icims': ['icims', 'icims.com'],
                        'custom': ['custom', 'built-in', 'internal']
                    }
                    
                    detected_platforms = []
                    for platform, keywords in platform_hints.items():
                        for keyword in keywords:
                            if keyword.lower() in html.lower():
                                detected_platforms.append(platform)
                                break
                    
                    if detected_platforms:
                        print(f"   🎯 Detected platforms: {', '.join(detected_platforms)}")
                    else:
                        print(f"   ❓ No clear platform detected")
                    
                    # Look for job data patterns
                    if 'jobs' in html.lower() or 'careers' in html.lower():
                        print(f"   📋 Career page content detected")
                    
                    # Check if it's a custom/redirect page
                    if len(html) < 1000:
                        print(f"   ⚠️  Very short page - might be redirect")
                    
                    # Look for specific Ashby patterns
                    if 'ashby' in html.lower():
                        ashby_pattern = r'https://jobs\.ashbyhq\.com/[^"\s]+'
                        ashby_urls = re.findall(ashby_pattern, html)
                        if ashby_urls:
                            print(f"   🔗 Ashby URL: {ashby_urls[0]}")
                    
                    return {
                        'company': company_name,
                        'url': career_url,
                        'status': response.status,
                        'platforms': detected_platforms,
                        'has_career_content': 'jobs' in html.lower() or 'careers' in html.lower()
                    }
                    
                else:
                    print(f"   ❌ Failed to load page")
                    return {
                        'company': company_name,
                        'url': career_url,
                        'status': response.status,
                        'platforms': [],
                        'has_career_content': False
                    }
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return {
                'company': company_name,
                'url': career_url,
                'status': 'error',
                'platforms': [],
                'has_career_content': False,
                'error': str(e)
            }

async def main():
    """Check multiple companies' career pages."""
    companies = [
        ("Character AI", "https://character.ai/careers"),
        ("Adept", "https://www.adept.ai/careers"),
        ("Replit", "https://replit.com/careers"),
    ]
    
    print("🔍 Checking Real Career Pages")
    print("=" * 50)
    
    results = []
    for company_name, career_url in companies:
        result = await check_company_careers(company_name, career_url)
        results.append(result)
        print()
    
    print("📊 SUMMARY:")
    print("=" * 50)
    for result in results:
        status_icon = "✅" if result['status'] == 200 else "❌"
        platforms = ', '.join(result['platforms']) if result['platforms'] else 'Unknown'
        print(f"{status_icon} {result['company']:15} | {platforms}")

if __name__ == "__main__":
    asyncio.run(main())
