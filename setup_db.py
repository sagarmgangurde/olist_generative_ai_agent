import sqlite3
import pandas as pd
from pathlib import Path

# Database location
DB_PATH = Path("db/olist.db")

# All CSVs (table name : filename)
FILES = {
    "olist_orders_dataset": "olist_orders_dataset.csv",
    "olist_order_items_dataset": "olist_order_items_dataset.csv",
    "olist_products_dataset": "olist_products_dataset.csv",
    "olist_order_payments_dataset": "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset": "olist_order_reviews_dataset.csv",
    "olist_customers_dataset": "olist_customers_dataset.csv",
    "olist_sellers_dataset": "olist_sellers_dataset.csv",
    "olist_geolocation_dataset": "olist_geolocation_dataset.csv",
}

# Raw data folder
DATA_FOLDER = Path("data/raw")

def load_all_tables():
    # create/connect database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("\n📦 Loading Olist CSV files into SQLite database...\n")

    for table_name, csv_file in FILES.items():
        csv_path = DATA_FOLDER / csv_file

        print(f"➡️  Loading {csv_file} → table: {table_name}")

        df = pd.read_csv(csv_path)

        # Write table into SQLite
        df.to_sql(table_name, conn, if_exists="replace", index=False)

    conn.close()
    print("\n✅ DONE! All tables have been loaded into db/olist.db\n")

if __name__ == "__main__":
    load_all_tables()
