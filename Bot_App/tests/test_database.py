import os
import sqlite3
import tempfile
from Bot_App.core import database


def test_initialize_db_creates_table():
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        db_path = tmp.name
    try:
        database.initialize_db(db_path)
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' "
                "AND name='schwab_orders';"
            )
            assert cursor.fetchone() is not None
    finally:
        os.remove(db_path)


def test_store_orders_inserts_data():
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        db_path = tmp.name
    try:
        database.initialize_db(db_path)
        test_order = [
            {
                "enteredTime": "2024-01-01T00:00:00Z",
                "orderLegCollection": [
                    {
                        "instruction": "BUY_TO_OPEN",
                        "positionEffect": "OPENING",
                        "instrument": {
                            "symbol": "AAPL",
                            "description": "AAPL 01/01/2025 $200 Call",
                        },
                    }
                ],
                "status": "FILLED",
                "quantity": 1,
                "tag": "test",
            }
        ]
        database.store_orders(test_order, db_path=db_path)
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM schwab_orders")
            assert cursor.fetchone()[0] == 1
    finally:
        os.remove(db_path)
