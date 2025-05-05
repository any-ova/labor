import psycopg2
from psycopg2 import sql


class Database:
    def __init__(self):
        self.conn = None
        self.cursor = None

    def connect(self, dbname, user, password, host='localhost', port='5432'):
        try:
            self.conn = psycopg2.connect(
                dbname=dbname,
                user=user,
                password=password,
                host=host,
                port=port
            )
            self.cursor = self.conn.cursor()
            return True
        except Exception as e:
            print(f"Database connection error: {e}")
            return False

    def execute_query(self, query, params=None, fetch=False):
        try:
            self.cursor.execute(query, params or ())
            if fetch:
                return self.cursor.fetchall()
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error executing query: {e}")
            return False

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()