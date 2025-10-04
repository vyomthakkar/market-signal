#!/usr/bin/env python3
"""
Main entry point for the Market Signal Twitter Scraper.

Usage:
    python run_scraper.py              # Use production-ready V2 scraper
    python run_scraper.py --v1         # Use original V1 scraper
"""
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and run the scraper
if __name__ == "__main__":
    import asyncio
    
    # Check if user wants V1 (original)
    if "--v1" in sys.argv:
        from scrapers import playwright_scrapper
        print("Running Original Scraper (V1)...")
        asyncio.run(playwright_scrapper.main())
    else:
        from scrapers import playwright_scrapper_v2
        print("Running Production-Ready Scraper (V2)...")
        asyncio.run(playwright_scrapper_v2.main())

