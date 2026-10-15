"""Notes Board: the web tier of a two-tier app (Flask) that stores notes in MySQL."""
import os

import pymysql
from flask import Flask, jsonify, redirect, render_template, request, url_for

app = Flask(__name__)

APP_VERSION = os.environ.get("APP_VERSION", "dev")
MAX_AUTHOR_LENGTH = 50
MAX_NOTE_LENGTH = 500

_schema_ready = False


def get_connection():
    """Open a new connection to the database tier. Settings come from environment variables."""
    return pymysql.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        port=int(os.environ.get("DB_PORT", "3306")),
        user=os.environ.get("DB_USER", "notesapp"),
        password=os.environ.get("DB_PASSWORD", ""),
        database=os.environ.get("DB_NAME", "notesdb"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5,
        autocommit=True,
    )


def ensure_schema():
    """Create the notes table the first time it is needed."""
    global _schema_ready
    if _schema_ready:
        return
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS notes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    author VARCHAR(50) NOT NULL,
                    content VARCHAR(500) NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
    finally:
        conn.close()
    _schema_ready = True


@app.route("/")
def index():
    ensure_schema()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, author, content, created_at FROM notes ORDER BY id DESC LIMIT 50"
            )
            notes = cur.fetchall()
    finally:
        conn.close()
    return render_template("index.html", notes=notes, version=APP_VERSION)


@app.route("/notes", methods=["POST"])
def add_note():
    author = (request.form.get("author") or "").strip()[:MAX_AUTHOR_LENGTH]
    content = (request.form.get("content") or "").strip()[:MAX_NOTE_LENGTH]
    if author and content:
        ensure_schema()
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO notes (author, content) VALUES (%s, %s)",
                    (author, content),
                )
        finally:
            conn.close()
    return redirect(url_for("index"))


@app.route("/api/notes")
def api_notes():
    ensure_schema()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, author, content, created_at FROM notes ORDER BY id DESC LIMIT 50"
            )
            rows = cur.fetchall()
    finally:
        conn.close()
    for row in rows:
        row["created_at"] = row["created_at"].isoformat()
    return jsonify(rows)


@app.route("/health")
def health():
    """Used by Docker and Jenkins to check that the web tier AND the database tier are up."""
    try:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        finally:
            conn.close()
    except pymysql.MySQLError:
        return jsonify(status="degraded", database="down", version=APP_VERSION), 503
    return jsonify(status="ok", database="up", version=APP_VERSION), 200


@app.errorhandler(pymysql.MySQLError)
def database_error(_error):
    return "The database is not reachable right now. Please try again shortly.", 503


if __name__ == "__main__":
    # Local development only. In Docker the app is served by gunicorn (see Dockerfile).
    app.run(host="127.0.0.1", port=5000)