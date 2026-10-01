"""Configuration for the Dorian Gray bot (reboot)."""

from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent.parent

# DORIAN_DATA_DIR / DORIAN_REVIEW_DIR let tests and alternative installs keep
# state and images somewhere other than the code folder.
DATA_DIR = Path(os.environ.get("DORIAN_DATA_DIR", BASE_DIR / "data"))
REVIEW_DIR = Path(os.environ.get("DORIAN_REVIEW_DIR", BASE_DIR / "review"))

INPUTS_DIR = DATA_DIR / "inputs"
BASE_PORTRAIT_PATH = Path(os.environ.get("DORIAN_BASE_PORTRAIT", INPUTS_DIR / "base_portrait.jpg"))
STATE_FILE = DATA_DIR / "state.json"
CHAIN_DIR = DATA_DIR / "chain"          # the image lineage: day_0001.jpg, day_0002.jpg, ...
RECORDS_DIR = DATA_DIR / "records"      # per-day prompt/scores/moves (local only)
LOG_FILE = DATA_DIR / "logs" / "run.log"
BROWSER_HISTORY_DIR = DATA_DIR / "browser_history"
CHROME_HISTORY_COPY = BROWSER_HISTORY_DIR / "History.copy.sqlite"
CHROME_HISTORY_SOURCE = Path(
    os.environ.get(
        "DORIAN_CHROME_HISTORY",
        Path.home() / "Library" / "Application Support" / "Google" / "Chrome" / "Default" / "History",
    )
)

# --- Image generation -------------------------------------------------------
IMAGE_MODEL = os.environ.get("DORIAN_IMAGE_MODEL", "gpt-image-1.5")
IMAGE_QUALITY = os.environ.get("DORIAN_IMAGE_QUALITY", "medium")
IMAGE_SIZE = os.environ.get("DORIAN_IMAGE_SIZE", "1024x1536")  # portrait, 2:3
# Each day's image is saved as a JPEG and the next day edits that JPEG.
# Generational JPEG loss is part of the work.
CHAIN_JPEG_QUALITY = int(os.environ.get("DORIAN_CHAIN_JPEG_QUALITY", "82"))

# --- Scoring / selection ----------------------------------------------------
LATE_NIGHT_THRESHOLD = 23.5
EARLY_MORNING_THRESHOLD = 6.0
WEATHER_RATE = 0.30            # how fast "recent weather" follows each day
MAX_CATCHUP_DAYS = 14          # missed days are folded into ONE update
AXIS_MOVES_PER_DAY = 2         # change budget: axis-driven moves per day
MIN_POLE_SALIENCE = 0.12
CHANNEL_REST_DAYS = 4          # a channel just used is penalised for ~this long
MOVE_REST_DAYS = 10            # the same exact move is penalised for ~this long
CAPTION_NO_REPEAT = 12         # a caption word is not reused within this many posts

# --- Bluesky ----------------------------------------------------------------
BLUESKY_SERVICE = "https://bsky.social"
IMAGE_POST_LIMIT_BYTES = 2_000_000


ACTIVITY_CATEGORIES = {
    "generative_ai": [
        "chatgpt.com", "openai.com", "claude.ai", "anthropic.com", "gemini.google.com",
        "perplexity.ai", "copilot.microsoft.com", "sora.com", "midjourney.com",
    ],
    "email_admin": ["gmail.com", "mail.google.com", "outlook.com", "outlook.live.com", "yahoo.com"],
    "search": ["google.com", "bing.com", "duckduckgo.com", "startpage.com"],
    "social_media": [
        "bsky.app", "twitter.com", "x.com", "facebook.com", "instagram.com",
        "tiktok.com", "reddit.com", "threads.net", "linkedin.com",
    ],
    "video_streaming": [
        "youtube.com", "netflix.com", "hulu.com", "disneyplus.com", "primevideo.com",
        "twitch.tv", "max.com", "vimeo.com",
    ],
    "news": [
        "bbc.com", "bbc.co.uk", "cnn.com", "nytimes.com", "theguardian.com", "reuters.com",
        "apnews.com", "wsj.com", "politico.com", "axios.com", "theverge.com",
        "arstechnica.com", "news.ycombinator.com", "washingtonpost.com", "theatlantic.com",
        "newyorker.com", "ft.com", "economist.com",
    ],
    "research_reference": [
        "scholar.google.com", "arxiv.org", "jstor.org", "wikipedia.org", "stackoverflow.com",
        "stackexchange.com", "github.com", "gitlab.com", "muse.jhu.edu", "philpapers.org",
    ],
    "archives_primary_sources": [
        "archive.org", "loc.gov", "archives.gov", "hathitrust.org", "doi.org", "ncbi.nlm.nih.gov",
    ],
    "work_tools": [
        "notion.so", "asana.com", "todoist.com", "trello.com", "slack.com", "discord.com",
        "zoom.us", "docs.google.com", "sheets.google.com", "drive.google.com",
        "jira.atlassian.net", "figma.com", "overleaf.com", "canvas", "courseworks",
    ],
    "shopping": ["amazon.com", "ebay.com", "etsy.com", "shopify.com", "target.com", "walmart.com"],
    "health": ["healthline.com", "mayoclinic.org", "webmd.com", "drugs.com", "mychart"],
    "finance": [
        "chase.com", "wellsfargo.com", "paypal.com", "stripe.com", "coinbase.com",
        "fidelity.com", "vanguard.com", "marketwatch.com", "finance.yahoo.com", "schwab.com",
    ],
    "education_university": [".edu", "coursera.org", "udemy.com", "edx.org", "khanacademy.org"],
    "entertainment_culture": [
        "spotify.com", "medium.com", "substack.com", "letterboxd.com", "goodreads.com", "imdb.com",
    ],
    "maps_travel_local": [
        "google.com/maps", "maps.google.com", "openstreetmap.org", "tripadvisor.com",
        "yelp.com", "booking.com", "airbnb.com",
    ],
    # Kept deliberately: the planning chats insisted this category not be forgotten.
    # Classified locally only; never leaves the machine.
    "adult": [
        "pornhub.com", "xvideos.com", "xnxx.com", "xhamster.com", "redtube.com",
        "youporn.com", "onlyfans.com", "chaturbate.com", "spankbang.com",
    ],
}
