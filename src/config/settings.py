"""
Configuration management using Pydantic and environment variables.

Centralizes all configuration and supports multiple environments.
"""
import os
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field, SecretStr, field_validator


class TwitterCredentials(BaseModel):
    """Twitter login credentials"""
    username: str = Field(..., description="Twitter username")
    password: SecretStr = Field(..., description="Twitter password")
    email: Optional[str] = Field(None, description="Email for verification")
    
    @classmethod
    def from_env(cls) -> "TwitterCredentials":
        """Load credentials from environment variables"""
        return cls(
            username=os.getenv("TWITTER_USERNAME", ""),
            password=os.getenv("TWITTER_PASSWORD", ""),
            email=os.getenv("TWITTER_EMAIL")
        )


class ScraperConfig(BaseModel):
    """Main scraper configuration"""
    
    # Browser settings
    headless: bool = Field(True, description="Run browser in headless mode")
    slow_mo: int = Field(0, description="Slow down operations (ms)")
    
    # Scraping settings
    tweets_per_hashtag: int = Field(500, description="Target tweets per hashtag", ge=1)
    hashtags: List[str] = Field(
        default_factory=lambda: ['nifty50', 'sensex', 'intraday', 'banknifty'],
        description="Hashtags to scrape"
    )
    
    # Rate limiting
    rate_limit_requests_per_second: float = Field(
        10.0,
        description="Max requests per second",
        gt=0
    )
    rate_limit_burst_size: int = Field(
        20,
        description="Max burst requests",
        ge=1
    )
    
    # Retry settings
    max_retries: int = Field(3, description="Max retry attempts", ge=0)
    retry_base_delay: float = Field(1.0, description="Initial retry delay (seconds)", gt=0)
    retry_max_delay: float = Field(60.0, description="Max retry delay (seconds)", gt=0)
    
    # Timeouts
    page_timeout: int = Field(60000, description="Page load timeout (ms)", gt=0)
    element_timeout: int = Field(30000, description="Element wait timeout (ms)", gt=0)
    
    # Output settings
    output_dir: Path = Field(
        default_factory=lambda: Path.cwd(),
        description="Output directory for results"
    )
    output_tweets_file: str = Field("raw_tweets.json", description="Output tweets filename")
    output_stats_file: str = Field("collection_stats.json", description="Output stats filename")
    
    # Storage settings (Phase 2)
    save_json: bool = Field(True, description="Save tweets as JSON (backward compatibility)")
    save_parquet: bool = Field(True, description="Save tweets as Parquet (efficient storage)")
    parquet_filename: str = Field("tweets.parquet", description="Parquet output filename")
    parquet_compression: str = Field("snappy", description="Parquet compression: snappy, gzip, zstd")
    
    # Data processing settings (Phase 1)
    enable_data_cleaning: bool = Field(True, description="Enable data cleaning and normalization")
    remove_urls_from_content: bool = Field(True, description="Remove URLs from cleaned content")
    detect_language: bool = Field(True, description="Detect tweet language")
    normalize_unicode: bool = Field(True, description="Normalize Unicode characters")
    
    # Debugging
    debug_screenshots: bool = Field(True, description="Save debug screenshots")
    debug_dir: Path = Field(
        default_factory=lambda: Path.cwd() / "debug",
        description="Debug output directory"
    )
    
    @field_validator('output_dir', 'debug_dir')
    @classmethod
    def create_directory(cls, v: Path) -> Path:
        """Ensure directory exists"""
        v.mkdir(parents=True, exist_ok=True)
        return v
    
    @classmethod
    def from_env(cls, **overrides) -> "ScraperConfig":
        """
        Load configuration from environment variables.
        
        Environment variables:
            SCRAPER_HEADLESS: true/false
            SCRAPER_TWEETS_PER_HASHTAG: integer
            SCRAPER_HASHTAGS: comma-separated list
            SCRAPER_MAX_RETRIES: integer
            etc.
        
        Args:
            **overrides: Override specific settings
        """
        config_dict = {
            'headless': os.getenv('SCRAPER_HEADLESS', 'true').lower() == 'true',
            'tweets_per_hashtag': int(os.getenv('SCRAPER_TWEETS_PER_HASHTAG', '500')),
            'hashtags': os.getenv(
                'SCRAPER_HASHTAGS',
                'nifty50,sensex,intraday,banknifty'
            ).split(','),
            'max_retries': int(os.getenv('SCRAPER_MAX_RETRIES', '3')),
            'debug_screenshots': os.getenv('SCRAPER_DEBUG', 'true').lower() == 'true',
        }
        
        # Apply overrides
        config_dict.update(overrides)
        
        return cls(**config_dict)
    
    def get_output_path(self, filename: str) -> Path:
        """Get full path for output file"""
        return self.output_dir / filename


# Default configuration instance
default_config = ScraperConfig()


def load_config(**overrides) -> ScraperConfig:
    """
    Load configuration with optional overrides.
    
    Priority (highest to lowest):
    1. Function arguments (overrides)
    2. Environment variables
    3. Default values
    
    Example:
        # Use defaults
        config = load_config()
        
        # Override specific settings
        config = load_config(headless=False, tweets_per_hashtag=100)
        
        # Load from env + override
        os.environ['SCRAPER_HEADLESS'] = 'false'
        config = load_config(tweets_per_hashtag=100)
    """
    return ScraperConfig.from_env(**overrides)

