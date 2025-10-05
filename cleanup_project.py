#!/usr/bin/env python3
"""
Project Cleanup Script - Reorganize root directory files

This script safely reorganizes the project structure by:
1. Creating necessary directories
2. Moving files to appropriate locations
3. Creating a backup manifest
4. Providing undo capability

Usage:
    python cleanup_project.py --preview    # Show what will be moved
    python cleanup_project.py --execute    # Actually move files
    python cleanup_project.py --undo       # Undo the cleanup
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime
import argparse


# File categorization
KEEP_IN_ROOT = [
    '.env',
    '.gitignore',
    'requirements.txt',
    'README.md',
    'run_scraper.py',
    'incremental_scraper.py',
    'scrape_plan.sh',
    'analyze_incremental_data.py',
    'view_tweets.py',
    'TODO.md',
    'TF_IDF_IMPLEMENTATION_PLAN.md',
]

DOCS_GUIDES = [
    'INCREMENTAL_SCRAPING_GUIDE.md',
    'QUICK_REFERENCE.md',
    'QUICK_START.md',
    'FINAL_RUN_CHECKLIST.md',
    'HOW_TO_USE_OUTPUT.md',
]

DOCS_IMPLEMENTATION = [
    'IMPLEMENTATION_STATUS.md',
    'IMPLEMENTATION_PHASE_1_2_COMPLETE.md',
    'INTEGRATION_COMPLETE.md',
    'INTEGRATION_SUMMARY.md',
    'PHASE_1_2_QUICKSTART.md',
    'PHASE_1_2_SUMMARY.txt',
]

DOCS_STRATEGIES = [
    'HASHTAG_STRATEGY.md',
    'LABELING_INSTRUCTIONS.md',
]

DOCS_TROUBLESHOOTING = [
    'ENGAGEMENT_FIX.md',
    'README_V2.md',
]

DOCS_FEATURES = [
    'FEATURES_SUMMARY.md',
    'PROJECT_STRUCTURE.md',
]

TEST_SCRIPTS = [
    'test_data_processing.py',
    'test_engagement.py',
    'test_sentiment.py',
    'test_task2.py',
    'test_tfidf.py',
]

DEBUG_SCRIPTS = [
    'debug_engagement_metrics.py',
    'debug_engagement_simple.py',
    'diagnose_engagement.py',
]

SCRIPTS_ANALYSIS = [
    'analyze_tweets.py',
    'check_output.py',
    'examine_data.py',
    'explore_data.py',
    'quick_analysis.py',
]

SCRIPTS_LABELING = [
    'interactive_labeling.py',
    'display_tweets_for_labeling.py',
]

ARCHIVE_DATA = [
    'collection_stats.json',
    'raw_tweets.json',
    'tweets.meta.json',
    'tweets.parquet',
    'tweets_clean.json',
    'tweets_english.parquet',
    'tweets_essential.csv',
    'sentiment_results.parquet',
]

ARCHIVE_LOGS = [
    'scraper_output.log',
]

TEMPLATES = [
    'manual_labels_template.csv',
]

# Move plan
MOVE_PLAN = {
    'docs/guides': DOCS_GUIDES,
    'docs/implementation': DOCS_IMPLEMENTATION,
    'docs/strategies': DOCS_STRATEGIES,
    'docs/troubleshooting': DOCS_TROUBLESHOOTING,
    'docs/features': DOCS_FEATURES,
    'tests': TEST_SCRIPTS,
    'debug/scripts': DEBUG_SCRIPTS,
    'scripts/analysis': SCRIPTS_ANALYSIS,
    'scripts/labeling': SCRIPTS_LABELING,
    'archive/data': ARCHIVE_DATA,
    'archive/logs': ARCHIVE_LOGS,
    'templates': TEMPLATES,
}


def preview_cleanup():
    """Show what will be moved without actually moving"""
    print("\n" + "="*80)
    print("📋 CLEANUP PREVIEW - Files to be reorganized")
    print("="*80)
    
    root = Path.cwd()
    total_moved = 0
    
    print("\n✅ Files staying in root:")
    for file in KEEP_IN_ROOT:
        if (root / file).exists():
            print(f"   • {file}")
    
    print("\n📁 Files to be moved:")
    for dest_dir, files in MOVE_PLAN.items():
        print(f"\n   → {dest_dir}/")
        for file in files:
            if (root / file).exists():
                print(f"      • {file}")
                total_moved += 1
            else:
                print(f"      ✗ {file} (not found)")
    
    print("\n" + "="*80)
    print(f"📊 SUMMARY")
    print("="*80)
    print(f"Files staying in root: {len(KEEP_IN_ROOT)}")
    print(f"Files to be moved: {total_moved}")
    print(f"New directory structure: {len(MOVE_PLAN)} directories")
    print("="*80)


def execute_cleanup():
    """Actually perform the cleanup"""
    print("\n" + "="*80)
    print("🧹 EXECUTING CLEANUP")
    print("="*80)
    
    root = Path.cwd()
    manifest = {
        'timestamp': datetime.now().isoformat(),
        'moves': []
    }
    
    # Create all necessary directories
    print("\n📁 Creating directory structure...")
    for dest_dir in MOVE_PLAN.keys():
        dest_path = root / dest_dir
        dest_path.mkdir(parents=True, exist_ok=True)
        print(f"   ✓ {dest_dir}/")
    
    # Move files
    print("\n🚚 Moving files...")
    moved_count = 0
    skipped_count = 0
    
    for dest_dir, files in MOVE_PLAN.items():
        dest_path = root / dest_dir
        
        for file in files:
            src = root / file
            dst = dest_path / file
            
            if src.exists() and src.is_file():
                try:
                    shutil.move(str(src), str(dst))
                    print(f"   ✓ {file} → {dest_dir}/")
                    manifest['moves'].append({
                        'file': file,
                        'from': str(src.relative_to(root)),
                        'to': str(dst.relative_to(root))
                    })
                    moved_count += 1
                except Exception as e:
                    print(f"   ✗ Failed to move {file}: {e}")
                    skipped_count += 1
            else:
                skipped_count += 1
    
    # Save manifest for undo
    manifest_file = root / '.cleanup_manifest.json'
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print("\n" + "="*80)
    print("✅ CLEANUP COMPLETE!")
    print("="*80)
    print(f"Moved: {moved_count} files")
    print(f"Skipped: {skipped_count} files (already moved or not found)")
    print(f"\nManifest saved to: {manifest_file}")
    print("\n💡 To undo: python cleanup_project.py --undo")
    print("="*80)


def undo_cleanup():
    """Undo the cleanup by restoring files to original locations"""
    print("\n" + "="*80)
    print("↩️  UNDOING CLEANUP")
    print("="*80)
    
    root = Path.cwd()
    manifest_file = root / '.cleanup_manifest.json'
    
    if not manifest_file.exists():
        print("\n❌ No cleanup manifest found. Cannot undo.")
        print("   Manifest file: .cleanup_manifest.json")
        return
    
    with open(manifest_file, 'r') as f:
        manifest = json.load(f)
    
    print(f"\nRestoring files from cleanup on {manifest['timestamp']}")
    print("\n🚚 Moving files back...")
    
    restored_count = 0
    failed_count = 0
    
    for move in manifest['moves']:
        src = root / move['to']
        dst = root / move['from']
        
        if src.exists():
            try:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dst))
                print(f"   ✓ {move['file']} → root/")
                restored_count += 1
            except Exception as e:
                print(f"   ✗ Failed to restore {move['file']}: {e}")
                failed_count += 1
        else:
            print(f"   ✗ {move['file']} not found at {move['to']}")
            failed_count += 1
    
    # Remove manifest
    manifest_file.unlink()
    
    print("\n" + "="*80)
    print("✅ UNDO COMPLETE!")
    print("="*80)
    print(f"Restored: {restored_count} files")
    print(f"Failed: {failed_count} files")
    print("="*80)


def main():
    parser = argparse.ArgumentParser(
        description="Clean up and reorganize project structure",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--preview',
        action='store_true',
        help='Preview what will be moved (safe, no changes)'
    )
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Execute the cleanup (moves files)'
    )
    parser.add_argument(
        '--undo',
        action='store_true',
        help='Undo the last cleanup'
    )
    
    args = parser.parse_args()
    
    if args.preview:
        preview_cleanup()
    elif args.execute:
        print("\n⚠️  WARNING: This will reorganize your project structure!")
        print("   A manifest will be saved to allow undo.")
        response = input("\n   Continue? (yes/no): ").lower()
        if response == 'yes':
            execute_cleanup()
        else:
            print("\n   Cancelled.")
    elif args.undo:
        print("\n⚠️  This will restore files to their original locations.")
        response = input("\n   Continue? (yes/no): ").lower()
        if response == 'yes':
            undo_cleanup()
        else:
            print("\n   Cancelled.")
    else:
        parser.print_help()
        print("\n💡 Start with: python cleanup_project.py --preview")


if __name__ == "__main__":
    main()
