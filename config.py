# =============================================================================
# DAILY FEED — CONFIGURATION
# Edit this file to add/remove assets, news sources, or keyword filters.
# =============================================================================

# --- ASSET TICKERS (Yahoo Finance) -------------------------------------------
# Key = display name shown in output, Value = Yahoo Finance ticker symbol.

ASSETS = {
    "commodities": {
        "Gold":             "GC=F",
        "Silver":           "SI=F",
        "Soybeans":         "ZS=F",
        "Sugar #11 (Raw)":  "SB=F",   # Note: London Sugar #5 (white) isn't on Yahoo Finance.
                                       # Sugar #11 is the primary global raw sugar benchmark.
    },
    "fx": {
        "AUD/USD":          "AUDUSD=X",
    },
    "indices": {
        "S&P 500":              "^GSPC",
        "US 10Y Yield (%)":     "^TNX",   # 10-Year US Treasury yield — value is a percentage, e.g. 4.25 = 4.25%
        "Hang Seng 50":         "^HSI",
        "South Africa Top 40":  "^J200",   # FTSE/JSE — verify ticker if data looks wrong
        "Switzerland SMI":      "^SSMI",
        "ASX 200 (XJO)":        "^AXJO",
    },
    "stocks": {
        "Palantir":             "PLTR",
        "McDonald's":           "MCD",
        "Tesla":                "TSLA",
        "Alphabet":             "GOOGL",
        "Lockheed Martin":      "LMT",   # #1 defence contractor by revenue
        "RTX (Raytheon)":       "RTX",   # #2 defence contractor
        "Northrop Grumman":     "NOC",   # #3 defence contractor
    },
}

# --- NEWS RSS FEEDS ----------------------------------------------------------
# Add or remove feeds freely. Any valid RSS URL works.

NEWS_FEEDS = [
    {"name": "BBC World",    "url": "http://feeds.bbci.co.uk/news/world/rss.xml"},
    {"name": "Al Jazeera",   "url": "https://www.aljazeera.com/xml/rss/all.xml"},
    {"name": "The Guardian", "url": "https://www.theguardian.com/world/rss"},
]

# --- NEWS KEYWORD FILTER -----------------------------------------------------
# A headline + summary must contain at least one of these to be included.
# More terms = more headlines captured. Remove terms to tighten the filter.

NEWS_KEYWORDS = [
    # Conflict & security
    "war", "conflict", "attack", "military", "nuclear", "missile",
    "sanctions", "invasion", "ceasefire", "coup", "siege", "troops", "airstrike",
    # Politics & diplomacy
    "election", "president", "prime minister", "summit", "treaty",
    "diplomacy", "veto", "nato", "un security council",
    # Economics & markets
    "recession", "inflation", "interest rate", "federal reserve",
    "gdp", "trade war", "tariff", "debt crisis", "default", "imf",
    # Energy & resources
    "oil", "gas", "opec", "energy crisis", "blackout",
    # Humanitarian & disasters
    "earthquake", "pandemic", "outbreak", "tsunami", "hurricane",
    "famine", "drought", "flood", "crisis", "collapse",
    # High-impact events
    "assassination", "explosion", "mass casualty", "hostage",
]

# Max headlines to include in final output
MAX_NEWS_ITEMS = 8

# Max entries to scan per RSS feed (keep high to find enough after filtering)
MAX_SCAN_PER_FEED = 40

# --- OUTPUT ------------------------------------------------------------------

OUTPUT_DIR    = "output"
JSON_FILENAME = "daily_feed.json"
MD_FILENAME   = "daily_feed.md"

# --- GIT / GITHUB ------------------------------------------------------------
# Set True to auto-commit and push the output folder after each run.
# Requirements: git installed, repo initialised, remote (GitHub) configured.

AUTO_GIT_PUSH = True
