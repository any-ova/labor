from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTableWidget,
                             QTableWidgetItem, QMessageBox, QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator


class ClientOrderForm(QWidget):
    def __init__(self, db_connection):
        super().__init__()
        self.db = db_connection
        if not hasattr(self.db, 'execute_query'):
            QMessageBox.critical(self, "Ошибка", "Неверный объект базы данных")
            self.close()
            return

        self.cart = []
        self.cart_items = {}
        self.current_client_id = None
        self.setup_ui()
        self.load_products()
        self.update_cart_table()  # Инициализируем корзину

    def setup_ui(self):
        self.setWindowTitle("Оформление заказа")
        self.setFixedSize(900, 700)

        main_layout = QVBoxLayout()

        # ========== Поиск/создание клиента ==========
        client_search_layout = QHBoxLayout()

        # Выбор режима (поиск или создание)
        self.client_mode = QComboBox()
        self.client_mode.addItems(["Поиск по телефону", "Создать нового клиента"])
        self.client_mode.currentIndexChanged.connect(self.toggle_client_mode)
        client_search_layout.addWidget(self.client_mode)

        # Поле телефона (для поиска)
        self.client_phone_input = QLineEdit()
        self.client_phone_input.setPlaceholderText("Введите телефон")
        client_search_layout.addWidget(self.client_phone_input)

        # Кнопка поиска/создания
        self.client_action_btn = QPushButton("Найти")
        self.client_action_btn.clicked.connect(self.handle_client_action)
        client_search_layout.addWidget(self.client_action_btn)

        main_layout.addLayout(client_search_layout)

        # ========== Данные клиента ==========
        client_data_layout = QVBoxLayout()

        # Имя
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Имя:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введите имя")
        name_layout.addWidget(self.name_input)
        client_data_layout.addLayout(name_layout)

        # Фамилия
        surname_layout = QHBoxLayout()
        surname_layout.addWidget(QLabel("Фамилия:"))
        self.surname_input = QLineEdit()
        self.surname_input.setPlaceholderText("Введите фамилию")
        surname_layout.addWidget(self.surname_input)
        client_data_layout.addLayout(surname_layout)

        # Email
        email_layout = QHBoxLayout()
        email_layout.addWidget(QLabel("Email:"))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Введите email")
        email_layout.addWidget(self.email_input)
        client_data_layout.addLayout(email_layout)

        # Телефон (только для отображения)
        phone_layout = QHBoxLayout()
        phone_layout.addWidget(QLabel("Телефон:"))
        self.phone_display = QLineEdit()
        self.phone_display.setReadOnly(True)
        phone_layout.addWidget(self.phone_display)
        client_data_layout.addLayout(phone_layout)

        # Кнопка обновления данных
        self.update_btn = QPushButton("Обновить данные")
        self.update_btn.setEnabled(False)  # Изначально неактивна
        self.update_btn.clicked.connect(self.update_client_data)
        client_data_layout.addWidget(self.update_btn)

        main_layout.addLayout(client_data_layout)

        # ========== Адрес доставки ==========
        address_layout = QHBoxLayout()
        address_layout.addWidget(QLabel("Адрес доставки:"))
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Введите адрес доставки")
        address_layout.addWidget(self.address_input)
        main_layout.addLayout(address_layout)



        # ========== Таблица товаров ==========
        main_layout.addWidget(QLabel("Выберите товары:"))
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(4)  # Товар, Цена, Количество, Добавить
        self.products_table.setHorizontalHeaderLabels(["Товар", "Цена", "Количество", "Добавить"])
        self.products_table.setEditTriggers(QTableWidget.NoEditTriggers)
        main_layout.addWidget(self.products_table)

        # ========== Корзина ==========
        main_layout.addWidget(QLabel("Корзина:"))
        self.cart_table = QTableWidget()  # Создаем таблицу корзины
        self.cart_table.setColumnCount(4)  # Товар, Цена, Количество, Удалить
        self.cart_table.setHorizontalHeaderLabels(["Товар", "Цена", "Количество", "Удалить"])
        self.cart_table.setEditTriggers(QTableWidget.NoEditTriggers)
        main_layout.addWidget(self.cart_table)  # Добавляем таблицу в layout

        # ========== Кнопки ==========
        btn_layout = QHBoxLayout()

        self.submit_btn = QPushButton("Оформить заказ")
        self.submit_btn.clicked.connect(self.submit_order)
        btn_layout.addWidget(self.submit_btn)

        self.filter_orders_btn = QPushButton("Фильтр заказов")
        self.filter_orders_btn.clicked.connect(self.open_order_filter)
        btn_layout.addWidget(self.filter_orders_btn)

        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    def search_client(self):
        phone = self.client_phone_input.text().strip()
        if not phone:
            QMessageBox.warning(self, "Ошибка", "Введите телефон для поиска")
            return

        try:
            result = self.db.execute_query(
                "SELECT id, name, surname, email FROM client WHERE phone = %s",
                (phone,),
                fetch=True
            )

            if not result:
                QMessageBox.information(self, "Информация", "Клиент не найден. Заполните данные вручную")
                self.current_client_id = None
                self.update_btn.setEnabled(False)
                return

            client_id, name, surname, email = result[0]
            self.current_client_id = client_id

            # Заполняем поля
            self.name_input.setText(name)
            self.surname_input.setText(surname)
            self.email_input.setText(email)
            self.phone_display.setText(phone)

            # Активируем кнопку обновления
            self.update_btn.setEnabled(True)

            QMessageBox.information(self, "Успех", "Данные клиента загружены")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при поиске клиента: {str(e)}")
            self.clear_client_fields()

    def update_client_data(self):
        """Обновляет или создает данные клиента"""
        phone = self.client_phone_input.text().strip()
        if not phone:
            QMessageBox.warning(self, "Ошибка", "Телефон обязателен")
            return

        name = self.name_input.text().strip()
        surname = self.surname_input.text().strip()
        email = self.email_input.text().strip()

        if not all([name, surname, email]):
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        try:
            # Создаем или обновляем клиента
            result = self.db.execute_query(
                "INSERT INTO client (name, surname, email, phone) "
                "VALUES (%s, %s, %s, %s) "
                "ON CONFLICT (phone) DO UPDATE SET "
                "name = EXCLUDED.name, "
                "surname = EXCLUDED.surname, "
                "email = EXCLUDED.email "
                "RETURNING id",
                (name, surname, email, phone),
                fetch=True
            )

            if result:
                self.current_client_id = result[0][0]
                QMessageBox.information(self, "Успех", "Данные клиента сохранены")
                # Блокируем редактирование после сохранения
                self.name_input.setReadOnly(True)
                self.surname_input.setReadOnly(True)
                self.email_input.setReadOnly(True)
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось сохранить клиента")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка базы данных: {str(e)}")

    def clear_client_fields(self):
        self.current_client_id = None
        self.name_input.clear()
        self.surname_input.clear()
        self.email_input.clear()
        self.phone_display.clear()

    def load_products(self):
        try:
            products = self.db.execute_query(
                "SELECT id, name, price FROM item WHERE in_stock > 0",
                fetch=True
            )

            if not products:
                QMessageBox.warning(self, "Ошибка", "Не удалось загрузить товары")
                return

            self.products_table.setColumnCount(4)  # Исправлено с 3 на 4
            self.products_table.setRowCount(len(products))

            for row, (product_id, name, price) in enumerate(products):
                # Название товара (нередактируемое)
                name_item = QTableWidgetItem(name)
                name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
                self.products_table.setItem(row, 0, name_item)

                # Цена товара (нередактируемая)
                price_item = QTableWidgetItem(f"{price:.2f}")
                price_item.setFlags(price_item.flags() & ~Qt.ItemIsEditable)
                self.products_table.setItem(row, 1, price_item)

                # Поле для ввода количества
                quantity_input = QLineEdit()
                quantity_input.setValidator(QIntValidator(1, 100))
                quantity_input.setText("1")
                self.products_table.setCellWidget(row, 2, quantity_input)

                # Кнопка добавления в корзину
                add_btn = QPushButton("Добавить")
                add_btn.clicked.connect(lambda _, r=row: self.add_to_cart(r))
                self.products_table.setCellWidget(row, 3, add_btn)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить товары: {e}")

    def add_to_cart(self, row):
        """Добавляем выбранный товар в корзину."""
        try:
            product_name = self.products_table.item(row, 0).text()
            price = float(self.products_table.item(row, 1).text())
            quantity = int(self.products_table.cellWidget(row, 2).text())

            if quantity <= 0:
                QMessageBox.warning(self, "Ошибка", "Количество должно быть больше 0")
                return

            # Получаем ID продукта перед добавлением в корзину
            product_id = self.get_product_id(row)
            if product_id is None:
                QMessageBox.warning(self, "Ошибка", "Не удалось определить ID товара")
                return

            # Проверяем, есть ли уже такой товар в корзине
            if product_id in self.cart_items:
                # Увеличиваем количество существующего товара
                self.cart_items[product_id]['quantity'] += quantity
            else:
                # Добавляем новый товар в корзину
                self.cart_items[product_id] = {
                    'name': product_name,
                    'price': price,
                    'quantity': quantity
                }
                # Добавляем в список для отображения
                self.cart.append(self.cart_items[product_id])

            self.update_cart_table()  # Обновляем корзину
            self.products_table.cellWidget(row, 2).setText("1")  # Сбрасываем поле ввода

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить товар: {str(e)}")

    def update_cart_table(self):
        """Обновляем отображение корзины"""
        self.cart_table.setRowCount(len(self.cart))
        for row, item in enumerate(self.cart):
            self.cart_table.setItem(row, 0, QTableWidgetItem(item['name']))
            self.cart_table.setItem(row, 1, QTableWidgetItem(f"{item['price']:.2f}"))
            self.cart_table.setItem(row, 2, QTableWidgetItem(str(item['quantity'])))

            # Кнопка удаления из корзины
            remove_btn = QPushButton("Удалить")
            remove_btn.clicked.connect(lambda _, r=row: self.remove_from_cart(r))
            self.cart_table.setCellWidget(row, 3, remove_btn)

    def remove_from_cart(self, row):
        """Удаляем товар из корзины."""
        if 0 <= row < len(self.cart):
            product_id = self.get_product_id_by_name(self.cart[row]['name'])
            del self.cart_items[product_id]
            self.cart.pop(row)
            self.update_cart_table()

    def get_product_id(self, row):
        """Получаем ID продукта из таблицы продуктов."""
        try:
            product_name = self.products_table.item(row, 0).text()
            result = self.db.execute_query(
                "SELECT id FROM item WHERE name = %s",
                (product_name,),
                fetch=True
            )
            if result and len(result) > 0:
                return result[0][0]
            return None
        except Exception as e:
            print(f"Ошибка получения ID товара: {e}")
            return None

    def get_product_id_by_name(self, name):
        """Получаем ID товара по названию."""
        try:
            result = self.db.execute_query(
                "SELECT id FROM item WHERE name = %s",
                (name,),
                fetch=True
            )
            if result:
                return result[0][0]
            return None
        except Exception as e:
            print(f"Ошибка получения ID товара: {e}")
            return None

    def get_client_id(self):
        """Создаем или получаем ID клиента."""
        try:
            phone = self.client_phone_input.text().strip()
            if not phone:
                QMessageBox.warning(self, "Ошибка", "Телефон обязателен для создания клиента")
                return None

            result = self.db.execute_query(
                "INSERT INTO client (name, surname, email, phone) "
                "VALUES (%s, %s, %s, %s) "
                "ON CONFLICT (phone) DO UPDATE SET "
                "name = EXCLUDED.name, "
                "surname = EXCLUDED.surname, "
                "email = EXCLUDED.email "
                "RETURNING id",
                (self.name_input.text(),
                 self.surname_input.text(),
                 self.email_input.text(),
                 phone),
                fetch=True
            )

            if result:
                return result[0][0]
            return None

        except Exception as e:
            print(f"Ошибка получения ID клиента: {e}")
            return None

    def submit_order(self):
        """Обрабатываем оформление заказа."""
        if not all([self.name_input.text(), self.surname_input.text(),
                    self.email_input.text(), self.address_input.text()]):
            QMessageBox.warning(self, "Ошибка", "Заполните все обязательные поля")
            return

        if not self.cart:
            QMessageBox.warning(self, "Ошибка", "Корзина пуста. Добавьте товары")
            return

        try:
            client_id = self.get_client_id()
            if not client_id:
                raise Exception("Не удалось создать/найти клиента")

            total = sum(item['price'] * item['quantity'] for item in self.cart)

            # Создаем заказ (без delivery_company_id)
            order_result = self.db.execute_query(
                "INSERT INTO orders (client_id, delivery_address, total, status) "
                "VALUES (%s, %s, %s, 'обрабатывается') RETURNING id",
                (client_id, self.address_input.text(), total),
                fetch=True
            )

            if not order_result:
                raise Exception("Не удалось создать заказ")

            order_id = order_result[0][0]

            # Добавляем товары в заказ (используем правильное имя столбца quantitity)
            for item in self.cart:
                product_id = self.get_product_id_by_name(item['name'])

                self.db.execute_query(
                    "INSERT INTO check_item (check_id, item_id, quantitity) "
                    "VALUES (%s, %s, %s)",
                    (order_id, product_id, item['quantity'])
                )

                # Обновляем остатки
                self.db.execute_query(
                    "UPDATE item SET in_stock = in_stock - %s WHERE id = %s",
                    (item['quantity'], product_id)
                )

            # Очищаем корзину
            self.show_receipt(order_id)
            self.cart.clear()
            self.cart_items.clear()
            self.update_cart_table()
            QMessageBox.information(self, "Успех", f"Заказ #{order_id} успешно оформлен!")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось оформить заказ: {str(e)}")

    def show_receipt(self, order_id):
        """Отображаем чек заказа."""
        try:
            # Получаем данные о заказе
            order_info = self.db.execute_query(
                "SELECT o.id, c.name, c.surname, o.total, o.delivery_address "
                "FROM orders o JOIN client c ON o.client_id = c.id "
                "WHERE o.id = %s",
                (order_id,),
                fetch=True
            )

            if not order_info:
                raise Exception("Не удалось получить данные заказа")

            # Получаем товары в заказе
            items = self.db.execute_query(
                "SELECT i.name, ci.quantitity, i.price "
                "FROM check_item ci JOIN item i ON ci.item_id = i.id "
                "WHERE ci.check_id = %s",
                (order_id,),
                fetch=True
            )

            # Формируем текст чека
            receipt_text = (
                f"Заказ №{order_info[0][0]}\n"
                f"Клиент: {order_info[0][1]} {order_info[0][2]}\n"
                f"Адрес: {order_info[0][4]}\n"
                f"Сумма: {order_info[0][3]:.2f}\n\n"
                "Товары:\n"
            )

            for item in items:
                receipt_text += f"- {item[0]}: {item[1]} x {item[2]:.2f}\n"

            # Показываем чек
            msg = QMessageBox()
            msg.setWindowTitle("Чек заказа")
            msg.setText(receipt_text)
            msg.exec_()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сформировать чек: {str(e)}")

    def open_order_filter(self):
        """Открывает форму фильтра заказов"""
        try:
            # Динамический импорт для избежания циклических зависимостей
            from views.order_filter_form import OrderFilterForm

            self.filter_form = OrderFilterForm(self.db)
            self.filter_form.show()
            self.hide()  # Скрываем текущую форму вместо закрытия
        except ImportError as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить модуль: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть форму: {str(e)}")

    def toggle_client_mode(self, index):
        """Переключает режим работы с клиентом"""
        if index == 0:  # Режим поиска
            self.client_action_btn.setText("Найти")
            self.client_phone_input.setReadOnly(False)
            self.client_phone_input.setPlaceholderText("Введите телефон для поиска")
            self.clear_client_fields()
        else:  # Режим создания
            self.client_action_btn.setText("Создать")
            self.client_phone_input.setReadOnly(False)
            self.client_phone_input.setPlaceholderText("Введите телефон нового клиента")
            self.clear_client_fields()

    def handle_client_action(self):
        """Обрабатывает действие с клиентом (поиск/создание)"""
        if self.client_mode.currentIndex() == 0:
            self.search_client()
        else:
            self.create_new_client()

    def create_new_client(self):
        """Создает нового клиента"""
        phone = self.client_phone_input.text().strip()
        if not phone:
            QMessageBox.warning(self, "Ошибка", "Введите телефон клиента")
            return

        # Очищаем поля и разрешаем редактирование
        self.clear_client_fields()
        self.name_input.setReadOnly(False)
        self.surname_input.setReadOnly(False)
        self.email_input.setReadOnly(False)

        # Устанавливаем телефон (только для отображения)
        self.phone_display.setText(phone)

        # Активируем кнопку сохранения
        self.update_btn.setEnabled(True)

        QMessageBox.information(self, "Создание", "Заполните данные нового клиента и нажмите 'Обновить данные'")

