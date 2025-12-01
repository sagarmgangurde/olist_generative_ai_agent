import sqlite3
import json

def read_schema(db_path="db/olist.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    schema = {}
    tables = cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table';"
    ).fetchall()

    for (table,) in tables:
        cols = cursor.execute(f"PRAGMA table_info({table});").fetchall()
        col_names = [col[1] for col in cols]
        schema[table] = col_names

    conn.close()
    return json.dumps(schema, indent=4)
