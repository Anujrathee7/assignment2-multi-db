"""Multi-database manager: a Flask back end serving three separate SQLite databases.

Every database/table name coming from the client is checked against the real
schema before it is used in SQL, and all values go through ? placeholders.
"""
import os
import sqlite3
from contextlib import contextmanager

from flask import Flask, abort, jsonify, render_template, request

from seed import SCHEMAS, db_path, seed_all, seed_database

app = Flask(__name__)

DATABASES = {
    "library": {"label": "Library", "description": "Books and library members"},
    "school": {"label": "School", "description": "Students and courses"},
    "store": {"label": "Store", "description": "Products and customer orders"},
}


@contextmanager
def connect(db):
    """Open a database, commit on success, and always close the file."""
    if db not in DATABASES:
        abort(404, f"Unknown database '{db}'")
    conn = sqlite3.connect(db_path(db))
    conn.row_factory = sqlite3.Row
    try:
        with conn:
            yield conn
    finally:
        conn.close()


def table_names(conn):
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY rowid"
    )
    return [r["name"] for r in rows]


def columns(conn, table):
    if table not in table_names(conn):
        abort(404, f"Unknown table '{table}'")
    return [
        {"name": c["name"], "type": c["type"], "notnull": bool(c["notnull"]), "pk": bool(c["pk"])}
        for c in conn.execute(f"PRAGMA table_info({table})")
    ]


def editable_values(cols, payload):
    """Pick the non-key columns out of a JSON payload, converting types."""
    names, values = [], []
    for col in cols:
        if col["pk"] or col["name"] not in payload:
            continue
        value = payload[col["name"]]
        if value == "":
            value = None
        elif value is not None and col["type"] == "INTEGER":
            value = int(value)
        elif value is not None and col["type"] == "REAL":
            value = float(value)
        if value is None and col["notnull"]:
            abort(400, f"'{col['name']}' is required")
        names.append(col["name"])
        values.append(value)
    return names, values


@app.errorhandler(400)
@app.errorhandler(404)
def json_error(err):
    return jsonify(error=err.description), err.code


@app.errorhandler(ValueError)
def bad_value(err):
    return jsonify(error=f"Invalid value: {err}"), 400


@app.route("/")
def index():
    return render_template("index.html")


@app.get("/api/databases")
def list_databases():
    result = []
    for key, meta in DATABASES.items():
        with connect(key) as conn:
            tables = [
                {"name": t, "rows": conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]}
                for t in table_names(conn)
            ]
        result.append({"key": key, **meta, "tables": tables})
    return jsonify(result)


@app.get("/api/<db>/<table>")
def read_rows(db, table):
    with connect(db) as conn:
        cols = columns(conn, table)
        rows = [dict(r) for r in conn.execute(f"SELECT * FROM {table} ORDER BY id")]
    return jsonify(columns=cols, rows=rows)


@app.post("/api/<db>/<table>")
def create_row(db, table):
    with connect(db) as conn:
        names, values = editable_values(columns(conn, table), request.get_json(force=True))
        cur = conn.execute(
            f"INSERT INTO {table} ({', '.join(names)}) VALUES ({', '.join('?' for _ in names)})",
            values,
        )
        return jsonify(id=cur.lastrowid), 201


@app.put("/api/<db>/<table>/<int:row_id>")
def update_row(db, table, row_id):
    with connect(db) as conn:
        names, values = editable_values(columns(conn, table), request.get_json(force=True))
        cur = conn.execute(
            f"UPDATE {table} SET {', '.join(f'{n} = ?' for n in names)} WHERE id = ?",
            [*values, row_id],
        )
        if cur.rowcount == 0:
            abort(404, f"No row with id {row_id}")
    return jsonify(ok=True)


@app.delete("/api/<db>/<table>/<int:row_id>")
def delete_row(db, table, row_id):
    with connect(db) as conn:
        columns(conn, table)  # validates the table name
        cur = conn.execute(f"DELETE FROM {table} WHERE id = ?", [row_id])
        if cur.rowcount == 0:
            abort(404, f"No row with id {row_id}")
    return jsonify(ok=True)


@app.post("/api/<db>/reset")
def reset_database(db):
    if db not in DATABASES:
        abort(404, f"Unknown database '{db}'")
    seed_database(db)
    return jsonify(ok=True)


if __name__ == "__main__":
    if not all(os.path.exists(db_path(name)) for name in SCHEMAS):
        seed_all()
    app.run(port=5000, debug=False)
