#!/usr/bin/env python3
"""
Simple engagement metrics debugger using the working scraper

This reuses the TwitterScraperV2 login (which works) to debug engagement extraction
"""

import asyncio
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from scrapers.playwright_scrapper_v2 import TwitterScraperV2
from config.settings import load_config, TwitterCredentials


async def debug_engagement():
    """Debug engagement metric extraction"""
    
    print("\n" + "="*80)
    print("🔍 DEBUGGING ENGAGEMENT METRICS")
    print("="*80)
    
    # Use working configuration
    config = load_config(
        headless=False,  # Visible for debugging
        tweets_per_hashtag=5  # Just 5 tweets for quick test
    )
    
    # Load credentials
    try:
        creds = TwitterCredentials.from_env()
    except Exception as e:
        print(f"❌ Failed to load credentials: {e}")
        return
    
    # Initialize scraper (uses working login)
    scraper = TwitterScraperV2(config)
    
    try:
        # Setup and login (this works!)
        await scraper.setup_browser()
        
        print("\n🔐 Logging in...")
        await scraper.login(
            username=creds.username,
            password=creds.password.get_secret_value(),
            email=creds.email
        )
        print("✅ Login successful!")
        
        # Navigate to search
        print("\n🔍 Loading #nifty50 search...")
        search_url = 'https://x.com/search?q=%23nifty50%20-filter%3Areplies&src=typed_query&f=live'
        await scraper.page.goto(search_url, wait_until='domcontentloaded', timeout=60000)
        await asyncio.sleep(5)
        
        print("\n📊 Analyzing tweet structure...")
        
        # Debug: Get detailed information about first tweet
        debug_info = await scraper.page.evaluate("""
            () => {
                const articles = document.querySelectorAll('article[data-testid="tweet"]');
                
                if (articles.length === 0) {
                    return { error: "No tweets found" };
                }
                
                const firstArticle = articles[0];
                const result = {
                    totalTweetsFound: articles.length,
                    engagementData: {
                        foundWithCurrentSelectors: {},
                        allDataTestIds: [],
                        allAriaLabels: [],
                        textContent: []
                    }
                };
                
                // Try current method (what scraper uses now)
                const metrics = firstArticle.querySelectorAll('[data-testid$="-count"]');
                result.engagementData.foundWithCurrentSelectors = {
                    count: metrics.length,
                    details: []
                };
                
                metrics.forEach(metric => {
                    const testId = metric.getAttribute('data-testid');
                    const value = metric.innerText;
                    result.engagementData.foundWithCurrentSelectors.details.push({
                        testId: testId,
                        text: value,
                        html: metric.outerHTML.substring(0, 150)
                    });
                });
                
                // Get ALL data-testid attributes
                const allTestIdElements = firstArticle.querySelectorAll('[data-testid]');
                allTestIdElements.forEach(el => {
                    const testId = el.getAttribute('data-testid');
                    const text = el.innerText || el.getAttribute('aria-label') || '';
                    
                    // Only include engagement-related ones
                    if (testId.includes('reply') || testId.includes('retweet') || 
                        testId.includes('like') || testId.includes('bookmark') || 
                        testId.includes('analytics') || testId.includes('count')) {
                        result.engagementData.allDataTestIds.push({
                            testId: testId,
                            text: text.substring(0, 100),
                            tag: el.tagName,
                            ariaLabel: el.getAttribute('aria-label')
                        });
                    }
                });
                
                // Get all aria-labels with engagement data
                const ariaElements = firstArticle.querySelectorAll('[aria-label]');
                ariaElements.forEach(el => {
                    const ariaLabel = el.getAttribute('aria-label') || '';
                    
                    // Check if contains engagement keywords
                    if (ariaLabel.match(/reply|retweet|like|view|bookmark/i)) {
                        result.engagementData.allAriaLabels.push({
                            ariaLabel: ariaLabel,
                            testId: el.getAttribute('data-testid'),
                            tag: el.tagName
                        });
                    }
                });
                
                // Get visible text from engagement area
                const role_group = firstArticle.querySelector('[role="group"]');
                if (role_group) {
                    const spans = role_group.querySelectorAll('span');
                    spans.forEach(span => {
                        const text = span.innerText;
                        if (text && text.trim()) {
                            result.engagementData.textContent.push({
                                text: text,
                                parent: span.parentElement?.getAttribute('data-testid') || 'unknown'
                            });
                        }
                    });
                }
                
                // Try to extract engagement using different methods
                result.extractionAttempts = {
                    method1_dataTestId: {},
                    method2_ariaLabel: {},
                    method3_buttonText: {}
                };
                
                // Method 1: Direct button data-testid
                const replyBtn = firstArticle.querySelector('[data-testid="reply"]');
                const retweetBtn = firstArticle.querySelector('[data-testid="retweet"]');
                const likeBtn = firstArticle.querySelector('[data-testid="like"]');
                const analyticsBtn = firstArticle.querySelector('[data-testid="analyticsButton"]');
                
                result.extractionAttempts.method1_dataTestId = {
                    reply: replyBtn ? replyBtn.getAttribute('aria-label') : null,
                    retweet: retweetBtn ? retweetBtn.getAttribute('aria-label') : null,
                    like: likeBtn ? likeBtn.getAttribute('aria-label') : null,
                    views: analyticsBtn ? analyticsBtn.getAttribute('aria-label') : null
                };
                
                // Method 2: Parse aria-labels for numbers
                if (replyBtn) {
                    const ariaLabel = replyBtn.getAttribute('aria-label') || '';
                    const match = ariaLabel.match(/(\d+)\s*repl/i);
                    result.extractionAttempts.method2_ariaLabel.replies = match ? parseInt(match[1]) : 0;
                }
                
                if (retweetBtn) {
                    const ariaLabel = retweetBtn.getAttribute('aria-label') || '';
                    const match = ariaLabel.match(/(\d+)\s*retweet/i);
                    result.extractionAttempts.method2_ariaLabel.retweets = match ? parseInt(match[1]) : 0;
                }
                
                if (likeBtn) {
                    const ariaLabel = likeBtn.getAttribute('aria-label') || '';
                    const match = ariaLabel.match(/(\d+)\s*like/i);
                    result.extractionAttempts.method2_ariaLabel.likes = match ? parseInt(match[1]) : 0;
                }
                
                if (analyticsBtn) {
                    const ariaLabel = analyticsBtn.getAttribute('aria-label') || '';
                    const match = ariaLabel.match(/(\d+)\s*view/i);
                    result.extractionAttempts.method2_ariaLabel.views = match ? parseInt(match[1]) : 0;
                }
                
                return result;
            }
        """)
        
        # Print results
        print("\n" + "="*80)
        print("📋 DEBUG RESULTS")
        print("="*80)
        
        if 'error' in debug_info:
            print(f"\n❌ Error: {debug_info['error']}")
        else:
            print(f"\n✅ Found {debug_info['totalTweetsFound']} tweets on page")
            
            print(f"\n1️⃣  CURRENT METHOD (data-testid ending with '-count'):")
            print(f"   Found: {debug_info['engagementData']['foundWithCurrentSelectors']['count']} elements")
            if debug_info['engagementData']['foundWithCurrentSelectors']['details']:
                for detail in debug_info['engagementData']['foundWithCurrentSelectors']['details']:
                    print(f"   • {detail['testId']}: '{detail['text']}'")
            else:
                print("   ⚠️  No elements found with this method!")
            
            print(f"\n2️⃣  ALL ENGAGEMENT-RELATED data-testid ATTRIBUTES:")
            if debug_info['engagementData']['allDataTestIds']:
                for item in debug_info['engagementData']['allDataTestIds'][:10]:
                    print(f"   • {item['testId']} ({item['tag']})")
                    if item['ariaLabel']:
                        print(f"     aria-label: {item['ariaLabel'][:80]}")
                    if item['text']:
                        print(f"     text: {item['text'][:80]}")
            else:
                print("   ⚠️  No engagement data-testids found!")
            
            print(f"\n3️⃣  ARIA-LABELS WITH ENGAGEMENT DATA:")
            if debug_info['engagementData']['allAriaLabels']:
                for item in debug_info['engagementData']['allAriaLabels'][:10]:
                    print(f"   • {item['ariaLabel'][:100]}")
                    print(f"     testId: {item['testId']}, tag: {item['tag']}")
            else:
                print("   ⚠️  No engagement aria-labels found!")
            
            print(f"\n4️⃣  EXTRACTION ATTEMPTS:")
            print(f"\n   Method 1 - Direct button aria-labels:")
            for key, value in debug_info['extractionAttempts']['method1_dataTestId'].items():
                print(f"   • {key}: {value if value else 'NOT FOUND'}")
            
            print(f"\n   Method 2 - Parsed from aria-labels:")
            if debug_info['extractionAttempts']['method2_ariaLabel']:
                for key, value in debug_info['extractionAttempts']['method2_ariaLabel'].items():
                    print(f"   • {key}: {value}")
            else:
                print("   • No values extracted")
            
            print(f"\n5️⃣  VISIBLE TEXT IN ENGAGEMENT AREA:")
            if debug_info['engagementData']['textContent']:
                for item in debug_info['engagementData']['textContent'][:15]:
                    print(f"   • '{item['text']}' (parent: {item['parent']})")
            else:
                print("   ⚠️  No text content found!")
        
        # Save to file
        debug_file = Path("debug/engagement_extraction_debug.json")
        debug_file.parent.mkdir(exist_ok=True)
        with open(debug_file, 'w') as f:
            json.dump(debug_info, f, indent=2)
        
        print(f"\n💾 Full debug data saved to: {debug_file}")
        
        print("\n" + "="*80)
        print("🔍 MANUAL INSPECTION")
        print("="*80)
        print("\nBrowser will stay open for 30 seconds.")
        print("Please manually check:")
        print("  1. Are engagement numbers (likes, retweets) visible on screen?")
        print("  2. Right-click on a like count → 'Inspect'")
        print("  3. Look at the HTML structure")
        print("\n⏰ Waiting 30 seconds...")
        
        await asyncio.sleep(30)
        
        print("\n" + "="*80)
        print("✅ DEBUG COMPLETE!")
        print("="*80)
        
        # Analyze results and suggest fix
        print("\n💡 ANALYSIS:")
        
        if debug_info['extractionAttempts']['method2_ariaLabel']:
            has_data = any(v > 0 for v in debug_info['extractionAttempts']['method2_ariaLabel'].values())
            if has_data:
                print("   ✅ Method 2 (aria-label parsing) found engagement data!")
                print("   → We can fix the scraper to use this method")
            else:
                print("   ⚠️  Engagement data might not be visible in search results")
        else:
            print("   ⚠️  Could not extract engagement with any method")
            print("   → Engagement metrics might not be available in search feed")
        
        print("\n📝 Next step:")
        print("   Check debug/engagement_extraction_debug.json for details")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(debug_engagement())
