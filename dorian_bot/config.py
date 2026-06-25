"""Configuration for the Dorian Gray Bluesky bot."""

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
BROWSER_HISTORY_DIR = DATA_DIR / "browser_history"
INPUTS_DIR = DATA_DIR / "inputs"
OUTPUTS_DIR = DATA_DIR / "outputs"
DAILY_OUTPUTS_DIR = OUTPUTS_DIR / "daily"

BASE_PORTRAIT_PATH = INPUTS_DIR / "base_portrait.jpg"
PORTRAIT_STATE_FILE = DATA_DIR / "portrait_state.json"
CHROME_HISTORY_COPY = BROWSER_HISTORY_DIR / "History.copy.sqlite"
CHROME_HISTORY_SOURCE = (
    Path.home()
    / "Library"
    / "Application Support"
    / "Google"
    / "Chrome"
    / "Default"
    / "History"
)

LATE_NIGHT_THRESHOLD = 23.5
EARLY_MORNING_THRESHOLD = 6.0
AXIS_UPDATE_RATE = 0.15

BLUESKY_SERVICE = "https://bsky.social"
IMAGE_POST_LIMIT_BYTES = 2_000_000

ACTIVITY_CATEGORIES = {
    "generative_ai": [
        "chatgpt.com",
        "openai.com",
        "claude.ai",
        "anthropic.com",
        "gemini.google.com",
        "perplexity.ai",
        "copilot.microsoft.com",
    ],
    "email_admin": [
        "gmail.com",
        "mail.google.com",
        "outlook.com",
        "outlook.live.com",
        "yahoo.com",
    ],
    "search": [
        "google.com",
        "bing.com",
        "duckduckgo.com",
        "startpage.com",
    ],
    "social_media": [
        "bsky.app",
        "twitter.com",
        "x.com",
        "facebook.com",
        "instagram.com",
        "tiktok.com",
        "reddit.com",
        "threads.net",
    ],
    "video_streaming": [
        "youtube.com",
        "netflix.com",
        "hulu.com",
        "disneyplus.com",
        "primevideo.com",
        "twitch.tv",
    ],
    "news": [
        "bbc.com",
        "cnn.com",
        "nytimes.com",
        "theguardian.com",
        "reuters.com",
        "apnews.com",
        "wsj.com",
        "politico.com",
        "axios.com",
        "theverge.com",
        "arstechnica.com",
        "news.ycombinator.com",
    ],
    "research_reference": [
        "scholar.google.com",
        "arxiv.org",
        "jstor.org",
        "wikipedia.org",
        "stackoverflow.com",
        "stackexchange.com",
        "github.com",
        "gitlab.com",
    ],
    "archives_primary_sources": [
        "archive.org",
        "loc.gov",
        "archives.gov",
        "hathitrust.org",
        "doi.org",
        "pmcentral.nih.gov",
    ],
    "work_tools": [
        "notion.so",
        "asana.com",
        "todoist.com",
        "trello.com",
        "slack.com",
        "discord.com",
        "zoom.us",
        "docs.google.com",
        "sheets.google.com",
        "drive.google.com",
        "github.com",
        "jira.atlassian.net",
        "figma.com",
    ],
    "shopping": [
        "amazon.com",
        "ebay.com",
        "etsy.com",
        "shopify.com",
    ],
    "health": [
        "healthline.com",
        "mayoclinic.org",
        "webmd.com",
        "drugs.com",
        "symptomchecker",
    ],
    "finance": [
        "chase.com",
        "wellsfargo.com",
        "paypal.com",
        "stripe.com",
        "coinbase.com",
        "fidelity.com",
        "vanguard.com",
        "marketwatch.com",
        "yahoofinance.com",
    ],
    "education_university": [
        ".edu",
        "coursera.org",
        "udemy.com",
        "edx.org",
        "khanacademy.org",
    ],
    "entertainment_culture": [
        "spotify.com",
        "medium.com",
        "substack.com",
        "letterboxd.com",
        "goodreads.com",
        "imdb.com",
    ],
    "maps_travel_local": [
        "google.com/maps",
        "maps.google.com",
        "openstreetmap.org",
        "tripadvisor.com",
        "yelp.com",
        "booking.com",
        "airbnb.com",
    ],
}

