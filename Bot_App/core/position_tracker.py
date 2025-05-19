import sqlite3
import logging
from datetime import datetime

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def initialize_open_positions_table(db_path="orders.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS open_positions (
            id TEXT PRIMARY KEY,
            ticker TEXT,
            description TEXT,
            price REAL,
            quantity REAL,
            entered_time TEXT
        );
    """)
    conn.commit()
    conn.close()

def consume_open_position(order, db_path="orders.db"):
    symbol = order.get("orderLegCollection", [{}])[0].get("instrument", {}).get("symbol")
    description = order.get("orderLegCollection", [{}])[0].get("instrument", {}).get("description")
    close_qty = order.get("quantity", 0)
    close_price = order.get("price", 0)
    if not symbol or not description or close_qty == 0:
        return None, 0

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, price, quantity FROM open_positions
        WHERE ticker = ? AND description = ?
        ORDER BY entered_time ASC
    """, (symbol, description))

    rows = cursor.fetchall()
    remaining = close_qty
    total_cost = 0
    consumed = 0

    for row_id, open_price, open_qty in rows:
        if remaining == 0:
            break
        take_qty = min(remaining, open_qty)
        consumed += take_qty
        total_cost += take_qty * open_price
        remaining -= take_qty
        new_qty = open_qty - take_qty

        if new_qty == 0:
            cursor.execute("DELETE FROM open_positions WHERE id = ?", (row_id,))
        else:
            cursor.execute("UPDATE open_positions SET quantity = ? WHERE id = ?", (new_qty, row_id))

    conn.commit()
    conn.close()

    if consumed == 0:
        return None, 0

    avg_open_price = total_cost / consumed
    return avg_open_price, consumed