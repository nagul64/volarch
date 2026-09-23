import json
import sqlite3
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).resolve().parent.parent / "volunteer.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS students (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    name               TEXT NOT NULL,
    school             TEXT,
    grade              TEXT,
    zip_code           TEXT,
    latitude           REAL,
    longitude          REAL,
    max_hours_per_week INTEGER,
    skills             TEXT NOT NULL DEFAULT '[]',
    interests          TEXT NOT NULL DEFAULT '[]',
    bio                TEXT
);

CREATE TABLE IF NOT EXISTS opportunities (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    title            TEXT NOT NULL,
    org_name         TEXT,
    category         TEXT,
    description      TEXT,
    tags             TEXT NOT NULL DEFAULT '[]',
    zip_code         TEXT,
    latitude         REAL,
    longitude        REAL,
    hours_min        INTEGER,
    hours_max        INTEGER,
    required_skills  TEXT NOT NULL DEFAULT '[]',
    helpful_skills   TEXT NOT NULL DEFAULT '[]'
);
"""


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def json_loads(value: str | None) -> list[str]:
    if not value:
        return []
    return json.loads(value)


def to_dict(row: sqlite3.Row) -> dict[str, Any]:
    d = dict(row)
    if "skills" in d:
        d["skills"] = json_loads(d.get("skills"))
    if "interests" in d:
        d["interests"] = json_loads(d.get("interests"))
    if "tags" in d:
        d["tags"] = json_loads(d.get("tags"))
    if "required_skills" in d:
        d["required_skills"] = json_loads(d.get("required_skills"))
    if "helpful_skills" in d:
        d["helpful_skills"] = json_loads(d.get("helpful_skills"))
    return d


def init_db() -> None:
    conn = get_conn()
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()


def count_rows(conn: sqlite3.Connection, table: str) -> int:
    return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def insert_student(conn: sqlite3.Connection, s: dict[str, Any]) -> None:
    conn.execute(
        """INSERT INTO students
           (name, school, grade, zip_code, latitude, longitude,
            max_hours_per_week, skills, interests, bio)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            s["name"], s["school"], s["grade"], s["zip_code"],
            s["latitude"], s["longitude"], s["max_hours_per_week"],
            json.dumps(s.get("skills", [])), json.dumps(s.get("interests", [])),
            s.get("bio", ""),
        ),
    )


def insert_opportunity(conn: sqlite3.Connection, o: dict[str, Any]) -> None:
    conn.execute(
        """INSERT INTO opportunities
           (title, org_name, category, description, tags, zip_code,
            latitude, longitude, hours_min, hours_max,
            required_skills, helpful_skills)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            o["title"], o["org_name"], o["category"], o["description"],
            json.dumps(o.get("tags", [])), o["zip_code"], o["latitude"],
            o["longitude"], o["hours_min"], o["hours_max"],
            json.dumps(o.get("required_skills", [])),
            json.dumps(o.get("helpful_skills", [])),
        ),
    )