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
            result = self.cursor.fetchall() if fetch else None
            self.conn.commit()  # Всегда делаем коммит
            return result if fetch else True
        except Exception as e:
            self.conn.rollback()
            print(f"Error executing query: {e}")
            return None if fetch else False

    def test_connection(self):
        try:
            self.cursor.execute("SELECT 1")
            self.conn.commit()
            print("Тест подключения: УСПЕШНО")
            return True
        except Exception as e:
            print(f"Тест подключения: ОШИБКА - {e}")
            return False
    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()