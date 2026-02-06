"""
Configuration module for RemoteDesktop GUI Application
"""
import os
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).parent.parent
SRC_DIR = BASE_DIR / "src"
TEMPLATES_DIR = BASE_DIR / "templates"
OUTPUT_DIR = BASE_DIR / "output"

# Outlook template paths
OUTLOOK_TEMPLATES_DEFAULT = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Templates"

# Application settings
APP_TITLE = "Service Desk Manager"
# Initial window size (width x height)
APP_WIDTH = 1200
APP_HEIGHT = 800
DEFAULT_PING_TIMEOUT = 2

# Email settings
DEFAULT_EMAIL_BCC = "servicedesk.europe@scotiabank.com"
DEFAULT_KEYWORDS = ["[Insert IP Address]", "[Recipient's Name]", "[Recipient Name]"]

# Default template file name placed in the app templates folder
DEFAULT_TEMPLATE_NAME = "Remote Desktop.oft"

# File types
EXCEL_EXTENSIONS = [".xlsx", ".xls"]
CSV_EXTENSION = ".csv"
TEMPLATE_EXTENSIONS = [".oft", ".msg"]

# Ensure directories exist
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTLOOK_TEMPLATES_DEFAULT.mkdir(parents=True, exist_ok=True)

# Logging configuration
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "service_desk_manager.log"
EVENT_LOG_SOURCE = "Service Desk Manager"
