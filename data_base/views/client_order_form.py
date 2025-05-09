from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTableWidget,
                             QTableWidgetItem, QMessageBox, QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator
from controllers.client_controller import ClientController
from controllers.product_controller import ProductController
from controllers.order_controller import OrderController


class ClientOrderForm(QWidget):
    def __init__(self, db_connection):
        super().__init__()
        # Инициализация контроллеров
        self.client_controller = ClientController(db_connection)
        self.product_controller = ProductController(db_connection)
        self.order_controller = OrderController(db_connection)

        self.cart = []
        self.cart_items = {}
        self.current_client_id = None
        self.setup_ui()
        self.load_products()
        self.update_cart_table()

    def setup_ui(self):
        self.setWindowTitle("Оформление заказа")
        self.setFixedSize(900, 700)

        main_layout = QVBoxLayout()

        # ========== Поиск/создание клиента ==========
        client_search_layout = QHBoxLayout()

        self.client_mode = QComboBox()
        self.client_mode.addItems(["Поиск по телефону", "Создать нового клиента"])
        self.client_mode.currentIndexChanged.connect(self.toggle_client_mode)
        client_search_layout.addWidget(self.client_mode)

        self.client_phone_input = QLineEdit()
        self.client_phone_input.setPlaceholderText("Введите телефон")
        client_search_layout.addWidget(self.client_phone_input)

        self.client_action_btn = QPushButton("Найти")
        self.client_action_btn.clicked.connect(self.handle_client_action)
        client_search_layout.addWidget(self.client_action_btn)

        main_layout.addLayout(client_search_layout)

        # ========== Данные клиента ==========
        client_data_layout = QVBoxLayout()

        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Имя:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введите имя")
        name_layout.addWidget(self.name_input)
        client_data_layout.addLayout(name_layout)

        surname_layout = QHBoxLayout()
        surname_layout.addWidget(QLabel("Фамилия:"))
        self.surname_input = QLineEdit()
        self.surname_input.setPlaceholderText("Введите фамилию")
        surname_layout.addWidget(self.surname_input)
        client_data_layout.addLayout(surname_layout)

        email_layout = QHBoxLayout()
        email_layout.addWidget(QLabel("Email:"))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Введите email")
        email_layout.addWidget(self.email_input)
        client_data_layout.addLayout(email_layout)

        phone_layout = QHBoxLayout()
        phone_layout.addWidget(QLabel("Телефон:"))
        self.phone_display = QLineEdit()
        self.phone_display.setReadOnly(True)
        phone_layout.addWidget(self.phone_display)
        client_data_layout.addLayout(phone_layout)

        self.update_btn = QPushButton("Обновить данные")
        self.update_btn.setEnabled(False)
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
        self.products_table.setColumnCount(4)
        self.products_table.setHorizontalHeaderLabels(["Товар", "Цена", "Количество", "Добавить"])
        self.products_table.setEditTriggers(QTableWidget.NoEditTriggers)
        main_layout.addWidget(self.products_table)

        # ========== Корзина ==========
        main_layout.addWidget(QLabel("Корзина:"))
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(4)
        self.cart_table.setHorizontalHeaderLabels(["Товар", "Цена", "Количество", "Удалить"])
        self.cart_table.setEditTriggers(QTableWidget.NoEditTriggers)
        main_layout.addWidget(self.cart_table)

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
            result = self.client_controller.handle_client_search(phone)

            if not result:
                # Клиент не найден - переходим в режим создания
                self.clear_client_fields()
                self.name_input.setReadOnly(False)
                self.surname_input.setReadOnly(False)
                self.email_input.setReadOnly(False)
                self.phone_display.setText(phone)
                self.update_btn.setEnabled(True)
                self.update_btn.setText("Создать клиента")
                self.current_client_id = None

                QMessageBox.information(self, "Информация",
                                        "Клиент не найден. Заполните данные для создания нового клиента")
                return

            # Клиент найден - заполняем данные
            client_id, name, surname, email, phone = result[0]
            self.current_client_id = client_id

            self.name_input.setText(name)
            self.surname_input.setText(surname)
            self.email_input.setText(email)
            self.phone_display.setText(phone)
            self.update_btn.setEnabled(True)
            self.update_btn.setText("Обновить данные")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при поиске клиента: {str(e)}")

    def update_client_data(self):
        phone = self.client_phone_input.text().strip()
        name = self.name_input.text().strip()
        surname = self.surname_input.text().strip()
        email = self.email_input.text().strip()

        if not all([name, surname, phone]):
            QMessageBox.warning(self, "Ошибка", "Имя, фамилия и телефон обязательны")
            return

        try:
            print(
                f"Данные для обновления: name={name}, surname={surname}, email={email}, phone={phone}, client_id={self.current_client_id}")  # Отладочный вывод

            result = self.client_controller.handle_client_update(
                name, surname, email, phone, self.current_client_id
            )

            if result:
                QMessageBox.information(self, "Успех", "Данные обновлены!")
                # Проверяем, что данные действительно обновились
                updated_client = self.client_controller.handle_client_search(phone)
                print("Проверка в БД:", updated_client)  # Должен показать новые данные
            else:
                QMessageBox.warning(self, "Ошибка", "Телефон занят или ошибка БД")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка: {str(e)}")

    def clear_client_fields(self):
        self.current_client_id = None
        self.name_input.clear()
        self.surname_input.clear()
        self.email_input.clear()
        self.phone_display.clear()

    def load_products(self):
        products = self.product_controller.get_available_products()

        if not products:
            QMessageBox.warning(self, "Ошибка", "Не удалось загрузить товары")
            return

        self.products_table.setColumnCount(4)
        self.products_table.setRowCount(len(products))

        for row, (product_id, name, price) in enumerate(products):
            name_item = QTableWidgetItem(name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.products_table.setItem(row, 0, name_item)

            price_item = QTableWidgetItem(f"{price:.2f}")
            price_item.setFlags(price_item.flags() & ~Qt.ItemIsEditable)
            self.products_table.setItem(row, 1, price_item)

            quantity_input = QLineEdit()
            quantity_input.setValidator(QIntValidator(1, 100))
            quantity_input.setText("1")
            self.products_table.setCellWidget(row, 2, quantity_input)

            add_btn = QPushButton("Добавить")
            add_btn.clicked.connect(lambda _, r=row: self.add_to_cart(r))
            self.products_table.setCellWidget(row, 3, add_btn)

    def add_to_cart(self, row):
        try:
            product_name = self.products_table.item(row, 0).text()
            price = float(self.products_table.item(row, 1).text())
            quantity = int(self.products_table.cellWidget(row, 2).text())

            if quantity <= 0:
                QMessageBox.warning(self, "Ошибка", "Количество должно быть больше 0")
                return

            product_id = self.product_controller.get_product_id_by_name(product_name)
            if product_id is None:
                QMessageBox.warning(self, "Ошибка", "Не удалось определить ID товара")
                return

            if product_id in self.cart_items:
                self.cart_items[product_id]['quantity'] += quantity
            else:
                self.cart_items[product_id] = {
                    'name': product_name,
                    'price': price,
                    'quantity': quantity
                }
                self.cart.append(self.cart_items[product_id])

            self.update_cart_table()
            self.products_table.cellWidget(row, 2).setText("1")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить товар: {str(e)}")

    def update_cart_table(self):
        self.cart_table.setRowCount(len(self.cart))
        for row, item in enumerate(self.cart):
            self.cart_table.setItem(row, 0, QTableWidgetItem(item['name']))
            self.cart_table.setItem(row, 1, QTableWidgetItem(f"{item['price']:.2f}"))
            self.cart_table.setItem(row, 2, QTableWidgetItem(str(item['quantity'])))

            remove_btn = QPushButton("Удалить")
            remove_btn.clicked.connect(lambda _, r=row: self.remove_from_cart(r))
            self.cart_table.setCellWidget(row, 3, remove_btn)

    def remove_from_cart(self, row):
        if 0 <= row < len(self.cart):
            product_id = self.product_controller.get_product_id_by_name(self.cart[row]['name'])
            del self.cart_items[product_id]
            self.cart.pop(row)
            self.update_cart_table()

    def submit_order(self):
        if not all([self.name_input.text(), self.surname_input.text(),
                    self.email_input.text(), self.address_input.text()]):
            QMessageBox.warning(self, "Ошибка", "Заполните все обязательные поля")
            return

        if not self.cart:
            QMessageBox.warning(self, "Ошибка", "Корзина пуста. Добавьте товары")
            return

        try:
            phone = self.client_phone_input.text().strip()
            if not phone:
                raise Exception("Телефон обязателен")

            # Получаем или создаем клиента
            result = self.client_controller.handle_client_update(
                self.name_input.text(),
                self.surname_input.text(),
                self.email_input.text(),
                phone,
                self.current_client_id  # Передаем текущий ID, если клиент существует
            )
            if not isinstance(result, int):
                raise Exception("Ошибка: некорректный ID клиента")

            client_id = result
            print(f"Используем client_id: {client_id} ({type(client_id)})")  # Для отладки
            if not result:
                raise Exception("Не удалось получить/создать клиента. Возможно телефон занят другим клиентом")

            # Обрабатываем разные форматы возвращаемого значения
            if isinstance(result, tuple):
                client_id = result[0][0]
            elif isinstance(result, int):
                client_id = result
            else:
                raise Exception("Неожиданный формат данных клиента")

            self.current_client_id = client_id  # Сохраняем ID для будущих обновлений

            # Подготавливаем товары для заказа
            order_items = []
            for item in self.cart:
                product_id = self.product_controller.get_product_id_by_name(item['name'])
                if not product_id:
                    raise Exception(f"Не найден ID товара: {item['name']}")

                order_items.append({
                    'id': product_id,
                    'price': item['price'],
                    'quantity': item['quantity']
                })

            # Создаем заказ
            order_id = self.order_controller.create_new_order(
                client_id,
                self.address_input.text(),
                order_items
            )

            if not order_id:
                raise Exception("Не удалось создать заказ в базе данных")

            # Обновляем остатки товаров
            for item in self.cart:
                product_id = self.product_controller.get_product_id_by_name(item['name'])
                self.product_controller.update_product_stock(product_id, item['quantity'])

            # Показываем чек и очищаем корзину
            self.show_receipt(order_id)
            self.cart.clear()
            self.cart_items.clear()
            self.update_cart_table()

            QMessageBox.information(self, "Успех", f"Заказ #{order_id} успешно оформлен!")

            # Сбрасываем форму для нового заказа
            self.address_input.clear()
            self.current_client_id = None

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось оформить заказ: {str(e)}")
            print(f"Ошибка при оформлении заказа: {str(e)}")  # Для отладки

    def show_receipt(self, order_id):
        try:
            # Получаем информацию о заказе
            order_info = self.order_controller.get_order_info(order_id)
            if not order_info:
                raise Exception("Заказ не найден")

            # Получаем товары в заказе
            items = self.order_controller.get_order_items(order_id)
            if not items:
                raise Exception("Товары в заказе не найдены")

            # Формируем текст чека
            receipt_text = (
                f"Заказ №{order_info[0]}\n"
                f"Клиент: {order_info[2]} {order_info[1]}\n"
                f"Адрес: {order_info[4]}\n"
                f"Сумма: {order_info[3]:.2f}\n\n"
                "Товары:\n"
            )

            for item in items:
                receipt_text += f"- {item[0]}: {item[1]} x {item[2]:.2f} = {item[1] * item[2]:.2f}\n"

            # Показываем чек
            msg = QMessageBox()
            msg.setWindowTitle(f"Чек заказа №{order_id}")
            msg.setText(receipt_text)
            msg.exec_()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при формировании чека: {str(e)}")
            print(f"[ОШИБКА] show_receipt: {str(e)}")

    def open_order_filter(self):
        try:
            from views.order_filter_form import OrderFilterForm
            self.filter_form = OrderFilterForm(self.order_controller)
            self.filter_form.show()
            self.hide()
        except ImportError as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить модуль: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть форму: {str(e)}")

    def toggle_client_mode(self, index):
        if index == 0:
            self.client_action_btn.setText("Найти")
            self.client_phone_input.setReadOnly(False)
            self.client_phone_input.setPlaceholderText("Введите телефон для поиска")
            self.clear_client_fields()
        else:
            self.client_action_btn.setText("Создать")
            self.client_phone_input.setReadOnly(False)
            self.client_phone_input.setPlaceholderText("Введите телефон нового клиента")
            self.clear_client_fields()

    def handle_client_action(self):
        phone = self.client_phone_input.text().strip()
        if not phone:
            QMessageBox.warning(self, "Ошибка", "Введите телефон клиента")
            return

        # Ищем клиента
        result = self.client_controller.handle_client_search(phone)

        if result:  # Клиент найден
            client_id, name, surname, email, phone = result
            self.current_client_id = client_id
            self.name_input.setText(name)
            self.surname_input.setText(surname)
            self.email_input.setText(email)
            self.phone_display.setText(phone)
            self.name_input.setReadOnly(False)  # Разрешаем редактирование
            self.surname_input.setReadOnly(False)
            self.email_input.setReadOnly(False)
            self.update_btn.setEnabled(True)
            self.update_btn.setText("Обновить данные")
        else:  # Клиент не найден - создаем нового
            self.clear_client_fields()
            self.name_input.setReadOnly(False)
            self.surname_input.setReadOnly(False)
            self.email_input.setReadOnly(False)
            self.phone_display.setText(phone)
            self.update_btn.setEnabled(True)
            self.update_btn.setText("Создать клиента")
            self.current_client_id = None

    def create_new_client(self):
        phone = self.client_phone_input.text().strip()
        if not phone:
            QMessageBox.warning(self, "Ошибка", "Введите телефон клиента")
            return

        self.clear_client_fields()
        self.name_input.setReadOnly(False)
        self.surname_input.setReadOnly(False)
        self.email_input.setReadOnly(False)
        self.phone_display.setText(phone)
        self.update_btn.setEnabled(True)
        self.update_btn.setText("Сохранить клиента")
        self.current_client_id = None

        QMessageBox.information(self, "Создание",
                                "Заполните данные нового клиента и нажмите 'Сохранить клиента'")