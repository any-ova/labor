class ProductModel:
    def __init__(self, db):
        self.db = db

    def get_available_products(self):
        return self.db.execute_query(
            "SELECT id, name, price FROM item WHERE in_stock > 0",
            fetch=True
        )

    def get_product_by_name(self, name):
        return self.db.execute_query(
            "SELECT id FROM item WHERE name = %s",
            (name,),
            fetch=True
        )

    def update_stock(self, product_id, quantity):
        return self.db.execute_query(
            "UPDATE item SET in_stock = in_stock - %s WHERE id = %s",
            (quantity, product_id)
        )