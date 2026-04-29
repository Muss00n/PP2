"""
db.py – all database interactions via psycopg2.

Connection settings are read from environment variables (or the defaults
below).  Set them before running:

    export DB_HOST=localhost
    export DB_PORT=5432
    export DB_NAME=snake_db
    export DB_USER=postgres
    export DB_PASS=secret
"""
import os
from datetime import datetime
from typing import Optional

try:
    import psycopg2
    import psycopg2.extras
    _PSYCOPG2_AVAILABLE = True
except ImportError:
    _PSYCOPG2_AVAILABLE = False
    print("[db] psycopg2 not installed – leaderboard features disabled.")

# ── Connection parameters ─────────────────────────────────────────────────────
DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "port":     int(os.getenv("DB_PORT", 5432)),
    "dbname":   os.getenv("DB_NAME", "snake_db"),
    "user":     os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASS", ""),
}

# ── Schema ────────────────────────────────────────────────────────────────────
_SCHEMA = """
CREATE TABLE IF NOT EXISTS players (
    id       SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS game_sessions (
    id            SERIAL PRIMARY KEY,
    player_id     INTEGER REFERENCES players(id),
    score         INTEGER   NOT NULL,
    level_reached INTEGER   NOT NULL,
    played_at     TIMESTAMP DEFAULT NOW()
);
"""


def _connect():
    if not _PSYCOPG2_AVAILABLE:
        return None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"[db] Connection failed: {e}")
        return None


def init_db() -> bool:
    """Create tables if they don't exist yet. Returns True on success."""
    conn = _connect()
    if conn is None:
        return False
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(_SCHEMA)
        return True
    except Exception as e:
        print(f"[db] init_db error: {e}")
        return False
    finally:
        conn.close()


def get_or_create_player(username: str) -> Optional[int]:
    """Return the player id, inserting a new row if needed."""
    conn = _connect()
    if conn is None:
        return None
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO players (username) VALUES (%s) "
                    "ON CONFLICT (username) DO NOTHING",
                    (username,),
                )
                cur.execute(
                    "SELECT id FROM players WHERE username = %s", (username,)
                )
                row = cur.fetchone()
                return row[0] if row else None
    except Exception as e:
        print(f"[db] get_or_create_player error: {e}")
        return None
    finally:
        conn.close()


def save_session(player_id: int, score: int, level_reached: int) -> bool:
    """Persist a finished game session."""
    conn = _connect()
    if conn is None:
        return False
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO game_sessions (player_id, score, level_reached) "
                    "VALUES (%s, %s, %s)",
                    (player_id, score, level_reached),
                )
        return True
    except Exception as e:
        print(f"[db] save_session error: {e}")
        return False
    finally:
        conn.close()


def get_top10():
    """
    Return a list of dicts for the top-10 all-time scores:
      rank, username, score, level_reached, played_at
    """
    conn = _connect()
    if conn is None:
        return []
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(
                """
                SELECT
                    ROW_NUMBER() OVER (ORDER BY gs.score DESC) AS rank,
                    p.username,
                    gs.score,
                    gs.level_reached,
                    gs.played_at
                FROM game_sessions gs
                JOIN players p ON p.id = gs.player_id
                ORDER BY gs.score DESC
                LIMIT 10
                """
            )
            return [dict(row) for row in cur.fetchall()]
    except Exception as e:
        print(f"[db] get_top10 error: {e}")
        return []
    finally:
        conn.close()


def get_personal_best(player_id: int) -> int:
    """Return the highest score ever recorded for this player (0 if none)."""
    conn = _connect()
    if conn is None:
        return 0
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COALESCE(MAX(score), 0) FROM game_sessions WHERE player_id = %s",
                (player_id,),
            )
            row = cur.fetchone()
            return row[0] if row else 0
    except Exception as e:
        print(f"[db] get_personal_best error: {e}")
        return 0
    finally:
        conn.close()
