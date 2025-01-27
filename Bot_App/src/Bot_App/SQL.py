import mysql.connector
import logging

class SQLDatabase:
    def __init__(self, host, username, password, database):
        self.host = host
        self.username = username
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(host=self.host, 
                                                      user=self.username, 
                                                      password=self.password, 
                                                      database=self.database)
            print("Connection successful")
        except Exception as e:
            print(f"Error connecting to database: {e}")
            self.connection = None

    def disconnect(self):
        if self.connection:
            self.connection.close()
            self.connection = None
            print("Disconnected from database")

    def execute_query(self, query, params=None):
        if not self.connection:
            logging.error("Not connected to any database")
            return None
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

    def commit(self):
        if self.connection:
            self.connection.commit()
        else:
            logging.error("Not connected to any database")