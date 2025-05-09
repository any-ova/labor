from models.order_model import OrderModel


class OrderController:
    def __init__(self, db):
        self.model = OrderModel(db)

    def create_new_order(self, client_id, delivery_address, items):
        if not isinstance(client_id, int):
            print(f"Ошибка: client_id должен быть числом, получено {type(client_id)}")
            return None
        if not client_id:
            print("Ошибка: не указан client_id")
            return None

        if not items:
            print("Ошибка: пустой список товаров")
            return None

        try:
            total = sum(item['price'] * item['quantity'] for item in items)
            print(f"Создание заказа для client_id={client_id}, total={total}")

            order_result = self.model.create_order(client_id, delivery_address, total)

            if not order_result:
                print("Ошибка при создании заказа")
                return None

            order_id = order_result[0][0]
            print(f"Заказ создан, ID: {order_id}")

            for item in items:
                print(f"Добавление товара {item['id']}, количество: {item['quantity']}")
                if not self.model.add_item_to_order(order_id, item['id'], item['quantity']):
                    print(f"Ошибка при добавлении товара {item['id']}")

            return order_id

        except Exception as e:
            print(f"Исключение при создании заказа: {str(e)}")
            return None

    def get_filtered_orders(self, filters):
        return self.model.get_filtered_orders(
            filters.get('date'),
            filters.get('client'),
            filters.get('status')
        )

    def get_order_info(self, order_id):
        """Получение информации о заказе"""
        return self.model.get_order_info(order_id)

    def get_order_items(self, order_id):
        """Получить список товаров заказа"""
        return self.model.get_order_items(order_id)