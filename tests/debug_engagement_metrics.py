#!/usr/bin/env python3
"""
Debug script to capture actual tweet HTML and see what engagement data is available

This will help us understand if engagement metrics are present but we're using wrong selectors
"""

import asyncio
from playwright.async_api import async_playwright
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "src"))

from config.settings import TwitterCredentials, load_config

async def debug_tweet_structure():
    """Login and capture actual tweet HTML structure"""
    
    print("="*80)
    print("🔍 DEBUGGING TWEET ENGAGEMENT METRICS")
    print("="*80)
    
    # Load credentials
    try:
        creds = TwitterCredentials.from_env()
    except Exception as e:
        print(f"❌ Failed to load credentials: {e}")
        return
    
    config = load_config(headless=False)  # Visible browser for debugging
    
    async with async_playwright() as p:
        print("\n🌐 Launching browser...")
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        # Login
        print("\n🔐 Logging in...")
        await page.goto('https://x.com/i/flow/login')
        await asyncio.sleep(3)
        
        await page.fill('input[autocomplete="username"]', creds.username)
        await asyncio.sleep(1)
        await page.click('text=Next')
        await asyncio.sleep(3)
        
        await page.fill('input[type="password"]', creds.password.get_secret_value())
        await asyncio.sleep(1)
        await page.click('text=Log in')
        await asyncio.sleep(5)
        
        print("✅ Login complete")
        
        # Navigate to search
        print("\n🔍 Searching #nifty50...")
        search_url = 'https://x.com/search?q=%23nifty50%20-filter%3Areplies&src=typed_query&f=live'
        await page.goto(search_url)
        await asyncio.sleep(5)
        
        print("\n📊 Extracting tweet structure...")
        
        # Get detailed tweet structure
        debug_info = await page.evaluate("""
            () => {
                const articles = document.querySelectorAll('article[data-testid="tweet"]');
                const debugData = {
                    totalTweets: articles.length,
                    sampleTweet: null,
                    engagementSelectors: {
                        'data-testid ending with -count': [],
                        'aria-label attributes': [],
                        'all data-testids': []
                    }
                };
                
                if (articles.length > 0) {
                    const firstArticle = articles[0];
                    
                    // Get all elements with data-testid
                    const allElements = firstArticle.querySelectorAll('[data-testid]');
                    allElements.forEach(el => {
                        const testId = el.getAttribute('data-testid');
                        debugData.engagementSelectors['all data-testids'].push({
                            testId: testId,
                            text: el.innerText ? el.innerText.substring(0, 50) : '',
                            tag: el.tagName
                        });
                    });
                    
                    // Look for elements ending with -count
                    const countElements = firstArticle.querySelectorAll('[data-testid$="-count"]');
                    countElements.forEach(el => {
                        debugData.engagementSelectors['data-testid ending with -count'].push({
                            testId: el.getAttribute('data-testid'),
                            text: el.innerText,
                            html: el.outerHTML.substring(0, 200)
                        });
                    });
                    
                    // Look for aria-labels (often contain engagement data)
                    const ariaElements = firstArticle.querySelectorAll('[aria-label]');
                    ariaElements.forEach(el => {
                        const ariaLabel = el.getAttribute('aria-label');
                        if (ariaLabel && (ariaLabel.includes('like') || ariaLabel.includes('retweet') || ariaLabel.includes('reply') || ariaLabel.includes('view'))) {
                            debugData.engagementSelectors['aria-label attributes'].push({
                                ariaLabel: ariaLabel,
                                tag: el.tagName,
                                testId: el.getAttribute('data-testid')
                            });
                        }
                    });
                    
                    // Get sample tweet content
                    const username = firstArticle.querySelector('[data-testid="User-Name"]')?.innerText || '';
                    const tweetText = firstArticle.querySelector('[data-testid="tweetText"]')?.innerText || '';
                    
                    debugData.sampleTweet = {
                        username: username.substring(0, 100),
                        content: tweetText.substring(0, 200)
                    };
                }
                
                return debugData;
            }
        """)
        
        # Print results
        print("\n" + "="*80)
        print("📋 DEBUG RESULTS")
        print("="*80)
        
        print(f"\n📊 Total tweets found: {debug_info['totalTweets']}")
        
        if debug_info['sampleTweet']:
            print(f"\n📝 Sample tweet:")
            print(f"   User: {debug_info['sampleTweet']['username']}")
            print(f"   Content: {debug_info['sampleTweet']['content']}")
        
        print(f"\n🔍 Engagement selectors analysis:")
        
        print(f"\n1️⃣  Elements with data-testid ending in '-count': {len(debug_info['engagementSelectors']['data-testid ending with -count'])}")
        for item in debug_info['engagementSelectors']['data-testid ending with -count'][:5]:
            print(f"   • testId: {item['testId']}")
            print(f"     text: {item['text']}")
            print(f"     html: {item['html'][:100]}...")
            print()
        
        print(f"\n2️⃣  Elements with engagement-related aria-labels: {len(debug_info['engagementSelectors']['aria-label attributes'])}")
        for item in debug_info['engagementSelectors']['aria-label attributes'][:10]:
            print(f"   • aria-label: {item['ariaLabel']}")
            print(f"     tag: {item['tag']}, testId: {item['testId']}")
            print()
        
        print(f"\n3️⃣  All data-testid attributes found (first 20):")
        for item in debug_info['engagementSelectors']['all data-testids'][:20]:
            print(f"   • {item['testId']} ({item['tag']}) - {item['text'][:30]}")
        
        # Save to file
        import json
        debug_file = Path("debug/engagement_debug.json")
        debug_file.parent.mkdir(exist_ok=True)
        with open(debug_file, 'w') as f:
            json.dump(debug_info, f, indent=2)
        
        print(f"\n💾 Full debug data saved to: {debug_file}")
        
        print("\n" + "="*80)
        print("⏸️  Browser will stay open for 30 seconds for manual inspection")
        print("   Check the engagement buttons/numbers on the page")
        print("="*80)
        
        await asyncio.sleep(30)
        
        await browser.close()
        
        print("\n✅ Debug complete!")
        print("\n💡 Next steps:")
        print("   1. Check debug/engagement_debug.json for detailed selector info")
        print("   2. Look for patterns in aria-labels or data-testids")
        print("   3. Update extraction code with correct selectors")

if __name__ == "__main__":
    asyncio.run(debug_tweet_structure())
