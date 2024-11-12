-- Создание таблицы типа компании
CREATE TABLE type_company (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- Вставка данных в таблицу type_company
INSERT INTO type_company (name) VALUES 
('ЗАО'),
('ООО'),
('ПАО'),
('ОАО');

-- Создание таблицы партнёров
CREATE TABLE partners (
    id SERIAL PRIMARY KEY,
    type_partner INT REFERENCES type_company(id),
    company_name VARCHAR(255) NOT NULL,
    ur_adress VARCHAR(255) NOT NULL,
    inn VARCHAR(50) NOT NULL,
    director_name VARCHAR(255) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL,
    rating INT,
    partner_type VARCHAR(50)
);

-- Пример заполнения таблицы партнёров
INSERT INTO partners (type_partner, company_name, ur_adress, inn, director_name, phone, email, rating, partner_type) VALUES
(1, 'Компания 1', 'Адрес 1', '1234567890', 'Иванов И.И.', '+7 123 456 78 90', 'ivanov@mail.ru', 10, 'ЗАО'),
(2, 'Компания 2', 'Адрес 2', '0987654321', 'Петров П.П.', '+7 987 654 32 10', 'petrov@mail.ru', 8, 'ООО'),
(3, 'Компания 3', 'Адрес 3', '1122334455', 'Сидоров С.С.', '+7 555 555 55 55', 'sidorov@mail.ru', 9, 'ПАО');