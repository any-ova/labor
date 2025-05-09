from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTableWidget,
                             QTableWidgetItem, QMessageBox, QComboBox,
                             QHeaderView)
from PyQt5.QtCore import Qt, QDate
from PyQt5 import QtGui


class OrderFilterForm(QWidget):
    def __init__(self, order_controller):
        super().__init__()
        self.order_controller = order_controller
        self.sort_order = Qt.DescendingOrder
        self.setup_ui()
        self.load_orders()

    def setup_ui(self):
        self.setWindowTitle("Фильтр заказов")
        self.setFixedSize(1000, 650)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # ========== Панель фильтров и сортировки ==========
        filter_panel = QWidget()
        filter_layout = QHBoxLayout(filter_panel)
        filter_layout.setContentsMargins(0, 0, 0, 0)
        filter_layout.setSpacing(15)

        # Фильтр по дате
        date_group = QWidget()
        date_layout = QVBoxLayout(date_group)
        date_layout.setContentsMargins(0, 0, 0, 0)
        date_layout.addWidget(QLabel("Дата:"))
        self.date_filter = QLineEdit()
        self.date_filter.setPlaceholderText("гггг-мм-дд")
        self.date_filter.setFixedWidth(120)
        date_layout.addWidget(self.date_filter)
        filter_layout.addWidget(date_group)

        # Фильтр по клиенту
        client_group = QWidget()
        client_layout = QVBoxLayout(client_group)
        client_layout.setContentsMargins(0, 0, 0, 0)
        client_layout.addWidget(QLabel("Клиент:"))
        self.client_filter = QLineEdit()
        self.client_filter.setPlaceholderText("Фамилия или имя")
        self.client_filter.setFixedWidth(200)
        client_layout.addWidget(self.client_filter)
        filter_layout.addWidget(client_group)

        # Фильтр по статусу
        status_group = QWidget()
        status_layout = QVBoxLayout(status_group)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.addWidget(QLabel("Статус:"))
        self.status_filter = QComboBox()
        self.status_filter.setFixedWidth(150)
        self.status_filter.addItems(
            ["Все", "оплачен", "не оплачен", "доставлен", "обрабатывается", "в процессе доставки"])
        status_layout.addWidget(self.status_filter)
        filter_layout.addWidget(status_group)

        # Кнопки сортировки
        sort_group = QWidget()
        sort_layout = QVBoxLayout(sort_group)
        sort_layout.setContentsMargins(0, 0, 0, 0)
        sort_layout.addWidget(QLabel("Сортировка:"))

        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["По дате (новые)", "По дате (старые)", "По сумме (↑)", "По сумме (↓)"])
        self.sort_combo.setFixedWidth(150)
        self.sort_combo.currentIndexChanged.connect(self.apply_sorting)
        sort_layout.addWidget(self.sort_combo)
        filter_layout.addWidget(sort_group)

        # Кнопки управления
        self.filter_btn = QPushButton("Поиск")
        self.filter_btn.setFixedWidth(100)
        self.filter_btn.clicked.connect(self.load_orders)

        self.clear_btn = QPushButton("Сброс")
        self.clear_btn.setFixedWidth(100)
        self.clear_btn.clicked.connect(self.clear_filters)

        self.export_btn = QPushButton("Экспорт")
        self.export_btn.setFixedWidth(100)
        self.export_btn.clicked.connect(self.export_to_csv)

        filter_layout.addWidget(self.filter_btn)
        filter_layout.addWidget(self.clear_btn)
        filter_layout.addWidget(self.export_btn)
        filter_layout.addStretch()

        main_layout.addWidget(filter_panel)

        # ========== Таблица заказов ==========
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(7)
        self.orders_table.setHorizontalHeaderLabels(
            ["ID", "Дата", "Клиент", "Телефон", "Сумма", "Статус", "Адрес"])

        # Настройка заголовков
        header = self.orders_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)

        # Включаем сортировку
        self.orders_table.setSortingEnabled(True)
        self.orders_table.sortByColumn(1, Qt.DescendingOrder)

        # Подключаем сигнал сортировки
        self.orders_table.horizontalHeader().sectionClicked.connect(self.on_header_clicked)

        self.orders_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.orders_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.orders_table.verticalHeader().setVisible(False)

        # Настройка размеров столбцов
        self.orders_table.setColumnWidth(0, 60)  # ID
        self.orders_table.setColumnWidth(1, 150)  # Дата
        self.orders_table.setColumnWidth(2, 200)  # Клиент
        self.orders_table.setColumnWidth(3, 120)  # Телефон
        self.orders_table.setColumnWidth(4, 100)  # Сумма
        self.orders_table.setColumnWidth(5, 120)  # Статус
        self.orders_table.setColumnWidth(6, 200)  # Адрес

        main_layout.addWidget(self.orders_table)
        self.setLayout(main_layout)

    def on_header_clicked(self, logical_index):
        """Обработчик клика по заголовку таблицы"""
        if logical_index == 1:  # Дата
            current_sort = getattr(self, 'current_date_sort', Qt.DescendingOrder)
            new_sort = Qt.AscendingOrder if current_sort == Qt.DescendingOrder else Qt.DescendingOrder
            self.current_date_sort = new_sort
            self.sort_combo.setCurrentIndex(0 if new_sort == Qt.DescendingOrder else 1)
        elif logical_index == 4:  # Сумма
            current_sort = getattr(self, 'current_amount_sort', Qt.AscendingOrder)
            new_sort = Qt.AscendingOrder if current_sort == Qt.DescendingOrder else Qt.DescendingOrder
            self.current_amount_sort = new_sort
            self.sort_combo.setCurrentIndex(2 if new_sort == Qt.AscendingOrder else 3)

        self.apply_sorting()


    def apply_sorting(self):
        """Применяет выбранную сортировку"""
        sort_option = self.sort_combo.currentText()

        if sort_option == "По дате (новые)":
            self.orders_table.sortByColumn(1, Qt.DescendingOrder)
        elif sort_option == "По дате (старые)":
            self.orders_table.sortByColumn(1, Qt.AscendingOrder)
        elif sort_option == "По сумме (↑)":
            self.orders_table.sortByColumn(4, Qt.AscendingOrder)
        elif sort_option == "По сумме (↓)":
            self.orders_table.sortByColumn(4, Qt.DescendingOrder)

    def load_orders(self):
        """Загрузка заказов с применением фильтров"""
        try:
            # Подготавливаем параметры фильтрации
            filters = {
                'date': self.date_filter.text().strip(),
                'client': self.client_filter.text().strip(),
                'status': self.status_filter.currentText()
            }

            # Получаем отфильтрованные заказы через контроллер
            orders = self.order_controller.get_filtered_orders(filters)

            # Блокируем сортировку во время обновления данных
            self.orders_table.setSortingEnabled(False)
            self.orders_table.setRowCount(0)

            if orders:
                self.orders_table.setRowCount(len(orders))

                for row_idx, (order_id, order_date, client_name,
                              phone, total, status, address) in enumerate(orders):
                    # ID
                    self.orders_table.setItem(row_idx, 0, QTableWidgetItem(str(order_id)))

                    # Дата
                    date_item = QTableWidgetItem(order_date.strftime('%Y-%m-%d %H:%M'))
                    date_item.setData(Qt.UserRole, order_date)
                    self.orders_table.setItem(row_idx, 1, date_item)

                    # Клиент
                    self.orders_table.setItem(row_idx, 2, QTableWidgetItem(client_name))

                    # Телефон
                    self.orders_table.setItem(row_idx, 3, QTableWidgetItem(phone if phone else ""))

                    # Сумма
                    amount_item = QTableWidgetItem(f"{float(total):.2f}")
                    amount_item.setData(Qt.UserRole, float(total))
                    self.orders_table.setItem(row_idx, 4, amount_item)


                    # Статус
                    status_item = QTableWidgetItem(status)
                    self.set_status_color(status_item, status)
                    self.orders_table.setItem(row_idx, 5, status_item)

                    # Адрес
                    self.orders_table.setItem(row_idx, 6, QTableWidgetItem(address))

            # Включаем сортировку обратно
            self.orders_table.setSortingEnabled(True)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить заказы:\n{str(e)}")

    def set_status_color(self, item, status):
        """Установка цвета фона в зависимости от статуса"""
        colors = {
            "оплачен": "#E8F5E9",  # Зеленый
            "не оплачен": "#FFEBEE",  # Красный
            "доставлен": "#E3F2FD",  # Синий
            "обрабатывается": "#FFF8E1",  # Желтый
            "в процессе доставки": "#EDE7F6"  # Фиолетовый
        }
        if status in colors:
            item.setBackground(QtGui.QColor(colors[status]))

    def clear_filters(self):
        """Сброс всех фильтров"""
        self.date_filter.clear()
        self.client_filter.clear()
        self.status_filter.setCurrentIndex(0)
        self.load_orders()

    def export_to_csv(self):
        """Экспорт данных в CSV файл"""
        try:
            from datetime import datetime
            file_name = f"orders_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

            with open(file_name, 'w', encoding='utf-8') as f:
                # Заголовки
                headers = []
                for col in range(self.orders_table.columnCount()):
                    headers.append(self.orders_table.horizontalHeaderItem(col).text())
                f.write(";".join(headers) + "\n")

                # Данные
                for row in range(self.orders_table.rowCount()):
                    row_data = []
                    for col in range(self.orders_table.columnCount()):
                        item = self.orders_table.item(row, col)
                        row_data.append(item.text() if item else "")
                    f.write(";".join(row_data) + "\n")

            QMessageBox.information(self, "Экспорт завершен",
                                    f"Данные успешно экспортированы в файл:\n{file_name}")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка экспорта", f"Не удалось экспортировать данные:\n{str(e)}")