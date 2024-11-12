import sys
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QLineEdit, QTableWidget, QTableWidgetItem,
    QDialog, QFormLayout, QSpinBox, QComboBox, QStyle, QFileDialog
)
from PySide6.QtCore import Qt, QSize
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from pdf_generator import create_pdf  # Импортируем функцию генерации PDF

# Подключение к базе данных
DATABASE_URI = 'postgresql://postgres:root@localhost:5432/datas'
engine = create_engine(DATABASE_URI)
Base = declarative_base()

# Модели базы данных
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
    partner_type = Column(String(50))
    type_company = relationship("TypeCompany")

# Создание таблиц в базе данных
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

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

        # Таблица истории
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["Продукция", "Наименование партнёра", "Количество продукции", "Дата продажи"])

        # Устанавливаем макет
        self.right_layout.addWidget(self.partners_list)
        content_layout.addWidget(left_panel)
        content_layout.addWidget(right_panel)
        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

        search_box.textChanged.connect(self.filter_partners)

    def create_pdf_report(self):
        partners_data = session.query(
            Partners.id,
            Partners.company_name,
            Partners.director_name,
            Partners.phone,
            Partners.rating,
            Partners.partner_type,
            Partners.email,
            Partners.ur_adress,
            Partners.inn
        ).all()

        type_company_data = session.query(
            TypeCompany.id,
            TypeCompany.name
        ).all()

        # Выбор пути сохранения PDF
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить PDF", "", "PDF Files (*.pdf);;All Files (*)", options=options)

        if file_path:
            create_pdf(partners_data, type_company_data, file_path)

    def load_partners_from_db(self):
        """Загрузка списка партнеров и отображение их в виджете"""
        self.partners_list.clear()
        partners = session.query(Partners).all()
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
            type_name = partner.type_company.name if partner.type_company else "Неизвестный тип"
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


        layout.addWidget(type_label)
        layout.addWidget(director_label)
        layout.addWidget(phone_label)
        layout.addWidget(rating_label)
        item_widget.setStyleSheet("background-color: #FFFFFF; border: 1px solid #F4E8D3; padding: 5px;")
        return item_widget

    def update_tab_styles(self):
        self.partners_button.setStyleSheet("text-align: left; padding: 10px; background-color: #67BA80;" if self.partners_button.isChecked() else "background-color: #FFFFFF; color: black;")
        self.history_button.setStyleSheet("text-align: left; padding: 10px; background-color: #67BA80;" if self.history_button.isChecked() else "background-color: #FFFFFF; color: black;")

    def select_partners_tab(self):
        self.partners_button.setChecked(True)
        self.history_button.setChecked(False)
        self.update_tab_styles()
        self.right_layout.removeWidget(self.history_table)
        self.history_table.setParent(None)
        self.right_layout.addWidget(self.partners_list)

    def select_history_tab(self):
        self.history_button.setChecked(True)
        self.partners_button.setChecked(False)
        self.update_tab_styles()
        self.right_layout.removeWidget(self.partners_list)
        self.partners_list.setParent(None)
        self.right_layout.addWidget(self.history_table)

    def highlight_selected_partner(self, item):
        for i in range(self.partners_list.count()):
            widget = self.partners_list.itemWidget(self.partners_list.item(i))
            widget.setStyleSheet("background-color: #FFFFFF; border: 1px solid #F4E8D3; padding: 5px;")
        selected_widget = self.partners_list.itemWidget(item)
        selected_widget.setStyleSheet("background-color: #67BA80; color: #FFFFFF; border: 1px solid #F4E8D3; padding: 5px;")

    def edit_partner(self, item):
        partner = item.data(Qt.UserRole)
        self.show_partner_edit_dialog(partner)

    def show_partner_edit_dialog(self, partner):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Редактировать партнёра: {partner.company_name}")
        form_layout = QFormLayout(dialog)

        name_edit = QLineEdit(partner.company_name)
        ur_adress_edit = QLineEdit(partner.ur_adress)
        inn_edit = QLineEdit(partner.inn)
        director_name_edit = QLineEdit(partner.director_name)
        phone_edit = QLineEdit(partner.phone)
        email_edit = QLineEdit(partner.email)
        rating_edit = QSpinBox()
        rating_edit.setValue(partner.rating if partner.rating else 0)

        # Выпадающий список типов компании
        type_combo = QComboBox()
        types = session.query(TypeCompany).all()
        for type_ in types:
            type_combo.addItem(type_.name, type_.id)
        type_combo.setCurrentIndex(type_combo.findData(partner.type_partner))

        # Добавляем выпадающий список для типа партнёра
        partner_type_combo = QComboBox()
        partner_type_combo.addItems(["ЗАО", "ООО", "ПАО", "ОАО"])

        form_layout.addRow("Тип партнёра:", partner_type_combo)
        form_layout.addRow("Наименование партнёра:", name_edit)
        form_layout.addRow("Юридический адрес:", ur_adress_edit)
        form_layout.addRow("ИНН:", inn_edit)
        form_layout.addRow("Имя директора:", director_name_edit)
        form_layout.addRow("Телефон:", phone_edit)
        form_layout.addRow("Email:", email_edit)
        form_layout.addRow("Рейтинг:", rating_edit)

        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(lambda: self.save_partner_changes(dialog, partner, type_combo, partner_type_combo, name_edit, ur_adress_edit, inn_edit, director_name_edit, phone_edit, email_edit, rating_edit))
        form_layout.addWidget(save_button)
        dialog.exec()

    def save_partner_changes(self, dialog, partner, type_combo, partner_type_combo, name_edit, ur_adress_edit, inn_edit, director_name_edit, phone_edit, email_edit, rating_edit):
        partner.type_partner = type_combo.currentData()
        partner.company_name = name_edit.text()
        partner.ur_adress = ur_adress_edit.text()
        partner.inn = inn_edit.text()
        partner.director_name = director_name_edit.text()
        partner.phone = phone_edit.text()
        partner.email = email_edit.text()
        partner.rating = rating_edit.value()
        partner.partner_type = partner_type_combo.currentText()
        session.commit()
        dialog.accept()
        self.load_partners_from_db()

    def add_partner(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить партнёра")
        form_layout = QFormLayout(dialog)

        type_combo = QComboBox()
        types = session.query(TypeCompany).all()
        for type_ in types:
            type_combo.addItem(type_.name, type_.id)

        name_edit = QLineEdit()
        ur_adress_edit = QLineEdit()
        inn_edit = QLineEdit()
        director_name_edit = QLineEdit()
        phone_edit = QLineEdit()
        email_edit = QLineEdit()
        rating_edit = QSpinBox()
        rating_edit.setMinimum(0)

        # Добавляем выпадающий список для типа партнёра
        partner_type_combo = QComboBox()
        partner_type_combo.addItems(["ЗАО", "ООО", "ПАО", "ОАО"])

        form_layout.addRow("Тип партнёра:", partner_type_combo)
        form_layout.addRow("Наименование партнёра:", name_edit)
        form_layout.addRow("Юридический адрес:", ur_adress_edit)
        form_layout.addRow("ИНН:", inn_edit)
        form_layout.addRow("Имя директора:", director_name_edit)
        form_layout.addRow("Телефон:", phone_edit)
        form_layout.addRow("Email:", email_edit)
        form_layout.addRow("Рейтинг:", rating_edit)

        add_button = QPushButton("Добавить")
        add_button.clicked.connect(lambda: self.save_new_partner(dialog, type_combo, partner_type_combo, name_edit, ur_adress_edit, inn_edit, director_name_edit, phone_edit, email_edit, rating_edit))
        form_layout.addWidget(add_button)
        dialog.exec()

    def save_new_partner(self, dialog, type_combo, partner_type_combo, name_edit, ur_adress_edit, inn_edit, director_name_edit, phone_edit, email_edit, rating_edit):
        partner = Partners(
            type_partner=type_combo.currentData(),
            company_name=name_edit.text(),
            ur_adress=ur_adress_edit.text(),
            inn=inn_edit.text(),
            director_name=director_name_edit.text(),
            phone=phone_edit.text(),
            email=email_edit.text(),
            rating=rating_edit.value(),
            partner_type=partner_type_combo.currentText()
        )
        session.add(partner)
        session.commit()
        dialog.accept()
        self.load_partners_from_db()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    master_app = MasterApp()
    master_app.show()
    sys.exit(app.exec())
