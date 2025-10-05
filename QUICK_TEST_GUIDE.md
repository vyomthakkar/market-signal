# Quick Test Guide 🚀

Fast reference for running tests in the refactored test suite.

## Setup (First Time)

```bash
# Install test dependencies
pip install -r requirements-dev.txt
```

## Run Tests

### Quick Commands

```bash
# Run all tests
pytest

# Run unit tests only (fast!)
pytest tests/unit

# Run integration tests
pytest tests/integration

# Run specific test file
pytest tests/unit/test_sentiment_analyzer.py

# Run with verbose output
pytest -v

# Run and show coverage
pytest --cov=src --cov-report=term-missing
```

### Using the Test Runner Script

```bash
# Make executable (first time)
chmod +x run_tests.sh

# Run all tests
./run_tests.sh all

# Run unit tests
./run_tests.sh unit

# Run with coverage report
./run_tests.sh coverage

# Run fast tests only
./run_tests.sh fast
```

## Test Organization

```
tests/
├── unit/              ← Fast isolated tests (80+ tests)
├── integration/       ← Tests with dependencies (35+ tests)
├── performance/       ← Benchmarks
├── scripts/
│   ├── debug/        ← Debug utilities (NOT tests)
│   └── tools/        ← Analysis tools (NOT tests)
└── conftest.py       ← Shared fixtures
```

## Common Test Commands

```bash
# Run only tests matching a pattern
pytest -k "sentiment"

# Run tests marked as unit
pytest -m unit

# Stop at first failure
pytest -x

# Show local variables on failure
pytest -l

# Run last failed tests
pytest --lf

# Run in parallel (faster!)
pytest -n auto
```

## Writing New Tests

### Example Unit Test

```python
import pytest
from src.analysis.features import SentimentAnalyzer

@pytest.fixture
def analyzer():
    return SentimentAnalyzer()

@pytest.mark.unit
def test_bullish_sentiment(analyzer):
    result = analyzer.analyze("Bullish breakout! 🚀")
    assert result['combined_sentiment_score'] > 0
    assert result['bullish_keyword_count'] >= 1
```

### Use Shared Fixtures

```python
def test_with_sample_data(sample_tweets):
    # sample_tweets is from conftest.py
    assert len(sample_tweets) > 0
```

## Utility Scripts (Not Tests)

```bash
# Analyze incremental data
python tests/scripts/tools/analyze_incremental_data.py

# View tweets interactively
python tests/scripts/tools/view_tweets.py --count 20

# Check scraper output
python tests/scripts/tools/check_output.py

# Debug engagement metrics
python tests/scripts/debug/debug_engagement_simple.py
```

## Test Markers

Filter tests by marker:

```bash
pytest -m unit          # Unit tests
pytest -m integration   # Integration tests
pytest -m slow          # Slow tests
pytest -m performance   # Benchmarks
pytest -m "not slow"    # Skip slow tests
```

## Coverage

```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Troubleshooting

### Import Errors
```bash
# Ensure you're in project root
cd /path/to/market-signal
pytest
```

### Can't Find pytest
```bash
# Install test dependencies
pip install -r requirements-dev.txt
```

### Tests Fail
```bash
# Run with more detail
pytest -vv

# Show print statements
pytest -s

# Show local variables on failure
pytest -l --tb=long
```

## Quick Reference

| Command | Description |
|---------|-------------|
| `pytest` | Run all tests |
| `pytest tests/unit` | Run unit tests |
| `pytest -v` | Verbose output |
| `pytest -k "sentiment"` | Run tests matching pattern |
| `pytest -m unit` | Run tests with marker |
| `pytest -x` | Stop at first failure |
| `pytest --lf` | Run last failed |
| `pytest --cov=src` | Run with coverage |
| `./run_tests.sh unit` | Use convenience script |

## More Help

- Full documentation: `tests/README.md`
- Refactoring details: `docs/TEST_REFACTORING_SUMMARY.md`
- Pytest docs: https://docs.pytest.org/

---

**Happy Testing!** 🎉
