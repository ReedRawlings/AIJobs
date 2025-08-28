#!/usr/bin/env python3
"""
Investigate Greenhouse job boards to discover available companies systematically.
"""

import asyncio
import aiohttp
import json
from typing import List, Dict, Any

async def discover_greenhouse_boards():
    """Try to discover Greenhouse job boards systematically."""
    print("🔍 Investigating Greenhouse Job Boards")
    print("=" * 50)
    
    # Common patterns to try
    common_names = [
        "character", "characterai", "character-ai", "character_ai",
        "adept", "adeptai", "adept-ai", "adept_ai",
        "replit", "replitai", "replit-ai", "replit_ai",
        "anthropic", "openai", "deepmind", "cohere",
        "huggingface", "hugging-face", "hugging_face",
        "stability", "stabilityai", "stability-ai", "stability_ai",
        "midjourney", "inflection", "inflectionai", "inflection-ai",
        "scale", "scaleai", "scale-ai", "scale_ai",
        "runway", "runwayml", "perplexity", "perplexityai"
    ]
    
    working_boards = []
    failed_boards = []
    
    async with aiohttp.ClientSession() as session:
        for name in common_names:
            url = f"https://boards-api.greenhouse.io/v1/boards/{name}"
            print(f"🔍 Testing: {name}")
            
            try:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        company_name = data.get('name', 'Unknown')
                        print(f"✅ {name} -> {company_name}")
                        working_boards.append({
                            'board_id': name,
                            'company_name': company_name,
                            'url': url
                        })
                    else:
                        print(f"❌ {name} -> {response.status}")
                        failed_boards.append(name)
                        
            except Exception as e:
                print(f"❌ {name} -> Error: {e}")
                failed_boards.append(name)
    
    print(f"\n📊 RESULTS:")
    print(f"✅ Working boards: {len(working_boards)}")
    print(f"❌ Failed boards: {len(failed_boards)}")
    
    if working_boards:
        print(f"\n🎯 WORKING BOARDS:")
        for board in working_boards:
            print(f"   {board['board_id']:20} -> {board['company_name']}")
    
    return working_boards, failed_boards

async def check_greenhouse_main_site():
    """Check if Greenhouse has a public directory of companies."""
    print(f"\n🌐 Checking Greenhouse main site for company directory...")
    
    async with aiohttp.ClientSession() as session:
        try:
            # Check if there's a public companies endpoint
            companies_url = "https://boards-api.greenhouse.io/v1/companies"
            async with session.get(companies_url, timeout=10) as response:
                print(f"Companies endpoint: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"Found companies data: {len(data) if isinstance(data, list) else 'object'}")
                else:
                    print("No public companies endpoint")
                    
        except Exception as e:
            print(f"Error checking companies endpoint: {e}")
        
        try:
            # Check main Greenhouse site
            main_url = "https://www.greenhouse.io"
            async with session.get(main_url, timeout=10) as response:
                print(f"Main site: {response.status}")
                if response.status == 200:
                    html = await response.text()
                    if "customers" in html.lower() or "companies" in html.lower():
                        print("Main site mentions customers/companies")
                    else:
                        print("Main site doesn't seem to list customers")
                        
        except Exception as e:
            print(f"Error checking main site: {e}")

async def main():
    """Main investigation function."""
    working, failed = await discover_greenhouse_boards()
    await check_greenhouse_main_site()
    
    print(f"\n💡 RECOMMENDATIONS:")
    if working:
        print(f"   • Found {len(working)} working board IDs")
        print(f"   • Update config with correct board IDs")
    
    if failed:
        print(f"   • {len(failed)} board IDs failed - may need different approach")
        print(f"   • Consider checking company websites directly")

if __name__ == "__main__":
    asyncio.run(main())
