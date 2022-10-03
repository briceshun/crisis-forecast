# Define Python user-defined exceptions
class Error(Exception):
    """Base class for other exceptions"""
    pass

class NoVideosError(Error):
    """Raised when response has no data - no videos posted"""
    pass