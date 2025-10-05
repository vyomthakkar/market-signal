#!/bin/bash
# Test runner script for market-signal project

set -e

echo "=================================="
echo "  Market Signal Test Suite"
echo "=================================="
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest not found. Installing..."
    pip install pytest pytest-cov
fi

# Parse arguments
case "${1:-all}" in
    all)
        echo "Running all tests..."
        pytest tests/ -v
        ;;
    unit)
        echo "Running unit tests only..."
        pytest tests/unit -m unit -v
        ;;
    integration)
        echo "Running integration tests..."
        pytest tests/integration -m integration -v
        ;;
    performance)
        echo "Running performance benchmarks..."
        pytest tests/performance -m performance -v
        ;;
    fast)
        echo "Running fast tests only (excluding slow tests)..."
        pytest tests/unit -m "unit and not slow" -v
        ;;
    coverage)
        echo "Running tests with coverage report..."
        pytest tests/ --cov=src --cov-report=html --cov-report=term-missing
        echo ""
        echo "✅ Coverage report generated in htmlcov/index.html"
        ;;
    watch)
        echo "Running tests in watch mode..."
        pytest tests/ -v --looponfail
        ;;
    *)
        echo "Usage: ./run_tests.sh [all|unit|integration|performance|fast|coverage|watch]"
        echo ""
        echo "Options:"
        echo "  all          - Run all tests (default)"
        echo "  unit         - Run unit tests only"
        echo "  integration  - Run integration tests"
        echo "  performance  - Run performance benchmarks"
        echo "  fast         - Run fast tests only"
        echo "  coverage     - Run tests with coverage report"
        echo "  watch        - Run tests in watch mode"
        exit 1
        ;;
esac

echo ""
echo "✅ Test run complete!"
