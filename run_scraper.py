#!/usr/bin/env python3
"""
Simple runner script for the AI Jobs Scraper.
Can be used for local testing or manual runs.
"""

import sys
import asyncio
from datetime import date
from main import main_async, setup_argparse

def main():
    """Run the scraper with command line arguments."""
    parser = setup_argparse()
    args = parser.parse_args()
    
    print("🚀 Starting AI Jobs Scraper...")
    print(f"📅 Target date: {args.date or date.today()}")
    print(f"🔍 Verbose mode: {args.verbose}")
    print("-" * 50)
    
    try:
        asyncio.run(main_async(args))
        print("\n✅ Scraper completed successfully!")
    except KeyboardInterrupt:
        print("\n⏹️  Scraper interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Scraper failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
