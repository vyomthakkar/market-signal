#!/usr/bin/env python3
"""
Main entry point for the Market Signal Twitter Scraper.

Usage:
    python run_scraper.py
"""
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and run the scraper
if __name__ == "__main__":
    from scrapers import playwright_scrapper
    import asyncio
    
    asyncio.run(playwright_scrapper.main())

