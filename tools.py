import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path("db/olist.db")

def run_sql(query: str) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query(query, conn)
    finally:
        conn.close()
    return df

def df_to_markdown(df: pd.DataFrame, max_rows: int = 20) -> str:
    if df.empty:
        return "⚠️ Query returned no results."
    return df.head(max_rows).to_markdown(index=False)
