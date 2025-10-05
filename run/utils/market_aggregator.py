"""
Market Aggregator - Overall market sentiment calculation

Aggregates per-hashtag signals into overall market sentiment using volume-based weighting.
"""

import logging
from typing import Dict, List
import numpy as np

logger = logging.getLogger(__name__)


class MarketAggregator:
    """
    Aggregates hashtag-level signals into overall market sentiment
    
    Uses volume-based weighting where hashtags with more tweets
    have proportionally more influence on the overall signal.
    """
    
    def __init__(self, min_confidence: float = 0.4):
        """
        Initialize market aggregator
        
        Args:
            min_confidence: Minimum aggregate confidence for actionable signal
        """
        self.min_confidence = min_confidence
    
    def aggregate_market_signal(
        self,
        hashtag_analyses: Dict,
        total_tweets: int
    ) -> Dict:
        """
        Aggregate per-hashtag signals into overall market sentiment
        
        Args:
            hashtag_analyses: Dict from HashtagAnalyzer (hashtag -> analysis)
            total_tweets: Total number of tweets analyzed
            
        Returns:
            Dict with overall market signal and statistics
        """
        if not hashtag_analyses:
            logger.warning("No hashtag analyses provided")
            return self._empty_market_signal()
        
        # Extract signals and weights
        hashtags = []
        signals = []
        confidences = []
        volumes = []
        
        for hashtag, analysis in hashtag_analyses.items():
            hashtags.append(hashtag)
            signals.append(analysis['signal_score'])
            confidences.append(analysis['confidence'])
            volumes.append(analysis['tweet_count'])
        
        signals = np.array(signals)
        confidences = np.array(confidences)
        volumes = np.array(volumes)
        
        # Volume-based weighting
        total_volume = volumes.sum()
        volume_weights = volumes / total_volume if total_volume > 0 else np.ones(len(volumes)) / len(volumes)
        
        # Aggregate signal (volume-weighted average)
        aggregate_signal = float(np.average(signals, weights=volume_weights))
        
        # Aggregate confidence (volume-weighted average)
        aggregate_confidence = float(np.average(confidences, weights=volume_weights))
        
        # Signal variance/disagreement
        signal_std = float(np.std(signals))
        
        # Determine label
        signal_label = self._determine_market_label(aggregate_signal, aggregate_confidence)
        
        # Market consensus
        consensus = self._calculate_market_consensus(signals, volume_weights)
        
        # Sentiment distribution across market
        sentiment_dist = self._aggregate_sentiment_distribution(hashtag_analyses, volumes)
        
        # Signal distribution
        signal_dist = self._aggregate_signal_distribution(hashtag_analyses, volumes)
        
        # Hashtag ranking
        hashtag_ranking = self._rank_hashtags(hashtag_analyses)
        
        # Risk indicators
        risk_indicators = self._calculate_risk_indicators(
            hashtag_analyses, signal_std, aggregate_confidence, total_tweets
        )
        
        return {
            'signal_label': signal_label,
            'signal_score': aggregate_signal,
            'confidence': aggregate_confidence,
            'consensus': consensus,
            'total_tweets': total_tweets,
            'hashtag_count': len(hashtag_analyses),
            
            # Statistics
            'signal_variance': signal_std,
            'sentiment_distribution': sentiment_dist,
            'signal_distribution': signal_dist,
            
            # Rankings
            'hashtag_ranking': hashtag_ranking,
            
            # Risk
            'risk_indicators': risk_indicators,
            
            # Metadata
            'weighting_method': 'volume_based'
        }
    
    def _determine_market_label(self, signal_score: float, confidence: float) -> str:
        """Determine overall market label"""
        if confidence < self.min_confidence:
            return 'HOLD'
        elif signal_score >= 0.5:
            return 'STRONG_BULLISH'
        elif signal_score > 0.2:
            return 'BULLISH'
        elif signal_score <= -0.5:
            return 'STRONG_BEARISH'
        elif signal_score < -0.2:
            return 'BEARISH'
        else:
            return 'NEUTRAL'
    
    def _calculate_market_consensus(self, signals: np.ndarray, weights: np.ndarray) -> str:
        """Calculate market consensus with weighting"""
        # Weighted bullish/bearish counts
        bullish_weight = np.sum(weights[signals > 0.2])
        bearish_weight = np.sum(weights[signals < -0.2])
        
        if bullish_weight > 0.7:
            return 'STRONG_BULLISH'
        elif bullish_weight > 0.5:
            return 'BULLISH'
        elif bearish_weight > 0.7:
            return 'STRONG_BEARISH'
        elif bearish_weight > 0.5:
            return 'BEARISH'
        else:
            return 'MIXED'
    
    def _aggregate_sentiment_distribution(
        self,
        hashtag_analyses: Dict,
        volumes: np.ndarray
    ) -> Dict:
        """Aggregate sentiment distribution across all hashtags"""
        total_bullish = 0
        total_bearish = 0
        total_neutral = 0
        total_tweets = volumes.sum()
        
        for analysis in hashtag_analyses.values():
            dist = analysis.get('sentiment_distribution', {})
            total_bullish += dist.get('bullish_count', 0)
            total_bearish += dist.get('bearish_count', 0)
            total_neutral += dist.get('neutral_count', 0)
        
        return {
            'bullish_count': int(total_bullish),
            'bearish_count': int(total_bearish),
            'neutral_count': int(total_neutral),
            'bullish_ratio': float(total_bullish / total_tweets) if total_tweets > 0 else 0.0,
            'bearish_ratio': float(total_bearish / total_tweets) if total_tweets > 0 else 0.0,
            'neutral_ratio': float(total_neutral / total_tweets) if total_tweets > 0 else 0.0
        }
    
    def _aggregate_signal_distribution(
        self,
        hashtag_analyses: Dict,
        volumes: np.ndarray
    ) -> Dict:
        """Aggregate signal label distribution"""
        signal_counts = {}
        total_tweets = volumes.sum()
        
        for analysis in hashtag_analyses.values():
            dist = analysis.get('signal_distribution', {})
            for label, info in dist.items():
                if label not in signal_counts:
                    signal_counts[label] = 0
                signal_counts[label] += info.get('count', 0)
        
        return {
            label: {
                'count': count,
                'ratio': float(count / total_tweets) if total_tweets > 0 else 0.0
            }
            for label, count in signal_counts.items()
        }
    
    def _rank_hashtags(self, hashtag_analyses: Dict) -> List[Dict]:
        """Rank hashtags by signal strength and confidence"""
        rankings = []
        
        for hashtag, analysis in hashtag_analyses.items():
            rankings.append({
                'hashtag': hashtag,
                'signal_label': analysis['signal_label'],
                'signal_score': analysis['signal_score'],
                'confidence': analysis['confidence'],
                'tweet_count': analysis['tweet_count'],
                'rank_score': analysis['signal_score'] * analysis['confidence']  # Combined score for ranking
            })
        
        # Sort by rank_score (descending)
        rankings.sort(key=lambda x: x['rank_score'], reverse=True)
        
        # Add rank position
        for i, item in enumerate(rankings, 1):
            item['rank'] = i
        
        return rankings
    
    def _calculate_risk_indicators(
        self,
        hashtag_analyses: Dict,
        signal_variance: float,
        confidence: float,
        total_tweets: int
    ) -> Dict:
        """Calculate risk indicators for the market signal"""
        # Count low confidence tweets
        low_confidence_count = 0
        ignore_count = 0
        
        for analysis in hashtag_analyses.values():
            dist = analysis.get('signal_distribution', {})
            ignore_count += dist.get('IGNORE', {}).get('count', 0)
            
            # Estimate low confidence as those below threshold
            valid_count = analysis.get('valid_tweet_count', 0)
            total_count = analysis.get('tweet_count', 0)
            low_confidence_count += (total_count - valid_count)
        
        return {
            'signal_volatility': float(signal_variance),
            'volatility_level': self._classify_volatility(signal_variance),
            'low_confidence_tweets': int(low_confidence_count),
            'low_confidence_ratio': float(low_confidence_count / total_tweets) if total_tweets > 0 else 0.0,
            'ignored_tweets': int(ignore_count),
            'overall_confidence_level': self._classify_confidence(confidence)
        }
    
    def _classify_volatility(self, variance: float) -> str:
        """Classify signal volatility"""
        if variance < 0.2:
            return 'LOW'
        elif variance < 0.4:
            return 'MODERATE'
        else:
            return 'HIGH'
    
    def _classify_confidence(self, confidence: float) -> str:
        """Classify confidence level"""
        if confidence >= 0.7:
            return 'HIGH'
        elif confidence >= 0.5:
            return 'MODERATE'
        else:
            return 'LOW'
    
    def _empty_market_signal(self) -> Dict:
        """Return empty market signal when no data available"""
        return {
            'signal_label': 'HOLD',
            'signal_score': 0.0,
            'confidence': 0.0,
            'consensus': 'NONE',
            'total_tweets': 0,
            'hashtag_count': 0,
            'signal_variance': 0.0,
            'sentiment_distribution': {
                'bullish_count': 0,
                'bearish_count': 0,
                'neutral_count': 0,
                'bullish_ratio': 0.0,
                'bearish_ratio': 0.0,
                'neutral_ratio': 0.0
            },
            'signal_distribution': {},
            'hashtag_ranking': [],
            'risk_indicators': {
                'signal_volatility': 0.0,
                'volatility_level': 'NONE',
                'low_confidence_tweets': 0,
                'low_confidence_ratio': 0.0,
                'ignored_tweets': 0,
                'overall_confidence_level': 'NONE'
            },
            'weighting_method': 'volume_based'
        }
