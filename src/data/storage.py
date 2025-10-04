"""
Parquet Storage Module

Handles:
- Efficient Parquet file writing with compression
- Schema management
- Partitioning strategies
- Metadata storage
- DataFrame conversion
"""

from __future__ import annotations  # Enable string annotations

import json
from pathlib import Path
from typing import List, Dict, Optional, Union
from datetime import datetime
import logging

try:
    import pandas as pd
    import pyarrow as pa
    import pyarrow.parquet as pq
    PARQUET_AVAILABLE = True
except ImportError:
    PARQUET_AVAILABLE = False
    pd = None
    pa = None
    pq = None

logger = logging.getLogger(__name__)


class ParquetWriter:
    """
    Production-ready Parquet writer for tweet data.
    
    Features:
    - Snappy/ZSTD compression (5-10x smaller than JSON)
    - Schema enforcement
    - Metadata storage
    - Partition support (by date/hashtag)
    - Append mode for incremental writes
    """
    
    # Define schema for tweet data
    TWEET_SCHEMA = {
        'tweet_id': 'string',
        'username': 'string',
        'timestamp': 'string',
        'content': 'string',
        'cleaned_content': 'string',
        'replies': 'int64',
        'retweets': 'int64',
        'likes': 'int64',
        'views': 'int64',
        'hashtags': 'object',  # List of strings
        'mentions': 'object',  # List of strings
        'extracted_urls': 'object',  # List of strings
        'detected_language': 'string',
        'processed_at': 'string'
    }
    
    def __init__(
        self,
        output_dir: Union[str, Path],
        compression: str = 'snappy',
        partition_by: Optional[str] = None
    ):
        """
        Initialize Parquet writer.
        
        Args:
            output_dir: Directory to save Parquet files
            compression: Compression algorithm ('snappy', 'gzip', 'zstd', 'none')
                        snappy: Fast compression/decompression (recommended)
                        zstd: Best compression ratio
                        gzip: Good balance
            partition_by: Optional partitioning strategy ('date', 'hashtag', None)
        """
        if not PARQUET_AVAILABLE:
            raise ImportError(
                "Parquet support requires pandas and pyarrow. "
                "Install with: pip install pandas pyarrow"
            )
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.compression = compression
        self.partition_by = partition_by
        
        # Statistics
        self.files_written = 0
        self.total_rows = 0
        
        logger.info(f"ParquetWriter initialized: {output_dir} (compression: {compression})")
    
    def write(
        self,
        tweets: List[Dict],
        filename: str = 'tweets.parquet',
        include_metadata: bool = True
    ) -> Path:
        """
        Write tweets to Parquet file.
        
        Args:
            tweets: List of tweet dictionaries
            filename: Output filename
            include_metadata: Include collection metadata in file
            
        Returns:
            Path to written file
        """
        if not tweets:
            logger.warning("No tweets to write")
            return None
        
        logger.info(f"Writing {len(tweets)} tweets to Parquet...")
        
        # Convert to DataFrame
        df = self._tweets_to_dataframe(tweets)
        
        # Apply schema
        df = self._apply_schema(df)
        
        # Write to Parquet
        output_path = self.output_dir / filename
        
        try:
            df.to_parquet(
                output_path,
                engine='pyarrow',
                compression=self.compression,
                index=False
            )
            
            self.files_written += 1
            self.total_rows += len(df)
            
            # Get file size
            file_size = output_path.stat().st_size
            size_mb = file_size / (1024 * 1024)
            
            logger.info(f"✓ Parquet file written: {output_path}")
            logger.info(f"  Rows: {len(df)}, Size: {size_mb:.2f} MB")
            logger.info(f"  Compression: {self.compression}")
            
            # Write metadata
            if include_metadata:
                self._write_metadata(output_path, tweets, df)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to write Parquet file: {e}")
            raise
    
    def append(
        self,
        tweets: List[Dict],
        filename: str = 'tweets.parquet'
    ) -> Path:
        """
        Append tweets to existing Parquet file or create new one.
        
        Args:
            tweets: List of tweet dictionaries
            filename: Output filename
            
        Returns:
            Path to file
        """
        output_path = self.output_dir / filename
        
        # If file exists, read and combine
        if output_path.exists():
            logger.info(f"Appending to existing file: {output_path}")
            
            # Read existing data
            existing_df = pd.read_parquet(output_path)
            
            # Convert new tweets to DataFrame
            new_df = self._tweets_to_dataframe(tweets)
            new_df = self._apply_schema(new_df)
            
            # Combine and deduplicate by tweet_id
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            combined_df = combined_df.drop_duplicates(subset=['tweet_id'], keep='last')
            
            # Write back
            combined_df.to_parquet(
                output_path,
                engine='pyarrow',
                compression=self.compression,
                index=False
            )
            
            logger.info(f"✓ Appended {len(new_df)} tweets (total: {len(combined_df)})")
            
            return output_path
        else:
            # Create new file
            return self.write(tweets, filename)
    
    def write_partitioned(
        self,
        tweets: List[Dict],
        partition_cols: List[str]
    ) -> Path:
        """
        Write tweets with partitioning.
        
        Args:
            tweets: List of tweet dictionaries
            partition_cols: Columns to partition by (e.g., ['collection_date'])
            
        Returns:
            Path to partitioned directory
        """
        if not tweets:
            logger.warning("No tweets to write")
            return None
        
        logger.info(f"Writing partitioned Parquet (by {partition_cols})...")
        
        # Convert to DataFrame
        df = self._tweets_to_dataframe(tweets)
        df = self._apply_schema(df)
        
        # Add partition column if needed
        if 'collection_date' in partition_cols and 'collection_date' not in df.columns:
            df['collection_date'] = pd.to_datetime('today').strftime('%Y-%m-%d')
        
        # Write partitioned
        output_path = self.output_dir / 'tweets_partitioned'
        
        try:
            df.to_parquet(
                output_path,
                engine='pyarrow',
                compression=self.compression,
                partition_cols=partition_cols,
                index=False
            )
            
            logger.info(f"✓ Partitioned Parquet written: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to write partitioned Parquet: {e}")
            raise
    
    def _tweets_to_dataframe(self, tweets: List[Dict]) -> pd.DataFrame:
        """Convert tweets to pandas DataFrame"""
        if not tweets:
            return pd.DataFrame()
        
        # Convert list fields to proper format
        for tweet in tweets:
            # Ensure lists are actually lists
            for field in ['hashtags', 'mentions', 'extracted_urls']:
                if field in tweet and not isinstance(tweet[field], list):
                    tweet[field] = []
        
        df = pd.DataFrame(tweets)
        return df
    
    def _apply_schema(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply schema and type conversions"""
        if df.empty:
            return df
        
        # Apply type conversions
        for col, dtype in self.TWEET_SCHEMA.items():
            if col in df.columns:
                try:
                    if dtype == 'int64':
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype('int64')
                    elif dtype == 'string':
                        df[col] = df[col].astype(str)
                    # 'object' type for lists is kept as-is
                except Exception as e:
                    logger.warning(f"Could not convert {col} to {dtype}: {e}")
        
        # Ensure required columns exist
        for col in ['tweet_id', 'username', 'content']:
            if col not in df.columns:
                logger.warning(f"Missing required column: {col}")
        
        return df
    
    def _write_metadata(self, parquet_path: Path, tweets: List[Dict], df: pd.DataFrame):
        """Write metadata JSON alongside Parquet file"""
        metadata = {
            'created_at': datetime.utcnow().isoformat(),
            'tweet_count': len(tweets),
            'columns': list(df.columns),
            'schema': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'compression': self.compression,
            'file_size_bytes': parquet_path.stat().st_size,
            'parquet_file': parquet_path.name
        }
        
        # Add summary statistics
        if 'detected_language' in df.columns:
            metadata['language_distribution'] = df['detected_language'].value_counts().to_dict()
        
        if 'username' in df.columns:
            metadata['unique_users'] = df['username'].nunique()
        
        # Write metadata
        metadata_path = parquet_path.with_suffix('.meta.json')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✓ Metadata written: {metadata_path}")
    
    def read(self, filename: str = 'tweets.parquet') -> pd.DataFrame:
        """
        Read Parquet file back to DataFrame.
        
        Args:
            filename: Parquet filename
            
        Returns:
            DataFrame with tweet data
        """
        file_path = self.output_dir / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"Parquet file not found: {file_path}")
        
        logger.info(f"Reading Parquet file: {file_path}")
        df = pd.read_parquet(file_path)
        
        logger.info(f"✓ Loaded {len(df)} tweets")
        return df
    
    def get_stats(self) -> Dict:
        """Get writer statistics"""
        return {
            'files_written': self.files_written,
            'total_rows': self.total_rows,
            'output_dir': str(self.output_dir),
            'compression': self.compression
        }


class StorageManager:
    """
    High-level storage manager for tweet data.
    
    Manages both JSON (backward compatibility) and Parquet (efficient storage).
    """
    
    def __init__(self, output_dir: Union[str, Path]):
        """
        Initialize storage manager.
        
        Args:
            output_dir: Directory for all output files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Parquet writer if available
        self.parquet_writer = None
        if PARQUET_AVAILABLE:
            self.parquet_writer = ParquetWriter(output_dir)
        else:
            logger.warning("Parquet not available, using JSON only")
    
    def save_tweets(
        self,
        tweets: List[Dict],
        save_json: bool = True,
        save_parquet: bool = True,
        json_filename: str = 'raw_tweets.json',
        parquet_filename: str = 'tweets.parquet'
    ) -> Dict[str, Path]:
        """
        Save tweets in multiple formats.
        
        Args:
            tweets: List of tweet dictionaries
            save_json: Save as JSON (default: True)
            save_parquet: Save as Parquet (default: True)
            json_filename: JSON filename
            parquet_filename: Parquet filename
            
        Returns:
            Dictionary with 'json' and 'parquet' paths
        """
        paths = {}
        
        # Save JSON (backward compatibility & debugging)
        if save_json:
            json_path = self.output_dir / json_filename
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(tweets, f, ensure_ascii=False, indent=2)
            
            json_size_mb = json_path.stat().st_size / (1024 * 1024)
            logger.info(f"✓ JSON saved: {json_path} ({json_size_mb:.2f} MB)")
            paths['json'] = json_path
        
        # Save Parquet (efficient storage)
        if save_parquet and self.parquet_writer:
            try:
                parquet_path = self.parquet_writer.write(tweets, parquet_filename)
                paths['parquet'] = parquet_path
                
                # Compare sizes
                if save_json and parquet_path:
                    json_size = paths['json'].stat().st_size
                    parquet_size = parquet_path.stat().st_size
                    compression_ratio = json_size / parquet_size if parquet_size > 0 else 0
                    logger.info(f"📊 Compression ratio: {compression_ratio:.1f}x "
                              f"(JSON: {json_size/1024:.1f}KB → Parquet: {parquet_size/1024:.1f}KB)")
                
            except Exception as e:
                logger.error(f"Failed to save Parquet: {e}")
        
        return paths
    
    def save_statistics(
        self,
        stats: Dict,
        filename: str = 'collection_stats.json'
    ) -> Path:
        """Save collection statistics"""
        stats_path = self.output_dir / filename
        
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✓ Statistics saved: {stats_path}")
        return stats_path
    
    def load_tweets(
        self,
        filename: str = 'tweets.parquet',
        format: str = 'parquet'
    ) -> Union[List[Dict], pd.DataFrame]:
        """
        Load tweets from storage.
        
        Args:
            filename: File to load
            format: 'parquet' or 'json'
            
        Returns:
            List of dicts (JSON) or DataFrame (Parquet)
        """
        if format == 'parquet' and self.parquet_writer:
            return self.parquet_writer.read(filename)
        elif format == 'json':
            json_path = self.output_dir / filename
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            raise ValueError(f"Unknown format: {format}")

