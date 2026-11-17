"""Small single-instance demo quotas. Never stores questions or answers."""
from datetime import datetime, timezone
from pathlib import Path
import os
import sqlite3
import time

ROOT = Path(__file__).resolve().parents[1]

class DemoLimit(Exception):
    """A public-friendly reason an API request was not allowed."""

def reserve_request(state, path=None, now=None, daily_limit=None):
    now = time.time() if now is None else now
    session_limit = int(os.getenv('SESSION_REQUEST_LIMIT', '20'))
    cooldown = int(os.getenv('REQUEST_COOLDOWN_SECONDS', '10'))
    if state.get('request_count', 0) >= session_limit:
        raise DemoLimit('You’ve reached this session’s demo limit. Contact Aegis to explore a tailored demonstration.')
    if now - state.get('last_request', float('-inf')) < cooldown:
        raise DemoLimit('Please wait a few seconds before asking another question.')
    limit = int(os.getenv('DAILY_REQUEST_LIMIT', '100')) if daily_limit is None else daily_limit
    db_path = Path(path) if path else ROOT / '.runtime' / 'usage.sqlite3'
    db_path.parent.mkdir(parents=True, exist_ok=True)
    day = datetime.fromtimestamp(now, timezone.utc).date().isoformat()
    with sqlite3.connect(db_path, timeout=10) as db:
        db.execute('CREATE TABLE IF NOT EXISTS usage (day TEXT PRIMARY KEY, requests INTEGER NOT NULL)')
        db.execute('BEGIN IMMEDIATE')
        used = db.execute('SELECT requests FROM usage WHERE day = ?', (day,)).fetchone()
        if (used[0] if used else 0) >= limit:
            raise DemoLimit('The demo has reached its daily question limit. Please try again tomorrow or contact Aegis.')
        db.execute('INSERT INTO usage VALUES (?, 1) ON CONFLICT(day) DO UPDATE SET requests = requests + 1', (day,))
        db.execute('DELETE FROM usage WHERE day < ?', (day,))
    # Reserve before any paid API work. Failures count toward the cap, too.
    state['request_count'] = state.get('request_count', 0) + 1
    state['last_request'] = now
