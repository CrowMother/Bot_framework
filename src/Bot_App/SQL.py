import sqlite3
from typing import List, Dict, Any
from Bot_App import util
import os

class SQLDatabase:
    def __init__(self, db_path: str):
        """Initialize database connection with the specified path."""
        self.db_path = db_path
        self.connection = None

    def connect(self) -> bool:
        """Connect to SQLite database. Creates file and directory if they don't exist."""
        try:
            # Create parent directory if it doesn't exist
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            # Create empty database file if it doesn't exist
            open(self.db_path, 'a').close()
            
            self.connection = sqlite3.connect(self.db_path)
            print(f"Connected to SQLite at {self.db_path}")
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def disconnect(self) -> None:
        """Close database connection."""
        if self.connection:
            try:
                self.connection.close()
                self.connection = None
                print("Disconnected from database")
            except Exception as e:
                print(f"Disconnect error: {e}")

    def execute_query(self, query, params=None):
        """Execute a SQL query."""
        if not self.connection:
            print("Not connected to database")
            return False
            
        try:
            cursor = self.connection.cursor()
            if params is not None:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return True
        except Exception as e:
            print(f"Query error: {e}")
            return False

    def commit(self) -> bool:
        """Commit pending transactions."""
        if not self.connection:
            print("Not connected to database")
            return False
            
        try:
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Commit error: {e}")
            return False

    def create_tables(self, table_statements: List[str]) -> None:
        """Execute multiple SQL statements to create tables."""
        if not self.connection:
            print("Not connected to database")
            return
            
        try:
            cursor = self.connection.cursor()
            for stmt in table_statements:
                cursor.execute(stmt)
            print(f"Successfully created {len(table_statements)} tables")
        except Exception as e:
            print(f"Table creation error: {e}")

    def get_data(self, query, params=None):
        if not self.connection:
            print("Not connected to database")
            return None
        try:
            cursor = self.connection.cursor()
            if params is not None:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print(f"SQL get_data error: {e}")
            return None
        
    def get_all_data(self, query, params=None):
        if not self.connection:
            print("Not connected to database")
            return None
        try:
            cursor = self.connection.cursor()
            if params is not None:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            columns = [desc[0] for desc in cursor.description]  # Get column names
            results = cursor.fetchall()
            data = [dict(zip(columns, row)) for row in results]  # Map columns to values

            print(f"Query executed: {query}")
            print(f"Fetched {len(results)} rows")
            return data
        except Exception as e:
            print(f"SQL get_data error: {e}")
            return None

    def check_if_data_exists(self, query, params=None):
        if not self.connection:
            print("Not connected to database")
            return None
        try:
            cursor = self.connection.cursor()
            if params is not None:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchone() is not None
        except Exception as e:
            print(f"SQL get_data error: {e}")
            return None
        
# Example usage:
# db = SQLDatabase('mydatabase.db')
# if db.connect():
#     try:
#         # Create a table
#         create_table = """
#             CREATE TABLE IF NOT EXISTS users (
#                 id INTEGER PRIMARY KEY,
#                 username TEXT UNIQUE NOT NULL,
#                 email TEXT NOT NULL
#             )
#         """
#         db.create_tables([create_table])
#         
#         # Insert data
#         insert_query = "INSERT INTO users (username, email) VALUES (?, ?)"
#         db.execute_query(insert_query, ('john_doe', 'john@example.com'))
#         db.commit()
#     finally:
#         db.disconnect()

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
        posted_at TEXT
);

    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_db()