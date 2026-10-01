"""Privacy-preserving Chrome history ingestion.

Only the domain and the visit time of each entry are kept. Full URLs, titles
and search terms are never read into the program's records.
"""

from datetime import date, datetime, timedelta
from typing import Dict, List, Optional
from urllib.parse import urlparse
import shutil
import sqlite3

from .config import CHROME_HISTORY_COPY, CHROME_HISTORY_SOURCE

CHROME_EPOCH_OFFSET_US = 11644473600000000


def copy_chrome_history() -> bool:
    if not CHROME_HISTORY_SOURCE.exists():
        print(f"Chrome History database not found at {CHROME_HISTORY_SOURCE}")
        return False
    CHROME_HISTORY_COPY.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(CHROME_HISTORY_SOURCE, CHROME_HISTORY_COPY)
    return True


def extract_domain(url: str) -> Optional[str]:
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    if domain.startswith("www."):
        domain = domain[4:]
    # keep a single path hint for a couple of host-ambiguous cases
    if domain == "google.com" and parsed.path.startswith("/maps"):
        return "google.com/maps"
    return domain or None


def _to_datetime(chrome_ts: int) -> datetime:
    return datetime.fromtimestamp((chrome_ts - CHROME_EPOCH_OFFSET_US) / 1_000_000)


def _to_chrome(value: datetime) -> int:
    return int(value.timestamp() * 1_000_000) + CHROME_EPOCH_OFFSET_US


def read_entries_for_day(day: date) -> List[Dict]:
    """Sanitized entries for one calendar day (local time)."""
    if not CHROME_HISTORY_COPY.exists():
        return []
    start = datetime.combine(day, datetime.min.time())
    end = start + timedelta(days=1)
    query = """
        SELECT u.url AS url, v.visit_time AS visit_time
        FROM urls u JOIN visits v ON u.id = v.url
        WHERE v.visit_time >= ? AND v.visit_time < ?
        ORDER BY v.visit_time ASC
    """
    conn = sqlite3.connect(f"file:{CHROME_HISTORY_COPY}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(query, (_to_chrome(start), _to_chrome(end))).fetchall()
    finally:
        conn.close()

    entries = []
    for row in rows:
        domain = extract_domain(row["url"])
        if not domain:
            continue
        ts = _to_datetime(row["visit_time"])
        entries.append({"domain": domain, "timestamp": ts.isoformat(), "hour": ts.hour, "minute": ts.minute})
    return entries
