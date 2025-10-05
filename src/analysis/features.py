"""
Feature Engineering Module

Sentiment analysis for Indian stock market tweets using:
1. Twitter-RoBERTa base sentiment (social media understanding)
2. Finance keyword enhancement (domain-specific boosting)
"""

import logging
from typing import Dict, List, Optional
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


# ==================== Batch Processing ====================

def analyze_tweets(
    tweets: List[Dict],
    keyword_boost_weight: float = 0.3,
    include_engagement: bool = True
) -> pd.DataFrame:
    """
    Analyze sentiment and engagement for multiple tweets
    
    Args:
        tweets: List of tweet dictionaries (must have 'content' or 'cleaned_content')
        keyword_boost_weight: Weight for keyword boost (default: 0.3)
        include_engagement: Whether to include engagement metrics (default: True)
        
    Returns:
        DataFrame with sentiment and engagement analysis results
    """
    sentiment_analyzer = SentimentAnalyzer(keyword_boost_weight=keyword_boost_weight)
    engagement_analyzer = EngagementAnalyzer() if include_engagement else None
    
    results = []
    for i, tweet in enumerate(tweets):
        content = tweet.get('cleaned_content', tweet.get('content', ''))
        
        # Sentiment analysis
        analysis = sentiment_analyzer.analyze(content)
        
        # Engagement analysis
        if include_engagement:
            engagement = engagement_analyzer.analyze(tweet)
            analysis.update(engagement)
        
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
    
    return df


def analyze_from_parquet(
    input_file: str,
    output_file: Optional[str] = None,
    keyword_boost_weight: float = 0.3
) -> pd.DataFrame:
    """
    Analyze sentiment from Parquet file
    
    Args:
        input_file: Path to input Parquet file with tweets
        output_file: Optional path to save results
        keyword_boost_weight: Weight for keyword boost
        
    Returns:
        DataFrame with sentiment analysis
    """
    logger.info(f"Loading tweets from {input_file}")
    df = pd.read_parquet(input_file)
    tweets = df.to_dict('records')
    
    results_df = analyze_tweets(tweets, keyword_boost_weight=keyword_boost_weight)
    
    if output_file:
        results_df.to_parquet(output_file, index=False)
        logger.info(f"✓ Saved results to {output_file}")
    
    return results_df

