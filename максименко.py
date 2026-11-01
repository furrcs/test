import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import psycopg2


# Подключение к базе данных
def connect_db():
    return psycopg2.connect(
        host="localhost",
        database="art_gallery",
        user="postgres",
        password="1234567890",
        port="5432"
    )


# Создание таблиц и связей
def create_tables():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
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
    """)

    conn.commit()
    cur.close()
    conn.close()


# Таблицы для главного окна
tables = {
    "Картины": {
        "table": "paintings",
        "columns": ["id", "title", "artist", "creation_year", "hall"],
        "names": ["ID", "Название", "Автор", "Год", "Зал"],
        "add": ["title", "artist", "creation_year", "hall"],
        "labels": ["Название", "Автор", "Год создания", "Зал"]
    },
    "Выставки": {
        "table": "exhibitions",
        "columns": ["id", "title", "exhibition_date", "hall"],
        "names": ["ID", "Название", "Дата", "Зал"],
        "add": ["title", "exhibition_date", "hall"],
        "labels": ["Название", "Дата (ГГГГ-ММ-ДД)", "Зал"]
    },
    "Сотрудники": {
        "table": "employees",
        "columns": ["id", "full_name", "position", "phone"],
        "names": ["ID", "ФИО", "Должность", "Телефон"],
        "add": ["full_name", "position", "phone"],
        "labels": ["ФИО", "Должность", "Телефон"]
    },
    "Экскурсии": {
        "table": "excursions",
        "columns": ["id", "title", "guide", "excursion_date"],
        "names": ["ID", "Название", "Экскурсовод", "Дата"],
        "add": ["title", "guide", "excursion_date"],
        "labels": ["Название", "Экскурсовод", "Дата (ГГГГ-ММ-ДД)"]
    },
    "Билеты": {
        "table": "tickets",
        "columns": ["id", "visitor", "ticket_type", "price", "status"],
        "names": ["ID", "Посетитель", "Тип", "Цена", "Статус"],
        "add": ["visitor", "ticket_type", "price"],
        "labels": ["ФИО посетителя", "Тип билета", "Цена"]
    },
    "Посетители": {
        "table": "visitors",
        "columns": ["id", "full_name", "visit_date"],
        "names": ["ID", "ФИО", "Дата посещения"],
        "add": ["full_name"],
        "labels": ["ФИО посетителя"]
    }
}


# Главное окно
root = tk.Tk()
root.title("Картинная галерея")
root.geometry("1000x600")

tk.Label(
    root,
    text="КАРТИННАЯ ГАЛЕРЕЯ",
    font=("Arial", 18, "bold")
).pack(pady=10)


# Выбор раздела
top = tk.Frame(root)
top.pack(pady=5)

tk.Label(top, text="Раздел:").pack(side="left", padx=5)

section = ttk.Combobox(
    top,
    values=list(tables.keys()),
    state="readonly",
    width=20
)
section.set("Картины")
section.pack(side="left", padx=5)


# Таблица данных
frame = tk.Frame(root)
frame.pack(fill="both", expand=True, padx=10, pady=10)

tree = ttk.Treeview(frame, show="headings")

scroll = ttk.Scrollbar(
    frame,
    orient="vertical",
    command=tree.yview
)

tree.configure(yscrollcommand=scroll.set)
tree.pack(side="left", fill="both", expand=True)
scroll.pack(side="right", fill="y")


# Загрузка данных
def load_data(event=None):
    info = tables[section.get()]

    try:
        conn = connect_db()
        cur = conn.cursor()

        cur.execute(
            f"SELECT {', '.join(info['columns'])} "
            f"FROM {info['table']} ORDER BY id"
        )

        rows = cur.fetchall()

        tree.delete(*tree.get_children())
        tree["columns"] = info["columns"]

        for col, name in zip(info["columns"], info["names"]):
            tree.heading(col, text=name)
            tree.column(col, width=150)

        for row in rows:
            tree.insert("", "end", values=row)

        cur.close()
        conn.close()

    except Exception as error:
        messagebox.showerror("Ошибка", str(error))


# Добавление записи
def add_record():
    info = tables[section.get()]
    values = []

    for label in info["labels"]:
        value = simpledialog.askstring(
            "Добавление записи",
            label,
            parent=root
        )

        if value is None:
            return

        if not value.strip():
            messagebox.showwarning(
                "Ошибка",
                "Заполни все поля"
            )
            return

        values.append(value.strip())

    conn = None

    try:
        conn = connect_db()
        cur = conn.cursor()

        columns = ", ".join(info["add"])
        placeholders = ", ".join(["%s"] * len(values))

        cur.execute(
            f"INSERT INTO {info['table']} ({columns}) "
            f"VALUES ({placeholders})",
            values
        )

        conn.commit()
        cur.close()
        conn.close()

        load_data()
        messagebox.showinfo("Успех", "Запись добавлена")

    except Exception as error:
        if conn:
            conn.rollback()
            conn.close()

        messagebox.showerror("Ошибка", str(error))


# Удаление записи
def delete_record():
    selected = tree.selection()

    if not selected:
        messagebox.showwarning(
            "Внимание",
            "Выбери запись в таблице"
        )
        return

    record = tree.item(selected[0])["values"]
    record_id = record[0]

    if not messagebox.askyesno(
        "Подтверждение",
        "Удалить выбранную запись?"
    ):
        return

    info = tables[section.get()]
    conn = None

    try:
        conn = connect_db()
        cur = conn.cursor()

        cur.execute(
            f"DELETE FROM {info['table']} WHERE id = %s",
            (record_id,)
        )

        conn.commit()
        cur.close()
        conn.close()

        load_data()

    except Exception as error:
        if conn:
            conn.rollback()
            conn.close()

        messagebox.showerror("Ошибка", str(error))


# Возврат билета
def return_ticket():
    if section.get() != "Билеты":
        messagebox.showwarning(
            "Внимание",
            "Сначала выбери раздел «Билеты»"
        )
        return

    selected = tree.selection()

    if not selected:
        messagebox.showwarning(
            "Внимание",
            "Выбери билет в таблице"
        )
        return

    record = tree.item(selected[0])["values"]
    ticket_id = record[0]

    if record[4] == "Возвращён":
        messagebox.showinfo(
            "Информация",
            "Билет уже возвращён"
        )
        return

    conn = None

    try:
        conn = connect_db()
        cur = conn.cursor()

        cur.execute(
            "UPDATE tickets SET status = %s WHERE id = %s",
            ("Возвращён", ticket_id)
        )

        conn.commit()
        cur.close()
        conn.close()

        load_data()
        messagebox.showinfo("Успех", "Возврат оформлен")

    except Exception as error:
        if conn:
            conn.rollback()
            conn.close()

        messagebox.showerror("Ошибка", str(error))


# Отчёты
def show_report():
    conn = None

    try:
        conn = connect_db()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM paintings")
        paintings_count = cur.fetchone()[0]

        cur.execute(
            "SELECT COUNT(*) FROM tickets WHERE status = 'Оплачен'"
        )
        tickets_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM visitors")
        visitors_count = cur.fetchone()[0]

        cur.close()
        conn.close()

        messagebox.showinfo(
            "Отчёт",
            f"Количество картин: {paintings_count}\n"
            f"Продано билетов: {tickets_count}\n"
            f"Посетителей в списке: {visitors_count}"
        )

    except Exception as error:
        if conn:
            conn.close()

        messagebox.showerror("Ошибка", str(error))


# Кнопки
buttons = tk.Frame(root)
buttons.pack(pady=10)

tk.Button(
    buttons,
    text="Показать",
    width=15,
    command=load_data
).pack(side="left", padx=5)

tk.Button(
    buttons,
    text="Добавить",
    width=15,
    command=add_record
).pack(side="left", padx=5)

tk.Button(
    buttons,
    text="Удалить",
    width=15,
    command=delete_record
).pack(side="left", padx=5)

tk.Button(
    buttons,
    text="Вернуть билет",
    width=15,
    command=return_ticket
).pack(side="left", padx=5)

tk.Button(
    buttons,
    text="Отчёты",
    width=15,
    command=show_report
).pack(side="left", padx=5)


# Переключение разделов
section.bind("<<ComboboxSelected>>", load_data)


# Создание таблиц и запуск программы
try:
    create_tables()
    load_data()
except Exception as error:
    messagebox.showerror("Ошибка базы данных", str(error))


root.mainloop()