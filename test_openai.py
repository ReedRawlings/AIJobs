#!/usr/bin/env python3
"""
Test different approaches to access OpenAI careers page.
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
import json

async def test_openai_careers():
    """Test different approaches to access OpenAI careers."""
    url = "https://openai.com/careers/search/"
    
    print("🔍 Testing OpenAI Careers Access")
    print("=" * 60)
    
    # Test different user agents and approaches
    test_configs = [
        {
            "name": "Default Browser",
            "headers": {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
        },
        {
            "name": "Mobile Browser",
            "headers": {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
            }
        },
        {
            "name": "Safari Browser",
            "headers": {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
            }
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        for config in test_configs:
            print(f"\n🧪 Testing: {config['name']}")
            print("-" * 40)
            
            try:
                async with session.get(url, headers=config['headers'], timeout=15) as response:
                    print(f"Status: {response.status}")
                    print(f"Headers: {dict(response.headers)}")
                    
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Look for job-related content
                        title = soup.find('title')
                        if title:
                            print(f"Page Title: {title.get_text()}")
                        
                        # Check for job listings
                        job_elements = soup.find_all(['div', 'section', 'article'], class_=lambda x: x and any(word in x.lower() for word in ['job', 'career', 'position', 'role']))
                        print(f"Job elements found: {len(job_elements)}")
                        
                        # Look for embedded job data
                        scripts = soup.find_all('script')
                        job_scripts = [s for s in scripts if s.string and any(word in s.string.lower() for word in ['job', 'position', 'career'])]
                        print(f"Job-related scripts: {len(job_scripts)}")
                        
                        # Check for iframes or embedded content
                        iframes = soup.find_all('iframe')
                        if iframes:
                            print(f"Found {len(iframes)} iframes")
                            for iframe in iframes:
                                src = iframe.get('src', '')
                                if src:
                                    print(f"  - {src}")
                        
                        # Look for common job board patterns
                        if 'greenhouse' in html.lower():
                            print("🔍 Found Greenhouse integration")
                        if 'lever' in html.lower():
                            print("🔍 Found Lever integration")
                        if 'workday' in html.lower():
                            print("🔍 Found Workday integration")
                        if 'ashby' in html.lower():
                            print("🔍 Found Ashby integration")
                        
                        # Check for redirects or different URLs
                        meta_refresh = soup.find('meta', attrs={'http-equiv': 'refresh'})
                        if meta_refresh:
                            print(f"Meta refresh found: {meta_refresh.get('content')}")
                        
                        print("✅ Successfully accessed page!")
                        return html
                        
                    elif response.status == 403:
                        print("❌ 403 Forbidden - likely anti-bot protection")
                    elif response.status == 429:
                        print("❌ 429 Too Many Requests - rate limited")
                    else:
                        print(f"❌ Unexpected status: {response.status}")
                        
            except Exception as e:
                print(f"❌ Error: {e}")
            
            # Wait between attempts
            await asyncio.sleep(2)
    
    print("\n❌ All approaches failed")
    return None

async def main():
    """Main function."""
    html = await test_openai_careers()
    
    if html:
        print("\n💡 Analysis:")
        print("1. Page accessed successfully")
        print("2. Check for embedded job board")
        print("3. Look for job data in scripts")
        print("4. Determine scraping approach")
    else:
        print("\n💡 Next Steps:")
        print("1. Try accessing manually in browser")
        print("2. Check if they moved to different platform")
        print("3. Look for API endpoints")
        print("4. Consider using Selenium for JavaScript-heavy pages")

if __name__ == "__main__":
    asyncio.run(main())
