"""
===================
USER DEFINED ERRORS
===================
Custom errors for
- error     : Base class for other exceptions
- noVideos  : Raised when no items returned - no videos found for query/date
- quotaLimit: Raised when all 12 API key limits are reached

"""

class error(Exception):
    pass

class noVideos(error):
    pass

class quotaLimit(error):
    pass