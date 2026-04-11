"""
SQLite база данных для автобан бота.
Хранит: баны, вайтлист, лид-магниты, статистику, логи
"""
import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()

    # Забаненные пользователи
    c.execute("""
        CREATE TABLE IF NOT EXISTS banned (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            reason TEXT DEFAULT 'Отписка от канала',
            banned_at TEXT DEFAULT CURRENT_TIMESTAMP,
            unbanned_at TEXT
        )
    """)

    # Белый список (кого никогда не банить)
    c.execute("""
        CREATE TABLE IF NOT EXISTS whitelist (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            added_by INTEGER,
            added_at TEXT DEFAULT CURRENT_TIMESTAMP,
            comment TEXT
        )
    """)

    # Лид-магниты
    c.execute("""
        CREATE TABLE IF NOT EXISTS lead_magnets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            title TEXT,
            content_text TEXT,
            content_file_id TEXT,
            content_url TEXT,
            invite_link TEXT,
            invite_link_id TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1,
            downloads INTEGER DEFAULT 0
        )
    """)

    # Статистика подписок
    c.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT,
            first_name TEXT,
            event TEXT NOT NULL,  -- subscribe, unsubscribe
            source TEXT,           -- invite_link, search, direct, other
            invite_link TEXT,
            invite_link_name TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Логи действий бота
    c.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            user_id INTEGER,
            details TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Ежедневные отчёты
    c.execute("""
        CREATE TABLE IF NOT EXISTS daily_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE NOT NULL,
            new_subs INTEGER DEFAULT 0,
            unsubs INTEGER DEFAULT 0,
            bans INTEGER DEFAULT 0,
            magnet_downloads INTEGER DEFAULT 0,
            sent_at TEXT
        )
    """)

    conn.commit()
    conn.close()


# ============ ЗАБАЛОЧЕННЫЕ ============

def add_banned(user_id, username=None, first_name=None, reason="Отписка от канала"):
    conn = get_conn()
    conn.execute(
        "INSERT OR IGNORE INTO banned (user_id, username, first_name, reason) VALUES (?, ?, ?, ?)",
        (user_id, username, first_name, reason)
    )
    conn.commit()
    conn.close()
    log_action("ban", user_id, f"Причина: {reason}")


def remove_banned(user_id):
    conn = get_conn()
    conn.execute(
        "UPDATE banned SET unbanned_at = CURRENT_TIMESTAMP WHERE user_id = ?",
        (user_id,)
    )
    conn.commit()
    conn.close()
    log_action("unban", user_id)


def is_banned(user_id):
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM banned WHERE user_id = ? AND unbanned_at IS NULL",
        (user_id,)
    ).fetchone()
    conn.close()
    return row is not None


def get_all_banned():
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM banned WHERE unbanned_at IS NULL ORDER BY banned_at DESC LIMIT 50"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ============ БЕЛЫЙ СПИСОК ============

def add_to_whitelist(user_id, username=None, added_by=None, comment=None):
    conn = get_conn()
    conn.execute(
        "INSERT OR IGNORE INTO whitelist (user_id, username, added_by, comment) VALUES (?, ?, ?, ?)",
        (user_id, username, added_by, comment)
    )
    conn.commit()
    conn.close()
    log_action("whitelist_add", user_id, comment)


def remove_from_whitelist(user_id):
    conn = get_conn()
    conn.execute("DELETE FROM whitelist WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    log_action("whitelist_remove", user_id)


def is_whitelisted(user_id):
    conn = get_conn()
    row = conn.execute("SELECT 1 FROM whitelist WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return row is not None


def get_whitelist():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM whitelist ORDER BY added_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ============ ЛИД-МАГНИТЫ ============

def create_magnet(topic, title, content_text=None, content_file_id=None, content_url=None):
    conn = get_conn()
    cur = conn.execute(
        "INSERT INTO lead_magnets (topic, title, content_text, content_file_id, content_url) VALUES (?, ?, ?, ?, ?)",
        (topic, title, content_text, content_file_id, content_url)
    )
    magnet_id = cur.lastrowid
    conn.commit()
    conn.close()
    log_action("magnet_create", None, f"{topic}: {title}")
    return magnet_id


def update_magnet_link(magnet_id, invite_link, invite_link_id):
    conn = get_conn()
    conn.execute(
        "UPDATE lead_magnets SET invite_link = ?, invite_link_id = ? WHERE id = ?",
        (invite_link, invite_link_id, magnet_id)
    )
    conn.commit()
    conn.close()


def deactivate_magnet(magnet_id):
    conn = get_conn()
    conn.execute(
        "UPDATE lead_magnets SET is_active = 0 WHERE id = ?",
        (magnet_id,)
    )
    conn.commit()
    conn.close()


def get_active_magnets():
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM lead_magnets WHERE is_active = 1 ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_magnet(magnet_id):
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM lead_magnets WHERE id = ?", (magnet_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_magnet_by_invite(invite_link_id):
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM lead_magnets WHERE invite_link_id = ?", (invite_link_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def increment_magnet_downloads(magnet_id):
    conn = get_conn()
    conn.execute(
        "UPDATE lead_magnets SET downloads = downloads + 1 WHERE id = ?",
        (magnet_id,)
    )
    conn.commit()
    conn.close()


# ============ СТАТИСТИКА ПОДПИСОК ============

def log_subscription(user_id, username, first_name, event, source=None, invite_link=None, invite_link_name=None):
    conn = get_conn()
    conn.execute(
        "INSERT INTO subscriptions (user_id, username, first_name, event, source, invite_link, invite_link_name) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (user_id, username, first_name, event, source, invite_link, invite_link_name)
    )
    conn.commit()
    conn.close()


def get_sub_stats():
    conn = get_conn()
    subs = conn.execute("SELECT COUNT(*) FROM subscriptions WHERE event = 'subscribe'").fetchone()[0]
    unsubs = conn.execute("SELECT COUNT(*) FROM subscriptions WHERE event = 'unsubscribe'").fetchone()[0]

    # За сегодня
    today = datetime.now().strftime("%Y-%m-%d")
    subs_today = conn.execute(
        "SELECT COUNT(*) FROM subscriptions WHERE event = 'subscribe' AND date(created_at) = ?", (today,)
    ).fetchone()[0]
    unsubs_today = conn.execute(
        "SELECT COUNT(*) FROM subscriptions WHERE event = 'unsubscribe' AND date(created_at) = ?", (today,)
    ).fetchone()[0]

    # По источникам
    sources = conn.execute(
        "SELECT source, COUNT(*) as cnt FROM subscriptions WHERE source IS NOT NULL GROUP BY source ORDER BY cnt DESC"
    ).fetchall()

    # Последние 10 подписок
    recent = conn.execute(
        "SELECT * FROM subscriptions WHERE event = 'subscribe' ORDER BY created_at DESC LIMIT 10"
    ).fetchall()

    conn.close()

    return {
        "total_subs": subs,
        "total_unsubs": unsubs,
        "subs_today": subs_today,
        "unsubs_today": unsubs_today,
        "net_subs": subs - unsubs,
        "sources": [dict(r) for r in sources],
        "recent_subs": [dict(r) for r in recent],
    }


# ============ ЛОГИ ============

def log_action(action, user_id=None, details=None):
    conn = get_conn()
    conn.execute(
        "INSERT INTO logs (action, user_id, details) VALUES (?, ?, ?)",
        (action, user_id, details)
    )
    conn.commit()
    conn.close()


def get_logs(limit=30):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM logs ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ============ ЕЖЕДНЕВНЫЕ ОТЧЁТЫ ============

def save_daily_report(date=None):
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    conn = get_conn()

    # Проверяем уже ли есть
    existing = conn.execute("SELECT id FROM daily_reports WHERE date = ?", (date,)).fetchone()
    if existing:
        conn.execute("DELETE FROM daily_reports WHERE date = ?", (date,))

    subs = conn.execute(
        "SELECT COUNT(*) FROM subscriptions WHERE date(created_at) = ? AND event = 'subscribe'", (date,)
    ).fetchone()[0]

    unsubs = conn.execute(
        "SELECT COUNT(*) FROM subscriptions WHERE date(created_at) = ? AND event = 'unsubscribe'", (date,)
    ).fetchone()[0]

    bans = conn.execute(
        "SELECT COUNT(*) FROM banned WHERE date(banned_at) = ?", (date,)
    ).fetchone()[0]

    downloads = conn.execute(
        "SELECT SUM(downloads) FROM lead_magnets"
    ).fetchone()[0] or 0

    conn.execute(
        "INSERT INTO daily_reports (date, new_subs, unsubs, bans, magnet_downloads) VALUES (?, ?, ?, ?, ?)",
        (date, subs, unsubs, bans, downloads)
    )
    conn.commit()
    conn.close()


def get_daily_reports(limit=7):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM daily_reports ORDER BY date DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# Инициализируем БД при импорте
init_db()
