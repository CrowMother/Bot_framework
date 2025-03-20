import sqlite3
from typing import List, Tuple, Any
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

            results = cursor.fetchall()
            print(f"Query executed: {query}")
            print(f"Fetched {len(results)} rows")
            return results
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
