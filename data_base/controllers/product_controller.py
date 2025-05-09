from models.product_model import ProductModel

class ProductController:
    def __init__(self, db):
        self.model = ProductModel(db)

    def get_available_products(self):
        return self.model.get_available_products()

    def get_product_id_by_name(self, name):
        result = self.model.get_product_by_name(name)
        return result[0][0] if result else None

    def update_product_stock(self, product_id, quantity):
        return self.model.update_stock(product_id, quantity)