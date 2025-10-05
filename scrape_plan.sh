#!/bin/bash
# Automated Scraping Plan for 2000+ Tweets
# Usage: bash scrape_plan.sh

echo "======================================================================="
echo "🚀 INCREMENTAL SCRAPING PLAN - 2000+ TWEETS"
echo "======================================================================="
echo ""
echo "This script will scrape 8 hashtags to reach 2000+ tweets"
echo "Estimated time: 90-120 minutes"
echo ""
echo "You can stop and resume anytime (Ctrl+C to stop)"
echo "Progress is saved after each hashtag"
echo ""
read -p "Press Enter to start or Ctrl+C to cancel..."

# Define hashtags and counts
declare -a hashtags=("nifty50" "banknifty" "sensex" "stockmarket" "intraday" "nse" "trading" "stocks")
declare -a counts=(300 300 300 300 250 250 250 250)

# Starting status
echo ""
echo "📊 Initial Status:"
python incremental_scraper.py --status
echo ""

# Loop through hashtags
for i in "${!hashtags[@]}"; do
    hashtag="${hashtags[$i]}"
    count="${counts[$i]}"
    
    echo ""
    echo "======================================================================="
    echo "📌 STEP $((i+1))/8: Scraping #${hashtag} (${count} tweets)"
    echo "======================================================================="
    
    # Scrape
    python incremental_scraper.py "$hashtag" --count "$count"
    
    if [ $? -ne 0 ]; then
        echo ""
        echo "⚠️  Error scraping #${hashtag}"
        echo "You can continue with next hashtag or fix the issue and try again"
        read -p "Continue with next hashtag? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Stopping. Run this script again to resume."
            exit 1
        fi
    fi
    
    # Show progress
    echo ""
    echo "📊 Current Progress:"
    python incremental_scraper.py --status | grep -E "(Total Unique Tweets|Hashtags Scraped)"
    echo ""
    
    # Wait between hashtags to avoid rate limiting
    if [ $i -lt $((${#hashtags[@]} - 1)) ]; then
        echo "⏳ Waiting 10 seconds before next hashtag..."
        sleep 10
    fi
done

echo ""
echo "======================================================================="
echo "✅ SCRAPING COMPLETE!"
echo "======================================================================="
echo ""
python incremental_scraper.py --status
echo ""
echo "💡 To export your data:"
echo "   python incremental_scraper.py --export ./final_output"
echo ""
