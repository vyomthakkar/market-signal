# Setup Instructions

## Prerequisites

Before running the analysis pipeline, ensure you have:

### 1. Python Environment

The project requires Python 3.8 or higher.

```bash
python3 --version  # Should be 3.8+
```

### 2. Install Dependencies

Install all required packages:

```bash
# From the project root directory
pip install -r requirements.txt
```

Or install individually:

```bash
pip install pandas pyarrow transformers torch scikit-learn matplotlib seaborn plotly
```

### 3. Verify Installation

Check that key packages are installed:

```bash
python3 -c "import pandas, torch, transformers, sklearn; print('✓ All dependencies installed')"
```

## Quick Test

### Test 1: Verify Data Exists

```bash
# Check if you have collected data
ls -lh data_store/tweets_incremental.parquet

# If file exists, check metadata
cat data_store/tweets_incremental.meta.json
```

If no data exists, run:

```bash
python3 run/1_collect_data.py --hashtags nifty50 --count 100
```

### Test 2: Run Analysis

```bash
# Run the main analysis script
python3 run/2_analyze_signals.py

# Expected output:
#   - Console summary of market signals
#   - JSON report saved to output/signal_report.json
#   - Analyzed tweets saved to output/analyzed_tweets.parquet
```

### Test 3: Generate Visualizations

```bash
python3 run/3_visualize_results.py

# Expected output:
#   - PNG charts in output/visualizations/
#   - Interactive HTML dashboard
```

## Troubleshooting Setup

### Issue: ModuleNotFoundError

**Error**: `ModuleNotFoundError: No module named 'pandas'`

**Solution**:
```bash
pip install pandas pyarrow
```

### Issue: Torch/Transformers Installation

**Error**: Issues installing torch or transformers

**Solution**:
```bash
# For CPU-only (smaller download)
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install transformers

# Or use the full version (with CUDA support)
pip install torch transformers
```

### Issue: Memory Error

**Error**: `MemoryError` or system slowdown during analysis

**Solution**: The sentiment model requires ~500MB-1GB RAM. For the first run, it will download the model (~500MB).

### Issue: Data File Not Found

**Error**: `FileNotFoundError: data_store/tweets_incremental.parquet`

**Solution**: You need to collect data first:
```bash
python3 run/1_collect_data.py
```

## First Run Expectations

### Initial Setup Time

- **First run**: ~5-10 minutes (downloads ML model ~500MB)
- **Subsequent runs**: ~1-2 minutes (model cached)

### Download Progress

On first run, you'll see:
```
Loading twitter-roberta-base-sentiment-latest model...
First run will download ~500MB (one-time)
Downloading: 100%|████████████████████| 501M/501M [02:15<00:00, 3.70MB/s]
✓ Model loaded on CPU
```

### Disk Space

Ensure you have:
- **500MB**: For ML model cache (`~/.cache/huggingface/`)
- **50-100MB**: For output files per analysis run

## Environment Variables (Optional)

Create a `.env` file for custom settings:

```bash
# Data paths
DATA_STORE_DIR=data_store
OUTPUT_DIR=output

# Analysis settings
MIN_TWEETS_PER_HASHTAG=20
MIN_CONFIDENCE_THRESHOLD=0.3

# Logging
LOG_LEVEL=INFO
```

## Recommended Workflow

### For First-Time Users

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Collect sample data**
   ```bash
   python3 run/1_collect_data.py --hashtags nifty50 --count 100
   ```

3. **Run analysis**
   ```bash
   python3 run/2_analyze_signals.py
   ```

4. **Review results**
   ```bash
   cat output/signal_report.json
   ```

### For Regular Use

Use the master script:

```bash
# Run complete pipeline (analysis + viz)
python3 run/run_all.py

# With new data collection
python3 run/run_all.py --collect --hashtags nifty50 sensex banknifty
```

## Next Steps

After successful setup:
- Read `run/README.md` for detailed usage
- Check `output/signal_report.json` for market signals
- Open `output/visualizations/interactive_dashboard.html` in browser

## Getting Help

If you encounter issues:

1. **Check logs**: Run with `--verbose` flag
   ```bash
   python3 run/2_analyze_signals.py --verbose
   ```

2. **Verify Python version**
   ```bash
   python3 --version  # Must be 3.8+
   ```

3. **Check disk space**
   ```bash
   df -h .
   ```

4. **Test dependencies individually**
   ```bash
   python3 -c "import pandas; print('pandas OK')"
   python3 -c "import torch; print('torch OK')"
   python3 -c "import transformers; print('transformers OK')"
   ```
