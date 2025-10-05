"""
Feature Engineering Module

Sentiment analysis for Indian stock market tweets using:
1. Twitter-RoBERTa base sentiment (social media understanding)
2. Finance keyword enhancement (domain-specific boosting)
3. TF-IDF term extraction (important term identification)
"""

import logging
from typing import Dict, List, Optional, Tuple, Set
import numpy as np
import pandas as pd

# Lazy imports for ML models
try:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    torch = None

# TF-IDF imports
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    TfidfVectorizer = None

logger = logging.getLogger(__name__)


# ==================== Finance Keywords ====================

BULLISH_KEYWORDS = {
    'bullish', 'bull', 'rally', 'surge', 'breakout', 'uptrend', 'momentum', 'strong',
    'buy', 'long', 'calls', 'green', 'profit', 'gain', 'positive', 'support',
    'target hit', 'target achieved', 'book profit', 'strength',
    'nifty up', 'sensex up', 'market up', 'bulls active',
}

BEARISH_KEYWORDS = {
    'bearish', 'bear', 'crash', 'dump', 'breakdown', 'downtrend', 'weak', 'resistance',
    'sell', 'short', 'puts', 'red', 'loss', 'losses', 'negative', 'fall',
    'stop loss', 'sl hit', 'weakness', 'exit',
    'nifty down', 'sensex down', 'market down', 'bears active',
}


# ==================== Twitter-RoBERTa Sentiment ====================

class SentimentAnalyzer:
    """
    Twitter-RoBERTa sentiment analyzer with finance keyword enhancement
    """
    
    def __init__(self, keyword_boost_weight: float = 0.3):
        """
        Initialize sentiment analyzer
        
        Args:
            keyword_boost_weight: How much to boost sentiment based on keywords (0-1)
        """
        self.keyword_boost_weight = keyword_boost_weight
        self.model = None
        self.tokenizer = None
        self._initialized = False
        
        if not TRANSFORMERS_AVAILABLE:
            logger.warning("Transformers not available. Install: pip install transformers torch")
    
    def _load_model(self):
        """Load RoBERTa model (lazy loading)"""
        if self._initialized or not TRANSFORMERS_AVAILABLE:
            return
        
        logger.info("Loading twitter-roberta-base-sentiment-latest model...")
        logger.info("First run will download ~500MB (one-time)")
        
        model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.eval()
        
        if torch.cuda.is_available():
            self.model = self.model.cuda()
            logger.info("✓ Model loaded on GPU")
        else:
            logger.info("✓ Model loaded on CPU")
        
        self._initialized = True
    
    def _analyze_base_sentiment(self, text: str) -> Dict[str, float]:
        """
        Get base sentiment from RoBERTa model
        
        Returns:
            dict with sentiment_score (-1 to +1), label, confidence, probabilities
        """
        if not text or not text.strip():
            return {
                'sentiment_score': 0.0,
                'sentiment_label': 'NEUTRAL',
                'confidence': 0.0,
                'probabilities': {'negative': 0.33, 'neutral': 0.34, 'positive': 0.33}
            }
        
        self._load_model()
        
        if not self._initialized:
            return {
                'sentiment_score': 0.0,
                'sentiment_label': 'NEUTRAL',
                'confidence': 0.0,
                'probabilities': {'negative': 0.33, 'neutral': 0.34, 'positive': 0.33}
            }
        
        # Tokenize and predict
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits[0], dim=0).cpu().numpy()
        
        # Map to labels
        labels = ['negative', 'neutral', 'positive']
        probabilities = {label: float(prob) for label, prob in zip(labels, probs)}
        
        predicted_idx = np.argmax(probs)
        predicted_label = labels[predicted_idx].upper()
        confidence = float(probs[predicted_idx])
        
        # Convert to continuous score: neg=-1, neutral=0, pos=+1
        sentiment_score = (
            probabilities['negative'] * -1.0 +
            probabilities['neutral'] * 0.0 +
            probabilities['positive'] * 1.0
        )
        
        return {
            'sentiment_score': sentiment_score,
            'sentiment_label': predicted_label,
            'confidence': confidence,
            'probabilities': probabilities
        }
    
    def _analyze_keywords(self, text: str) -> Dict:
        """
        Analyze finance keywords and calculate sentiment boost
        
        Returns:
            dict with bullish_count, bearish_count, keyword_boost
        """
        if not text:
            return {
                'bullish_count': 0,
                'bearish_count': 0,
                'keyword_boost': 0.0,
                'bullish_keywords': [],
                'bearish_keywords': []
            }
        
        text_lower = text.lower()
        
        # Find matching keywords
        bullish_found = [kw for kw in BULLISH_KEYWORDS if kw in text_lower]
        bearish_found = [kw for kw in BEARISH_KEYWORDS if kw in text_lower]
        
        # Calculate boost: (bullish - bearish) / 3, capped at [-1, +1], then weighted
        net_keywords = len(bullish_found) - len(bearish_found)
        keyword_boost = np.clip(net_keywords / 3.0, -1.0, 1.0) * self.keyword_boost_weight
        
        return {
            'bullish_count': len(bullish_found),
            'bearish_count': len(bearish_found),
            'keyword_boost': float(keyword_boost),
            'bullish_keywords': bullish_found,
            'bearish_keywords': bearish_found
        }
    
    def analyze(self, text: str) -> Dict:
        """
        Analyze sentiment with keyword enhancement
        
        Args:
            text: Tweet content to analyze
            
        Returns:
            dict with base sentiment, keyword analysis, and combined sentiment
        """
        # Base sentiment from RoBERTa
        base = self._analyze_base_sentiment(text)
        
        # Keyword analysis
        keywords = self._analyze_keywords(text)
        
        # Combined sentiment
        combined_score = base['sentiment_score'] + keywords['keyword_boost']
        combined_score = np.clip(combined_score, -1.0, 1.0)
        
        # Determine combined label
        if combined_score < -0.1:
            combined_label = 'BEARISH'
        elif combined_score > 0.1:
            combined_label = 'BULLISH'
        else:
            combined_label = 'NEUTRAL'
        
        return {
            # Base sentiment
            'base_sentiment_score': base['sentiment_score'],
            'base_sentiment_label': base['sentiment_label'],
            'base_confidence': base['confidence'],
            'probabilities': base['probabilities'],
            
            # Keywords
            'bullish_keyword_count': keywords['bullish_count'],
            'bearish_keyword_count': keywords['bearish_count'],
            'keyword_boost': keywords['keyword_boost'],
            'bullish_keywords': keywords['bullish_keywords'],
            'bearish_keywords': keywords['bearish_keywords'],
            
            # Combined
            'combined_sentiment_score': float(combined_score),
            'combined_sentiment_label': combined_label,
        }


# ==================== Engagement Metrics ====================

class EngagementAnalyzer:
    """
    Analyzes tweet engagement metrics and calculates virality score
    """
    
    def __init__(
        self,
        engagement_weight: float = 0.3,
        retweet_weight: float = 0.5,
        reply_weight: float = 0.3,
        like_weight: float = 0.2
    ):
        """
        Initialize engagement analyzer
        
        Args:
            engagement_weight: Weight for overall engagement rate in virality score
            retweet_weight: Weight for retweets (most viral)
            reply_weight: Weight for replies (discussion indicator)
            like_weight: Weight for likes (basic engagement)
        """
        self.engagement_weight = engagement_weight
        self.retweet_weight = retweet_weight
        self.reply_weight = reply_weight
        self.like_weight = like_weight
    
    def analyze(self, tweet: Dict) -> Dict[str, float]:
        """
        Analyze engagement metrics for a tweet
        
        Args:
            tweet: Tweet dictionary with engagement fields
            
        Returns:
            dict with engagement metrics and virality score
        """
        likes = tweet.get('likes', 0)
        retweets = tweet.get('retweets', 0)
        replies = tweet.get('replies', 0)
        views = tweet.get('views', 0)
        
        # Basic metrics
        total_engagement = likes + retweets + replies
        
        # Engagement rate (per 1000 views)
        engagement_rate = 0.0
        if views > 0:
            engagement_rate = (total_engagement / views) * 1000
        
        # Virality ratio (retweets are most viral)
        virality_ratio = 0.0
        if likes > 0:
            virality_ratio = retweets / likes
        
        # Reply ratio (indicates discussion/controversy)
        reply_ratio = 0.0
        if total_engagement > 0:
            reply_ratio = replies / total_engagement
        
        # Like ratio
        like_ratio = 0.0
        if views > 0:
            like_ratio = likes / views
        
        # ========== Combined Virality Score ==========
        # Normalize each component to [0, 1] range, then weighted average
        
        # 1. Normalize engagement rate (cap at 50 per 1000 views = high engagement)
        norm_engagement = min(engagement_rate / 50.0, 1.0)
        
        # 2. Normalize virality ratio (cap at 0.5 = very viral)
        norm_virality = min(virality_ratio / 0.5, 1.0)
        
        # 3. Reply ratio is already 0-1
        norm_reply = reply_ratio
        
        # 4. Normalize like ratio (cap at 0.05 = 5% like rate is excellent)
        norm_like = min(like_ratio / 0.05, 1.0)
        
        # Combined virality score (weighted average, scaled to 0-1)
        virality_score = (
            norm_engagement * self.engagement_weight +
            norm_virality * self.retweet_weight +
            norm_reply * self.reply_weight +
            norm_like * self.like_weight
        )
        
        # Normalize to 0-1 range
        total_weight = self.engagement_weight + self.retweet_weight + self.reply_weight + self.like_weight
        virality_score = virality_score / total_weight
        
        return {
            # Raw metrics
            'likes': likes,
            'retweets': retweets,
            'replies': replies,
            'views': views,
            'total_engagement': total_engagement,
            
            # Calculated metrics
            'engagement_rate': float(engagement_rate),
            'virality_ratio': float(virality_ratio),
            'reply_ratio': float(reply_ratio),
            'like_ratio': float(like_ratio),
            
            # Combined score
            'virality_score': float(virality_score),
        }


# ==================== TF-IDF Analysis ====================

class TFIDFAnalyzer:
    """
    TF-IDF analysis for extracting important terms from tweets
    
    Identifies significant words/phrases that distinguish each tweet
    from the corpus, useful for understanding key topics and trends.
    """
    
    def __init__(
        self,
        max_features: int = 1000,
        ngram_range: Tuple[int, int] = (1, 2),
        min_df: int = 2,
        max_df: float = 0.8,
        top_n_terms: int = 10
    ):
        """
        Initialize TF-IDF analyzer
        
        Args:
            max_features: Maximum number of features (vocabulary size)
            ngram_range: Range of n-grams (1,2 = unigrams + bigrams)
            min_df: Minimum document frequency (ignore rare terms)
            max_df: Maximum document frequency (ignore very common terms)
            top_n_terms: Number of top terms to extract per tweet
        """
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.min_df = min_df
        self.max_df = max_df
        self.top_n_terms = top_n_terms
        
        self.vectorizer = None
        self.feature_names = None
        self._is_fitted = False
        
        if not SKLEARN_AVAILABLE:
            logger.warning("scikit-learn not available. Install: pip install scikit-learn")
    
    def fit(self, texts: List[str]) -> 'TFIDFAnalyzer':
        """
        Fit TF-IDF vectorizer on corpus
        
        Args:
            texts: List of tweet texts
            
        Returns:
            self for chaining
        """
        if not SKLEARN_AVAILABLE:
            logger.warning("Cannot fit TF-IDF: scikit-learn not installed")
            return self
        
        logger.info(f"Fitting TF-IDF on {len(texts)} tweets...")
        
        # Initialize vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            ngram_range=self.ngram_range,
            min_df=self.min_df,
            max_df=self.max_df,
            stop_words='english',
            lowercase=True,
            token_pattern=r'\b[a-zA-Z][a-zA-Z]+\b'  # At least 2 chars, alpha only
        )
        
        # Fit on corpus
        self.vectorizer.fit(texts)
        self.feature_names = self.vectorizer.get_feature_names_out()
        self._is_fitted = True
        
        logger.info(f"✓ TF-IDF fitted with {len(self.feature_names)} features")
        
        return self
    
    def transform(self, text: str) -> Dict:
        """
        Extract TF-IDF features for a single text
        
        Args:
            text: Tweet content
            
        Returns:
            Dictionary with top terms, scores, and vector
        """
        if not self._is_fitted:
            return {
                'top_tfidf_terms': [],
                'top_tfidf_scores': [],
                'tfidf_vector': [],
                'finance_term_density': 0.0
            }
        
        # Transform text to TF-IDF vector
        tfidf_vector = self.vectorizer.transform([text]).toarray()[0]
        
        # Get top N terms
        top_indices = np.argsort(tfidf_vector)[-self.top_n_terms:][::-1]
        top_indices = [i for i in top_indices if tfidf_vector[i] > 0]  # Only non-zero
        
        top_terms = [self.feature_names[i] for i in top_indices]
        top_scores = [float(tfidf_vector[i]) for i in top_indices]
        
        # Calculate finance term density (% of words that are finance-related)
        words = text.lower().split()
        if words:
            finance_words = sum(1 for word in words if word in BULLISH_KEYWORDS or word in BEARISH_KEYWORDS)
            finance_term_density = finance_words / len(words)
        else:
            finance_term_density = 0.0
        
        return {
            'top_tfidf_terms': top_terms,
            'top_tfidf_scores': top_scores,
            'tfidf_vector': tfidf_vector.tolist(),
            'finance_term_density': float(finance_term_density),
            'num_tfidf_features': len(top_terms)
        }
    
    def get_trending_terms(self, texts: List[str], n: int = 10) -> List[Tuple[str, float]]:
        """
        Get top N trending terms across all texts
        
        Args:
            texts: List of tweet texts
            n: Number of top terms to return
            
        Returns:
            List of (term, average_score) tuples
        """
        if not self._is_fitted:
            return []
        
        # Transform all texts
        tfidf_matrix = self.vectorizer.transform(texts).toarray()
        
        # Calculate average TF-IDF score for each term across all documents
        avg_scores = tfidf_matrix.mean(axis=0)
        
        # Get top N
        top_indices = np.argsort(avg_scores)[-n:][::-1]
        trending = [(self.feature_names[i], float(avg_scores[i])) for i in top_indices]
        
        return trending
    
    def get_document_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate cosine similarity between two texts
        
        Args:
            text1, text2: Texts to compare
            
        Returns:
            Similarity score (0-1)
        """
        if not self._is_fitted:
            return 0.0
        
        # Transform both texts
        vec1 = self.vectorizer.transform([text1]).toarray()[0]
        vec2 = self.vectorizer.transform([text2]).toarray()[0]
        
        # Cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))


# ==================== Signal Generation with Confidence ====================

def calculate_confidence_score(tweet_features: Dict) -> Dict[str, float]:
    """
    Calculate confidence score (0-1) from multiple features
    
    Confidence indicates how much we should trust the signal.
    Higher confidence = More reliable signal
    
    Components:
    - Content quality (40%): From TF-IDF analysis
    - Sentiment strength (30%): From RoBERTa model confidence
    - Social proof (30%): From engagement/virality
    
    Args:
        tweet_features: Dictionary with all tweet features
        
    Returns:
        Dict with confidence score and component breakdown
    """
    # 1. Content Quality (from TF-IDF) - 40% weight
    finance_density = tweet_features.get('finance_term_density', 0.0)
    top_terms = set(tweet_features.get('top_tfidf_terms', []))
    
    # Base quality from finance density (10% density = max score)
    quality_score = min(finance_density * 10, 1.0)
    
    # Penalize spam terms
    spam_terms = {'join', 'telegram', 'dm', 'subscribe', 'link', 'whatsapp', 
                  'channel', 'click', 'follow', 'free'}
    if top_terms & spam_terms:
        quality_score *= 0.3  # 70% penalty for spam
    
    # Boost for technical/analysis terms
    technical_terms = {'breakout', 'breakdown', 'support', 'resistance',
                      'target', 'stop loss', 'levels', 'rsi', 'macd',
                      'analysis', 'chart', 'pattern'}
    if top_terms & technical_terms:
        quality_score = min(quality_score * 1.3, 1.0)  # 30% boost
    
    
    # 2. Sentiment Strength (from RoBERTa) - 30% weight
    sentiment_confidence = tweet_features.get('base_confidence', 0.5)
    
    
    # 3. Social Proof (from engagement) - 30% weight
    virality_score = tweet_features.get('virality_score', 0.0)
    
    
    # Combined confidence (weighted average)
    confidence = (
        quality_score * 0.40 +
        sentiment_confidence * 0.30 +
        virality_score * 0.30
    )
    
    return {
        'confidence': float(np.clip(confidence, 0.0, 1.0)),
        'confidence_components': {
            'content_quality': float(quality_score),
            'sentiment_strength': float(sentiment_confidence),
            'social_proof': float(virality_score)
        }
    }


def calculate_trading_signal(tweet_features: Dict) -> Dict:
    """
    Generate trading signal with confidence score and interval
    
    Formula:
    - Base signal = sentiment × (base_weight + virality_boost)
    - Final signal = base_signal × confidence
    - Confidence interval = signal ± margin (based on confidence)
    
    Args:
        tweet_features: Dictionary with all tweet features
        
    Returns:
        Dict with signal score, label, confidence, and interval
    """
    # 1. Calculate base signal (sentiment × virality)
    sentiment = tweet_features.get('combined_sentiment_score', 0.0)
    virality = tweet_features.get('virality_score', 0.0)
    
    # Base signal: sentiment weighted by engagement
    base_signal = sentiment * (0.5 + virality * 0.5)
    
    
    # 2. Calculate confidence from multiple features
    confidence_result = calculate_confidence_score(tweet_features)
    confidence = confidence_result['confidence']
    
    
    # 3. Adjust signal by confidence
    # High confidence → Keep signal as-is
    # Low confidence → Dampen signal toward 0
    final_signal = base_signal * confidence
    
    
    # 4. Determine label with confidence thresholds
    if confidence < 0.3:
        label = 'IGNORE'  # Too low confidence to act
        strength = 'NONE'
    elif abs(final_signal) < 0.2:
        label = 'HOLD'
        strength = 'WEAK'
    elif final_signal >= 0.5:
        label = 'STRONG_BUY'
        strength = 'STRONG'
    elif final_signal > 0.2:
        label = 'BUY'
        strength = 'MODERATE'
    elif final_signal <= -0.5:
        label = 'STRONG_SELL'
        strength = 'STRONG'
    elif final_signal < -0.2:
        label = 'SELL'
        strength = 'MODERATE'
    else:
        label = 'HOLD'
        strength = 'WEAK'
    
    
    # 5. Calculate confidence interval
    # Higher confidence = narrower interval
    # Lower confidence = wider interval
    interval_width = (1 - confidence) * 0.5  # Range: 0 to 0.5
    confidence_interval_lower = max(final_signal - interval_width, -1.0)
    confidence_interval_upper = min(final_signal + interval_width, 1.0)
    
    
    return {
        'signal_score': float(final_signal),
        'signal_label': label,
        'signal_strength': strength,
        'confidence': confidence,
        'confidence_interval': (float(confidence_interval_lower), 
                               float(confidence_interval_upper)),
        'base_signal': float(base_signal),  # Before confidence adjustment
        **confidence_result  # Include confidence components
    }


def aggregate_signals(tweet_signals: List[Dict], min_confidence: float = 0.3) -> Dict:
    """
    Aggregate multiple tweet signals into a single composite signal
    
    Uses confidence-weighted averaging to combine signals.
    Higher confidence tweets have more influence on the aggregate.
    
    Args:
        tweet_signals: List of signal dictionaries from calculate_trading_signal()
        min_confidence: Minimum confidence threshold to include (default: 0.3)
        
    Returns:
        Dict with aggregate signal, confidence interval, and statistics
    """
    # Filter to tweets meeting minimum confidence
    valid_signals = [
        s for s in tweet_signals 
        if s['confidence'] >= min_confidence
    ]
    
    if not valid_signals:
        return {
            'aggregate_signal': 0.0,
            'aggregate_label': 'HOLD',
            'aggregate_confidence': 0.0,
            'confidence_interval': (0.0, 0.0),
            'num_tweets': 0,
            'num_valid_tweets': 0,
            'signal_std': 0.0,
            'consensus': 'NONE'
        }
    
    # Extract signals and confidences
    signals = np.array([s['signal_score'] for s in valid_signals])
    confidences = np.array([s['confidence'] for s in valid_signals])
    
    # Weighted average by confidence
    aggregate_signal = float(np.average(signals, weights=confidences))
    aggregate_confidence = float(np.mean(confidences))
    
    # Calculate statistics
    signal_std = float(np.std(signals))
    
    # Confidence interval for aggregate
    # Wider interval if signals disagree (high std) or low confidence
    margin = signal_std * (1 - aggregate_confidence) * 0.5
    confidence_interval_lower = max(aggregate_signal - margin, -1.0)
    confidence_interval_upper = min(aggregate_signal + margin, 1.0)
    
    # Determine label
    if aggregate_confidence < 0.4:
        label = 'HOLD'  # Low confidence, don't act
    elif aggregate_signal >= 0.5:
        label = 'STRONG_BUY'
    elif aggregate_signal > 0.2:
        label = 'BUY'
    elif aggregate_signal <= -0.5:
        label = 'STRONG_SELL'
    elif aggregate_signal < -0.2:
        label = 'SELL'
    else:
        label = 'HOLD'
    
    # Determine consensus
    bullish_count = sum(1 for s in signals if s > 0.2)
    bearish_count = sum(1 for s in signals if s < -0.2)
    total = len(signals)
    
    if bullish_count / total > 0.7:
        consensus = 'STRONG_BULLISH'
    elif bullish_count / total > 0.5:
        consensus = 'BULLISH'
    elif bearish_count / total > 0.7:
        consensus = 'STRONG_BEARISH'
    elif bearish_count / total > 0.5:
        consensus = 'BEARISH'
    else:
        consensus = 'MIXED'
    
    return {
        'aggregate_signal': aggregate_signal,
        'aggregate_label': label,
        'aggregate_confidence': aggregate_confidence,
        'confidence_interval': (float(confidence_interval_lower), 
                               float(confidence_interval_upper)),
        'num_tweets': len(tweet_signals),
        'num_valid_tweets': len(valid_signals),
        'signal_std': signal_std,
        'consensus': consensus,
        'bullish_ratio': float(bullish_count / total) if total > 0 else 0.0,
        'bearish_ratio': float(bearish_count / total) if total > 0 else 0.0
    }


# ==================== Batch Processing ====================

def analyze_tweets(
    tweets: List[Dict],
    keyword_boost_weight: float = 0.3,
    include_engagement: bool = True,
    include_tfidf: bool = True,
    calculate_signals: bool = True
) -> pd.DataFrame:
    """
    Analyze sentiment, engagement, TF-IDF, and generate trading signals for multiple tweets
    
    Args:
        tweets: List of tweet dictionaries (must have 'content' or 'cleaned_content')
        keyword_boost_weight: Weight for keyword boost (default: 0.3)
        include_engagement: Whether to include engagement metrics (default: True)
        include_tfidf: Whether to include TF-IDF features (default: True)
        calculate_signals: Whether to calculate trading signals with confidence (default: True)
        
    Returns:
        DataFrame with complete analysis including trading signals and confidence scores
    """
    sentiment_analyzer = SentimentAnalyzer(keyword_boost_weight=keyword_boost_weight)
    engagement_analyzer = EngagementAnalyzer() if include_engagement else None
    tfidf_analyzer = TFIDFAnalyzer() if include_tfidf else None
    
    # Extract content for TF-IDF fitting
    contents = [tweet.get('cleaned_content', tweet.get('content', '')) for tweet in tweets]
    
    # Fit TF-IDF on entire corpus first
    if include_tfidf and tfidf_analyzer:
        tfidf_analyzer.fit(contents)
    
    results = []
    for i, tweet in enumerate(tweets):
        content = contents[i]
        
        # Sentiment analysis
        analysis = sentiment_analyzer.analyze(content)
        
        # Engagement analysis
        if include_engagement and engagement_analyzer:
            engagement = engagement_analyzer.analyze(tweet)
            analysis.update(engagement)
        
        # TF-IDF analysis
        if include_tfidf and tfidf_analyzer:
            tfidf_features = tfidf_analyzer.transform(content)
            analysis.update(tfidf_features)
        
        # Calculate trading signal with confidence
        if calculate_signals:
            signal = calculate_trading_signal(analysis)
            analysis.update(signal)
        
        # Add tweet metadata
        analysis['tweet_id'] = tweet.get('tweet_id', i)
        analysis['username'] = tweet.get('username', '')
        analysis['content'] = content
        analysis['timestamp'] = tweet.get('timestamp', '')
        
        results.append(analysis)
        
        if (i + 1) % 10 == 0:
            logger.info(f"Processed {i + 1}/{len(tweets)} tweets")
    
    df = pd.DataFrame(results)
    logger.info(f"✓ Analyzed {len(df)} tweets")
    
    # Log trending terms if TF-IDF was used
    if include_tfidf and tfidf_analyzer and tfidf_analyzer._is_fitted:
        trending = tfidf_analyzer.get_trending_terms(contents, n=10)
        logger.info(f"Top 10 trending terms: {[term for term, _ in trending]}")
    
    return df


def analyze_from_parquet(
    input_file: str,
    output_file: Optional[str] = None,
    keyword_boost_weight: float = 0.3,
    include_tfidf: bool = True
) -> pd.DataFrame:
    """
    Analyze sentiment, engagement, and TF-IDF from Parquet file
    
    Args:
        input_file: Path to input Parquet file with tweets
        output_file: Optional path to save results
        keyword_boost_weight: Weight for keyword boost
        include_tfidf: Whether to include TF-IDF features
        
    Returns:
        DataFrame with complete analysis
    """
    logger.info(f"Loading tweets from {input_file}")
    df = pd.read_parquet(input_file)
    tweets = df.to_dict('records')
    
    results_df = analyze_tweets(
        tweets,
        keyword_boost_weight=keyword_boost_weight,
        include_tfidf=include_tfidf
    )
    
    if output_file:
        results_df.to_parquet(output_file, index=False)
        logger.info(f"✓ Saved results to {output_file}")
    
    return results_df

