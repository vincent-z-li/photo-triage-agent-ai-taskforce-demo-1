"""Custom exceptions for the agent server application."""


class PhotoTriageError(Exception):
    """Base exception for photo triage operations."""
    pass


class ImageProcessingError(PhotoTriageError):
    """Exception raised when image processing fails."""
    pass


class QualityAnalysisError(PhotoTriageError):
    """Exception raised when quality analysis fails."""
    pass


class ValidationError(Exception):
    """Exception raised when validation fails."""
    pass


class ModelError(Exception):
    """Exception raised when AI model operations fail."""
    pass


class MCPServerError(Exception):
    """Exception raised when MCP server operations fail."""
    pass