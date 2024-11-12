import sys
import logging
logging.basicConfig(level=logging.DEBUG)
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QLineEdit, QTableWidget,
    QTableWidgetItem, QDialog, QFormLayout, QMessageBox, QSpinBox, QComboBox
)
from PySide6.QtCore import Qt, QSize
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Подключение к базе данных
DATABASE_URI = 'postgresql://postgres:root@localhost:5432/asd'
engine = create_engine(DATABASE_URI)
Base = declarative_base()

# Модели для базы данных
class TypeCompany(Base):
    __tablename__ = 'type_company'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)

class Partners(Base):
    __tablename__ = 'partners'
    id = Column(Integer, primary_key=True)
    type_partner = Column(Integer, ForeignKey('type_company.id'))
    company_name = Column(String(255), nullable=False)
    ur_adress = Column(String(255), nullable=False)
    inn = Column(String(50), nullable=False)
    director_name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=False)
    email = Column(String(255), nullable=False)
    rating = Column(Integer, nullable=True)
    type_company = relationship("TypeCompany")

class ProductType(Base):
    __tablename__ = 'product_type'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    coefficient = Column(Float, nullable=False)

class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True)
    type = Column(Integer, ForeignKey('product_type.id'))
    description = Column(String(255))
    article = Column(Integer)
    price = Column(Float)
    size = Column(Float)
    class_id = Column(Integer)
    product_type = relationship("ProductType")

class Material(Base):
    __tablename__ = 'material'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    defect = Column(Float)

class MaterialProduct(Base):
    __tablename__ = 'material_product'
    id = Column(Integer, primary_key=True)
    id_product = Column(Integer, ForeignKey('product.id'))
    id_material = Column(Integer, ForeignKey('material.id'))

class PartnerProduct(Base):
    __tablename__ = 'partner_product'
    id = Column(Integer, primary_key=True)
    id_product = Column(Integer, ForeignKey('product.id'))
    id_partner = Column(Integer, ForeignKey('partners.id'))
    quantity = Column(Integer)
    date_of_sale = Column(String(50))  # Use a string for simplicity

    product = relationship("Product")
    partner = relationship("Partners")

# Создание таблиц в базе данных
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# Функция для расчета скидки
def calculate_discount(sales_volume):
    if sales_volume <= 10000:
        return 0
    elif 10000 < sales_volume <= 50000:
        return 5
    elif 50000 < sales_volume <= 300000:
        return 10
    else:
        return 15

# Функция для расчета необходимого материала
def calculate_material_needed(product_id, quantity):
    product = session.query(Product).filter_by(id=product_id).first()
    if not product:
        raise ValueError("Продукт не найден.")

    materials = session.query(MaterialProduct).filter_by(id_product=product_id).all()
    total_material_needed = 0

    for material_product in materials:
        material = session.query(Material).filter_by(id=material_product.id_material).first()
        if not material:
            continue
        # Расчет материала с учетом брака
        material_needed = product.size * quantity * material.defect
        total_material_needed += material_needed

    return total_material_needed

# Главный класс приложения
class MasterApp(QWidget):
    def __init__(self):
        super().__init__()

        # Установка иконки приложения
        self.setWindowTitle("Мастер пол")
        self.setWindowIcon(QIcon("logo.png"))  # Замените на путь к вашему логотипу
        self.setFixedSize(1440, 1024)

        # Главный макет
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Верхняя панель
        top_panel = QWidget()
        top_panel.setStyleSheet("background-color: #F4E8D3; padding: 5px;")
        top_layout = QHBoxLayout(top_panel)

        # Иконка и текст для верхней панели
        top_icon_label = QLabel()
        top_icon_label.setPixmap(QIcon("logo.png").pixmap(50, 50))  # Замените на путь к вашему логотипу
        top_label = QLabel("Мастер пол")
        top_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-left: 0px;")

        search_box = QLineEdit()
        search_box.setPlaceholderText("Поиск")
        search_box.setFixedWidth(200)
        search_box.setStyleSheet("padding: 5px; margin-left: 10px;")

        add_partner_button = QPushButton("Добавить партнёра")
        add_partner_button.setFixedWidth(150)
        add_partner_button.clicked.connect(self.show_add_partner_dialog)

        # Добавляем элементы в верхнюю панель
        top_layout.addWidget(top_icon_label)
        top_layout.addWidget(top_label)
        top_layout.addWidget(search_box)
        top_layout.addWidget(add_partner_button)
        top_layout.addStretch()
        main_layout.addWidget(top_panel)

        # Панель навигации
        navigation_panel = QWidget()
        navigation_panel.setFixedHeight(100)
        navigation_panel.setStyleSheet("background-color: #F4E8D3;")
        nav_layout = QHBoxLayout(navigation_panel)

        # Кнопки навигации с иконками
        self.partners_button = QPushButton("Партнёры")
        self.partners_button.setIcon(QIcon("partner.png"))  # Замените на путь к вашему логотипу
        self.partners_button.setCheckable(True)
        self.partners_button.setChecked(True)
        self.partners_button.clicked.connect(self.select_partners_tab)

        self.history_button = QPushButton("История")
        self.history_button.setIcon(QIcon("history.png"))  # Замените на путь к вашему логотипу
        self.history_button.setCheckable(True)
        self.history_button.clicked.connect(self.select_history_tab)

        self.update_tab_styles()

        nav_layout.addStretch()
        nav_layout.addWidget(self.partners_button)
        nav_layout.addWidget(self.history_button)
        main_layout.addWidget(navigation_panel)

        # Панель с контентом
        content_layout = QHBoxLayout()
        right_panel = QWidget()
        self.right_layout = QVBoxLayout(right_panel)
        self.right_layout.setContentsMargins(10, 10, 10, 0)
        self.partners_list = QListWidget()
        self.partners_list.setStyleSheet("background-color: #FFFFFF; border: none;")
        self.partners_list.itemClicked.connect(self.highlight_selected_partner)
        self.partners_list.itemDoubleClicked.connect(self.edit_partner)
        self.load_partners_from_db()
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["Продукция", "Наименование партнёра", "Количество продукции", "Дата продажи"])
        self.right_layout.addWidget(self.partners_list)
        content_layout.addWidget(right_panel)
        main_layout.addLayout(content_layout)

        self.setLayout(main_layout)

    def load_partners_from_db(self):
        self.partners_list.clear()
        partners = session.query(Partners).all()
        for partner in partners:
            item = QListWidgetItem()
            item_widget = self.create_partner_item(partner)
            item.setSizeHint(QSize(item_widget.sizeHint().width(), item_widget.sizeHint().height() + 20))
            self.partners_list.addItem(item)

            self.partners_list.setItemWidget(item, item_widget)
            item.setData(Qt.UserRole, partner)  # Сохраняем объект партнёра в item

    def load_history_from_db(self):
        # Очистить таблицу истории
        self.history_table.setRowCount(0)

        # Выполняем запрос к базе данных, объединяя таблицы PartnerProduct, Product и Partners
        partner_products = session.query(PartnerProduct, Product, Partners).join(Product, Product.id == PartnerProduct.id_product).join(Partners, Partners.id == PartnerProduct.id_partner).all()

        print(f"Найдено записей: {len(partner_products)}")  # Отладочная информация

        # Заполняем таблицу данными
        for row_num, (partner_product, product, partner) in enumerate(partner_products):
            print(f"Добавление строки: {row_num}")  # Отладочная информация

            # Добавляем строку в таблицу
            self.history_table.insertRow(row_num)

            # Вставляем данные в ячейки таблицы
            self.history_table.setItem(row_num, 0, QTableWidgetItem(product.description))
            self.history_table.setItem(row_num, 1, QTableWidgetItem(partner.company_name))
            self.history_table.setItem(row_num, 2, QTableWidgetItem(str(partner_product.quantity)))
            self.history_table.setItem(row_num, 3, QTableWidgetItem(partner_product.date_of_sale))

    def show_add_partner_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить партнёра")

        # Формы для ввода данных партнёра
        form_layout = QFormLayout(dialog)
        company_name_edit = QLineEdit()
        ur_address_edit = QLineEdit()
        inn_edit = QLineEdit()
        director_name_edit = QLineEdit()
        phone_edit = QLineEdit()
        email_edit = QLineEdit()
        type_company_edit = QComboBox()

        # Получение данных для выбора типа компании
        types = session.query(TypeCompany).all()
        for type in types:
            type_company_edit.addItem(type.name, type.id)

        form_layout.addRow("Название компании:", company_name_edit)
        form_layout.addRow("Юридический адрес:", ur_address_edit)
        form_layout.addRow("ИНН:", inn_edit)
        form_layout.addRow("ФИО директора:", director_name_edit)
        form_layout.addRow("Телефон:", phone_edit)
        form_layout.addRow("Email:", email_edit)
        form_layout.addRow("Тип компании:", type_company_edit)

        # Кнопка сохранения
        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(lambda: self.save_partner(company_name_edit, ur_address_edit,
                                                              inn_edit, director_name_edit, phone_edit,
                                                              email_edit, type_company_edit, dialog))
        form_layout.addWidget(save_button)

        dialog.setLayout(form_layout)
        dialog.exec_()

    def save_partner(self, company_name_edit, ur_address_edit, inn_edit, director_name_edit,
                     phone_edit, email_edit, type_company_edit, dialog):
        partner = Partners(company_name=company_name_edit.text(),
                           ur_adress=ur_address_edit.text(),
                           inn=inn_edit.text(),
                           director_name=director_name_edit.text(),
                           phone=phone_edit.text(),
                           email=email_edit.text(),
                           type_partner=type_company_edit.currentData())
        session.add(partner)
        session.commit()
        dialog.accept()
        self.load_partners_from_db()

    def update_tab_styles(self):
        # Устанавливаем стиль для активной вкладки
        self.partners_button.setStyleSheet("background-color: #E5C59B;")
        self.history_button.setStyleSheet("background-color: #FFFFFF;")

    def select_partners_tab(self):
        self.update_tab_styles()
        self.load_partners_from_db()

    def select_history_tab(self):
        self.update_tab_styles()
        self.load_history_from_db()

    def highlight_selected_partner(self, item):
        partner = item.data(Qt.UserRole)
        print(f"Выбран партнёр: {partner.company_name}")

    def edit_partner(self, item):
        partner = item.data(Qt.UserRole)
        print(f"Редактирование партнёра: {partner.company_name}")

# Запуск приложения
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MasterApp()
    window.show()
    sys.exit(app.exec_())
