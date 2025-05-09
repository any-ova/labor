class OrderModel:
    def __init__(self, db):
        self.db = db

    def create_order(self, client_id, delivery_address, total, status='обрабатывается'):
        return self.db.execute_query(
            "INSERT INTO orders (client_id, delivery_address, total, status, order_date) "
            "VALUES (%s, %s, %s, %s, NOW()) RETURNING id",
            (client_id, delivery_address, total, status),
            fetch=True
        )

    def add_item_to_order(self, order_id, item_id, quantity):
        return self.db.execute_query(
            "INSERT INTO check_item (check_id, item_id, quantitity) "
            "VALUES (%s, %s, %s)",
            (order_id, item_id, quantity)
        )

    def get_filtered_orders(self, date_filter=None, client_filter=None, status_filter=None):
        params = []
        query = """
            SELECT 
                o.id, 
                o.order_date, 
                c.surname  || ' ' || c.name as client_name,
                c.phone,
                o.total, 
                o.status, 
                o.delivery_address
            FROM orders o
            JOIN client c ON o.client_id = c.id
            WHERE 1=1
        """

        if date_filter:
            query += " AND o.order_date::date = %s"
            params.append(date_filter)

        if client_filter:
            query += " AND (c.surname ILIKE %s OR c.name ILIKE %s)"
            params.extend([f"%{client_filter}%", f"%{client_filter}%"])

        if status_filter and status_filter != "Все":
            query += " AND o.status = %s"
            params.append(status_filter)

        query += " ORDER BY o.order_date DESC"

        return self.db.execute_query(query, params, fetch=True)

    def get_order_info(self, order_id):
        """Получение информации о заказе по ID"""
        query = """
        SELECT 
            o.id,
            c.name,
            c.surname,
            o.total,
            o.delivery_address,
            o.status
        FROM orders o
        JOIN client c ON o.client_id = c.id
        WHERE o.id = %s
        """
        result = self.db.execute_query(query, (order_id,), fetch=True)
        return result[0] if result else None

    def get_order_items(self, order_id):
        """Получить товары в заказе"""
        query = """
        SELECT 
            i.name,
            ci.quantitity,
            i.price
        FROM check_item ci
        JOIN item i ON ci.item_id = i.id
        WHERE ci.check_id = %s
        """
        return self.db.execute_query(query, (order_id,), fetch=True)