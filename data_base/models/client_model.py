from PyQt5.QtWidgets import QMessageBox


class ClientModel:
    def __init__(self, db_connection):
        self.db = db_connection

    def get_client_by_phone(self, phone):
        """Поиск клиента по телефону"""
        query = "SELECT id, name, surname, email, phone FROM client WHERE phone = %s"
        result = self.db.execute_query(query, (phone,), fetch=True)
        return result[0] if result else None

    def create_client(self, name, surname, email, phone):
        """Создание нового клиента"""
        query = """
        INSERT INTO client (name, surname, email, phone) 
        VALUES (%s, %s, %s, %s) 
        RETURNING id
        """
        return self.db.execute_query(query, (name, surname, email, phone), fetch=True)

    def update_client(self, client_id, name, surname, email, phone):
        query = """
        UPDATE client 
        SET name = %s, surname = %s, email = %s, phone = %s 
        WHERE id = %s 
        RETURNING id
        """
        try:
            result = self.db.execute_query(query, (name, surname, email, phone, client_id), fetch=True)
            if result and result[0]:
                print(f"Успешно обновлен клиент ID: {result[0][0]}")
                return True
            print("Не удалось обновить клиента (возможно, ID не существует)")
            return False
        except Exception as e:
            print(f"Ошибка при обновлении клиента: {e}")
            return False