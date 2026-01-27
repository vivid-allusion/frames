"""Global constants for the application."""

# API Configuration
DEFAULT_TIMEOUT = 120  # seconds
DEFAULT_MAX_RETRIES = 3
DEFAULT_MAX_WAIT_TIME = 1200  # seconds
DEFAULT_RATE_LIMIT_RETRY_DELAY = 60  # seconds

# Image Processing
DEFAULT_IMAGE_DOWNLOAD_TIMEOUT = 30  # seconds

# File System
TIMESTAMP_FORMAT = "%y%m%d_%H%M%S"
TIME_FORMAT = "%H%M%S"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# HTTP constants
HTTP_OK = 200
URL_VALIDATION_TIMEOUT = 5  # seconds

# Code quality thresholds
MAX_FILE_SIZE_LINES = 300
MAX_FUNCTION_SIZE_LINES = 25
MAX_FUNCTION_PARAMETERS = 3
