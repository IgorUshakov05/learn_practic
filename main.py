from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QLineEdit, QTableWidget, QTableWidgetItem,
    QDialog, QFormLayout, QSpinBox, QComboBox, QFileDialog
)
from PySide6.QtCore import Qt, QSize
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Настройка базы данных
DATABASE_URI = 'postgresql://postgres:root@localhost:5432/datas'
engine = create_engine(DATABASE_URI)
Base = declarative_base()

# Модели
class Address(Base):
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True)
    index = Column(Integer, nullable=False)
    region = Column(String(255), nullable=False)
    city = Column(String(255), nullable=False)
    street = Column(String(255), nullable=False)
    number = Column(Integer, nullable=False)

class ProductType(Base):
    __tablename__ = 'product_type'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)

class Partner(Base):
    __tablename__ = 'partners'
    id = Column(Integer, primary_key=True)
    company_name = Column(String(255), nullable=False)
    director_name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=False)
    email = Column(String(255), nullable=False)
    rating = Column(Integer, nullable=True)
    partner_type = Column(String(50))
    address_id = Column(Integer, ForeignKey('address.id'))
    product_type_id = Column(Integer, ForeignKey('product_type.id'))
    
    address = relationship("Address")
    product_type = relationship("ProductType")

# Создание таблиц в базе данных
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# Интерфейс приложения
class MasterApp(QWidget):
    def __init__(self):
        super().__init__()

        # Установка иконки приложения
        self.setWindowTitle("Мастер пол")
        self.setWindowIcon(QIcon("./logo.png"))
        self.setFixedSize(1440, 1024)

        # Главный макет
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Верхняя панель
        top_panel = QWidget()
        top_panel.setStyleSheet("background-color: #F4E8D3; padding: 10px;")
        top_layout = QHBoxLayout(top_panel)

        top_icon_label = QLabel()
        top_icon_label.setPixmap(QIcon("./logo.png").pixmap(50, 50))
        top_label = QLabel("Мастер пол")
        top_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-left: 10px;")

        search_box = QLineEdit()
        search_box.setPlaceholderText("Поиск по названию или директору")
        search_box.setFixedWidth(300)
        search_box.setStyleSheet("padding: 5px; margin-left: 10px;")

        add_partner_button = QPushButton("Добавить партнёра")
        add_partner_button.setFixedWidth(150)
        add_partner_button.clicked.connect(self.add_partner)

        create_pdf_button = QPushButton("Создать PDF")
        create_pdf_button.setFixedWidth(150)
        create_pdf_button.clicked.connect(self.create_pdf_report)

        # Добавляем элементы в верхнюю панель
        top_layout.addWidget(top_icon_label)
        top_layout.addWidget(top_label)
        top_layout.addWidget(search_box)
        top_layout.addWidget(add_partner_button)
        top_layout.addWidget(create_pdf_button)
        top_layout.addStretch()
        main_layout.addWidget(top_panel)

        # Создание панели навигации и содержимого
        content_layout = QHBoxLayout()
        left_panel = QWidget()
        left_panel.setFixedWidth(200)
        left_panel.setStyleSheet("background-color: #F4E8D3;")

        left_layout = QVBoxLayout(left_panel)
        left_layout.setAlignment(Qt.AlignTop)

        # Кнопки навигации
        self.partners_button = QPushButton("Партнёры")
        self.partners_button.setIcon(QIcon("./logo.png"))
        self.partners_button.setCheckable(True)
        self.partners_button.setChecked(True)
        self.partners_button.clicked.connect(self.select_partners_tab)

        self.history_button = QPushButton("История")
        self.history_button.setIcon(QIcon('./logo.png'))
        self.history_button.setCheckable(True)
        self.history_button.clicked.connect(self.select_history_tab)

        self.update_tab_styles()

        left_layout.addWidget(self.partners_button)
        left_layout.addWidget(self.history_button)

        right_panel = QWidget()
        self.right_layout = QVBoxLayout(right_panel)
        self.right_layout.setContentsMargins(10, 10, 10, 0)

        # Список партнёров
        self.partners_list = QListWidget()
        self.partners_list.setStyleSheet("background-color: #FFFFFF; border: none;")
        self.partners_list.itemClicked.connect(self.highlight_selected_partner)
        self.partners_list.itemDoubleClicked.connect(self.edit_partner)

        # Загружаем данные партнёров
        self.load_partners_from_db()

        # Устанавливаем макет
        self.right_layout.addWidget(self.partners_list)
        content_layout.addWidget(left_panel)
        content_layout.addWidget(right_panel)
        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

        search_box.textChanged.connect(self.filter_partners)

    def create_pdf_report(self):
        partners_data = session.query(
            Partner.id,
            Partner.company_name,
            Partner.director_name,
            Partner.phone,
            Partner.rating,
            Partner.partner_type,
            Partner.email,
            Partner.address.region,
            Partner.address.city,
            Partner.address.street,
            Partner.address.number,
            Partner.product_type.name
        ).join(Address).join(ProductType).all()

        # Выбор пути сохранения PDF
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить PDF", "", "PDF Files (*.pdf);;All Files (*)", options=options)

        if file_path:
            self.create_pdf(partners_data, file_path)

    def load_partners_from_db(self):
        """Загрузка списка партнеров и отображение их в виджете"""
        self.partners_list.clear()
        partners = session.query(Partner).all()
        for partner in partners:
            item = QListWidgetItem()
            item_widget = self.create_partner_item(partner)
            item.setSizeHint(QSize(item_widget.sizeHint().width(), item_widget.sizeHint().height() + 20))
            self.partners_list.addItem(item)
            self.partners_list.setItemWidget(item, item_widget)
            item.setData(Qt.UserRole, partner)

    def create_partner_item(self, partner=None):
        """Форматирование виджета с информацией о партнере"""
        item_widget = QWidget()
        layout = QVBoxLayout(item_widget)
        layout.setContentsMargins(10, 10, 10, 10)

        if partner:
            address = f"{partner.address.city}, {partner.address.street}, {partner.address.number}"
            type_name = partner.product_type.name if partner.product_type else "Неизвестный тип"
            type_label = QLabel(f"{type_name} | {partner.company_name}")
            director_label = QLabel(f"Директор: {partner.director_name}")
            phone_label = QLabel(f"Телефон: {partner.phone}")
            rating_label = QLabel(f"Рейтинг: {partner.rating}")
            item_widget.setProperty("partner_id", partner.id)  # ID партнёра
        else:
            type_label = QLabel("Тип | Наименование партнёра")
            director_label = QLabel("Директор")
            phone_label = QLabel("+7 223 322 22 32")
            rating_label = QLabel("Рейтинг: 10")

        layout.addWidget(type_label)
        layout.addWidget(director_label)
        layout.addWidget(phone_label)
        layout.addWidget(rating_label)
        item_widget.setStyleSheet("background-color: #FFFFFF; border: 1px solid #F4E8D3; padding: 5px;")
        return item_widget

    def select_partners_tab(self):
        """Метод для выбора вкладки партнёров"""
        pass  # Действия для отображения вкладки партнёров

    def select_history_tab(self):
        """Метод для выбора вкладки истории"""
        pass  # Действия для отображения вкладки истории

    def update_tab_styles(self):
        """Обновление стилей вкладок"""
        pass  # Логика обновления стилей вкладок

    def filter_partners(self, text):
        """Фильтрация партнёров по тексту поиска"""
        pass  # Логика фильтрации

    def highlight_selected_partner(self):
        """Метод для выделения партнёра при клике"""
        pass  # Логика выделения партнёра

    def edit_partner(self):
        """Метод для редактирования информации партнёра"""
        pass  # Логика редактирования партнёра

    def add_partner(self):
        """Метод для добавления нового партнёра"""
        pass  # Логика добавления партнёра

    def create_pdf(self, data, file_path):
        """Метод для создания PDF"""
        pass  # Логика создания PDF

if __name__ == '__main__':
    app = QApplication([])
    window = MasterApp()
    window.show()
    app.exec()
