"""
Hashtag Analyzer - Per-hashtag signal aggregation

Groups tweets by hashtag and calculates aggregated signals for each hashtag.
"""

import logging
from typing import Dict, List, Optional
from collections import Counter
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class HashtagAnalyzer:
    """
    Analyzes signals on a per-hashtag basis
    
    For each hashtag, computes:
    - Aggregate signal (confidence-weighted)
    - Sentiment distribution
    - Engagement metrics
    - Trending terms
    - Signal consensus
    """
    
    def __init__(self, min_tweets: int = 20, min_confidence: float = 0.3):
        """
        Initialize hashtag analyzer
        
        Args:
            min_tweets: Minimum tweets required per hashtag for reliable signal
            min_confidence: Minimum confidence threshold for including tweets
        """
        self.min_tweets = min_tweets
        self.min_confidence = min_confidence
    
    def analyze_by_hashtag(self, df: pd.DataFrame) -> Dict:
        """
        Analyze signals grouped by hashtag
        
        Args:
            df: DataFrame with analyzed tweets (must have signal columns)
            
        Returns:
            Dict mapping hashtag -> signal analysis
        """
        if 'hashtags' not in df.columns:
            logger.warning("No 'hashtags' column found in DataFrame")
            return {}
        
        # Explode hashtags (one row per hashtag per tweet)
        df_exploded = self._explode_hashtags(df)
        
        if df_exploded.empty:
            logger.warning("No hashtags found in tweets")
            return {}
        
        # Group by hashtag
        hashtag_groups = df_exploded.groupby('hashtag')
        
        results = {}
        for hashtag, group_df in hashtag_groups:
            # Skip if too few tweets
            if len(group_df) < self.min_tweets:
                logger.info(f"Skipping #{hashtag}: only {len(group_df)} tweets (min: {self.min_tweets})")
                continue
            
            # Analyze this hashtag
            analysis = self._analyze_single_hashtag(hashtag, group_df)
            results[hashtag] = analysis
        
        logger.info(f"Analyzed {len(results)} hashtags")
        return results
    
    def _explode_hashtags(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Explode hashtags column so each tweet-hashtag pair gets a row
        
        Handles both list and string hashtag formats.
        """
        df_copy = df.copy()
        
        # Normalize hashtags to lowercase lists
        def normalize_hashtags(tags):
            # Handle None/NaN - check for scalar None or use try/except for arrays
            if tags is None:
                return []
            try:
                if pd.isna(tags):
                    return []
            except (ValueError, TypeError):
                # pd.isna() on arrays raises ValueError, so tags is an array/list
                pass
            
            if isinstance(tags, str):
                # Handle empty string or "[]"
                if not tags or tags == '[]':
                    return []
                # Parse string representation of list
                import ast
                try:
                    tags = ast.literal_eval(tags)
                except Exception as e:
                    logger.debug(f"Failed to parse hashtag string: {repr(tags)[:50]}")
                    return []
            if isinstance(tags, (list, np.ndarray)):
                result = [str(tag).lower().strip('#').strip() for tag in tags if tag]
                return result
            return []
        
        df_copy['hashtags_normalized'] = df_copy['hashtags'].apply(normalize_hashtags)
        
        # Log statistics
        total_tweets = len(df_copy)
        tweets_with_hashtags = (df_copy['hashtags_normalized'].apply(len) > 0).sum()
        logger.info(f"Hashtag extraction: {tweets_with_hashtags}/{total_tweets} tweets have hashtags")
        
        if tweets_with_hashtags == 0:
            logger.warning("⚠️  No hashtags found in any tweets!")
            logger.warning("Check the format of the 'hashtags' column in your data")
            return pd.DataFrame()
        
        # Filter out tweets with no hashtags
        df_copy = df_copy[df_copy['hashtags_normalized'].apply(len) > 0]
        
        # Explode
        df_exploded = df_copy.explode('hashtags_normalized')
        df_exploded = df_exploded.rename(columns={'hashtags_normalized': 'hashtag'})
        
        # Log unique hashtags found
        unique_hashtags = df_exploded['hashtag'].nunique()
        logger.info(f"Found {unique_hashtags} unique hashtags")
        
        return df_exploded.reset_index(drop=True)
    
    def _analyze_single_hashtag(self, hashtag: str, df: pd.DataFrame) -> Dict:
        """
        Analyze a single hashtag's tweets
        
        Args:
            hashtag: The hashtag (without #)
            df: DataFrame of tweets for this hashtag
            
        Returns:
            Dict with comprehensive hashtag analysis
        """
        # Filter to valid confidence tweets
        df_valid = df[df['confidence'] >= self.min_confidence].copy()
        
        # Basic stats
        tweet_count = len(df)
        valid_tweet_count = len(df_valid)
        
        # Time range
        time_range = {}
        if 'timestamp' in df.columns:
            df['timestamp_dt'] = pd.to_datetime(df['timestamp'])
            time_range = {
                'earliest': str(df['timestamp_dt'].min()),
                'latest': str(df['timestamp_dt'].max()),
                'span_hours': (df['timestamp_dt'].max() - df['timestamp_dt'].min()).total_seconds() / 3600
            }
        
        # Aggregate signal (confidence-weighted)
        signal_score = 0.0
        signal_label = 'HOLD'
        confidence = 0.0
        consensus = 'NONE'
        
        if valid_tweet_count > 0:
            signals = df_valid['signal_score'].values
            confidences = df_valid['confidence'].values
            
            # Weighted average
            signal_score = float(np.average(signals, weights=confidences))
            confidence = float(np.mean(confidences))
            
            # Determine label
            signal_label = self._determine_signal_label(signal_score, confidence)
            
            # Consensus
            consensus = self._calculate_consensus(signals)
        
        # Sentiment distribution
        sentiment_dist = self._calculate_sentiment_distribution(df_valid)
        
        # Engagement metrics
        engagement_metrics = self._calculate_engagement_metrics(df)
        
        # Trending terms (TF-IDF)
        trending_terms = self._extract_trending_terms(df_valid)
        
        # Confidence breakdown
        confidence_breakdown = self._calculate_confidence_breakdown(df_valid)
        
        # Signal distribution
        signal_dist = self._calculate_signal_distribution(df)
        
        return {
            'hashtag': hashtag,
            'tweet_count': tweet_count,
            'valid_tweet_count': valid_tweet_count,
            'time_range': time_range,
            
            # Signal
            'signal_label': signal_label,
            'signal_score': signal_score,
            'confidence': confidence,
            'consensus': consensus,
            
            # Distributions
            'sentiment_distribution': sentiment_dist,
            'signal_distribution': signal_dist,
            
            # Metrics
            'engagement_metrics': engagement_metrics,
            'trending_terms': trending_terms,
            'confidence_breakdown': confidence_breakdown,
        }
    
    def _determine_signal_label(self, signal_score: float, confidence: float) -> str:
        """Determine signal label from score and confidence"""
        if confidence < 0.4:
            return 'HOLD'
        elif signal_score >= 0.5:
            return 'STRONG_BUY'
        elif signal_score > 0.2:
            return 'BUY'
        elif signal_score <= -0.5:
            return 'STRONG_SELL'
        elif signal_score < -0.2:
            return 'SELL'
        else:
            return 'HOLD'
    
    def _calculate_consensus(self, signals: np.ndarray) -> str:
        """Calculate consensus from signal array"""
        bullish = np.sum(signals > 0.2)
        bearish = np.sum(signals < -0.2)
        total = len(signals)
        
        bullish_ratio = bullish / total if total > 0 else 0
        bearish_ratio = bearish / total if total > 0 else 0
        
        if bullish_ratio > 0.7:
            return 'STRONG_BULLISH'
        elif bullish_ratio > 0.5:
            return 'BULLISH'
        elif bearish_ratio > 0.7:
            return 'STRONG_BEARISH'
        elif bearish_ratio > 0.5:
            return 'BEARISH'
        else:
            return 'MIXED'
    
    def _calculate_sentiment_distribution(self, df: pd.DataFrame) -> Dict:
        """Calculate sentiment distribution"""
        if df.empty:
            return {
                'avg_sentiment': 0.0,
                'bullish_count': 0,
                'bearish_count': 0,
                'neutral_count': 0,
                'bullish_ratio': 0.0,
                'bearish_ratio': 0.0,
                'neutral_ratio': 0.0
            }
        
        avg_sentiment = float(df['combined_sentiment_score'].mean())
        
        bullish = df['combined_sentiment_score'] > 0.1
        bearish = df['combined_sentiment_score'] < -0.1
        neutral = ~(bullish | bearish)
        
        bullish_count = int(bullish.sum())
        bearish_count = int(bearish.sum())
        neutral_count = int(neutral.sum())
        total = len(df)
        
        return {
            'avg_sentiment': avg_sentiment,
            'bullish_count': bullish_count,
            'bearish_count': bearish_count,
            'neutral_count': neutral_count,
            'bullish_ratio': bullish_count / total if total > 0 else 0.0,
            'bearish_ratio': bearish_count / total if total > 0 else 0.0,
            'neutral_ratio': neutral_count / total if total > 0 else 0.0
        }
    
    def _calculate_engagement_metrics(self, df: pd.DataFrame) -> Dict:
        """Calculate engagement metrics"""
        if df.empty or 'virality_score' not in df.columns:
            return {
                'avg_virality': 0.0,
                'total_likes': 0,
                'total_retweets': 0,
                'total_replies': 0,
                'high_engagement_count': 0,
                'high_engagement_ratio': 0.0
            }
        
        return {
            'avg_virality': float(df['virality_score'].mean()),
            'total_likes': int(df['likes'].sum()) if 'likes' in df.columns else 0,
            'total_retweets': int(df['retweets'].sum()) if 'retweets' in df.columns else 0,
            'total_replies': int(df['replies'].sum()) if 'replies' in df.columns else 0,
            'high_engagement_count': int((df['virality_score'] > 0.5).sum()),
            'high_engagement_ratio': float((df['virality_score'] > 0.5).mean())
        }
    
    def _extract_trending_terms(self, df: pd.DataFrame, top_n: int = 10) -> List[Dict]:
        """Extract top trending TF-IDF terms"""
        if df.empty or 'top_tfidf_terms' not in df.columns:
            return []
        
        # Collect all terms with scores
        term_scores = []
        for _, row in df.iterrows():
            terms = row.get('top_tfidf_terms', [])
            scores = row.get('top_tfidf_scores', [])
            
            if isinstance(terms, list) and isinstance(scores, list):
                for term, score in zip(terms, scores):
                    term_scores.append((term, score))
        
        if not term_scores:
            return []
        
        # Aggregate by term (average score)
        term_dict = {}
        for term, score in term_scores:
            if term not in term_dict:
                term_dict[term] = []
            term_dict[term].append(score)
        
        # Calculate average and sort
        term_avg = [(term, np.mean(scores)) for term, scores in term_dict.items()]
        term_avg.sort(key=lambda x: x[1], reverse=True)
        
        return [
            {'term': term, 'score': float(score)}
            for term, score in term_avg[:top_n]
        ]
    
    def _calculate_confidence_breakdown(self, df: pd.DataFrame) -> Dict:
        """Calculate confidence component breakdown"""
        if df.empty or 'confidence_components' not in df.columns:
            return {
                'content_quality': 0.0,
                'sentiment_strength': 0.0,
                'social_proof': 0.0
            }
        
        # Extract components
        components = df['confidence_components'].apply(
            lambda x: x if isinstance(x, dict) else {}
        )
        
        return {
            'content_quality': float(components.apply(lambda x: x.get('content_quality', 0)).mean()),
            'sentiment_strength': float(components.apply(lambda x: x.get('sentiment_strength', 0)).mean()),
            'social_proof': float(components.apply(lambda x: x.get('social_proof', 0)).mean())
        }
    
    def _calculate_signal_distribution(self, df: pd.DataFrame) -> Dict:
        """Calculate signal label distribution"""
        if df.empty or 'signal_label' not in df.columns:
            return {}
        
        counts = df['signal_label'].value_counts()
        total = len(df)
        
        return {
            label: {
                'count': int(count),
                'ratio': float(count / total)
            }
            for label, count in counts.items()
        }
