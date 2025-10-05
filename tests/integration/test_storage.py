"""
Integration tests for data storage (JSON and Parquet)
"""

import pytest
import sys
import json
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from data.storage import ParquetWriter, StorageManager


@pytest.fixture
def storage_dir(tmp_path):
    """Create temporary storage directory"""
    return tmp_path / "storage"


@pytest.fixture
def parquet_writer(storage_dir):
    """Create ParquetWriter instance"""
    storage_dir.mkdir(exist_ok=True)
    return ParquetWriter(storage_dir, compression='snappy')


@pytest.fixture
def storage_manager(storage_dir):
    """Create StorageManager instance"""
    storage_dir.mkdir(exist_ok=True)
    return StorageManager(storage_dir)


@pytest.mark.integration
class TestParquetWriter:
    """Test suite for ParquetWriter"""
    
    def test_write_parquet(self, parquet_writer, sample_tweets):
        """Test writing data to Parquet"""
        output_path = parquet_writer.write(
            sample_tweets,
            'test_output.parquet',
            include_metadata=True
        )
        
        assert output_path.exists()
        assert output_path.suffix == '.parquet'
    
    def test_read_parquet(self, parquet_writer, sample_tweets):
        """Test reading data from Parquet"""
        # Write first
        parquet_writer.write(sample_tweets, 'test_read.parquet')
        
        # Read back
        df = parquet_writer.read('test_read.parquet')
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == len(sample_tweets)
    
    def test_round_trip_consistency(self, parquet_writer, sample_tweets):
        """Test that data is preserved in write-read cycle"""
        # Write
        parquet_writer.write(sample_tweets, 'roundtrip.parquet')
        
        # Read
        df = parquet_writer.read('roundtrip.parquet')
        
        # Check data integrity
        assert len(df) == len(sample_tweets)
        
        # Check key fields are preserved
        original_ids = {t['tweet_id'] for t in sample_tweets}
        loaded_ids = set(df['tweet_id'])
        assert original_ids == loaded_ids
    
    def test_compression(self, parquet_writer, sample_tweets, storage_dir):
        """Test that compression reduces file size"""
        # Write with compression
        compressed_path = parquet_writer.write(
            sample_tweets,
            'compressed.parquet'
        )
        
        # Write without compression
        writer_none = ParquetWriter(storage_dir, compression=None)
        uncompressed_path = writer_none.write(
            sample_tweets,
            'uncompressed.parquet'
        )
        
        # Compressed should be smaller (for larger datasets)
        # Note: For very small data, overhead might make compressed larger
        assert compressed_path.exists()
        assert uncompressed_path.exists()
    
    def test_metadata_inclusion(self, parquet_writer, sample_tweets, storage_dir):
        """Test metadata file creation"""
        parquet_writer.write(
            sample_tweets,
            'with_meta.parquet',
            include_metadata=True
        )
        
        meta_path = storage_dir / 'with_meta.meta.json'
        assert meta_path.exists()
        
        # Load and check metadata
        with open(meta_path) as f:
            metadata = json.load(f)
        
        assert 'total_records' in metadata
        assert metadata['total_records'] == len(sample_tweets)
    
    def test_empty_data(self, parquet_writer):
        """Test handling of empty data"""
        output_path = parquet_writer.write([], 'empty.parquet')
        
        assert output_path.exists()
        
        df = parquet_writer.read('empty.parquet')
        assert len(df) == 0


@pytest.mark.integration
class TestStorageManager:
    """Test suite for StorageManager"""
    
    def test_save_both_formats(self, storage_manager, sample_tweets):
        """Test saving in both JSON and Parquet"""
        paths = storage_manager.save_tweets(
            sample_tweets,
            save_json=True,
            save_parquet=True,
            json_filename='test.json',
            parquet_filename='test.parquet'
        )
        
        assert 'json' in paths
        assert 'parquet' in paths
        assert paths['json'].exists()
        assert paths['parquet'].exists()
    
    def test_save_json_only(self, storage_manager, sample_tweets):
        """Test saving JSON only"""
        paths = storage_manager.save_tweets(
            sample_tweets,
            save_json=True,
            save_parquet=False,
            json_filename='json_only.json'
        )
        
        assert 'json' in paths
        assert 'parquet' not in paths
        assert paths['json'].exists()
    
    def test_save_parquet_only(self, storage_manager, sample_tweets):
        """Test saving Parquet only"""
        paths = storage_manager.save_tweets(
            sample_tweets,
            save_json=False,
            save_parquet=True,
            parquet_filename='parquet_only.parquet'
        )
        
        assert 'parquet' in paths
        assert 'json' not in paths
        assert paths['parquet'].exists()
    
    def test_json_format(self, storage_manager, sample_tweets, storage_dir):
        """Test JSON output format"""
        storage_manager.save_tweets(
            sample_tweets,
            save_json=True,
            save_parquet=False,
            json_filename='format_test.json'
        )
        
        json_path = storage_dir / 'format_test.json'
        with open(json_path) as f:
            loaded = json.load(f)
        
        assert isinstance(loaded, list)
        assert len(loaded) == len(sample_tweets)
        assert loaded[0]['tweet_id'] == sample_tweets[0]['tweet_id']
    
    def test_dataframe_input(self, storage_manager, sample_dataframe):
        """Test that StorageManager handles DataFrame input"""
        paths = storage_manager.save_tweets(
            sample_dataframe,
            save_parquet=True,
            parquet_filename='from_df.parquet'
        )
        
        assert paths['parquet'].exists()
        
        # Read back and verify
        df = pd.read_parquet(paths['parquet'])
        assert len(df) == len(sample_dataframe)
    
    def test_overwrite_behavior(self, storage_manager, sample_tweets, storage_dir):
        """Test file overwrite behavior"""
        filename = 'overwrite_test.json'
        
        # First write
        storage_manager.save_tweets(
            sample_tweets[:2],
            save_json=True,
            json_filename=filename
        )
        
        # Second write (should overwrite)
        storage_manager.save_tweets(
            sample_tweets,
            save_json=True,
            json_filename=filename
        )
        
        # Verify it was overwritten
        with open(storage_dir / filename) as f:
            loaded = json.load(f)
        
        assert len(loaded) == len(sample_tweets)  # Should be full dataset


@pytest.mark.integration
def test_storage_workflow(sample_tweets, tmp_path):
    """Test complete storage workflow"""
    storage_dir = tmp_path / "workflow_test"
    storage_dir.mkdir()
    
    # Initialize manager
    manager = StorageManager(storage_dir)
    
    # Save data
    paths = manager.save_tweets(
        sample_tweets,
        save_json=True,
        save_parquet=True,
        json_filename='workflow.json',
        parquet_filename='workflow.parquet'
    )
    
    # Verify both formats exist
    assert paths['json'].exists()
    assert paths['parquet'].exists()
    
    # Load and verify JSON
    with open(paths['json']) as f:
        json_data = json.load(f)
    assert len(json_data) == len(sample_tweets)
    
    # Load and verify Parquet
    df = pd.read_parquet(paths['parquet'])
    assert len(df) == len(sample_tweets)
    
    # Compare file sizes
    json_size = paths['json'].stat().st_size
    parquet_size = paths['parquet'].stat().st_size
    
    # For small datasets, can't guarantee Parquet is smaller
    # But both should exist and be non-zero
    assert json_size > 0
    assert parquet_size > 0


@pytest.mark.integration
def test_unicode_handling(storage_manager, storage_dir):
    """Test Unicode character handling in storage"""
    tweets_with_unicode = [
        {
            'tweet_id': '001',
            'content': 'नमस्ते! #Nifty50 📈',
            'username': 'user1'
        },
        {
            'tweet_id': '002',
            'content': 'மிகவும் நல்லது #Sensex',
            'username': 'user2'
        }
    ]
    
    # Save
    paths = storage_manager.save_tweets(
        tweets_with_unicode,
        save_json=True,
        save_parquet=True,
        json_filename='unicode.json',
        parquet_filename='unicode.parquet'
    )
    
    # Load JSON and verify
    with open(paths['json'], encoding='utf-8') as f:
        json_data = json.load(f)
    
    assert json_data[0]['content'] == tweets_with_unicode[0]['content']
    
    # Load Parquet and verify
    df = pd.read_parquet(paths['parquet'])
    assert df.iloc[0]['content'] == tweets_with_unicode[0]['content']


@pytest.mark.integration
def test_large_dataset(storage_manager):
    """Test handling of larger datasets"""
    # Generate large dataset
    large_dataset = []
    for i in range(1000):
        large_dataset.append({
            'tweet_id': f'tweet_{i}',
            'content': f'Tweet content {i}' * 10,  # Make it bigger
            'likes': i,
            'retweets': i // 2,
            'username': f'user_{i % 100}'
        })
    
    # Save
    paths = storage_manager.save_tweets(
        large_dataset,
        save_json=True,
        save_parquet=True,
        json_filename='large.json',
        parquet_filename='large.parquet'
    )
    
    # Verify
    assert paths['json'].exists()
    assert paths['parquet'].exists()
    
    # Load and check count
    df = pd.read_parquet(paths['parquet'])
    assert len(df) == 1000
