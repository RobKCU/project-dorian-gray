"""Privacy-preserving Chrome history ingestion."""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse
import shutil
import sqlite3

from .config import CHROME_HISTORY_COPY, CHROME_HISTORY_SOURCE


def copy_chrome_history() -> bool:
    if not CHROME_HISTORY_SOURCE.exists():
        print(f"Chrome History database not found at {CHROME_HISTORY_SOURCE}")
        return False

    CHROME_HISTORY_COPY.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(CHROME_HISTORY_SOURCE, CHROME_HISTORY_COPY)
    print(f"Copied Chrome history to {CHROME_HISTORY_COPY}")
    return True


def extract_domain(url: str) -> Optional[str]:
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    if domain.startswith("www."):
        domain = domain[4:]
    return domain or None


def _chrome_timestamp_to_datetime(chrome_timestamp: int) -> datetime:
    unix_timestamp_us = chrome_timestamp - 11644473600000000
    return datetime.fromtimestamp(unix_timestamp_us / 1_000_000)


def _datetime_to_chrome_timestamp(value: datetime) -> int:
    return int(value.timestamp() * 1_000_000) + 11644473600000000


def read_entries_for_day(target_date: datetime) -> List[Dict]:
    if not CHROME_HISTORY_COPY.exists():
        print("History copy is missing. Run with --copy-history first.")
        return []

    day_start = datetime.combine(target_date.date(), datetime.min.time())
    day_end = day_start + timedelta(days=1)

    query = """
        SELECT DISTINCT u.url, v.visit_time
        FROM urls u
        JOIN visits v ON u.id = v.url
        WHERE v.visit_time >= ? AND v.visit_time < ?
        ORDER BY v.visit_time ASC
    """

    entries = []
    conn = sqlite3.connect(CHROME_HISTORY_COPY)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            query,
            (_datetime_to_chrome_timestamp(day_start), _datetime_to_chrome_timestamp(day_end)),
        ).fetchall()
    finally:
        conn.close()

    for row in rows:
        domain = extract_domain(row["url"])
        if not domain:
            continue
        timestamp = _chrome_timestamp_to_datetime(row["visit_time"])
        entries.append(
            {
                "domain": domain,
                "timestamp": timestamp.isoformat(),
                "hour": timestamp.hour,
                "minute": timestamp.minute,
            }
        )

    return entries

