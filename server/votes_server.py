#!/usr/bin/env python3
"""Vote API for whatisfabledoing.com. Stdlib only.

GET  /votes -> {"<report url>": count, ...}
POST /vote  {"reportId": "<report url>"} -> {"count": n, "voted": true|false}

One vote per report per voter key (sha256 of salt + client IP + user agent).
Report ids are validated against the live report log so arbitrary ids can't
be written. Per-IP rate limiting. Meant to run on 127.0.0.1 behind nginx,
which must set X-Real-IP.
"""

import hashlib
import json
import os
import re
import sqlite3
import threading
import time
import urllib.request
from collections import defaultdict, deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(os.environ.get("VOTES_PORT", "8127"))
DB_PATH = os.environ.get("VOTES_DB", "/opt/fable-votes/votes.db")
SALT_PATH = os.environ.get("VOTES_SALT_FILE", "/opt/fable-votes/salt")
REPORTS_URL = os.environ.get(
    "VOTES_REPORTS_URL",
    "https://whatisfabledoing.com/data/fable-field-reports.md",
)
ALLOWED_ORIGINS = {
    "https://whatisfabledoing.com",
    "https://www.whatisfabledoing.com",
    "http://localhost:8642",
    "http://127.0.0.1:8642",
}
REPORTS_TTL = 300          # seconds to cache the known-report-id set
RATE_GET = (120, 60)       # max requests per window-seconds, per IP
RATE_POST = (20, 600)

_db_lock = threading.Lock()
_rate_lock = threading.Lock()
_rate: dict = defaultdict(deque)
_reports_lock = threading.Lock()
_known_reports: set = set()
_reports_fetched_at = 0.0


def get_salt() -> str:
    try:
        with open(SALT_PATH) as f:
            return f.read().strip()
    except FileNotFoundError:
        salt = os.urandom(32).hex()
        fd = os.open(SALT_PATH, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as f:
            f.write(salt)
        return salt


SALT = None  # initialised in main()


def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db() -> None:
    with db() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS votes (
                 report_id TEXT NOT NULL,
                 voter_key TEXT NOT NULL,
                 created_at TEXT NOT NULL DEFAULT (datetime('now')),
                 PRIMARY KEY (report_id, voter_key)
               )"""
        )


def known_reports() -> set:
    """Report URLs currently in the published log, cached for REPORTS_TTL."""
    global _known_reports, _reports_fetched_at
    with _reports_lock:
        if _known_reports and time.time() - _reports_fetched_at < REPORTS_TTL:
            return _known_reports
        try:
            with urllib.request.urlopen(REPORTS_URL, timeout=10) as res:
                text = res.read().decode("utf-8", "replace")
            found = set(re.findall(r"^###\s+\[.+?\]\((\S+?)\)", text, re.M))
            if found:
                _known_reports = found
                _reports_fetched_at = time.time()
        except OSError:
            pass  # keep the previous set; empty set rejects all votes
        return _known_reports


def rate_limited(ip: str, kind: str) -> bool:
    limit, window = RATE_POST if kind == "post" else RATE_GET
    now = time.time()
    key = f"{kind}:{ip}"
    with _rate_lock:
        q = _rate[key]
        while q and q[0] < now - window:
            q.popleft()
        if len(q) >= limit:
            return True
        q.append(now)
        return False


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _ip(self) -> str:
        return self.headers.get("X-Real-IP") or self.client_address[0]

    def _send(self, code: int, body: dict) -> None:
        data = json.dumps(body).encode()
        self.send_response(code)
        origin = self.headers.get("Origin", "")
        if origin in ALLOWED_ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self.send_response(204)
        origin = self.headers.get("Origin", "")
        if origin in ALLOWED_ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Access-Control-Max-Age", "86400")
            self.send_header("Vary", "Origin")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):
        if self.path != "/votes":
            return self._send(404, {"error": "not found"})
        if rate_limited(self._ip(), "get"):
            return self._send(429, {"error": "rate limited"})
        with _db_lock, db() as conn:
            rows = conn.execute(
                "SELECT report_id, COUNT(*) FROM votes GROUP BY report_id"
            ).fetchall()
        self._send(200, {r: c for r, c in rows})

    def do_POST(self):
        if self.path != "/vote":
            return self._send(404, {"error": "not found"})
        ip = self._ip()
        if rate_limited(ip, "post"):
            return self._send(429, {"error": "rate limited"})
        try:
            length = min(int(self.headers.get("Content-Length", 0)), 4096)
            payload = json.loads(self.rfile.read(length) or b"{}")
            report_id = payload.get("reportId", "")
        except (ValueError, json.JSONDecodeError):
            return self._send(400, {"error": "bad request"})
        if not isinstance(report_id, str) or not (0 < len(report_id) <= 500):
            return self._send(400, {"error": "bad reportId"})
        if report_id not in known_reports():
            return self._send(404, {"error": "unknown reportId"})

        ua = self.headers.get("User-Agent", "")
        voter_key = hashlib.sha256(f"{SALT}|{ip}|{ua}".encode()).hexdigest()[:16]
        with _db_lock, db() as conn:
            cur = conn.execute(
                "INSERT OR IGNORE INTO votes (report_id, voter_key) VALUES (?, ?)",
                (report_id, voter_key),
            )
            count = conn.execute(
                "SELECT COUNT(*) FROM votes WHERE report_id = ?", (report_id,)
            ).fetchone()[0]
        self._send(200, {"count": count, "voted": cur.rowcount > 0})

    def log_message(self, fmt, *args):
        print(f"{self._ip()} {fmt % args}", flush=True)


def main():
    global SALT
    SALT = get_salt()
    init_db()
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"fable-votes listening on 127.0.0.1:{PORT}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
