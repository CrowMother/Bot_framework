import sqlite3
from typing import List, Dict, Any
from Bot_App import util
import os

def raw_data_to_sql(data: List[Dict], db_name: str = "./test.db"):
    os.makedirs(os.path.dirname(db_name), exist_ok=True)
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    extracted_rows = []
    for order in data:
        legs = order.get("orderLegCollection", [])
        for leg in legs:
            merged = {**order, **leg, "instrument": leg.get("instrument", {})}
            flat_row = util.flatten_dict(merged)
            extracted_rows.append(flat_row)

    if not extracted_rows:
        print("No positions found to export to SQLite.")
        return

    # Dynamically create table schema based on flattened keys
    columns = sorted(extracted_rows[0].keys())
    columns_sql = ", ".join([f"[{col}] TEXT" for col in columns])
    cursor.execute(f"DROP TABLE IF EXISTS positions")
    cursor.execute(f"CREATE TABLE positions ({columns_sql})")

    for row in extracted_rows:
        placeholders = ", ".join(["?" for _ in columns])
        values = [str(row.get(col, '')) for col in columns]
        cursor.execute(f"INSERT INTO positions ({', '.join(['['+col+']' for col in columns])}) VALUES ({placeholders})", values)

    conn.commit()
    conn.close()
    print(f"Exported positions to SQLite DB: {db_name}")


def initialize_db(db_path="orders.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # REMOVE FOR DEBUGGIN!!!!!!!!!!!!!!!!!
    # cursor.execute("""DROP TABLE IF EXISTS schwab_orders;""")
    # check if table exists
    cursor.execute("""
        SELECT name FROM sqlite_master WHERE type='table' AND name='schwab_orders';
    """)
    table_exists = cursor.fetchone() is not None
    if table_exists:
        print("Table 'schwab_orders' already exists.")
        return
    
    cursor.execute("""

    CREATE TABLE schwab_orders (
        id TEXT PRIMARY KEY,
        entered_time TEXT,
        ticker TEXT,
        instruction TEXT,
        position_effect TEXT,
        order_status TEXT,
        quantity REAL,
        tag TEXT,
        full_json TEXT,
        posted_to_discord INTEGER DEFAULT 0,
        posted_at TEXT,
        description TEXT
);

    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_db()