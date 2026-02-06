"""
Logging module for Service Desk Manager
Logs to both file and Windows Event Viewer
"""
import logging
import logging.handlers
from pathlib import Path
from .config import LOG_FILE, LOG_DIR, APP_TITLE

# Create logger
logger = logging.getLogger("ServiceDeskManager")
logger.setLevel(logging.DEBUG)

# File handler
log_dir = Path(LOG_DIR)
log_dir.mkdir(parents=True, exist_ok=True)

file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(logging.DEBUG)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Try to add Windows Event Log handler
try:
    import winreg
    
    # Check if event source exists, if not try to create it
    try:
        win_handler = logging.handlers.NTEventLogHandler(APP_TITLE)
        win_handler.setLevel(logging.WARNING)
        logger.addHandler(win_handler)
    except Exception as e:
        # Event source may require admin privileges to create
        logger.warning(f"Could not setup Windows Event Log handler: {e}")
        logger.warning("Run as Administrator to enable Event Viewer logging")
except ImportError:
    logger.warning("Windows registry module not available on this system")

def log_info(message: str):
    """Log info level message"""
    logger.info(message)

def log_error(message: str, exception: Exception = None):
    """Log error level message"""
    if exception:
        logger.error(f"{message}: {str(exception)}", exc_info=True)
    else:
        logger.error(message)

def log_warning(message: str):
    """Log warning level message"""
    logger.warning(message)

def log_debug(message: str):
    """Log debug level message"""
    logger.debug(message)
