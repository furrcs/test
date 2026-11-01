DROP DATABASE IF EXISTS vetclinic;
CREATE DATABASE vetclinic ENCODING 'UTF8';

\c vetclinic

CREATE TABLE Breeds (
    breed_id SERIAL PRIMARY KEY,
    pet_type VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE Services (
    service_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    price DECIMAL(10,2) NOT NULL
);

CREATE TABLE Suppliers (
    supplier_id SERIAL PRIMARY KEY,
    company_name VARCHAR(200) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100),
    address VARCHAR(200)
);

CREATE TABLE Medicines (
    medicine_id SERIAL PRIMARY KEY,
    supplier_id INT REFERENCES Suppliers(supplier_id) ON DELETE SET NULL,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    unit VARCHAR(50),
    stock INT DEFAULT 0,
    UNIQUE (supplier_id, name)
);

CREATE TABLE Employees (
    employee_id SERIAL PRIMARY KEY,
    name VARCHAR(30) NOT NULL,
    surname VARCHAR(30) NOT NULL,
    third_name VARCHAR(30),
    phone VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(100),
    role VARCHAR(20) NOT NULL
);

CREATE TABLE Clients (
    client_id SERIAL PRIMARY KEY,
    name VARCHAR(30) NOT NULL,
    surname VARCHAR(30) NOT NULL,
    third_name VARCHAR(30),
    phone VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(100)
);

CREATE TABLE Pets (
    pet_id SERIAL PRIMARY KEY,
    breed_id INT REFERENCES Breeds(breed_id) ON DELETE SET NULL,
    name VARCHAR(100) NOT NULL,
    gender VARCHAR(10) NOT NULL,
    color VARCHAR(50),
    birth_date DATE,
    CHECK (gender IN ('самец', 'самка'))
);

CREATE TABLE Client_pet (
    client_id INT REFERENCES Clients(client_id) ON DELETE CASCADE,
    pet_id INT REFERENCES Pets(pet_id) ON DELETE CASCADE,
    PRIMARY KEY (client_id, pet_id)
);

CREATE TABLE Appointments (
    appointment_id SERIAL PRIMARY KEY,
    pet_id INT REFERENCES Pets(pet_id) ON DELETE SET NULL,
    client_id INT REFERENCES Clients(client_id) ON DELETE SET NULL,
    employee_id INT REFERENCES Employees(employee_id) ON DELETE SET NULL,
    appointment_date TIMESTAMP NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'запланирован',
    CHECK (status IN ('запланирован', 'завершён', 'отменён'))
);

CREATE TABLE Medical_records (
    record_id SERIAL PRIMARY KEY,
    appointment_id INT REFERENCES Appointments(appointment_id) ON DELETE CASCADE,
    reason TEXT,
    diagnosis TEXT,
    temperature DECIMAL(4,1),
    weight DECIMAL(5,2),
    recommendations TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (appointment_id)
);

CREATE TABLE Appointment_service (
    appointment_id INT REFERENCES Appointments(appointment_id) ON DELETE CASCADE,
    service_id INT REFERENCES Services(service_id) ON DELETE CASCADE,
    quantity INT NOT NULL DEFAULT 1,
    price DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (appointment_id, service_id)
);

CREATE TABLE Appointment_medicine (
    appointment_id INT REFERENCES Appointments(appointment_id) ON DELETE CASCADE,
    medicine_id INT REFERENCES Medicines(medicine_id) ON DELETE CASCADE,
    quantity INT NOT NULL DEFAULT 1,
    dosage VARCHAR(100),
    price DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (appointment_id, medicine_id)
);

CREATE TABLE Payments (
    payment_id SERIAL PRIMARY KEY,
    employee_id INT REFERENCES Employees(employee_id) ON DELETE SET NULL,
    client_id INT REFERENCES Clients(client_id) ON DELETE SET NULL,
    appointment_id INT REFERENCES Appointments(appointment_id),
    payment_date TIMESTAMP,
    payment_method VARCHAR(20),
    amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) NOT NULL,
    UNIQUE (appointment_id),
    CHECK (amount >= 0),
    CHECK (status IN ('не оплачен', 'оплачен'))
);




INSERT INTO Breeds (pet_type, name) VALUES
('кошка',  'Британская короткошёрстная'),
('кошка',  'Мейн-кун'),
('кошка',  'Сфинкс'),
('кошка',  'Шотландская вислоухая'),
('собака', 'Лабрадор-ретривер'),
('собака', 'Немецкая овчарка'),
('собака', 'Йоркширский терьер'),
('собака', 'Хаски'),
('собака', 'Чихуахуа'),
('птица',  'Волнистый попугай'),
('грызун', 'Джунгарский хомяк');

INSERT INTO Services (name, price) VALUES
('Первичный приём',            800.00),
('Повторный приём',            500.00),
('Вакцинация',                1200.00),
('УЗИ',                       1800.00),
('Рентген',                   2200.00),
('Общий анализ крови',         900.00),
('Биохимический анализ крови',1500.00),
('Стрижка когтей',             300.00),
('Кастрация',                 5000.00),
('Стерилизация',              7000.00),
('Чистка зубов',              3500.00),
('Установка микрочипа',       1500.00);

INSERT INTO Suppliers (company_name, phone, email, address) VALUES
('ООО "ВетФарм"',   '+7-495-111-22-33', 'sales@vetfarm.ru', 'г. Москва, ул. Ленина, 15'),
('ЗАО "ЗооМед"',    '+7-812-444-55-66', 'info@zoomed.ru',   'г. Санкт-Петербург, пр. Мира, 8'),
('ИП Смирнов А.В.', '+7-903-777-88-99', 'smirnov@mail.ru',  'г. Казань, ул. Гагарина, 42'),
('ООО "ПетТовары"', '+7-499-222-33-44', NULL,               'г. Москва, ш. Энтузиастов, 100');

INSERT INTO Medicines (supplier_id, name, price, unit, stock) VALUES
(1, 'Амоксициллин 15%',        450.00, 'флакон 10 мл',    25),
(1, 'Новокаин 0.5%',           120.00, 'ампула 5 мл',    100),
(1, 'Дексаметазон',            280.00, 'ампула 2 мл',     40),
(2, 'Мелоксикам (Метакам)',    890.00, 'флакон 10 мл',    15),
(2, 'Фуросемид',                95.00, 'ампула 2 мл',     80),
(2, 'Тиамин (B1)',             150.00, 'ампула 1 мл',     60),
(3, 'Габапентин',              620.00, 'упаковка 30 капс.',20),
(3, 'Омепразол',               340.00, 'упаковка 30 капс.',30),
(4, 'Витамины VetLife',        550.00, 'флакон 50 мл',    50),
(4, 'Шампунь лечебный',        780.00, 'бутылка 250 мл',  12);

INSERT INTO Employees (name, surname, third_name, phone, email, role) VALUES
('Ольга',     'Иванова',  'Петровна',     '+7-901-100-10-10', 'ivanova@vetclinic.ru', 'admin'),
('Дмитрий',   'Соколов',  'Андреевич',    '+7-901-200-20-20', 'sokolov@vetclinic.ru', 'doctor'),
('Екатерина', 'Морозова', 'Сергеевна',    '+7-901-300-30-30', 'morozova@vetclinic.ru', 'doctor'),
('Артём',     'Кузнецов', 'Игоревич',     '+7-901-400-40-40', 'kuznetsov@vetclinic.ru', 'assistant'),
('Мария',     'Попова',   'Владимировна', '+7-901-500-50-50', 'popova@vetclinic.ru', 'receptionist'),
('Игорь',     'Лебедев',  NULL,           '+7-901-600-60-60', NULL, 'doctor');

INSERT INTO Clients (name, surname, third_name, phone, email) VALUES
('Анна',     'Петрова',  'Ивановна',     '+7-910-101-01-01', 'anna.p@mail.ru'),
('Сергей',   'Волков',   'Дмитриевич',   '+7-910-202-02-02', 'volkov@yandex.ru'),
('Елена',    'Зайцева',  NULL,           '+7-910-303-03-03', 'zaitseva@gmail.com'),
('Михаил',   'Орлов',    'Александрович','+7-910-404-04-04', NULL),
('Татьяна',  'Никитина', 'Юрьевна',      '+7-910-505-05-05', 'nikitina@mail.ru'),
('Андрей',   'Фёдоров',  'Олегович',     '+7-910-606-06-06', 'fedorov@bk.ru'),
('Светлана', 'Козлова',  'Михайловна',   '+7-910-707-07-07', 'kozlova@mail.ru');

INSERT INTO Pets (breed_id, name, gender, color, birth_date) VALUES
(1,  'Мурка',  'самка',  'серая',         '2021-05-10'),
(5,  'Барсик', 'самец',  'палевый',       '2020-03-15'),
(2,  'Симба',  'самец',  'рыжий',         '2022-07-01'),
(6,  'Рекс',   'самец',  'чёрный',        '2019-11-20'),
(7,  'Чип',    'самец',  'коричневый',    '2023-02-14'),
(3,  'Луна',   'самка',  'белый',         '2021-09-30'),
(10, 'Кеша',   'самец',  'зелёный',       '2022-04-12'),
(4,  'Плюша',  'самка',  'серо-белый',    '2020-12-25'),
(8,  'Найда',  'самка',  'серо-белый',    '2018-06-05'),
(9,  'Бублик', 'самец',  'бежевый',       '2023-01-08'),
(11, 'Хома',   'самец',  'рыже-серый',    '2023-03-20');

INSERT INTO Client_pet (client_id, pet_id) VALUES
(1, 1),  (1, 2),   -- Анна: Мурка, Барсик
(2, 3),  (2, 4),   -- Сергей: Симба, Рекс
(3, 5),  (3, 6),   -- Елена: Чип, Луна
(4, 7),            -- Михаил: Кеша
(5, 8),            -- Татьяна: Плюша
(6, 9),  (6, 10),  -- Андрей: Найда, Бублик
(7, 11);           -- Светлана: Хома

INSERT INTO Appointments (pet_id, client_id, employee_id, appointment_date, status) VALUES
(1, 1, 2, '2025-09-01 10:00:00', 'завершён'),
(3, 2, 3, '2025-09-01 11:30:00', 'завершён'),
(4, 2, 6, '2025-09-02 09:00:00', 'завершён'),
(2, 1, 2, '2025-09-03 14:00:00', 'завершён'),
(5, 3, 3, '2025-09-05 15:30:00', 'отменён'),
(7, 4, 3, '2025-09-07 12:00:00', 'завершён'),
(6, 3, 2, '2025-09-10 16:00:00', 'завершён'),
(8, 5, 6, '2025-09-12 10:30:00', 'завершён'),
(1, 1, 2, '2025-10-15 09:30:00', 'запланирован'),
(11,7, 3, '2025-10-16 11:00:00', 'запланирован');

INSERT INTO Medical_records (appointment_id, reason, diagnosis, temperature, weight, recommendations, description) VALUES
(1, 'Плановый осмотр',            'Здорова',                     38.5, 4.20, 'Повторный осмотр через год',       'Общее состояние удовлетворительное'),
(2, 'Кашель, вялость',            'Бронхит',                     39.2, 5.80, 'Антибиотики 7 дней, повтор через 5 дней', 'Хрипы в лёгких, назначено лечение'),
(3, 'Хромота на заднюю лапу',     'Растяжение связок',           38.7,28.50, 'Ограничить активность 2 недели',   'Рентген без переломов'),
(4, 'Вакцинация',                 'Здоров',                      38.4, 4.50, 'Следующая вакцинация через год',   'Привит от бешенства и комплексно'),
(6, 'Потеря аппетита',            'Гастрит',                     39.0, 0.05, 'Диета, омепразол 10 дней',         'Птица ослаблена, назначено лечение'),
(7, 'Плановый осмотр',            'Здорова',                     38.3, 3.80, 'Обработка от паразитов',           'Проблем не выявлено'),
(8, 'Расчёсы на боках',           'Аллергический дерматит',      38.6, 6.10, 'Гипоаллергенный корм, шампунь',    'Назначен лечебный шампунь');

INSERT INTO Appointment_service (appointment_id, service_id, quantity, price) VALUES
(1, 1,  1,  800.00),   -- Мурка: первичный приём
(1, 8,  1,  300.00),   -- Мурка: стрижка когтей
(2, 1,  1,  800.00),   -- Симба: первичный приём
(2, 5,  1, 2200.00),   -- Симба: рентген
(3, 1,  1,  800.00),   -- Рекс: первичный приём
(3, 5,  1, 2200.00),   -- Рекс: рентген
(4, 3,  1, 1200.00),   -- Барсик: вакцинация
(6, 1,  1,  800.00),   -- Кеша: первичный приём
(7, 1,  1,  800.00),   -- Луна: первичный приём
(7, 12, 1, 1500.00),   -- Луна: микрочип
(8, 1,  1,  800.00),   -- Плюша: первичный приём
(8, 4,  1, 1800.00);   -- Плюша: УЗИ

INSERT INTO Appointment_medicine (appointment_id, medicine_id, quantity, dosage, price) VALUES
(2, 1, 1, '1 мл 2 раза в день',             450.00),   -- Симба: Амоксициллин
(2, 8, 1, '1 капсула в день',               340.00),   -- Симба: Омепразол
(6, 8, 1, '1 капсула в день',               340.00),   -- Кеша: Омепразол
(8, 10,1, 'Наносить на поражённые участки', 780.00);   -- Плюша: Шампунь

INSERT INTO Payments (employee_id, client_id, appointment_id, payment_date, payment_method, amount, status) VALUES
(5, 1, 1, '2025-09-01 10:45:00', 'карта',    1100.00, 'оплачен'),   -- Мурка (800+300)
(5, 2, 2, '2025-09-01 12:30:00', 'наличные', 3790.00, 'оплачен'),   -- Симба (800+2200+450+340)
(5, 2, 3, '2025-09-02 10:00:00', 'карта',    3000.00, 'оплачен'),   -- Рекс (800+2200)
(5, 1, 4, '2025-09-03 14:30:00', 'карта',    1200.00, 'оплачен'),   -- Барсик (вакцинация)
(5, 4, 6, '2025-09-07 12:45:00', 'наличные', 1140.00, 'оплачен'),   -- Кеша (800+340)
(5, 3, 7, NULL,                  NULL,       2300.00, 'не оплачен'),-- Луна (800+1500) — долг
(5, 5, 8, NULL,                  NULL,       3380.00, 'не оплачен');-- Плюша (800+1800+780) — долг


DROP DATABASE IF EXISTS school;
CREATE DATABASE school ENCODING 'UTF8';

\c school

CREATE TABLE classes (
    class_id SERIAL PRIMARY KEY,
    name VARCHAR(5) NOT NULL UNIQUE
);

CREATE TABLE subjects (
    subject_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE teachers (
    teacher_id SERIAL PRIMARY KEY,
    last_name VARCHAR(50) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    middle_name VARCHAR(50),
    phone VARCHAR(30) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE students (
    student_id SERIAL PRIMARY KEY,
    last_name VARCHAR(50) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    middle_name VARCHAR(50),
    birth_date DATE,
    phone VARCHAR(30) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    class_id INTEGER NOT NULL REFERENCES classes (class_id)
);

CREATE TABLE teachings (
    teaching_id SERIAL PRIMARY KEY,
    teacher_id INTEGER NOT NULL REFERENCES teachers (teacher_id),
    subject_id INTEGER NOT NULL REFERENCES subjects (subject_id),
    class_id INTEGER NOT NULL REFERENCES classes (class_id),
    UNIQUE (teacher_id, subject_id, class_id)
);

CREATE TABLE lessons (
    lesson_number INTEGER  PRIMARY KEY,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    CHECK (end_time > start_time)
);

CREATE TABLE schedule (
    schedule_id SERIAL PRIMARY KEY,
    class_id INTEGER NOT NULL REFERENCES classes (class_id),
    subject_id INTEGER NOT NULL REFERENCES subjects (subject_id),
    teacher_id INTEGER NOT NULL REFERENCES teachers (teacher_id),
    week_day INTEGER NOT NULL CHECK (week_day BETWEEN 1 AND 7),
    lesson_number INTEGER  NOT NULL REFERENCES lessons (lesson_number),
    UNIQUE (class_id, week_day, lesson_number),
    UNIQUE (teacher_id, week_day, lesson_number)
);

CREATE TABLE grades (
    grade_id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students (student_id),
    teaching_id INTEGER NOT NULL REFERENCES teachings (teaching_id),
    grade INTEGER NOT NULL CHECK (grade BETWEEN 1 AND 5),
    grade_date DATE NOT NULL
);


DROP DATABASE IF EXISTS furniture;
CREATE DATABASE furniture ENCODING 'UTF8';

\c furniture

CREATE TABLE client (
    client_id   SERIAL PRIMARY KEY,
    last_name   VARCHAR(50) NOT NULL,
    first_name  VARCHAR(50) NOT NULL,
    middle_name VARCHAR(50),
    phone       VARCHAR(20),
    email       VARCHAR(100)
);
CREATE TABLE employee (
    employee_id SERIAL PRIMARY KEY,
    last_name   VARCHAR(50) NOT NULL,
    first_name  VARCHAR(50) NOT NULL,
    middle_name VARCHAR(50),
    position    VARCHAR(20) NOT NULL
                CHECK (position IN ('товаровед','менеджер','технолог')),
    phone       VARCHAR(20),
    email       VARCHAR(100)
);
CREATE TABLE supplier (
    supplier_id  SERIAL PRIMARY KEY,
    company_name VARCHAR(100) NOT NULL,
    phone        VARCHAR(20),
    address      VARCHAR(200),
    email        VARCHAR(100)
);
CREATE TABLE material (
    material_id   SERIAL PRIMARY KEY,
    supplier_id   INTEGER REFERENCES supplier(supplier_id),
    name          VARCHAR(100) NOT NULL,
    material_type VARCHAR(50),
    unit          VARCHAR(20),
    price         NUMERIC(10,2)
);
CREATE TABLE supply (
    supply_id   SERIAL PRIMARY KEY,
    supplier_id INTEGER REFERENCES supplier(supplier_id),
    supply_date DATE
);
CREATE TABLE supply_item (
    supply_id   INTEGER REFERENCES supply(supply_id) ON DELETE CASCADE,
    material_id INTEGER REFERENCES material(material_id),
    quantity    NUMERIC(10,2),
    PRIMARY KEY (supply_id, material_id)
);
CREATE TABLE product (
    product_id     SERIAL PRIMARY KEY,
    name           VARCHAR(100) NOT NULL,
    furniture_type VARCHAR(50),
    price          NUMERIC(10,2)
);
CREATE TABLE product_material (
    product_id  INTEGER REFERENCES product(product_id) ON DELETE CASCADE,
    material_id INTEGER REFERENCES material(material_id),
    quantity    NUMERIC(10,2),
    PRIMARY KEY (product_id, material_id)
);
CREATE TABLE orders (
    order_id    SERIAL PRIMARY KEY,
    client_id   INTEGER REFERENCES client(client_id),
    employee_id INTEGER REFERENCES employee(employee_id),
    order_date  DATE,
    due_date    DATE,
    status      VARCHAR(20) NOT NULL DEFAULT 'новый'
                CHECK (status IN ('новый','в_работе','выполнен','отменён')),
    total_cost  NUMERIC(12,2)
);
CREATE TABLE order_item (
    order_id   INTEGER REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES product(product_id),
    quantity   INTEGER,
    PRIMARY KEY (order_id, product_id)
);


DROP DATABASE IF EXISTS art_gallery;
CREATE DATABASE art_gallery ENCODING 'UTF8';

\c art_gallery

CREATE TABLE IF NOT EXISTS artists (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS halls (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    floor INTEGER
);

CREATE TABLE IF NOT EXISTS paintings (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    artist VARCHAR(100) NOT NULL,
    creation_year INTEGER,
    hall VARCHAR(50),
    artist_id INTEGER REFERENCES artists(id),
    hall_id INTEGER REFERENCES halls(id)
);

CREATE TABLE IF NOT EXISTS exhibitions (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    exhibition_date DATE,
    hall VARCHAR(50),
    hall_id INTEGER REFERENCES halls(id)
);

CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    position VARCHAR(50),
    phone VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS excursions (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    guide VARCHAR(100),
    excursion_date DATE,
    employee_id INTEGER REFERENCES employees(id)
);

CREATE TABLE IF NOT EXISTS visitors (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    visit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tickets (
    id SERIAL PRIMARY KEY,
    visitor VARCHAR(100) NOT NULL,
    ticket_type VARCHAR(30),
    price NUMERIC(8,2),
    status VARCHAR(30) DEFAULT 'Оплачен',
    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    visitor_id INTEGER REFERENCES visitors(id),
    employee_id INTEGER REFERENCES employees(id)
);

CREATE TABLE IF NOT EXISTS excursion_registrations (
    id SERIAL PRIMARY KEY,
    visitor_id INTEGER REFERENCES visitors(id),
    excursion_id INTEGER REFERENCES excursions(id),
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS employee_schedules (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employees(id),
    work_date DATE NOT NULL,
    start_time TIME,
    end_time TIME
);

CREATE TABLE IF NOT EXISTS exhibition_paintings (
    exhibition_id INTEGER REFERENCES exhibitions(id),
    painting_id INTEGER REFERENCES paintings(id),
    PRIMARY KEY (exhibition_id, painting_id)
);

DROP DATABASE IF EXISTS construction_company;
CREATE DATABASE construction_company ENCODING 'UTF8';

\c construction_company

CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    last_name VARCHAR(80) NOT NULL,
    first_name VARCHAR(80) NOT NULL,
    middle_name VARCHAR(80),
    title VARCHAR(120) NOT NULL,
    hire_date DATE NOT NULL DEFAULT CURRENT_DATE,
    salary NUMERIC(12,2) NOT NULL CHECK (salary >= 0),
    department_id INTEGER NOT NULL REFERENCES departments(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    phone VARCHAR(30),
    email VARCHAR(160),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(180) NOT NULL,
    contact_name VARCHAR(160),
    phone VARCHAR(30),
    email VARCHAR(160),
    address VARCHAR(250),
    city VARCHAR(100),
    country VARCHAR(100) NOT NULL DEFAULT 'Россия'
);

CREATE TABLE suppliers (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(180) NOT NULL UNIQUE,
    contact_name VARCHAR(160),
    phone VARCHAR(30),
    email VARCHAR(160),
    address VARCHAR(250),
    country VARCHAR(100) NOT NULL DEFAULT 'Россия'
);

CREATE TABLE materials (
    id SERIAL PRIMARY KEY,
    material_name VARCHAR(180) NOT NULL UNIQUE,
    unit VARCHAR(30) NOT NULL,
    unit_price NUMERIC(14,2) NOT NULL CHECK (unit_price >= 0),
    stock_quantity NUMERIC(14,3) NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    min_stock NUMERIC(14,3) NOT NULL DEFAULT 0 CHECK (min_stock >= 0)
);

CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    project_name VARCHAR(180) NOT NULL UNIQUE,
    start_date DATE NOT NULL,
    end_date DATE,
    status VARCHAR(40) NOT NULL DEFAULT 'Проектирование'
        CHECK (status IN ('Проектирование','В работе','Приостановлен','Завершён')),
    manager_id INTEGER REFERENCES employees(id) ON UPDATE CASCADE ON DELETE SET NULL,
    CHECK (end_date IS NULL OR end_date >= start_date)
);

CREATE TABLE construction_objects (
    id SERIAL PRIMARY KEY,
    address VARCHAR(250) NOT NULL,
    city VARCHAR(100) NOT NULL,
    object_type VARCHAR(100) NOT NULL,
    area NUMERIC(14,2) NOT NULL CHECK (area > 0),
    floors INTEGER NOT NULL CHECK (floors > 0),
    project_id INTEGER NOT NULL REFERENCES projects(id) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE contracts (
    id SERIAL PRIMARY KEY,
    contract_number VARCHAR(60) NOT NULL UNIQUE,
    contract_date DATE NOT NULL,
    total_amount NUMERIC(16,2) NOT NULL CHECK (total_amount > 0),
    client_id INTEGER NOT NULL REFERENCES clients(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    status VARCHAR(40) NOT NULL DEFAULT 'Действует'
        CHECK (status IN ('Черновик','Действует','Исполнен','Расторгнут'))
);

CREATE TABLE project_employees (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON UPDATE CASCADE ON DELETE CASCADE,
    employee_id INTEGER NOT NULL REFERENCES employees(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    role VARCHAR(120) NOT NULL,
    UNIQUE(project_id, employee_id)
);

CREATE TABLE supplies (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    material_id INTEGER NOT NULL REFERENCES materials(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    supplier_id INTEGER REFERENCES suppliers(id) ON UPDATE CASCADE ON DELETE SET NULL,
    supply_date DATE NOT NULL,
    quantity NUMERIC(14,3) NOT NULL CHECK (quantity > 0),
    price NUMERIC(16,2) NOT NULL CHECK (price >= 0),
    status VARCHAR(40) NOT NULL DEFAULT 'Получена'
        CHECK (status IN ('Ожидается','В пути','Получена','Частично получена','Отменена'))
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    order_number VARCHAR(60) NOT NULL UNIQUE,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    material_id INTEGER NOT NULL REFERENCES materials(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    supplier_id INTEGER NOT NULL REFERENCES suppliers(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    quantity NUMERIC(14,3) NOT NULL CHECK (quantity > 0),
    unit VARCHAR(30) NOT NULL,
    unit_price NUMERIC(14,2) NOT NULL CHECK (unit_price >= 0),
    order_date DATE NOT NULL DEFAULT CURRENT_DATE,
    planned_delivery_date DATE NOT NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'Создан'
        CHECK (status IN ('Создан','Согласован','Заказан','В пути','Доставлен','Отменён')),
    comment TEXT,
    created_by INTEGER
);

CREATE TABLE vehicles (
    id SERIAL PRIMARY KEY,
    plate_number VARCHAR(20) NOT NULL UNIQUE,
    vehicle_type VARCHAR(80) NOT NULL,
    brand VARCHAR(100) NOT NULL,
    capacity_tons NUMERIC(8,2) NOT NULL CHECK (capacity_tons > 0),
    status VARCHAR(40) NOT NULL DEFAULT 'Свободен'
        CHECK (status IN ('Свободен','Назначен','В рейсе','На обслуживании'))
);

CREATE TABLE drivers (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL UNIQUE REFERENCES employees(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    license_number VARCHAR(40) NOT NULL UNIQUE,
    phone VARCHAR(30),
    status VARCHAR(40) NOT NULL DEFAULT 'Доступен'
        CHECK (status IN ('Доступен','Назначен','В рейсе','Недоступен'))
);

CREATE TABLE deliveries (
    id SERIAL PRIMARY KEY,
    delivery_number VARCHAR(60) NOT NULL UNIQUE,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    vehicle_id INTEGER REFERENCES vehicles(id) ON UPDATE CASCADE ON DELETE SET NULL,
    driver_id INTEGER REFERENCES drivers(id) ON UPDATE CASCADE ON DELETE SET NULL,
    from_address VARCHAR(250) NOT NULL DEFAULT 'Склад',
    to_address VARCHAR(250) NOT NULL,
    planned_date DATE NOT NULL,
    planned_time TIME NOT NULL DEFAULT '10:00',
    actual_date DATE,
    status VARCHAR(40) NOT NULL DEFAULT 'Запланирована'
        CHECK (status IN ('Запланирована','Назначен транспорт','В пути','Доставлена','Отменена')),
    comment TEXT
);

CREATE TABLE routes (
    id SERIAL PRIMARY KEY,
    delivery_id INTEGER NOT NULL REFERENCES deliveries(id) ON UPDATE CASCADE ON DELETE CASCADE,
    sequence_no INTEGER NOT NULL CHECK (sequence_no > 0),
    address VARCHAR(250) NOT NULL,
    planned_arrival TIME,
    status VARCHAR(40) NOT NULL DEFAULT 'Ожидает'
        CHECK (status IN ('Ожидает','Пройден','Пропущен')),
    UNIQUE(delivery_id, sequence_no)
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role_name VARCHAR(80) NOT NULL CHECK (role_name IN ('Администратор','Менеджер','Сотрудник ПТО','Сотрудник ОМТС','Диспетчер гаража','Клиент')),
    employee_id INTEGER UNIQUE REFERENCES employees(id) ON UPDATE CASCADE ON DELETE SET NULL,
    client_id INTEGER UNIQUE REFERENCES clients(id) ON UPDATE CASCADE ON DELETE SET NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (employee_id IS NULL OR client_id IS NULL)
);

CREATE TABLE user_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON UPDATE CASCADE ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    entity_name VARCHAR(100),
    entity_id INTEGER,
    details TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_deliveries_date ON deliveries(planned_date);
CREATE INDEX idx_supplies_project ON supplies(project_id);
CREATE INDEX idx_logs_created_at ON user_logs(created_at);

-- Демонстрационные данные: исходные данные пользователя сохранены и дополнены.
INSERT INTO departments (name, description) VALUES
('Администрация','Управление организацией и информационной системой'),
('ПТО','Проектно-техническое сопровождение строительства'),
('ОМТС','Закупка и снабжение строительными материалами'),
('Гараж','Транспорт и доставка материалов');

INSERT INTO employees (last_name, first_name, middle_name, title, hire_date, salary, department_id, phone, email) VALUES
('Иванов','Алексей','Сергеевич','Главный инженер','2021-01-15',120000,2,'+79990000001','ivanov@stroy.example'),
('Петров','Дмитрий','Олегович','Прораб','2022-03-10',95000,2,'+79990000002','petrov@stroy.example'),
('Сидоров','Максим','Андреевич','Менеджер по закупкам','2023-05-20',85000,3,'+79990000003','sidorov@stroy.example'),
('Смирнова','Елена','Игоревна','Администратор системы','2020-09-01',110000,1,'+79990000004','smirnova@stroy.example'),
('Кузнецов','Олег','Викторович','Диспетчер гаража','2022-11-15',90000,4,'+79990000005','kuznetsov@stroy.example'),
('Волкова','Анна','Павловна','Менеджер проектов','2024-02-01',98000,1,'+79990000006','volkova@stroy.example');

INSERT INTO clients (company_name, contact_name, phone, email, address, city, country) VALUES
('ООО СтройИнвест','Сергей Волков','+79991112233','volkov@stroyinvest.ru','ул. Ленина, 10','Москва','Россия'),
('ООО АльфаСтрой','Ирина Морозова','+79991112234','info@alfastroy.ru','пр. Мира, 15','Санкт-Петербург','Россия'),
('ЗАО Монолит','Павел Егоров','+79991112235','contact@monolit.ru','ул. Советская, 7','Казань','Россия');

INSERT INTO suppliers (company_name, contact_name, phone, email, address, country) VALUES
('МеталлТорг','Александр Крылов','+79995556677','sales@metalltorg.example','Промышленная, 1','Россия'),
('БетонСнаб','Виктор Громов','+79995556678','info@betonsnab.example','Заводская, 4','Россия'),
('ЛесМаркет','Николай Орлов','+79995556679','order@lesmarket.example','Лесная, 8','Россия');

INSERT INTO materials (material_name, unit, unit_price, stock_quantity, min_stock) VALUES
('Арматура А500','тонна',65000,18,5),
('Бетон М300','м3',5800,140,30),
('Цемент М500','мешок',450,700,100),
('Кирпич облицовочный','шт',35,25000,5000),
('Доска обрезная','м3',14000,28,8);

INSERT INTO projects (project_name, start_date, end_date, status, manager_id) VALUES
('ЖК Северный','2025-01-10','2027-12-31','В работе',1),
('Бизнес-центр Плаза','2025-03-01','2026-10-30','В работе',2),
('Школа №25','2025-02-15','2026-08-15','Проектирование',1);

INSERT INTO construction_objects (address, city, object_type, area, floors, project_id) VALUES
('ул. Парковая, 5','Москва','Жилой комплекс',25000,18,1),
('ул. Парковая, 7','Москва','Жилой комплекс',18000,16,1),
('пр. Мира, 25','Москва','Бизнес-центр',32000,22,2),
('ул. Молодёжная, 18','Казань','Школа',12000,4,3);

INSERT INTO contracts (contract_number, contract_date, total_amount, client_id, project_id, status) VALUES
('CNT-2025-001','2025-01-05',250000000,1,1,'Действует'),
('CNT-2025-002','2025-02-20',180000000,2,2,'Действует'),
('CNT-2025-003','2025-02-01',95000000,3,3,'Действует');

INSERT INTO project_employees (project_id, employee_id, role) VALUES
(1,1,'Руководитель проекта'),(1,2,'Прораб'),(2,2,'Руководитель проекта'),(2,3,'Снабжение'),(3,1,'Главный инженер');

INSERT INTO supplies (project_id, material_id, supplier_id, supply_date, quantity, price, status) VALUES
(1,1,1,'2025-01-20',15,975000,'Получена'),
(1,2,2,'2025-01-25',120,696000,'Получена'),
(2,3,2,'2025-03-10',500,225000,'Получена'),
(2,4,1,'2025-03-15',20000,700000,'Получена'),
(3,5,3,'2025-02-25',30,420000,'Получена');

INSERT INTO vehicles (plate_number, vehicle_type, brand, capacity_tons, status) VALUES
('А123ВС777','Бортовой грузовик','КамАЗ',10,'Свободен'),
('В456ОР799','Самосвал','КамАЗ',15,'Свободен'),
('С789ТК750','Фургон','ГАЗ',3.5,'Свободен');

INSERT INTO drivers (employee_id, license_number, phone, status) VALUES
(5,'RU-DRV-0001','+79990000005','Доступен');

-- Хеши паролей создаются Python-приложением при первом запуске, если seed-пользователей ещё нет.
-- Ниже временные маркеры заменяются на валидные PBKDF2-хеши в файле setup_seed_users.py.
ALTER TABLE orders ADD CONSTRAINT fk_orders_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON UPDATE CASCADE ON DELETE SET NULL;

INSERT INTO users (username, password_hash, role_name, employee_id, client_id) VALUES
('admin','RESET_ON_FIRST_LOGIN','Администратор',4,NULL),
('manager','RESET_ON_FIRST_LOGIN','Менеджер',6,NULL),
('pto','RESET_ON_FIRST_LOGIN','Сотрудник ПТО',1,NULL),
('omts','RESET_ON_FIRST_LOGIN','Сотрудник ОМТС',3,NULL),
('garage','RESET_ON_FIRST_LOGIN','Диспетчер гаража',5,NULL),
('client1','RESET_ON_FIRST_LOGIN','Клиент',NULL,1);

INSERT INTO orders (order_number, project_id, material_id, supplier_id, quantity, unit, unit_price, order_date, planned_delivery_date, status, comment) VALUES
('ORD-2026-001',1,3,2,500,'мешок',450,CURRENT_DATE,CURRENT_DATE + 7,'Заказан','Цемент для объекта №1'),
('ORD-2026-002',2,1,1,8,'тонна',65000,CURRENT_DATE,CURRENT_DATE + 10,'Согласован','Арматура для бизнес-центра'),
('ORD-2026-003',3,5,3,12,'м3',14000,CURRENT_DATE,CURRENT_DATE + 14,'Создан','Пиломатериалы для школы');

INSERT INTO deliveries (delivery_number, order_id, vehicle_id, driver_id, from_address, to_address, planned_date, planned_time, status, comment) VALUES
('DLV-2026-001',1,1,1,'Склад ОМТС','ул. Парковая, 5, Москва',CURRENT_DATE + 7,'10:00','Назначен транспорт','Доставка цемента на объект №1'),
('DLV-2026-002',2,2,1,'Склад поставщика','пр. Мира, 25, Москва',CURRENT_DATE + 10,'12:30','Запланирована','Доставка арматуры');

INSERT INTO routes (delivery_id, sequence_no, address, planned_arrival, status) VALUES
(1,1,'Склад ОМТС','09:00','Ожидает'),(1,2,'ул. Парковая, 5, Москва','10:00','Ожидает'),
(2,1,'Склад поставщика','11:00','Ожидает'),(2,2,'пр. Мира, 25, Москва','12:30','Ожидает');

-- Виды для удобного отображения связанных данных.
CREATE VIEW v_client_contracts AS
SELECT c.id AS contract_id, c.contract_number, c.contract_date, c.total_amount, c.status,
       cl.company_name AS client, p.project_name AS project
FROM contracts c JOIN clients cl ON cl.id=c.client_id JOIN projects p ON p.id=c.project_id;

CREATE VIEW v_orders AS
SELECT o.id, o.order_number, p.project_name AS project, m.material_name AS material,
       s.company_name AS supplier, o.quantity, o.unit, o.unit_price,
       o.planned_delivery_date, o.status
FROM orders o JOIN projects p ON p.id=o.project_id
JOIN materials m ON m.id=o.material_id JOIN suppliers s ON s.id=o.supplier_id;

CREATE VIEW v_deliveries AS
SELECT d.id, d.delivery_number, o.order_number, v.plate_number,
       e.last_name || ' ' || e.first_name AS driver,
       d.from_address, d.to_address, d.planned_date, d.planned_time, d.status
FROM deliveries d JOIN orders o ON o.id=d.order_id
LEFT JOIN vehicles v ON v.id=d.vehicle_id
LEFT JOIN drivers dr ON dr.id=d.driver_id
LEFT JOIN employees e ON e.id=dr.employee_id;


DROP DATABASE IF EXISTS art_school;
CREATE DATABASE art_school ENCODING 'UTF8';

\c art_school

\i art_school.sql

insert into roles values (1, 'Админ');
insert into employees values (1, 'тест', 'тест', 'тест', 'тест', 'тест', 'admin', '1234567890', 1);