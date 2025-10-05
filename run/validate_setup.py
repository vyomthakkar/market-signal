#!/usr/bin/env python3
"""
Setup Validation Script

Checks if environment is properly configured for running the analysis pipeline.
"""

import sys
from pathlib import Path

def check_python_version():
    """Check Python version"""
    print("Checking Python version...", end=" ")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} (need 3.8+)")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    print("\nChecking dependencies...")
    
    required = {
        'pandas': 'Data manipulation',
        'pyarrow': 'Parquet file support',
        'numpy': 'Numerical computing',
        'transformers': 'Sentiment analysis models',
        'torch': 'PyTorch (ML backend)',
        'sklearn': 'TF-IDF and ML utilities',
        'matplotlib': 'Visualization',
        'plotly': 'Interactive charts'
    }
    
    missing = []
    for package, description in required.items():
        try:
            __import__(package)
            print(f"  ✓ {package:15} ({description})")
        except ImportError:
            print(f"  ✗ {package:15} ({description}) - MISSING")
            missing.append(package)
    
    return len(missing) == 0, missing

def check_data_files():
    """Check if data files exist"""
    print("\nChecking data files...")
    
    data_file = Path('data_store/tweets_incremental.parquet')
    meta_file = Path('data_store/tweets_incremental.meta.json')
    
    has_data = False
    
    if data_file.exists():
        size_mb = data_file.stat().st_size / 1024 / 1024
        print(f"  ✓ Data file exists: {data_file} ({size_mb:.1f} MB)")
        has_data = True
    else:
        print(f"  ✗ Data file not found: {data_file}")
    
    if meta_file.exists():
        print(f"  ✓ Metadata file exists: {meta_file}")
    else:
        print(f"  ℹ Metadata file not found: {meta_file} (optional)")
    
    return has_data

def check_disk_space():
    """Check available disk space"""
    print("\nChecking disk space...", end=" ")
    
    import shutil
    try:
        usage = shutil.disk_usage(Path.cwd())
        free_gb = usage.free / 1024 / 1024 / 1024
        
        if free_gb < 1:
            print(f"⚠️  Low space: {free_gb:.1f} GB (need 1GB+ for model download)")
            return False
        else:
            print(f"✓ {free_gb:.1f} GB available")
            return True
    except:
        print("? Unable to check")
        return True

def check_output_directory():
    """Check/create output directory"""
    print("\nChecking output directory...", end=" ")
    
    output_dir = Path('output')
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created {output_dir}/")
    else:
        print(f"✓ Exists: {output_dir}/")
    
    return True

def main():
    """Run all validation checks"""
    print("="*80)
    print("🔍 VALIDATING SETUP FOR MARKET SIGNAL ANALYSIS")
    print("="*80 + "\n")
    
    checks = []
    
    # Python version
    checks.append(("Python version", check_python_version()))
    
    # Dependencies
    deps_ok, missing = check_dependencies()
    checks.append(("Dependencies", deps_ok))
    
    # Data files
    checks.append(("Data files", check_data_files()))
    
    # Disk space
    checks.append(("Disk space", check_disk_space()))
    
    # Output directory
    checks.append(("Output directory", check_output_directory()))
    
    # Summary
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80 + "\n")
    
    all_passed = True
    for check_name, passed in checks:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status:8} {check_name}")
        if not passed:
            all_passed = False
    
    print()
    
    if all_passed:
        print("✅ All checks passed! You're ready to run the analysis.")
        print("\nNext steps:")
        print("  1. If you don't have data: python3 run/1_collect_data.py")
        print("  2. Run analysis: python3 run/2_analyze_signals.py")
        print("  3. Or run everything: python3 run/run_all.py")
        print()
        return 0
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        
        if not checks[1][1]:  # Dependencies failed
            print("\n  Install dependencies:")
            print("    pip install -r requirements.txt")
            if missing:
                print(f"\n  Or install missing packages:")
                print(f"    pip install {' '.join(missing)}")
        
        if not checks[2][1]:  # Data files missing
            print("\n  Collect data:")
            print("    python3 run/1_collect_data.py --hashtags nifty50 --count 100")
        
        print()
        return 1

if __name__ == '__main__':
    sys.exit(main())
