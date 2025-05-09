from models.client_model import ClientModel

class ClientController:
    def __init__(self, db_connection):
        self.model = ClientModel(db_connection)

    def handle_client_search(self, phone):
        """Поиск клиента по телефону"""
        return self.model.get_client_by_phone(phone)

    def handle_client_update(self, name, surname, email, phone, client_id=None):
        """Должен возвращать ID клиента (int) или None при ошибке"""
        existing_client = self.model.get_client_by_phone(phone)

        # Для существующего клиента
        if client_id is not None:
            if existing_client and existing_client[0] != client_id:
                print(f"Телефон {phone} занят другим клиентом")
                return None
            result = self.model.update_client(client_id, name, surname, email, phone)
            return client_id if result else None

        # Для нового клиента
        if existing_client:
            return existing_client[0]

        result = self.model.create_client(name, surname, email, phone)
        return result[0][0] if result else None