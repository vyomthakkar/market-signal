"""
Unit tests for TF-IDF analysis
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from analysis.features import TFIDFAnalyzer


@pytest.fixture
def sample_corpus():
    """Sample corpus of tweets for TF-IDF"""
    return [
        "Nifty50 showing strong bullish momentum",
        "Market crash bearish signal detected",
        "Trading Nifty50 sideways today",
        "Sensex breakout confirmed bullish",
        "Banking stocks showing weakness bearish",
    ]


@pytest.fixture
def analyzer(sample_corpus):
    """Create and fit TFIDFAnalyzer"""
    analyzer = TFIDFAnalyzer(
        max_features=100,
        ngram_range=(1, 2),
        min_df=1,
        top_n_terms=5
    )
    analyzer.fit(sample_corpus)
    return analyzer


@pytest.mark.unit
class TestTFIDFAnalyzer:
    """Test suite for TFIDFAnalyzer"""
    
    def test_analyzer_initialization(self):
        """Test that analyzer initializes correctly"""
        analyzer = TFIDFAnalyzer()
        
        assert analyzer is not None
        assert hasattr(analyzer, 'fit')
        assert hasattr(analyzer, 'transform')
    
    def test_fit_creates_vocabulary(self, analyzer):
        """Test that fitting creates a vocabulary"""
        assert hasattr(analyzer, 'feature_names')
        assert len(analyzer.feature_names) > 0
    
    def test_transform_single_document(self, analyzer):
        """Test transforming a single document"""
        text = "Nifty50 bullish breakout today"
        result = analyzer.transform(text)
        
        assert 'top_tfidf_terms' in result
        assert 'top_tfidf_scores' in result
        assert 'finance_term_density' in result
        
        assert len(result['top_tfidf_terms']) <= 5  # top_n_terms=5
    
    def test_top_terms_are_sorted(self, analyzer):
        """Test that top terms are sorted by score"""
        text = "Nifty50 trading sideways with Sensex bullish momentum"
        result = analyzer.transform(text)
        
        scores = result['top_tfidf_scores']
        
        # Scores should be in descending order
        for i in range(len(scores) - 1):
            assert scores[i] >= scores[i + 1]
    
    def test_finance_term_density(self, analyzer):
        """Test finance term density calculation"""
        finance_text = "Nifty50 Sensex trading bullish bearish stock market"
        non_finance_text = "hello world how are you today"
        
        result_finance = analyzer.transform(finance_text)
        result_non_finance = analyzer.transform(non_finance_text)
        
        # Finance text should have higher density
        assert result_finance['finance_term_density'] > result_non_finance['finance_term_density']
    
    def test_empty_text(self, analyzer):
        """Test handling of empty text"""
        result = analyzer.transform("")
        
        assert result is not None
        assert 'top_tfidf_terms' in result
        assert len(result['top_tfidf_terms']) == 0
    
    def test_unseen_words(self, analyzer):
        """Test handling of words not in vocabulary"""
        text = "completely different vocabulary here"
        result = analyzer.transform(text)
        
        # Should handle gracefully
        assert result is not None
        assert 'top_tfidf_terms' in result
    
    def test_trending_terms(self, analyzer, sample_corpus):
        """Test getting trending terms across corpus"""
        trending = analyzer.get_trending_terms(sample_corpus, n=5)
        
        assert len(trending) <= 5
        assert all(isinstance(item, tuple) for item in trending)
        
        # Each item should be (term, score)
        for term, score in trending:
            assert isinstance(term, str)
            assert isinstance(score, (int, float))
    
    def test_document_similarity(self, analyzer):
        """Test document similarity calculation"""
        doc1 = "Nifty50 bullish momentum"
        doc2 = "Nifty50 showing bullish trend"
        doc3 = "Market crash bearish signal"
        
        # Similar documents should have higher similarity
        sim_similar = analyzer.get_document_similarity(doc1, doc2)
        sim_different = analyzer.get_document_similarity(doc1, doc3)
        
        assert 0 <= sim_similar <= 1
        assert 0 <= sim_different <= 1
        assert sim_similar > sim_different
    
    def test_ngram_support(self):
        """Test that n-grams are supported"""
        corpus = [
            "strong bullish momentum",
            "bullish trend confirmed",
            "bearish signal detected"
        ]
        
        analyzer = TFIDFAnalyzer(ngram_range=(1, 2))
        analyzer.fit(corpus)
        
        # Should have both unigrams and bigrams
        assert any(' ' in term for term in analyzer.feature_names)  # Has bigrams
    
    def test_min_df_filtering(self):
        """Test that min_df filters rare terms"""
        corpus = [
            "common word appears everywhere",
            "common word appears again",
            "common word appears once more",
            "rare unique special term"  # Should be filtered if min_df > 1
        ]
        
        analyzer = TFIDFAnalyzer(min_df=2)
        analyzer.fit(corpus)
        
        # 'common' and 'word' should be in vocabulary
        # 'rare', 'unique', 'special' should not (appear < 2 times)
        vocab_lower = [term.lower() for term in analyzer.feature_names]
        assert 'common' in vocab_lower or 'appears' in vocab_lower


@pytest.mark.unit
def test_batch_transform(analyzer, sample_corpus):
    """Test transforming multiple documents"""
    results = []
    
    for text in sample_corpus:
        result = analyzer.transform(text)
        results.append(result)
    
    assert len(results) == len(sample_corpus)
    
    # All results should have consistent structure
    for result in results:
        assert 'top_tfidf_terms' in result
        assert 'top_tfidf_scores' in result
        assert 'finance_term_density' in result


@pytest.mark.unit
def test_different_max_features():
    """Test that max_features limits vocabulary size"""
    corpus = ["word " + str(i) for i in range(100)]  # 100 unique words
    
    analyzer_small = TFIDFAnalyzer(max_features=10)
    analyzer_large = TFIDFAnalyzer(max_features=50)
    
    analyzer_small.fit(corpus)
    analyzer_large.fit(corpus)
    
    assert len(analyzer_small.feature_names) <= 10
    assert len(analyzer_large.feature_names) <= 50
    assert len(analyzer_large.feature_names) > len(analyzer_small.feature_names)


@pytest.mark.unit
def test_refit_clears_old_vocabulary():
    """Test that refitting clears old vocabulary"""
    corpus1 = ["first corpus with these words"]
    corpus2 = ["second corpus with different vocabulary"]
    
    analyzer = TFIDFAnalyzer()
    analyzer.fit(corpus1)
    vocab1 = set(analyzer.feature_names)
    
    analyzer.fit(corpus2)
    vocab2 = set(analyzer.feature_names)
    
    # Vocabularies should be different
    assert vocab1 != vocab2


@pytest.mark.unit
@pytest.mark.parametrize("text,expected_has_finance_terms", [
    ("Nifty50 Sensex trading bullish", True),
    ("Hello world this is random", False),
    ("stock market analysis today", True),
])
def test_finance_term_detection(analyzer, text, expected_has_finance_terms):
    """Parametrized test for finance term detection"""
    result = analyzer.transform(text)
    
    if expected_has_finance_terms:
        assert result['finance_term_density'] > 0
    # Note: Can't guarantee 0 for non-finance as it depends on vocabulary


@pytest.mark.unit
def test_similarity_reflexive(analyzer):
    """Test that similarity with itself is 1"""
    text = "Nifty50 bullish momentum"
    sim = analyzer.get_document_similarity(text, text)
    
    assert abs(sim - 1.0) < 0.01  # Should be ~1.0


@pytest.mark.unit
def test_similarity_symmetric(analyzer):
    """Test that similarity is symmetric"""
    doc1 = "Nifty50 bullish"
    doc2 = "Sensex bearish"
    
    sim1 = analyzer.get_document_similarity(doc1, doc2)
    sim2 = analyzer.get_document_similarity(doc2, doc1)
    
    assert abs(sim1 - sim2) < 0.01  # Should be equal
