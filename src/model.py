from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime

class Tweet(BaseModel):
    """
    Model for storing scraped tweet data from Indian stock market discussions.
    
    Enhanced with Phase 1 & 2 improvements:
    - Cleaned content fields
    - Language detection
    - URL extraction
    - Processing metadata
    """
    
    # Core identification
    tweet_id: Optional[str] = None  # If you can extract it
    username: str
    user_handle: str = Field(..., description="@username format")
    
    # Content (original and cleaned)
    content: str = Field(..., min_length=1, description="Original tweet content")
    cleaned_content: Optional[str] = Field(None, description="Cleaned and normalized content")
    
    timestamp: datetime
    
    # Engagement metrics
    likes: int = Field(default=0, ge=0)
    retweets: int = Field(default=0, ge=0)
    replies: int = Field(default=0, ge=0)
    views: Optional[int] = Field(default=None, ge=0)
    quotes: Optional[int] = Field(default=None, ge=0)
    bookmarks: Optional[int] = Field(default=None, ge=0)
    
    # Extracted entities
    hashtags: List[str] = Field(default_factory=list)
    mentions: List[str] = Field(default_factory=list)
    extracted_urls: List[str] = Field(default_factory=list, description="URLs extracted from content")
    
    # Language & Processing (Phase 1 additions)
    detected_language: Optional[str] = Field(default="unknown", description="ISO 639-1 language code")
    processed_at: Optional[datetime] = Field(None, description="When tweet was processed")
    
    # Metadata
    tweet_url: Optional[str] = None
    is_retweet: bool = False
    is_reply: bool = False
    scraped_at: datetime = Field(default_factory=datetime.now)
    
    # Optional - useful for analysis
    language: Optional[str] = "en"  # Kept for backward compatibility
    has_media: bool = False
    media_urls: List[str] = Field(default_factory=list)
    
    @field_validator('user_handle')
    @classmethod
    def validate_handle(cls, v: str) -> str:
        """Ensure handle starts with @"""
        if not v.startswith('@'):
            return f'@{v}'
        return v
    
    @field_validator('hashtags', 'mentions')
    @classmethod
    def clean_tags(cls, v: List[str]) -> List[str]:
        """Remove # and @ symbols, convert to lowercase"""
        cleaned = []
        for item in v:
            item = item.strip().lower()
            item = item.lstrip('#@')
            if item:
                cleaned.append(item)
        return cleaned
    
    @field_validator('content')
    @classmethod
    def clean_content(cls, v: str) -> str:
        """Basic content cleaning"""
        return v.strip()
        
        
        
