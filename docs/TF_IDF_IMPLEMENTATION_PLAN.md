# TF-IDF Implementation Plan for Market Signal Generation

## 🎯 Objective
Transform tweet content into numerical features using TF-IDF to extract important terms and patterns for market signal generation.

---

## 📊 What is TF-IDF?

**TF-IDF (Term Frequency-Inverse Document Frequency)** identifies important words in documents:
- **TF (Term Frequency)**: How often a word appears in a document
- **IDF (Inverse Document Frequency)**: How rare/unique a word is across all documents
- **TF-IDF Score**: TF × IDF - Higher = more important

**Example:**
- "profit" appears in 1/100 tweets → High IDF (rare/important)
- "the" appears in 99/100 tweets → Low IDF (common/unimportant)

---

## 🏗️ Implementation Plan

### **Phase 1: Basic TF-IDF Features** ⭐ Start Here

**Goal:** Extract top important terms from each tweet

**Implementation:**
1. Create `TFIDFAnalyzer` class in `features.py`
2. Use `sklearn.TfidfVectorizer` with finance-specific parameters
3. Extract top N terms per tweet with their scores
4. Identify trending/important terms across all tweets

**Output per tweet:**
- `top_tfidf_terms`: List of top 5-10 important words
- `tfidf_scores`: Scores for each term
- `tfidf_vector`: Full numerical vector (for ML later)

**Configuration:**
- Min word frequency: 2 (ignore very rare words)
- Max features: 500-1000 (keep vocabulary manageable)
- N-grams: 1-2 (single words + 2-word phrases like "nifty breakout")
- Remove stop words: Yes (ignore "the", "is", "a", etc.)

---

### **Phase 2: Finance-Domain TF-IDF** 🎯

**Goal:** Focus on finance-relevant terms only

**Enhancement:**
1. Pre-filter vocabulary to finance terms
2. Custom stop words (remove spam terms like "join", "telegram")
3. Weight finance keywords higher (boost "nifty", "sensex", technical terms)

**Finance Vocabulary Categories:**
- **Market indices:** nifty, sensex, banknifty, finnifty
- **Actions:** buy, sell, breakout, breakdown, support, resistance
- **Metrics:** profit, loss, target, stop loss, ROI
- **Technical:** bullish, bearish, rally, crash, momentum
- **Numbers/Prices:** Pattern matching for ₹, %, k, cr, lakh

---

### **Phase 3: Aggregated Market Signals** 📈

**Goal:** Extract market-level insights from all tweets

**Aggregations:**
1. **Trending Terms**: Top 10 terms across all recent tweets
2. **Bullish/Bearish Term Frequency**: Count of bullish vs bearish terms
3. **Topic Clustering**: Group similar tweets (e.g., all about "nifty options")
4. **Term Sentiment Correlation**: Which terms correlate with positive sentiment?

**Market Signal Output:**
```python
{
    'trending_terms': ['nifty', 'breakout', 'profit', 'target'],
    'bullish_term_frequency': 45,
    'bearish_term_frequency': 12,
    'net_market_sentiment': 'BULLISH',  # Based on term distribution
    'top_stocks_mentioned': ['HAL', 'TATAMOTORS', 'KIOCL']
}
```

---

### **Phase 4: Combined Feature Vector** 🎯

**Goal:** Create comprehensive numerical representation

**Combine:**
1. Sentiment score (from RoBERTa) → 1 feature
2. Virality score (from engagement) → 1 feature  
3. TF-IDF vector → 500-1000 features
4. Finance keyword counts → 10-20 features

**Total:** ~500-1000 dimensional feature vector per tweet

**Use cases:**
- ML model input (if building classifier/predictor later)
- Similarity search (find similar tweets)
- Clustering (group tweets by topic)
- Anomaly detection (unusual market chatter)

---

## 🛠️ Technical Implementation

### **Step 1: Basic Structure**

```python
class TFIDFAnalyzer:
    """
    TF-IDF analysis for tweet content
    """
    
    def __init__(
        self,
        max_features: int = 1000,
        ngram_range: tuple = (1, 2),
        min_df: int = 2,
        custom_vocabulary: Optional[Set[str]] = None
    ):
        # Initialize TfidfVectorizer
        # Set up finance-specific parameters
        pass
    
    def fit(self, tweets: List[str]):
        """Fit TF-IDF on tweet corpus"""
        pass
    
    def transform(self, tweet: str) -> Dict:
        """Extract TF-IDF features for a single tweet"""
        return {
            'top_terms': [...],
            'top_scores': [...],
            'tfidf_vector': [...]
        }
    
    def get_trending_terms(self, n: int = 10) -> List[Tuple[str, float]]:
        """Get top N trending terms across all tweets"""
        pass
```

### **Step 2: Integration**

Update `analyze_tweets()` to include TF-IDF:

```python
def analyze_tweets(tweets, include_tfidf=True):
    sentiment_analyzer = SentimentAnalyzer()
    engagement_analyzer = EngagementAnalyzer()
    tfidf_analyzer = TFIDFAnalyzer()
    
    # Fit TF-IDF on entire corpus first
    if include_tfidf:
        tfidf_analyzer.fit([t['content'] for t in tweets])
    
    # Process each tweet
    for tweet in tweets:
        result = {}
        result.update(sentiment_analyzer.analyze(tweet['content']))
        result.update(engagement_analyzer.analyze(tweet))
        
        if include_tfidf:
            result.update(tfidf_analyzer.transform(tweet['content']))
        
        # Combined signal score
        result['signal_score'] = calculate_signal(result)
```

---

## 📊 Output Examples

### **Per-Tweet Output:**
```python
{
    # Existing
    'combined_sentiment_score': 0.75,
    'virality_score': 0.42,
    
    # New TF-IDF features
    'top_tfidf_terms': ['nifty', 'breakout', 'target hit', 'bullish', 'profit'],
    'top_tfidf_scores': [0.89, 0.76, 0.65, 0.58, 0.52],
    'tfidf_vector': [0.0, 0.89, 0.0, ...],  # 1000-dim vector
    'finance_term_density': 0.35,  # 35% of words are finance terms
}
```

### **Aggregated Market Signal:**
```python
{
    'timestamp': '2025-10-05T13:30:00',
    'total_tweets': 100,
    'trending_terms': [
        ('nifty', 45),
        ('breakout', 23),
        ('profit', 18),
        ('target', 15)
    ],
    'market_sentiment': 'BULLISH',
    'sentiment_confidence': 0.73,
    'most_mentioned_stocks': ['HAL', 'TATA', 'SENSEX']
}
```

---

## 🎯 Implementation Steps (Recommended Order)

### **Step 1: Basic TF-IDF** ✅ Start Here
- [ ] Create `TFIDFAnalyzer` class
- [ ] Implement fit/transform methods
- [ ] Extract top N terms per tweet
- [ ] Test on existing 23 tweets
- [ ] Visualize most important terms

**Estimated time:** 1-2 hours  
**Output:** Top terms per tweet

### **Step 2: Finance Domain Focus** 
- [ ] Create finance vocabulary list
- [ ] Add custom stop words (spam terms)
- [ ] Weight finance terms higher
- [ ] Filter to relevant terms only

**Estimated time:** 1 hour  
**Output:** More relevant, finance-focused terms

### **Step 3: Aggregation & Market Signals**
- [ ] Trending terms across all tweets
- [ ] Bullish/bearish term frequency
- [ ] Stock mention extraction
- [ ] Time-based aggregations

**Estimated time:** 2 hours  
**Output:** Market-level signals

### **Step 4: Integration**
- [ ] Add to main analysis pipeline
- [ ] Update test scripts
- [ ] Create visualization dashboard
- [ ] Save to Parquet with all features

**Estimated time:** 1 hour  
**Output:** Full feature pipeline

---

## 💡 Key Decisions

### **1. Vocabulary Size**
- **Option A:** Full vocabulary (5000+ terms) - More features, slower
- **Option B:** Limited vocabulary (500-1000 terms) - Faster, more focused
- **Recommendation:** Start with Option B (1000 max features)

### **2. N-gram Range**
- **Option A:** Unigrams only (1,1) - Single words only
- **Option B:** Unigrams + Bigrams (1,2) - Words + 2-word phrases
- **Recommendation:** Option B - Captures "target hit", "stop loss", etc.

### **3. Minimum Document Frequency**
- **Option A:** min_df=1 - Keep all terms (noisy)
- **Option B:** min_df=2 - Only terms appearing 2+ times (cleaner)
- **Recommendation:** Option B - Reduces noise

### **4. Finance-Specific vs Generic**
- **Option A:** Generic TF-IDF on all words
- **Option B:** Finance-focused vocabulary only
- **Recommendation:** Start with A, enhance with B later

---

## 🎯 Expected Benefits

1. **Term Importance:** Know which words matter most in each tweet
2. **Trend Detection:** Identify what the market is talking about
3. **Feature Engineering:** Rich numerical features for ML
4. **Pattern Recognition:** Find similar tweets/topics
5. **Signal Enhancement:** Combine TF-IDF with sentiment for stronger signals

---

## 📊 Success Metrics

- **Coverage:** What % of tweets contain finance terms?
- **Relevance:** Are top TF-IDF terms actually meaningful?
- **Diversity:** How many unique important terms per tweet?
- **Consistency:** Do similar tweets have similar TF-IDF vectors?

---

## 🚀 Next Steps

**Ready to implement Step 1 (Basic TF-IDF)?**

This will add:
- Top 5-10 important terms per tweet
- TF-IDF scores for those terms
- Trending terms across all tweets
- Numerical feature vectors for each tweet

Should I proceed with the implementation? 🎯
