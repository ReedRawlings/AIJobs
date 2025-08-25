#!/usr/bin/env python3
"""
Analyze the actual structure of the Ashby script to understand how jobs are stored.
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
import json
import re

async def analyze_script_structure():
    """Analyze the script structure to understand job data format."""
    url = "https://jobs.ashbyhq.com/openai"
    
    print("🔍 Analyzing Ashby Script Structure")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        
        try:
            async with session.get(url, headers=headers, timeout=15) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Find the main script
                    scripts = soup.find_all('script')
                    main_script = None
                    
                    for script in scripts:
                        if script.string and len(script.string) > 100000:
                            main_script = script.string
                            break
                    
                    if not main_script:
                        print("❌ No large script found")
                        return None
                    
                    print(f"✅ Found main script ({len(main_script)} characters)")
                    
                    # Look for different patterns in the script
                    print("\n🔍 Analyzing script content...")
                    
                    # Pattern 1: Look for "jobs" keyword
                    jobs_positions = [m.start() for m in re.finditer(r'jobs', main_script)]
                    print(f"Found 'jobs' keyword {len(jobs_positions)} times")
                    
                    if jobs_positions:
                        # Look at the context around the first few "jobs" occurrences
                        for i, pos in enumerate(jobs_positions[:5]):
                            context_start = max(0, pos - 100)
                            context_end = min(len(main_script), pos + 200)
                            context = main_script[context_start:context_end]
                            print(f"\nContext around 'jobs' #{i+1}:")
                            print(f"  ...{context}...")
                    
                    # Pattern 2: Look for job-related patterns
                    print("\n🔍 Looking for job-related patterns...")
                    
                    # Look for job title patterns
                    title_patterns = [
                        r'"title"\s*:\s*"([^"]+)"',
                        r'title:\s*"([^"]+)"',
                        r'title:\s*\'([^\']+)\''
                    ]
                    
                    for pattern in title_patterns:
                        matches = re.findall(pattern, main_script)
                        if matches:
                            print(f"Found {len(matches)} title matches with pattern: {pattern}")
                            print(f"Sample titles: {matches[:5]}")
                    
                    # Pattern 3: Look for job ID patterns
                    id_patterns = [
                        r'"id"\s*:\s*"([^"]+)"',
                        r'id:\s*"([^"]+)"',
                        r'id:\s*\'([^\']+)\''
                    ]
                    
                    for pattern in id_patterns:
                        matches = re.findall(pattern, main_script)
                        if matches:
                            print(f"Found {len(matches)} ID matches with pattern: {pattern}")
                            print(f"Sample IDs: {matches[:5]}")
                    
                    # Pattern 4: Look for the actual job data structure
                    print("\n🔍 Looking for job data structure...")
                    
                    # Try to find where jobs array starts
                    jobs_array_start = main_script.find('"jobs"')
                    if jobs_array_start != -1:
                        print(f"Found 'jobs' at position {jobs_array_start}")
                        
                        # Look at the context around this
                        context_start = max(0, jobs_array_start - 50)
                        context_end = min(len(main_script), jobs_array_start + 300)
                        context = main_script[context_start:context_end]
                        print(f"Context around 'jobs':")
                        print(f"  ...{context}...")
                        
                        # Try to find the complete jobs array
                        # Look for the opening bracket after "jobs"
                        bracket_start = main_script.find('[', jobs_array_start)
                        if bracket_start != -1:
                            print(f"Found opening bracket at position {bracket_start}")
                            
                            # Try to find the closing bracket
                            bracket_count = 0
                            bracket_end = bracket_start
                            
                            for i in range(bracket_start, len(main_script)):
                                if main_script[i] == '[':
                                    bracket_count += 1
                                elif main_script[i] == ']':
                                    bracket_count -= 1
                                    if bracket_count == 0:
                                        bracket_end = i + 1
                                        break
                            
                            if bracket_end > bracket_start:
                                jobs_array = main_script[bracket_start:bracket_end]
                                print(f"Extracted jobs array ({len(jobs_array)} characters)")
                                
                                # Try to parse as JSON
                                try:
                                    jobs_data = json.loads(jobs_array)
                                    if isinstance(jobs_data, list):
                                        print(f"✅ Successfully parsed jobs array with {len(jobs_data)} jobs!")
                                        
                                        # Show first job structure
                                        if jobs_data:
                                            first_job = jobs_data[0]
                                            print(f"\nFirst job structure:")
                                            for key, value in first_job.items():
                                                if isinstance(value, str) and len(value) > 100:
                                                    print(f"  {key}: {value[:100]}...")
                                                else:
                                                    print(f"  {key}: {value}")
                                            
                                            return jobs_data
                                    
                                except json.JSONDecodeError as e:
                                    print(f"❌ Failed to parse jobs array as JSON: {e}")
                                    print("Array content preview:")
                                    print(jobs_array[:500])
                    
                    # If we didn't find the jobs array, look for individual job objects
                    print("\n🔍 Looking for individual job objects...")
                    
                    # Look for objects that contain both id and title
                    job_object_pattern = r'\{[^{}]*"id"[^{}]*"title"[^{}]*\}'
                    job_objects = re.findall(job_object_pattern, main_script, re.DOTALL)
                    
                    if job_objects:
                        print(f"Found {len(job_objects)} potential job objects")
                        
                        # Try to parse the first one
                        first_job_text = job_objects[0]
                        print(f"First job object text: {first_job_text[:200]}...")
                        
                        # Try to clean and parse
                        try:
                            # Remove any trailing commas and clean up
                            cleaned = re.sub(r',\s*}', '}', first_job_text)
                            cleaned = re.sub(r'[^\x20-\x7E]', '', cleaned)
                            
                            job_data = json.loads(cleaned)
                            print(f"✅ Successfully parsed first job object!")
                            print(f"Keys: {list(job_data.keys())}")
                            
                            return [job_data]  # Return as list for consistency
                            
                        except json.JSONDecodeError as e:
                            print(f"❌ Failed to parse job object: {e}")
                    
                    print("\n❌ Could not identify job data structure")
                    return None
                        
                else:
                    print(f"❌ Failed to load page: {response.status}")
                    return None
                    
        except Exception as e:
            print(f"❌ Error: {e}")
            return None

async def main():
    """Main function."""
    jobs = await analyze_script_structure()
    
    if jobs:
        print(f"\n🎉 Successfully analyzed script structure!")
        print(f"Found {len(jobs)} jobs with proper structure")
        print("\nNow we understand how to extract the data properly!")
    else:
        print("\n❌ Could not analyze script structure")
        print("Need to try a different approach")

if __name__ == "__main__":
    asyncio.run(main())
