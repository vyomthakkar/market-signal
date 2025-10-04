# How to Use Your Scraped Data 🚀

## 📁 Output Files

After running the scraper, you'll have these files:

```
project/
├── raw_tweets.json           # Original JSON (21.4 KB)
├── tweets.parquet            # Efficient Parquet (18.8 KB, 12% smaller!)
├── collection_stats.json     # Collection statistics
└── output/
    ├── processed_tweets.parquet      # Alternative location
    └── processed_tweets.meta.json    # Metadata
```

---

## 🔍 Quick Verification

### **Method 1: Run Verification Script**
```bash
python check_output.py
```

**Shows:**
- ✅ File sizes and tweet counts
- ✅ Collection statistics
- ✅ Data quality metrics
- ✅ Top users and hashtags
- ✅ Sample tweets
- ✅ Format comparison

---

## 🎯 Interactive Exploration

### **Method 2: Interactive Explorer**
```bash
python explore_data.py
```

**Features:**
- 🔍 Search tweets by keyword
- 👤 Filter by username
- #️⃣ Find tweets with specific hashtags
- 🌍 Language breakdown
- 💾 Export to CSV
- 📊 View statistics

---

## 🐍 Programmatic Access

### **Method 3: Python/Pandas**

#### Load Parquet Data
```python
import pandas as pd

# Load data
df = pd.read_parquet('tweets.parquet')

print(f"Loaded {len(df)} tweets")
print(df.head())
```

#### Load JSON Data
```python
import json

with open('raw_tweets.json', 'r', encoding='utf-8') as f:
    tweets = json.load(f)

print(f"Loaded {len(tweets)} tweets")
```

---

## 📊 Common Analysis Tasks

### **1. Search for Keywords**
```python
# Find tweets mentioning "Nifty"
nifty_tweets = df[df['cleaned_content'].str.contains('Nifty', case=False, na=False)]
print(f"Found {len(nifty_tweets)} tweets about Nifty")

# Show them
for _, tweet in nifty_tweets.iterrows():
    print(f"@{tweet['username']}: {tweet['cleaned_content'][:70]}...")
```

### **2. Filter by User**
```python
# Get all tweets from specific user
user_tweets = df[df['username'] == 'NiftyNerve']
print(f"@NiftyNerve has {len(user_tweets)} tweets")
```

### **3. Filter by Language**
```python
# Get Hindi tweets
hindi_tweets = df[df['detected_language'] == 'hi']
print(f"Found {len(hindi_tweets)} Hindi tweets")

# Get English tweets
english_tweets = df[df['detected_language'] == 'en']
print(f"Found {len(english_tweets)} English tweets")
```

### **4. Find Hashtags**
```python
from collections import Counter

# Extract all hashtags
all_hashtags = []
for tags in df['hashtags']:
    if isinstance(tags, list):
        all_hashtags.extend([str(t).lower() for t in tags])

# Count them
hashtag_counts = Counter(all_hashtags).most_common(10)
print("Top hashtags:")
for tag, count in hashtag_counts:
    print(f"  #{tag}: {count}")
```

### **5. Engagement Analysis**
```python
# Find most engaging tweets
df['engagement'] = df['likes'] + df['retweets'] + df['replies']
top_tweets = df.nlargest(10, 'engagement')

print("Most engaging tweets:")
for _, tweet in top_tweets.iterrows():
    print(f"@{tweet['username']}: {tweet['engagement']} total engagement")
    print(f"  {tweet['cleaned_content'][:60]}...")
```

### **6. Time Analysis**
```python
# Convert timestamp to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Group by hour
df['hour'] = df['timestamp'].dt.hour
tweets_by_hour = df.groupby('hour').size()

print("Tweets by hour:")
print(tweets_by_hour)
```

### **7. Content Analysis**
```python
# Calculate content length
df['length'] = df['cleaned_content'].str.len()

print(f"Average tweet length: {df['length'].mean():.0f} characters")
print(f"Shortest tweet: {df['length'].min()} characters")
print(f"Longest tweet: {df['length'].max()} characters")

# Find longest tweet
longest = df.loc[df['length'].idxmax()]
print(f"\nLongest tweet by @{longest['username']}:")
print(longest['cleaned_content'])
```

---

## 💾 Export Options

### **1. Export to CSV**
```python
# Export all data
df.to_csv('tweets.csv', index=False, encoding='utf-8')

# Export specific columns
df[['username', 'cleaned_content', 'likes']].to_csv('tweets_simple.csv', index=False)

# Export filtered data
english_tweets = df[df['detected_language'] == 'en']
english_tweets.to_csv('tweets_english.csv', index=False)
```

### **2. Export to Excel**
```python
# Requires: pip install openpyxl
df.to_excel('tweets.xlsx', index=False, sheet_name='Tweets')
```

### **3. Export to JSON**
```python
import json

# Convert DataFrame to list of dicts
tweets_list = df.to_dict('records')

# Save as JSON
with open('tweets_export.json', 'w', encoding='utf-8') as f:
    json.dump(tweets_list, f, indent=2, ensure_ascii=False, default=str)
```

### **4. Export to Parquet**
```python
# Filter and save
filtered_df = df[df['likes'] > 10]  # Only tweets with likes
filtered_df.to_parquet('tweets_popular.parquet')
```

---

## 🔧 Advanced Usage

### **1. Sentiment Analysis** (requires additional packages)
```python
# pip install textblob
from textblob import TextBlob

def get_sentiment(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity

df['sentiment'] = df['cleaned_content'].apply(get_sentiment)

# Classify
df['sentiment_label'] = df['sentiment'].apply(
    lambda x: 'positive' if x > 0.1 else ('negative' if x < -0.1 else 'neutral')
)

print(df['sentiment_label'].value_counts())
```

### **2. Word Cloud**
```python
# pip install wordcloud matplotlib
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Combine all text
all_text = ' '.join(df['cleaned_content'].tolist())

# Generate word cloud
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_text)

# Display
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.savefig('wordcloud.png')
print("Saved wordcloud.png")
```

### **3. Network Analysis** (who mentions whom)
```python
import pandas as pd

# Extract mention relationships
mentions_data = []
for _, tweet in df.iterrows():
    if tweet['mentions'] and len(tweet['mentions']) > 0:
        for mention in tweet['mentions']:
            mentions_data.append({
                'from': tweet['username'],
                'to': mention
            })

mentions_df = pd.DataFrame(mentions_data)
print(f"Found {len(mentions_df)} mention relationships")
```

---

## 📚 Example Scripts Included

1. **check_output.py** - Comprehensive verification
2. **explore_data.py** - Interactive explorer
3. **analyze_tweets.py** - Example analysis (modify this!)

---

## 🎯 Quick Commands

```bash
# Verify output
python check_output.py

# Interactive exploration
python explore_data.py

# Custom analysis
python analyze_tweets.py

# Load in Python
python -c "import pandas as pd; df = pd.read_parquet('tweets.parquet'); print(df)"

# Count tweets
python -c "import pandas as pd; print(f'Total tweets: {len(pd.read_parquet(\"tweets.parquet\"))}')"

# Export to CSV
python -c "import pandas as pd; pd.read_parquet('tweets.parquet').to_csv('tweets.csv', index=False)"
```

---

## 🐛 Troubleshooting

### **"File not found" error**
```bash
# Check if files exist
ls -lh *.json *.parquet

# Run from project root
cd /path/to/market-signal
python check_output.py
```

### **"pandas not installed" error**
```bash
pip install pandas pyarrow
```

### **"No module named 'openpyxl'" (for Excel export)**
```bash
pip install openpyxl
```

---

## 💡 Tips

1. **Parquet is faster** - Use Parquet for large datasets
2. **Filter before loading** - Use pandas filters to load only what you need
3. **Use chunking** - For very large datasets, process in chunks
4. **Save intermediate results** - Save filtered data to avoid reprocessing
5. **Use cleaned_content** - The `cleaned_content` field is better for analysis

---

## 📖 Documentation

- Full implementation docs: `docs/PHASE_1_2_DATA_PROCESSING.md`
- Quick start guide: `PHASE_1_2_QUICKSTART.md`
- Implementation summary: `IMPLEMENTATION_PHASE_1_2_COMPLETE.md`

---

**Happy analyzing! 🚀**

