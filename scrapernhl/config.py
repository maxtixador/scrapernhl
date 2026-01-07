"""Config.py : Constants, headers, session configuration for NHL data scraping"""
import numpy as np
from scrapernhl.core.logging_config import get_logger

LOG = get_logger(__name__)

# DEFAULTS
DEFAULT_TEAM = "MTL" # Montreal Canadiens
DEFAULT_SEASON = "20252026" # 2025-2026 NHL Season
DEFAULT_DATE = "2025-11-11" # RANDOM DATE IN SEASON




# API ENDPOINTS
NHL_API_BASE_URL = "https://api-web.nhle.com"
NHL_API_BASE_URL_V1 = f"{NHL_API_BASE_URL}/v1"

STANDINGS_ENDPOINT = f"{NHL_API_BASE_URL_V1}/standings/{{date}}" # date in YYYY-MM-DD format
TEAM_SCHEDULE_ENDPOINT = f"{NHL_API_BASE_URL_V1}/club-schedule-season/{{team}}/{{season}}" # team_abbreviation in XXX format, season in YYYYYYYY format
FRANCHISES_ENDPOINT = f"{NHL_API_BASE_URL}/stats/rest/en/franchise?sort=fullName&include=lastSeason.id&include=firstSeason.id"



# Constants
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119 Safari/537.36",
    "Accept": "application/json,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
}

DEFAULT_TIMEOUT = 10  # seconds

# Canonical faceoff dots in NHL coordinates
_DOT_LABELS = np.array([
    "OZ_L", "OZ_R", "OZ_C",
    "NZ_L", "NZ_R", "NZ_C",
    "DZ_L", "DZ_R", "DZ_C"
])

_DOT_XY = np.array([
    ( 69,  22),  # OZ_L
    ( 69, -22),  # OZ_R
    ( 69,   0),  # OZ_C (center - helper dot)
    ( 20,  22),  # NZ_L
    ( 20, -22),  # NZ_R
    (  0,   0),  # NZ_C
    (-69,  22),  # DZ_L
    (-69, -22),  # DZ_R
    (-69,   0),  # DZ_C (center - helper dot)
], dtype=float)