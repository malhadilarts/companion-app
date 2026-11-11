import json
import sqlite3
import time
from pathlib import Path
from config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS identity (
    id INTEGER PRIMARY KEY CHECK (id=1),
    name TEXT NOT NULL,
    pubkey TEXT,
    privkey TEXT,
    created_at REAL NOT NULL,
    registered INTEGER DEFAULT 0,
    reg_code TEXT
);
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kind TEXT NOT NULL,          -- fact | episode | insight | document
    content TEXT NOT NULL,
    embedding BLOB,
    source TEXT,
    pinned INTEGER DEFAULT 0,
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    model TEXT,
    created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS levels (
    level TEXT PRIMARY KEY,
    unlocked INTEGER DEFAULT 0,
    unlocked_at REAL
);
CREATE TABLE IF NOT EXISTS tools (
    name TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    schema TEXT NOT NULL,
    enabled INTEGER DEFAULT 1,
    created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    content TEXT NOT NULL,
    chunks INTEGER DEFAULT 0,
    created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS scheduled (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    task TEXT NOT NULL,
    run_at REAL NOT NULL,
    repeat_seconds INTEGER DEFAULT 0,
    enabled INTEGER DEFAULT 1,
    last_run REAL
);
CREATE TABLE IF NOT EXISTS network (
    endpoint TEXT PRIMARY KEY,
    allowed INTEGER DEFAULT 0
);
"""

DEFAULT_LEVELS = ["S1","S2","S3","S4","S5","S6","S7","S8","S9","S10",
                  "B1","B2","B3","B4","B5","B6","B7","B8"]

def conn():
    c = sqlite3.connect(str(DB_PATH))
    c.row_factory = sqlite3.Row
    return c

def init():
    c = conn()
    c.executescript(SCHEMA)
    for lvl in DEFAULT_LEVELS:
        c.execute("INSERT OR IGNORE INTO levels(level,unlocked) VALUES (?,0)", (lvl,))
    # unlock S1 by default
    c.execute("UPDATE levels SET unlocked=1, unlocked_at=? WHERE level='S1' AND unlocked=0", (time.time(),))
    c.execute("INSERT OR IGNORE INTO settings(key,value) VALUES ('current_level','S1')")
    c.execute("INSERT OR IGNORE INTO settings(key,value) VALUES ('airgap','0')")
    c.execute("INSERT OR IGNORE INTO settings(key,value) VALUES ('guardian','1')")
    c.execute("INSERT OR IGNORE INTO network(endpoint,allowed) VALUES ('ollama',1)")
    c.execute("INSERT OR IGNORE INTO network(endpoint,allowed) VALUES ('anthropic',0)")
    c.execute("INSERT OR IGNORE INTO network(endpoint,allowed) VALUES ('gemini',0)")
    c.execute("INSERT OR IGNORE INTO network(endpoint,allowed) VALUES ('web',0)")
    c.commit()
    c.close()

def get_setting(key, default=None):
    c = conn()
    r = c.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    c.close()
    return r["value"] if r else default

def set_setting(key, value):
    c = conn()
    c.execute("INSERT INTO settings(key,value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
              (key, str(value)))
    c.commit()
    c.close()

def unlock_level(level):
    c = conn()
    c.execute("UPDATE levels SET unlocked=1, unlocked_at=? WHERE level=? AND unlocked=0", (time.time(), level))
    c.commit()
    c.close()

def is_unlocked(level):
    c = conn()
    r = c.execute("SELECT unlocked FROM levels WHERE level=?", (level,)).fetchone()
    c.close()
    return bool(r and r["unlocked"])

def all_levels():
    c = conn()
    rows = c.execute("SELECT level,unlocked,unlocked_at FROM levels").fetchall()
    c.close()
    return [dict(r) for r in rows]

def current_level():
    return get_setting("current_level", "S1")

def set_current_level(lvl):
    set_setting("current_level", lvl)
    unlock_level(lvl)

init()
