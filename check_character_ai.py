#!/usr/bin/env python3
"""
Find Character AI's actual career page.
"""

import asyncio
import aiohttp
import re

async def find_character_ai_careers():
    """Find Character AI's career page."""
    print("🔍 Finding Character AI Careers")
    print("=" * 40)
    
    # Try different possible career URLs
    possible_urls = [
        "https://character.ai/careers",
        "https://character.ai/jobs", 
        "https://character.ai/join-us",
        "https://character.ai/team",
        "https://character.ai/about",
        "https://character.ai/",
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    async with aiohttp.ClientSession() as session:
        for url in possible_urls:
            print(f"🔍 Trying: {url}")
            
            try:
                async with session.get(url, headers=headers, timeout=10) as response:
                    print(f"   Status: {response.status}")
                    
                    if response.status == 200:
                        html = await response.text()
                        
                        # Look for career-related content
                        career_keywords = ['career', 'job', 'position', 'opening', 'hire', 'recruit', 'join', 'team']
                        found_keywords = []
                        
                        for keyword in career_keywords:
                            if keyword.lower() in html.lower():
                                found_keywords.append(keyword)
                        
                        if found_keywords:
                            print(f"   ✅ Career keywords found: {', '.join(found_keywords)}")
                            
                            # Look for job listings or career links
                            if 'job' in html.lower() or 'career' in html.lower():
                                print(f"   📋 This looks like a career page!")
                                
                                # Check for platform indicators
                                if 'ashby' in html.lower():
                                    print(f"   🎯 Uses Ashby platform")
                                elif 'greenhouse' in html.lower():
                                    print(f"   🎯 Uses Greenhouse platform")
                                elif 'lever' in html.lower():
                                    print(f"   🎯 Uses Lever platform")
                                else:
                                    print(f"   ❓ Platform not detected")
                                
                                return url, html
                        else:
                            print(f"   ❌ No career content found")
                    else:
                        print(f"   ❌ Page not accessible")
                        
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    return None, None

async def main():
    """Main function."""
    career_url, html = await find_character_ai_careers()
    
    if career_url:
        print(f"\n🎯 FOUND CAREER PAGE: {career_url}")
        print("You can now update the config with this URL!")
    else:
        print(f"\n❌ No career page found")
        print("Character AI might not have public job listings")

if __name__ == "__main__":
    asyncio.run(main())
