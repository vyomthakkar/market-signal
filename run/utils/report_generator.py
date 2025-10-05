"""
Report Generator - JSON output formatting

Formats analysis results into structured JSON reports.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generates JSON reports from analysis results
    """
    
    def __init__(self, output_dir: str = 'output'):
        """
        Initialize report generator
        
        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_report(
        self,
        overall_market: Dict,
        hashtag_analyses: Dict,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Generate comprehensive JSON report
        
        Args:
            overall_market: Overall market signal from MarketAggregator
            hashtag_analyses: Per-hashtag analyses from HashtagAnalyzer
            metadata: Optional metadata about the analysis
            
        Returns:
            Complete report dict
        """
        timestamp = datetime.now().isoformat()
        
        report = {
            'metadata': {
                'generated_at': timestamp,
                'version': '1.0.0',
                **(metadata or {})
            },
            'overall_market': overall_market,
            'hashtags': hashtag_analyses,
            'summary': self._generate_summary(overall_market, hashtag_analyses)
        }
        
        return report
    
    def save_report(
        self,
        report: Dict,
        filename: str = 'signal_report.json'
    ) -> Path:
        """
        Save report to JSON file
        
        Args:
            report: Report dict to save
            filename: Output filename
            
        Returns:
            Path to saved file
        """
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Report saved to {output_path}")
        return output_path
    
    def _generate_summary(
        self,
        overall_market: Dict,
        hashtag_analyses: Dict
    ) -> Dict:
        """Generate executive summary"""
        # Find strongest signals
        strongest_bullish = None
        strongest_bearish = None
        
        for hashtag, analysis in hashtag_analyses.items():
            score = analysis['signal_score']
            
            if score > 0.2:  # Bullish
                if strongest_bullish is None or score > strongest_bullish['score']:
                    strongest_bullish = {'hashtag': hashtag, 'score': score}
            elif score < -0.2:  # Bearish
                if strongest_bearish is None or score < strongest_bearish['score']:
                    strongest_bearish = {'hashtag': hashtag, 'score': score}
        
        # Market direction
        signal_score = overall_market.get('signal_score', 0)
        if signal_score > 0.2:
            market_direction = 'BULLISH'
        elif signal_score < -0.2:
            market_direction = 'BEARISH'
        else:
            market_direction = 'NEUTRAL'
        
        return {
            'market_direction': market_direction,
            'confidence_level': overall_market.get('risk_indicators', {}).get('overall_confidence_level', 'UNKNOWN'),
            'strongest_bullish_hashtag': strongest_bullish,
            'strongest_bearish_hashtag': strongest_bearish,
            'total_hashtags_analyzed': len(hashtag_analyses),
            'recommendation': self._generate_recommendation(overall_market)
        }
    
    def _generate_recommendation(self, overall_market: Dict) -> str:
        """Generate trading recommendation"""
        label = overall_market.get('signal_label', 'HOLD')
        confidence = overall_market.get('confidence', 0)
        volatility = overall_market.get('risk_indicators', {}).get('volatility_level', 'UNKNOWN')
        
        recommendations = {
            'STRONG_BULLISH': 'Strong buy signal detected. Consider long positions.',
            'BULLISH': 'Moderate buy signal. Enter with caution.',
            'NEUTRAL': 'Market shows no clear direction. Hold positions.',
            'BEARISH': 'Moderate sell signal. Consider reducing positions.',
            'STRONG_BEARISH': 'Strong sell signal detected. Consider short positions or exit.',
            'HOLD': 'Insufficient confidence for trading action. Monitor the market.'
        }
        
        base_rec = recommendations.get(label, 'No recommendation available.')
        
        # Add confidence and volatility warnings
        warnings = []
        if confidence < 0.5:
            warnings.append('Low confidence - signal reliability is questionable.')
        if volatility == 'HIGH':
            warnings.append('High volatility detected - expect significant disagreement in signals.')
        
        if warnings:
            return f"{base_rec} ⚠️ {' '.join(warnings)}"
        
        return base_rec
    
    def print_console_summary(self, report: Dict):
        """
        Print a formatted console summary of the report
        
        Args:
            report: Complete report dict
        """
        overall = report['overall_market']
        summary = report['summary']
        
        print("\n" + "="*80)
        print("🌐 OVERALL MARKET SENTIMENT")
        print("="*80)
        
        print(f"\n📊 Market Signal: {overall['signal_label']} {self._get_signal_emoji(overall['signal_label'])}")
        print(f"📈 Signal Score: {overall['signal_score']:+.3f}")
        print(f"⭐ Confidence: {overall['confidence']*100:.1f}%")
        print(f"🎯 Consensus: {overall['consensus']}")
        print(f"📝 Total Tweets: {overall['total_tweets']:,}")
        print(f"#️⃣  Hashtags Analyzed: {overall['hashtag_count']}")
        
        print(f"\n💡 Recommendation:")
        print(f"   {summary['recommendation']}")
        
        # Sentiment distribution
        sent_dist = overall['sentiment_distribution']
        print(f"\n📊 Sentiment Distribution:")
        print(f"   Bullish: {sent_dist['bullish_count']:,} ({sent_dist['bullish_ratio']*100:.1f}%)")
        print(f"   Bearish: {sent_dist['bearish_count']:,} ({sent_dist['bearish_ratio']*100:.1f}%)")
        print(f"   Neutral: {sent_dist['neutral_count']:,} ({sent_dist['neutral_ratio']*100:.1f}%)")
        
        # Hashtag ranking
        print(f"\n🏆 Hashtag Performance Ranking:")
        for item in overall['hashtag_ranking'][:5]:  # Top 5
            emoji = self._get_signal_emoji(item['signal_label'])
            print(f"   {item['rank']}. #{item['hashtag']}: {item['signal_label']} "
                  f"({item['signal_score']:+.2f}, {item['confidence']*100:.1f}% conf) {emoji}")
        
        # Risk indicators
        risk = overall['risk_indicators']
        print(f"\n⚠️  Risk Indicators:")
        print(f"   Signal Volatility: {risk['volatility_level']} ({risk['signal_volatility']:.2f})")
        print(f"   Confidence Level: {risk['overall_confidence_level']}")
        print(f"   Low Confidence Tweets: {risk['low_confidence_tweets']:,} ({risk['low_confidence_ratio']*100:.1f}%)")
        
        print("\n" + "="*80)
        print("✅ Analysis Complete!")
        print("="*80)
        print(f"\n📄 Full report saved to: {self.output_dir / 'signal_report.json'}")
        print()
    
    def _get_signal_emoji(self, label: str) -> str:
        """Get emoji for signal label"""
        emojis = {
            'STRONG_BUY': '🚀',
            'STRONG_BULLISH': '🚀',
            'BUY': '📈',
            'BULLISH': '📈',
            'HOLD': '⏸️',
            'NEUTRAL': '➖',
            'SELL': '📉',
            'BEARISH': '📉',
            'STRONG_SELL': '⚠️',
            'STRONG_BEARISH': '⚠️',
            'IGNORE': '🚫'
        }
        return emojis.get(label, '❓')
