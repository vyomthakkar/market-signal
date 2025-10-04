"""
Custom exception hierarchy for the scraper.

Provides specific exceptions for different error scenarios,
making error handling more precise and actionable.
"""


class ScraperException(Exception):
    """Base exception for all scraper-related errors"""
    pass


class RateLimitException(ScraperException):
    """Raised when Twitter rate limits are hit"""
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = None):
        super().__init__(message)
        self.retry_after = retry_after  # Seconds until retry allowed


class LoginException(ScraperException):
    """Raised when login fails"""
    pass


class NetworkException(ScraperException):
    """Raised for network-related errors"""
    pass


class ValidationException(ScraperException):
    """Raised when data validation fails"""
    pass


class BrowserException(ScraperException):
    """Raised for browser/Playwright-related errors"""
    pass


class DataExtractionException(ScraperException):
    """Raised when tweet data extraction fails"""
    pass

