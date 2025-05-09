import sys
from PyQt5.QtWidgets import QApplication
from models.database import Database
from views.client_order_form import ClientOrderForm


def create_connection():
    db = Database()
    if not db.connect("LAB1", "postgres", "123"):
        print("Не удалось подключиться к базе данных")
        return None

    # Добавляем тест соединения сразу после подключения
    if not db.test_connection():
        print("Тест соединения с БД не пройден")
        return None

    return db


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Создаем подключение и сразу тестируем его
    db_connection = create_connection()
    if not db_connection:
        sys.exit(1)

    # Создаем и показываем форму только если подключение успешно
    window = ClientOrderForm(db_connection)
    window.show()

    sys.exit(app.exec_())