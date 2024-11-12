from fpdf import FPDF

# Регистрируем шрифт (FreeSans поддерживает Unicode)
def register_font(pdf):
    try:
        # Убедитесь, что файл шрифта существует по указанному пути
        pdf.add_font('FreeSans', '', './freesans.ttf', uni=True)
    except Exception as e:
        print(f"Ошибка при добавлении шрифта: {e}")
        pdf.add_font('Arial', '', '', uni=True)  # Использовать Arial как fallback, если FreeSans не доступен

# Функция для создания PDF с таблицей
def create_pdf(partners_data, type_company_data, file_path):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Регистрируем шрифт для использования
    register_font(pdf)

    # Заголовок таблицы
    pdf.set_font('FreeSans', '', 14)
    pdf.cell(200, 10, 'Типы компаний', ln=True, align='C')
    pdf.ln(10)  # Отступ

    # Добавляем таблицу для типа компаний
    col_widths = [30, 60]
    pdf.set_font('FreeSans', '', 12)
    for row in type_company_data:
        for i, cell in enumerate(row):
            pdf.cell(col_widths[i], 10, str(cell), border=1, align='C')
        pdf.ln()

    pdf.add_page()  # Добавляем новую страницу для таблицы партнеров

    # Заголовок таблицы для партнеров
    pdf.set_font('FreeSans', '', 14)
    pdf.cell(200, 10, 'Партнеры', ln=True, align='C')
    pdf.ln(10)  # Отступ

    # Добавляем таблицу для партнеров
    col_widths = [30, 60, 60, 60, 30, 40, 50, 50, 30]  # Ширина столбцов
    pdf.set_font('FreeSans', '', 12)
    for row in partners_data:
        for i, cell in enumerate(row):
            pdf.cell(col_widths[i], 10, str(cell), border=1, align='C')
        pdf.ln()

    pdf.output(file_path)
    print(f"PDF файл успешно создан: {file_path}")

