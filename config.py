"""
Configuration for R&I Newsletter Automation System (v2 - Tracker-Driven)
"""
import os
from datetime import datetime
from typing import List, Dict

# Google Workspace Configuration
GOOGLE_EMAIL = "jake.williams@deliveroo.co.uk"
MCP_SERVER = "user-google_workspace_mcp"

# Tracker Spreadsheet Configuration
TRACKER_SPREADSHEET_ID = "1MzU3blV44VooYEGRNczi1uXmXntMrGb1JfJ9T6z1VgA"
TRACKER_SHEET_NAME = "Submissions"
TRACKER_RANGE = "Submissions!A1:F100"

# Newsletter Metadata
NEWSLETTER_QUARTER = "Q1"
NEWSLETTER_YEAR = 2026
NEWSLETTER_TITLE = "Research & Insights Newsletter"
NEWSLETTER_SUBTITLE = f"{NEWSLETTER_QUARTER} {NEWSLETTER_YEAR} | January - March"
NEWSLETTER_DEADLINE = "2026-04-03"

# Content Configuration
MAX_FEATURED_ITEMS = 6
MAX_SUMMARY_LENGTH_FEATURED = 300
MAX_SUMMARY_LENGTH_LISTED = 120

# Customer Corner (toggleable)
CUSTOMER_CORNER_ENABLED = True

# PDF Export Configuration
PDF_ENGINE = "playwright"

# API Configuration (for Claude summarization)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Output Configuration
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
OUTPUT_FOLDER_ID = None

# Legacy compatibility
INCLUDED_MIME_TYPES = [
    "application/vnd.google-apps.document",
    "application/vnd.google-apps.presentation",
    "application/vnd.google-apps.spreadsheet",
]
