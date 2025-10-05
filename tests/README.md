# Test Suite Documentation

This directory contains the refactored test suite for the market-signal project, following pytest best practices.

## Directory Structure

```
tests/
├── unit/                          # Unit tests (fast, isolated)
│   ├── test_sentiment_analyzer.py
│   ├── test_engagement_metrics.py
│   ├── test_data_processing.py
│   ├── test_tfidf_analyzer.py
│   └── test_rate_limiter.py
│
├── integration/                   # Integration tests
│   ├── test_analysis_pipeline.py
│   ├── test_storage.py
│   └── test_visualizations.py
│
├── performance/                   # Performance benchmarks
│   └── test_parallel_processing.py
│
├── fixtures/                      # Test fixtures
│   └── __init__.py
│
├── scripts/                       # Utility scripts (NOT tests)
│   ├── debug/                     # Debug scripts
│   │   ├── debug_engagement_simple.py
│   │   ├── debug_engagement_metrics.py
│   │   └── ...
│   ├── tools/                     # Data analysis tools
│   │   ├── analyze_incremental_data.py
│   │   ├── check_output.py
│   │   ├── view_tweets.py
│   │   └── explore_data.py
│   └── legacy/                    # Old test scripts (for reference)
│
├── conftest.py                    # Shared pytest fixtures
└── README.md                      # This file
```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test Categories
```bash
# Unit tests only (fast)
pytest tests/unit -m unit

# Integration tests
pytest tests/integration -m integration

# Performance benchmarks
pytest tests/performance -m performance

# Exclude slow tests
pytest -m "not slow"
```

### Run Specific Test Files
```bash
# Test sentiment analyzer
pytest tests/unit/test_sentiment_analyzer.py

# Test with verbose output
pytest tests/unit/test_sentiment_analyzer.py -v

# Test specific function
pytest tests/unit/test_sentiment_analyzer.py::test_bullish_sentiment
```

### Run with Coverage
```bash
# Generate coverage report
pytest --cov=src --cov-report=html

# View coverage in browser
open htmlcov/index.html
```

## Test Markers

Tests are marked with pytest markers for categorization:

- `@pytest.mark.unit` - Fast unit tests
- `@pytest.mark.integration` - Integration tests with dependencies
- `@pytest.mark.slow` - Slow tests (>1s)
- `@pytest.mark.performance` - Performance benchmarks
- `@pytest.mark.requires_data` - Tests requiring actual data files

## Writing New Tests

### Unit Test Template

```python
import pytest
from src.module import MyClass

@pytest.fixture
def my_instance():
    return MyClass()

@pytest.mark.unit
def test_my_feature(my_instance):
    result = my_instance.my_method()
    assert result is not None
    assert result > 0
```

### Using Shared Fixtures

The `conftest.py` file provides shared fixtures:

```python
def test_with_sample_data(sample_tweets):
    # sample_tweets fixture is automatically available
    assert len(sample_tweets) > 0
```

Available shared fixtures:
- `sample_tweets` - List of sample tweet dictionaries
- `sample_dataframe` - DataFrame with sample tweets
- `sample_bullish_tweet` - Single bullish tweet
- `sample_bearish_tweet` - Single bearish tweet
- `temp_output_dir` - Temporary directory for test outputs
- `temp_parquet_file` - Temporary parquet file with sample data
- `temp_json_file` - Temporary JSON file with sample data

### Parametrized Tests

Use `@pytest.mark.parametrize` for testing multiple cases:

```python
@pytest.mark.parametrize("text,expected_sentiment", [
    ("Bullish breakout! 🚀", "positive"),
    ("Market crash! 📉", "negative"),
    ("Trading sideways", "neutral"),
])
def test_sentiment_cases(text, expected_sentiment):
    result = analyze_sentiment(text)
    assert result['label'] == expected_sentiment
```

## Utility Scripts

Scripts in `tests/scripts/` are NOT tests but utility tools:

### Debug Scripts (`tests/scripts/debug/`)
Used for debugging specific issues:
```bash
python tests/scripts/debug/debug_engagement_simple.py
```

### Analysis Tools (`tests/scripts/tools/`)
Used for data analysis and exploration:
```bash
# Analyze incremental data
python tests/scripts/tools/analyze_incremental_data.py

# View tweets interactively
python tests/scripts/tools/view_tweets.py --count 20

# Check scraper output
python tests/scripts/tools/check_output.py
```

## Test Guidelines

### Unit Tests
- **Fast**: Should run in milliseconds
- **Isolated**: No external dependencies (files, network, DB)
- **Deterministic**: Same input = same output
- **Focused**: Test one thing at a time

### Integration Tests
- Test interaction between components
- May use temporary files/directories
- Should clean up after themselves
- Can be slower than unit tests

### What to Test
1. **Normal cases** - Expected inputs and outputs
2. **Edge cases** - Empty data, zero values, boundaries
3. **Error cases** - Invalid inputs, missing fields
4. **Data preservation** - Round-trip consistency

### What NOT to Test
- External libraries (they have their own tests)
- Simple getters/setters without logic
- Trivial one-liners

## Continuous Integration

Tests are automatically run on:
- Every commit (if CI is configured)
- Pull requests
- Before deployment

## Troubleshooting

### Import Errors
If you get import errors, ensure you're in the project root:
```bash
cd /path/to/market-signal
pytest
```

### Module Not Found
The `conftest.py` adds `src/` to the path. If tests can't find modules:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
```

### Fixture Not Found
Fixtures from `conftest.py` are automatically discovered. If not working:
1. Ensure `conftest.py` is in `tests/` directory
2. Check fixture name spelling
3. Run with `-v` to see fixture resolution

### Tests Failing After Refactor
If tests fail after the refactor:
1. Check that old test scripts are in `scripts/legacy/`
2. Update imports if module structure changed
3. Review fixture definitions in `conftest.py`

## Migration from Old Tests

Old test files have been moved to `tests/scripts/legacy/`. They were:
- **Demo scripts** with print statements instead of assertions
- **Not using pytest** fixtures or features
- **Duplicated** across multiple files

New tests:
- ✅ Use proper pytest assertions
- ✅ Use shared fixtures
- ✅ Are organized by type (unit/integration)
- ✅ Have clear documentation
- ✅ Run faster and more reliably

## Best Practices

1. **Name tests clearly**: `test_bullish_sentiment_detection()` not `test1()`
2. **One assertion concept per test**: Test one thing at a time
3. **Use fixtures**: Don't repeat setup code
4. **Mark appropriately**: Add `@pytest.mark.unit` etc.
5. **Document why**: Add docstrings explaining what's being tested
6. **Keep tests fast**: Mock expensive operations
7. **Clean up**: Use tmp_path for temporary files

## Getting Help

- Pytest documentation: https://docs.pytest.org/
- Project-specific questions: Check the main README.md
- Test failures: Run with `-vv` for detailed output

---

**Last Updated**: 2025-10-05
**Refactored By**: Automated test refactoring process
