import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime
from decimal import Decimal
import psycopg2
import csv
from tkinter import filedialog
from psycopg2 import sql

DB = dict(dbname="art_school", user="postgres", host="localhost", port="5432")
BG, NAVY, BLUE, WHITE, MUTED = "#F2F5FA", "#243B64", "#355C9A", "#FFFFFF", "#65738B"

TABLES = {
    "Ученики": ("students", "student_id", [
        ("surname", "Фамилия", "text"), ("name", "Имя", "text"),
        ("third_name", "Отчество", "text"), ("birth_date", "Дата рождения (ГГГГ-ММ-ДД)", "date"),
        ("phone", "Телефон", "text"), ("group_id", "Группа", "groups")]),
    "Сотрудники": ("employees", "employee_id", [
        ("surname", "Фамилия", "text"), ("name", "Имя", "text"),
        ("third_name", "Отчество", "text"), ("phone", "Телефон", "text"),
        ("email", "Электронная почта", "text"), ("login", "Логин", "text"),
        ("password", "Пароль", "password"), ("role_id", "Роль", "roles")]),
    "Группы": ("groups", "group_id", [
        ("name", "Название группы", "text"), ("year", "Учебный год", "integer"),
        ("teacher_id", "Преподаватель", "employees")]),
    "Дисциплины": ("disciplines", "discipline_id", [
        ("name", "Название дисциплины", "text"), ("price", "Стоимость", "decimal")]),
    "Занятия": ("lessons", "lesson_id", [
        ("lesson_date", "Дата (ГГГГ-ММ-ДД)", "date"),
        ("lesson_time", "Время (ЧЧ:ММ)", "time"),
        ("classroom", "Кабинет", "text"), ("group_id", "Группа", "groups"),
        ("teacher_id", "Преподаватель", "employees"),
        ("discipline_id", "Дисциплина", "disciplines")]),
    "Оценки": ("grades", "grade_id", [
        ("student_id", "Ученик", "students"),
        ("discipline_id", "Дисциплина", "disciplines"),
        ("grade_date", "Дата (ГГГГ-ММ-ДД)", "date"),
        ("value", "Оценка", "grade")]),
    "Посещаемость": ("attendance", "attendance_id", [
        ("lesson_id", "Занятие", "lessons"),
        ("student_id", "Ученик", "students"),
        ("mark", "Посещаемость", "attendance"),
        ("attendance_date", "Дата посещения (ГГГГ-ММ-ДД)", "date")]),
}
TABLES.update({
    "Кураторы": ("curators", "curator_id", [
        ("employee_id", "ФИО куратора", "employees"),
        ("group_id", "Группа", "groups"),
        ("discipline_id", "Дисциплина", "disciplines")]),
    "Оплата обучения": ("payments", "payment_id", [
        ("student_id", "Ученик", "students"),
        ("payment_date", "Дата оплаты (ГГГГ-ММ-ДД)", "date"),
        ("period", "Период оплаты (например 2026-10)", "text"),
        ("amount", "Сумма", "decimal"),
        ("method", "Способ оплаты", "method"),
        ("note", "Примечание", "text")]),
    "Доступ учеников": ("student_accounts", "account_id", [
        ("student_id", "Ученик", "students"),
        ("login", "Логин", "text"),
        ("password", "Пароль", "password")]),
})
REPORTS = {
    "Сводка посещаемости": "attendance_summary",
    "Ведомость успеваемости": "grade_summary",
    "Финансовый отчёт": "payment_summary",
    "Долги по оплате": "payment_debts",
    "Нагрузка преподавателей": "teacher_load",
    "Состав групп": "group_roster",
    "Список кураторов": "curator_report",
}
VIEWS = {"Расписание": "v_schedule", "Оценки учеников": "v_student_grades",
         "Отчёт по посещаемости": "v_attendance_report"}
LABELS = dict(student_id="ID ученика", employee_id="ID сотрудника", group_id="Группа",
              discipline_id="Дисциплина", lesson_id="Занятие", grade_id="ID оценки",
              attendance_id="ID записи", role_id="Роль", surname="Фамилия", name="Имя",
              third_name="Отчество", birth_date="Дата рождения", phone="Телефон",
              email="Почта", login="Логин", password="Пароль", year="Учебный год",
              price="Стоимость", lesson_date="Дата занятия", lesson_time="Время",
              classroom="Кабинет", grade_date="Дата оценки", value="Оценка",
              mark="Посещение", group_name="Группа", teacher_name="Преподаватель",
              discipline_name="Дисциплина", student_name="Ученик")
FK_TABLES = {"groups": ("group_id", "name"), "employees": ("employee_id", "surname"),
             "disciplines": ("discipline_id", "name"), "students": ("student_id", "surname"),
             "lessons": ("lesson_id", "lesson_date"), "roles": ("role_id", "name")}
LABELS.update({"curator_id":"ID куратора", "payment_id":"ID платежа", "account_id":"ID доступа",
               "payment_date":"Дата оплаты", "period":"Период", "amount":"Сумма",
               "method":"Способ оплаты", "note":"Примечание", "attendance_date":"Дата посещения",
               "total_lessons":"Всего занятий", "missed":"Пропусков", "attendance_percent":"Посещаемость, %",
               "average_grade":"Средний балл", "grade_count":"Количество оценок", "paid":"Оплачено",
               "expected":"Начислено", "debt":"Задолженность", "lessons_count":"Количество занятий",
               "curator_name":"Куратор", "students_count":"Количество учеников"})
SCHEMA = [
    """CREATE TABLE IF NOT EXISTS roles (
       role_id SERIAL PRIMARY KEY, name VARCHAR(100) UNIQUE NOT NULL)""",
    """CREATE TABLE IF NOT EXISTS employees (
       employee_id SERIAL PRIMARY KEY, surname VARCHAR(100) NOT NULL,
       name VARCHAR(100) NOT NULL, third_name VARCHAR(100), phone VARCHAR(30),
       email VARCHAR(150), login VARCHAR(100) UNIQUE NOT NULL,
       password VARCHAR(255) NOT NULL, role_id INTEGER REFERENCES roles(role_id))""",
    """CREATE TABLE IF NOT EXISTS groups (
       group_id SERIAL PRIMARY KEY, name VARCHAR(100) UNIQUE NOT NULL,
       year INTEGER NOT NULL DEFAULT 2026,
       teacher_id INTEGER REFERENCES employees(employee_id))""",
    """CREATE TABLE IF NOT EXISTS disciplines (
       discipline_id SERIAL PRIMARY KEY, name VARCHAR(150) UNIQUE NOT NULL,
       price NUMERIC(10,2) NOT NULL DEFAULT 0)""",
    """CREATE TABLE IF NOT EXISTS students (
       student_id SERIAL PRIMARY KEY, surname VARCHAR(100) NOT NULL,
       name VARCHAR(100) NOT NULL, third_name VARCHAR(100), birth_date DATE,
       phone VARCHAR(30), group_id INTEGER REFERENCES groups(group_id))""",
    """CREATE TABLE IF NOT EXISTS lessons (
       lesson_id SERIAL PRIMARY KEY, lesson_date DATE NOT NULL,
       lesson_time TIME NOT NULL, classroom VARCHAR(100),
       group_id INTEGER REFERENCES groups(group_id),
       teacher_id INTEGER REFERENCES employees(employee_id),
       discipline_id INTEGER REFERENCES disciplines(discipline_id))""",
    """CREATE TABLE IF NOT EXISTS grades (
       grade_id SERIAL PRIMARY KEY, student_id INTEGER REFERENCES students(student_id),
       discipline_id INTEGER REFERENCES disciplines(discipline_id),
       grade_date DATE NOT NULL DEFAULT CURRENT_DATE,
       value INTEGER CHECK(value BETWEEN 1 AND 5))""",
    """CREATE TABLE IF NOT EXISTS attendance (
       attendance_id SERIAL PRIMARY KEY, lesson_id INTEGER REFERENCES lessons(lesson_id),
       student_id INTEGER REFERENCES students(student_id),
       mark VARCHAR(50) NOT NULL DEFAULT 'Присутствовал',
       UNIQUE(lesson_id, student_id))""",
]
VIEW_SQL = [
    """CREATE OR REPLACE VIEW v_schedule AS
       SELECT l.lesson_id, l.lesson_date, l.lesson_time, l.classroom,
              g.name AS group_name, concat_ws(' ', e.surname, e.name) AS teacher_name,
              d.name AS discipline_name FROM lessons l
       LEFT JOIN groups g ON g.group_id=l.group_id
       LEFT JOIN employees e ON e.employee_id=l.teacher_id
       LEFT JOIN disciplines d ON d.discipline_id=l.discipline_id""",
    """CREATE OR REPLACE VIEW v_student_grades AS
       SELECT concat_ws(' ', s.surname, s.name, s.third_name) AS student_name,
              d.name AS discipline_name, gr.grade_date, gr.value FROM grades gr
       JOIN students s ON s.student_id=gr.student_id
       JOIN disciplines d ON d.discipline_id=gr.discipline_id""",
    """CREATE OR REPLACE VIEW v_attendance_report AS
       SELECT l.lesson_date, l.lesson_time, g.name AS group_name,
              concat_ws(' ', s.surname, s.name) AS student_name, a.mark
       FROM attendance a JOIN lessons l ON l.lesson_id=a.lesson_id
       JOIN students s ON s.student_id=a.student_id
       LEFT JOIN groups g ON g.group_id=l.group_id""",
]


class ArtSchoolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("АИС художественной школы")
        self.root.geometry("1180x720")
        self.root.minsize(900, 580)
        self.root.configure(bg=BG)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.conn = None
        self.employee = None
        self.current_key = None
        self.tree = None
        self.all_rows = []
        self.columns = []
        self.status = tk.StringVar(value="")
        self.setup_style()
        self.root.after(50, self.connect_dialog)

    def setup_style(self):
        style = ttk.Style(self.root)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("Treeview", rowheight=29, font=("Arial", 10))
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        style.configure("TButton", padding=(12, 7))
        style.configure("TCombobox", padding=4)

    def clear(self):
        self.root.unbind("<Return>")
        for widget in self.root.winfo_children():
            widget.destroy()

    def error(self, title, exc, parent=None):
        if self.conn and not self.conn.closed:
            self.conn.rollback()
        messagebox.showerror(title, str(exc), parent=parent or self.root)

    def connect_dialog(self):
        self.root.withdraw()
        win = tk.Toplevel(self.root)
        win.title("Подключение к PostgreSQL")
        win.geometry("440x280")
        win.resizable(False, False)
        win.configure(bg=BG)
        win.protocol("WM_DELETE_WINDOW", self.close)
        win.grab_set()
        tk.Label(win, text="ХУДОЖЕСТВЕННАЯ ШКОЛА", font=("Arial", 17, "bold"),
                 bg=BG, fg=NAVY).pack(pady=(25, 12))
        tk.Label(win, text="Пароль PostgreSQL (пользователь postgres)",
                 bg=BG, fg=NAVY).pack()
        password = ttk.Entry(win, show="*", width=35)
        password.pack(pady=12)
        password.focus_set()

        def connect():
            try:
                self.conn = psycopg2.connect(**DB, password=password.get(), connect_timeout=5)
                self.prepare_database()
                win.destroy()
                self.root.deiconify()
                self.show_login()
            except Exception as exc:
                self.error("Ошибка подключения или подготовки БД", exc, win)
                if self.conn:
                    self.conn.close()
                    self.conn = None

        ttk.Button(win, text="Подключиться", command=connect).pack(pady=8)
        win.bind("<Return>", lambda _e: connect())

    def prepare_database(self):
        with self.conn:
            with self.conn.cursor() as cur:
                for command in SCHEMA:
                    cur.execute(command)
                for role in ("Администратор", "Преподаватель"):
                    cur.execute("INSERT INTO roles(name) VALUES (%s) ON CONFLICT DO NOTHING", (role,))
                cur.execute("SELECT role_id FROM roles WHERE name='Администратор'")
                admin_role = cur.fetchone()[0]
                cur.execute("SELECT role_id FROM roles WHERE name='Преподаватель'")
                teacher_role = cur.fetchone()[0]
                cur.execute("""INSERT INTO employees
                    (surname,name,login,password,role_id)
                    SELECT 'Администратор','Системы','admin','admin123',%s
                    WHERE NOT EXISTS (SELECT 1 FROM employees WHERE login='admin')""", (admin_role,))
                cur.execute("""INSERT INTO employees
                    (surname,name,third_name,phone,email,login,password,role_id)
                    SELECT 'Иванов','Иван','Иванович','+79990000000',
                           'teacher@example.com','teacher1','teacher123',%s
                    WHERE NOT EXISTS (SELECT 1 FROM employees WHERE login='teacher1')""", (teacher_role,))
                cur.execute("SELECT employee_id FROM employees WHERE login='teacher1'")
                teacher_id = cur.fetchone()[0]
                for group in ("Группа 1", "Группа 2", "Группа 3",
                              "Подготовительная группа", "Продвинутая группа"):
                    cur.execute("""INSERT INTO groups(name,year,teacher_id)
                                   SELECT %s,2026,%s WHERE NOT EXISTS
                                   (SELECT 1 FROM groups WHERE name=%s)""",
                                (group, teacher_id, group))
                for name, price in (
                    ("Рисунок", 500), ("Живопись", 600), ("Скульптура", 700),
                    ("Композиция", 550), ("Графика", 500), ("История искусства", 450),
                    ("Акварель", 550), ("Цветоведение", 500), ("Основы дизайна", 650),
                    ("Академический рисунок", 700), ("Живопись маслом", 750),
                    ("Иллюстрация", 600)
                ):
                    cur.execute("""INSERT INTO disciplines(name,price)
                                   SELECT %s,%s WHERE NOT EXISTS
                                   (SELECT 1 FROM disciplines WHERE name=%s)""", (name, price, name))
                students = [
                    ("Петрова","Анна","Сергеевна","2012-05-15","+79990000001","Группа 1"),
                    ("Смирнова","Алиса","Игоревна","2012-03-14","+79990000101","Группа 1"),
                    ("Козлов","Артём","Сергеевич","2011-07-22","+79990000102","Группа 1"),
                    ("Морозова","Ева","Андреевна","2013-01-09","+79990000103","Группа 1"),
                    ("Волков","Максим","Дмитриевич","2012-11-30","+79990000104","Группа 1"),
                    ("Павлова","Мария","Олеговна","2011-05-17","+79990000201","Группа 2"),
                    ("Новиков","Илья","Романович","2012-09-03","+79990000202","Группа 2"),
                    ("Фёдорова","София","Алексеевна","2013-06-25","+79990000203","Группа 2"),
                    ("Орлов","Даниил","Иванович","2011-12-12","+79990000204","Группа 2"),
                    ("Зайцева","Полина","Максимовна","2012-02-08","+79990000301","Группа 3"),
                    ("Белов","Кирилл","Евгеньевич","2011-08-19","+79990000302","Группа 3"),
                    ("Соколова","Дарья","Павловна","2013-04-11","+79990000303","Группа 3"),
                    ("Григорьев","Марк","Артёмович","2012-10-27","+79990000304","Группа 3"),
                    ("Кузнецова","Виктория","Денисовна","2014-02-18","+79990000401","Подготовительная группа"),
                    ("Михайлов","Егор","Андреевич","2014-06-21","+79990000402","Подготовительная группа"),
                    ("Васильева","Арина","Петровна","2014-09-10","+79990000403","Подготовительная группа"),
                    ("Никитин","Лев","Андреевич","2010-01-20","+79990000501","Продвинутая группа"),
                    ("Романова","Елизавета","Михайловна","2010-04-02","+79990000502","Продвинутая группа"),
                    ("Егоров","Тимур","Олегович","2009-08-18","+79990000503","Продвинутая группа"),
                    ("Андреева","Полина","Ильинична","2011-10-05","+79990000504","Продвинутая группа"),
                ]
                for surname, name, third, birth, phone, group in students:
                    cur.execute("SELECT 1 FROM students WHERE phone=%s", (phone,))
                    if cur.fetchone():
                        continue
                    cur.execute("""INSERT INTO students(surname,name,third_name,birth_date,phone,group_id)
                                   SELECT %s,%s,%s,%s,%s,group_id FROM groups WHERE name=%s""",
                                (surname, name, third, birth, phone, group))
                for day, tm, room, group, discipline in (
                    ("2026-10-20","10:00","Кабинет 1","Группа 1","Рисунок"),
                    ("2026-10-20","12:00","Кабинет 2","Группа 2","Живопись"),
                    ("2026-10-21","11:00","Кабинет 1","Группа 3","Композиция"),
                    ("2026-10-22","15:00","Мастерская","Подготовительная группа","Акварель")
                ):
                    cur.execute("""SELECT 1 FROM lessons
                                   WHERE lesson_date=%s AND lesson_time=%s AND classroom=%s""",
                                (day, tm, room))
                    if cur.fetchone():
                        continue
                    cur.execute("""INSERT INTO lessons
                                   (lesson_date,lesson_time,classroom,group_id,teacher_id,discipline_id)
                                   SELECT %s,%s,%s,g.group_id,%s,d.discipline_id
                                   FROM groups g CROSS JOIN disciplines d
                                   WHERE g.name=%s AND d.name=%s""",
                                (day, tm, room, teacher_id, group, discipline))
                cur.execute("SELECT student_id FROM students ORDER BY student_id LIMIT 10")
                student_ids = [x[0] for x in cur.fetchall()]
                cur.execute("SELECT discipline_id FROM disciplines ORDER BY discipline_id LIMIT 4")
                discipline_ids = [x[0] for x in cur.fetchall()]
                for i, sid in enumerate(student_ids):
                    did = discipline_ids[i % len(discipline_ids)]
                    cur.execute("""INSERT INTO grades(student_id,discipline_id,grade_date,value)
                                   SELECT %s,%s,CURRENT_DATE,%s WHERE NOT EXISTS
                                   (SELECT 1 FROM grades WHERE student_id=%s AND discipline_id=%s)""",
                                (sid, did, 3 + i % 3, sid, did))
                cur.execute("SELECT lesson_id FROM lessons ORDER BY lesson_id")
                lesson_ids = [x[0] for x in cur.fetchall()]
                for i, sid in enumerate(student_ids[:8]):
                    lid = lesson_ids[i % len(lesson_ids)]
                    cur.execute("""INSERT INTO attendance(lesson_id,student_id,mark)
                                   SELECT %s,%s,%s WHERE NOT EXISTS
                                   (SELECT 1 FROM attendance WHERE lesson_id=%s AND student_id=%s)""",
                                (lid, sid, "Отсутствовал" if i % 4 == 0 else "Присутствовал", lid, sid))
                # Не заменяем существующие представления: у них может быть
                # другой порядок столбцов или зависимые объекты.
                view_names = (
                    "v_schedule", "v_student_grades", "v_attendance_report"
                )
                for view_name, command in zip(view_names, VIEW_SQL):
                    cur.execute("SELECT to_regclass(%s)", (f"public.{view_name}",))
                    if cur.fetchone()[0] is None:
                        cur.execute(command)

    def show_login(self):
        self.clear()
        card = tk.Frame(self.root, bg=WHITE, padx=48, pady=36,
                        highlightbackground="#D7DFEC", highlightthickness=1)
        card.place(relx=.5, rely=.5, anchor="center")
        tk.Label(card, text="ХУДОЖЕСТВЕННАЯ ШКОЛА", font=("Arial", 20, "bold"),
                 bg=WHITE, fg=NAVY).pack(pady=(0, 8))
        tk.Label(card, text="Автоматизированная информационная система",
                 bg=WHITE, fg=MUTED).pack(pady=(0, 20))
        tk.Label(card, text="Логин", bg=WHITE, fg=NAVY).pack(anchor="w")
        username = ttk.Entry(card, width=37)
        username.pack(pady=(4, 12), ipady=4)
        tk.Label(card, text="Пароль", bg=WHITE, fg=NAVY).pack(anchor="w")
        password = ttk.Entry(card, width=37, show="*")
        password.pack(pady=(4, 18), ipady=4)

        def login():
            if not username.get().strip() or not password.get():
                messagebox.showwarning("Вход", "Введите логин и пароль.", parent=self.root)
                return
            try:
                with self.conn.cursor() as cur:
                    cur.execute("""SELECT e.employee_id,e.surname,e.name,e.third_name,
                                          e.role_id,r.name
                                   FROM employees e LEFT JOIN roles r ON r.role_id=e.role_id
                                   WHERE e.login=%s AND e.password=%s""",
                                (username.get().strip(), password.get()))
                    self.employee = cur.fetchone()
                if not self.employee:
                    messagebox.showerror("Вход", "Неверный логин или пароль.", parent=self.root)
                    return
                self.show_main()
            except Exception as exc:
                self.error("Ошибка входа", exc)
        ttk.Button(card, text="ВОЙТИ", command=login).pack(fill="x")
        tk.Label(card, text="Демо: admin / admin123    •    teacher1 / teacher123",
                 bg=WHITE, fg=MUTED, font=("Arial", 9)).pack(pady=(15, 0))
        username.focus_set()
        self.root.bind("<Return>", lambda _e: login())

    @property
    def is_admin(self):
        return bool(self.employee and self.employee[5] == "Администратор")

    def allowed(self, key, operation="view"):
        if not self.employee:
            return False
        if key in VIEWS:
            return operation == "view"
        if key not in TABLES:
            return False
        if operation == "view":
            return self.is_admin or key in ("Ученики", "Оценки", "Посещаемость")
        return self.is_admin or key in ("Ученики", "Оценки", "Посещаемость")

    def header(self, title):
        bar = tk.Frame(self.root, bg=NAVY, height=70)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        tk.Label(bar, text=title, font=("Arial", 18, "bold"),
                 bg=NAVY, fg=WHITE).pack(side="left", padx=25)
        if self.employee:
            full = " ".join(str(x) for x in self.employee[1:4] if x)
            tk.Label(bar, text=f"{full}  |  {self.employee[5]}",
                     bg=NAVY, fg=WHITE).pack(side="right", padx=25)

    def show_main(self):
        self.clear()
        self.header("ХУДОЖЕСТВЕННАЯ ШКОЛА")
        body = tk.Frame(self.root, bg=BG, padx=32, pady=24)
        body.pack(fill="both", expand=True)
        tk.Label(body, text="Главное меню", bg=BG, fg=NAVY,
                 font=("Arial", 23, "bold")).pack(anchor="w")
        tk.Label(body, text="Выберите раздел для работы",
                 bg=BG, fg=MUTED).pack(anchor="w", pady=(5, 20))
        keys = list(TABLES) + list(VIEWS)
        keys = [key for key in keys if self.allowed(key)]
        grid = tk.Frame(body, bg=BG)
        grid.pack(fill="both", expand=True)
        for i, key in enumerate(keys):
            tk.Button(grid, text=key, bg=WHITE, fg=NAVY, relief="flat",
                      font=("Arial", 12, "bold"), cursor="hand2",
                      command=lambda k=key: self.open_section(k)).grid(
                          row=i // 3, column=i % 3, padx=8, pady=8, sticky="nsew")
        for i in range(3):
            grid.columnconfigure(i, weight=1)
        for i in range((len(keys) + 2) // 3):
            grid.rowconfigure(i, weight=1)
        ttk.Button(body, text="Выйти из системы", command=self.logout).pack(anchor="e", pady=12)

    def open_section(self, key):
        if not self.allowed(key):
            messagebox.showerror("Доступ", "Недостаточно прав.", parent=self.root)
            return
        self.current_key = key
        self.clear()
        self.header(key)
        body = tk.Frame(self.root, bg=BG, padx=20, pady=15)
        body.pack(fill="both", expand=True)
        tools = tk.Frame(body, bg=BG)
        tools.pack(fill="x", pady=(0, 10))
        tk.Label(tools, text="Поиск:", bg=BG, fg=NAVY).pack(side="left")
        search_var = tk.StringVar()
        search = ttk.Entry(tools, textvariable=search_var, width=38)
        search.pack(side="left", padx=8)
        ttk.Button(tools, text="Сбросить", command=lambda: search_var.set("")).pack(side="left")
        ttk.Label(tools, textvariable=self.status).pack(side="right")
        holder = tk.Frame(body)
        holder.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(holder, show="headings", selectmode="browse")
        ybar = ttk.Scrollbar(holder, orient="vertical", command=self.tree.yview)
        xbar = ttk.Scrollbar(holder, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        ybar.grid(row=0, column=1, sticky="ns")
        xbar.grid(row=1, column=0, sticky="ew")
        holder.rowconfigure(0, weight=1)
        holder.columnconfigure(0, weight=1)
        self.tree.tag_configure("odd", background="#F3F6FB")
        self.tree.bind("<Double-1>", lambda _e: self.manage_record(key, "edit")
                       if key in TABLES and self.allowed(key, "edit") else None)
        actions = tk.Frame(body, bg=BG)
        actions.pack(fill="x", pady=(12, 0))
        if key in TABLES and self.allowed(key, "edit"):
            for label, op in (("Добавить", "add"), ("Редактировать", "edit"),
                              ("Удалить", "delete")):
                ttk.Button(actions, text=label, command=lambda o=op: self.manage_record(key, o)).pack(
                    side="left", padx=(0, 6))
        ttk.Button(actions, text="Обновить", command=self.load_table).pack(side="left", padx=5)
        ttk.Button(actions, text="Назад", command=self.show_main).pack(side="right")
        search_var.trace_add("write", lambda *_: self.filter_rows(search_var.get()))
        self.load_table()

    def load_table(self):
        key = self.current_key
        table = TABLES[key][0] if key in TABLES else VIEWS[key]
        try:
            with self.conn.cursor() as cur:
                cur.execute(sql.SQL("SELECT * FROM {}").format(sql.Identifier(table)))
                self.all_rows = cur.fetchall()
                self.columns = [d[0] for d in cur.description]
            self.tree["columns"] = self.columns
            for col in self.columns:
                self.tree.heading(col, text=LABELS.get(col, col.replace("_", " ").capitalize()),
                                  command=lambda c=col: self.sort_column(c))
                self.tree.column(col, width=170, minwidth=85, stretch=True)
            self.visible_rows = list(self.all_rows)
            self.render_rows(self.all_rows)
        except Exception as exc:
            self.error("Ошибка загрузки", exc)

    def render_rows(self, rows):
        self.tree.delete(*self.tree.get_children())
        for i, row in enumerate(rows):
            values = []
            for col, value in zip(self.columns, row):
                if col == "password":
                    values.append("••••••••")
                else:
                    values.append("" if value is None else str(value))
            # iid is positional, not the first column value: views may have duplicate values.
            self.tree.insert("", "end", iid=str(i), values=values,
                             tags=("odd",) if i % 2 else ())
        self.status.set(f"Записей: {len(rows)}")

    def filter_rows(self, query):
        query = query.casefold().strip()
        rows = [row for row in self.all_rows if not query or any(
            query in str(value).casefold() for col, value in zip(self.columns, row)
            if value is not None and col != "password")]
        self.render_rows(rows)
        self.visible_rows = rows

    def sort_column(self, col):
        index = self.columns.index(col)
        current = list(getattr(self, "visible_rows", self.all_rows))
        reverse = getattr(self, "sort_reverse", False)
        current.sort(key=lambda r: (r[index] is None,
                                    str(r[index]).casefold() if r[index] is not None else ""),
                     reverse=reverse)
        self.sort_reverse = not reverse
        self.visible_rows = current
        self.render_rows(current)

    def selected_id(self):
        selection = self.tree.selection()
        if not selection:
            return None
        idx = int(selection[0])
        rows = getattr(self, "visible_rows", self.all_rows)
        return rows[idx][0]

    def manage_record(self, key, operation):
        if not self.allowed(key, operation):
            messagebox.showerror("Доступ", "Недостаточно прав.", parent=self.root)
            return
        record_id = None if operation == "add" else self.selected_id()
        if operation != "add" and record_id is None:
            messagebox.showwarning("Выбор записи", "Сначала выберите строку.", parent=self.root)
            return
        table, pk, _ = TABLES[key]
        if operation == "delete":
            if not messagebox.askyesno("Удаление", "Удалить выбранную запись?", parent=self.root):
                return
            try:
                with self.conn:
                    with self.conn.cursor() as cur:
                        cur.execute(sql.SQL("DELETE FROM {} WHERE {}=%s").format(
                            sql.Identifier(table), sql.Identifier(pk)), (record_id,))
                self.load_table()
            except Exception as exc:
                self.error("Не удалось удалить запись (возможно, есть связанные данные)", exc)
            return
        self.open_form(key, operation, record_id)

    def foreign_options(self, kind):
        idcol, _ = FK_TABLES[kind]
        queries = {
            "groups": "SELECT group_id, name FROM groups ORDER BY name",
            "employees": """SELECT employee_id, concat_ws(' ',surname,name,third_name)
                            FROM employees ORDER BY surname,name""",
            "disciplines": "SELECT discipline_id, name FROM disciplines ORDER BY name",
            "students": """SELECT student_id, concat_ws(' ',surname,name,third_name)
                           FROM students ORDER BY surname,name""",
            "lessons": """SELECT lesson_id, concat(lesson_date,' ',lesson_time,' — ',
                          coalesce(classroom,'')) FROM lessons ORDER BY lesson_date DESC,lesson_time""",
            "roles": "SELECT role_id, name FROM roles ORDER BY name",
        }
        with self.conn.cursor() as cur:
            cur.execute(queries[kind])
            return cur.fetchall()

    def open_form(self, key, operation, record_id):
        table, pk, fields = TABLES[key]
        existing = {}
        try:
            with self.conn.cursor() as cur:
                cur.execute("""SELECT column_name,is_nullable,column_default
                               FROM information_schema.columns
                               WHERE table_schema='public' AND table_name=%s""", (table,))
                metadata = {x[0]: (x[1], x[2]) for x in cur.fetchall()}
                if operation == "edit":
                    cur.execute(sql.SQL("SELECT * FROM {} WHERE {}=%s").format(
                        sql.Identifier(table), sql.Identifier(pk)), (record_id,))
                    row = cur.fetchone()
                    if row is None:
                        messagebox.showerror("Ошибка", "Запись больше не существует.", parent=self.root)
                        return
                    existing = dict(zip([d[0] for d in cur.description], row))
        except Exception as exc:
            self.error("Ошибка чтения записи", exc)
            return

        win = tk.Toplevel(self.root)
        win.title(("Добавление" if operation == "add" else "Редактирование") + " — " + key)
        win.geometry("560x650")
        win.minsize(440, 420)
        win.transient(self.root)
        win.grab_set()
        win.configure(bg=BG)
        tk.Label(win, text=("Добавить" if operation == "add" else "Изменить") + " — " + key,
                 font=("Arial", 18, "bold"), bg=BG, fg=NAVY).pack(pady=(18, 12))
        footer = tk.Frame(win, bg=BG, padx=24, pady=14)
        footer.pack(side="bottom", fill="x")
        outer = tk.Frame(win, bg=BG)
        outer.pack(fill="both", expand=True)
        canvas = tk.Canvas(outer, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        form = tk.Frame(canvas, bg=BG, padx=25)
        form_id = canvas.create_window((0, 0), window=form, anchor="nw")
        form.bind("<Configure>", lambda _e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(form_id, width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        widgets = {}
        for field, label, kind in fields:
            if field not in metadata:
                continue
            nullable, default = metadata[field]
            required = nullable == "NO" and (operation == "edit" or default is None)
            tk.Label(form, text=label + (" *" if required else ""), bg=BG, fg=NAVY,
                     font=("Arial", 10, "bold")).pack(anchor="w", pady=(9, 3))
            current = existing.get(field)
            if kind in FK_TABLES:
                try:
                    opts = self.foreign_options(kind)
                except Exception as exc:
                    self.error("Ошибка списка", exc, win)
                    win.destroy()
                    return
                display = ["— Не выбрано —"] + [f"{id_} — {label_}" for id_, label_ in opts]
                widget = ttk.Combobox(form, state="readonly", values=display)
                chosen = next((i + 1 for i, x in enumerate(opts) if x[0] == current), 0)
                widget.current(chosen)
                widgets[field] = (kind, widget, opts)
            elif kind == "grade":
                widget = ttk.Combobox(form, state="readonly", values=["", "1", "2", "3", "4", "5"])
                widget.set(str(current) if current is not None else "")
                widgets[field] = (kind, widget, None)
            elif kind == "method":
                widget = ttk.Combobox(form, state="readonly", values=["Наличные", "Карта", "Перевод", "Банк"])
                widget.set(str(current) if current is not None else "Наличные")
                widgets[field] = (kind, widget, None)
            elif kind == "attendance":
                widget = ttk.Combobox(form, state="readonly",
                                      values=["Присутствовал", "Отсутствовал", "Опоздал", "Уважительная причина"])
                widget.set(str(current) if current is not None else "Присутствовал")
                widgets[field] = (kind, widget, None)
            else:
                widget = ttk.Entry(form, show="*" if kind == "password" else "")
                if current is not None and kind != "password":
                    widget.insert(0, str(current))
                if operation == "add" and kind == "date" and field in ("grade_date",):
                    widget.insert(0, date.today().isoformat())
                if operation == "add" and kind == "integer" and field == "year":
                    widget.insert(0, str(date.today().year))
                widgets[field] = (kind, widget, None)
            widget.pack(fill="x", ipady=3)
            if kind == "password" and operation == "edit":
                tk.Label(form, text="Оставьте пустым, чтобы не менять пароль",
                         bg=BG, fg=MUTED, font=("Arial", 9)).pack(anchor="w")

        def save():
            values = {}
            try:
                for field, (kind, widget, options) in widgets.items():
                    raw = widget.get().strip()
                    if kind in FK_TABLES:
                        idx = widget.current()
                        value = options[idx - 1][0] if idx > 0 else None
                    elif kind == "password" and operation == "edit" and not raw:
                        continue
                    elif not raw:
                        value = None
                    elif kind == "date":
                        value = date.fromisoformat(raw)
                    elif kind == "time":
                        value = datetime.strptime(raw, "%H:%M:%S" if len(raw.split(":")) == 3 else "%H:%M").time()
                    elif kind in ("integer", "grade"):
                        value = int(raw)
                    elif kind == "decimal":
                        value = Decimal(raw.replace(",", "."))
                        if value < 0:
                            raise ValueError("Стоимость не может быть отрицательной")
                    else:
                        value = raw
                    if kind == "grade" and value is not None and not 1 <= value <= 5:
                        raise ValueError("Оценка должна быть от 1 до 5")
                    nullable, default = metadata[field]
                    if value is None and nullable == "NO" and (operation == "edit" or default is None):
                        raise ValueError(f"Заполните поле «{next(x[1] for x in fields if x[0] == field)}»")
                    values[field] = value
                if not values:
                    raise ValueError("Нет данных для сохранения")
                with self.conn:
                    with self.conn.cursor() as cur:
                        if operation == "add":
                            cols = list(values)
                            cur.execute(sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
                                sql.Identifier(table),
                                sql.SQL(", ").join(map(sql.Identifier, cols)),
                                sql.SQL(", ").join(sql.Placeholder() for _ in cols)),
                                [values[c] for c in cols])
                        else:
                            cols = list(values)
                            cur.execute(sql.SQL("UPDATE {} SET {} WHERE {}=%s").format(
                                sql.Identifier(table),
                                sql.SQL(", ").join(sql.SQL("{}=%s").format(sql.Identifier(c)) for c in cols),
                                sql.Identifier(pk)), [values[c] for c in cols] + [record_id])
                win.destroy()
                self.load_table()
                messagebox.showinfo("Готово", "Запись успешно сохранена.", parent=self.root)
            except (ValueError, psycopg2.Error) as exc:
                self.error("Ошибка сохранения", exc, win)
        ttk.Button(footer, text="Сохранить", command=save).pack(side="left", padx=(0, 8))
        ttk.Button(footer, text="Отмена", command=win.destroy).pack(side="left")

    def logout(self):
        self.employee = None
        self.show_login()

    def close(self):
        if self.conn and not self.conn.closed:
            self.conn.close()
        self.root.destroy()



class ExtendedSchoolApp(ArtSchoolApp):
    """Расширенная версия с разграничением доступа и отчётами."""

    def prepare_database(self):
        # Старые таблицы и представления сохраняются без удаления.
        super().prepare_database()
        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute("""CREATE TABLE IF NOT EXISTS curators (
                    curator_id SERIAL PRIMARY KEY,
                    employee_id INTEGER REFERENCES employees(employee_id),
                    group_id INTEGER REFERENCES groups(group_id),
                    discipline_id INTEGER REFERENCES disciplines(discipline_id))""")
                cur.execute("""CREATE TABLE IF NOT EXISTS payments (
                    payment_id SERIAL PRIMARY KEY,
                    student_id INTEGER REFERENCES students(student_id),
                    payment_date DATE NOT NULL DEFAULT CURRENT_DATE,
                    period VARCHAR(30) NOT NULL,
                    amount NUMERIC(12,2) NOT NULL CHECK(amount >= 0),
                    method VARCHAR(50) NOT NULL DEFAULT 'Наличные',
                    note TEXT)""")
                cur.execute("""CREATE TABLE IF NOT EXISTS student_accounts (
                    account_id SERIAL PRIMARY KEY,
                    student_id INTEGER REFERENCES students(student_id),
                    login VARCHAR(100) NOT NULL,
                    password VARCHAR(255) NOT NULL)""")
                # Добавляем дату посещения, если в старой БД такого поля нет.
                cur.execute("ALTER TABLE attendance ADD COLUMN IF NOT EXISTS attendance_date DATE")
                cur.execute("""UPDATE attendance a SET attendance_date=l.lesson_date
                    FROM lessons l WHERE a.lesson_id=l.lesson_id AND a.attendance_date IS NULL""")
                # Дополнительные группы, без повторного создания существующих.
                for group in ["Группа 4", "Группа 5", "Группа 6", "Группа 7", "Группа 8",
                              "Группа 9", "Группа 10", "Младшая группа А", "Младшая группа Б",
                              "Средняя группа А", "Средняя группа Б", "Старшая группа А",
                              "Старшая группа Б", "Подготовительная группа 2",
                              "Продвинутая группа 2"]:
                    cur.execute("""INSERT INTO groups(name,year)
                        SELECT %s,2026 WHERE NOT EXISTS(SELECT 1 FROM groups WHERE name=%s)""",
                        (group, group))
                cur.execute("SELECT role_id FROM roles WHERE name='Преподаватель'")
                role_id = cur.fetchone()[0]
                teachers = [
                    ("Соколова", "Елена", "Петровна", "teacher2", "Живопись"),
                    ("Морозов", "Андрей", "Викторович", "teacher3", "Скульптура"),
                    ("Кузнецова", "Мария", "Игоревна", "teacher4", "Композиция"),
                    ("Васильев", "Павел", "Сергеевич", "teacher5", "Графика"),
                    ("Орлова", "Наталья", "Алексеевна", "teacher6", "Акварель"),
                    ("Фёдоров", "Дмитрий", "Олегович", "teacher7", "История искусства"),
                    ("Белова", "Татьяна", "Романовна", "teacher8", "Основы дизайна"),
                ]
                for surname, name, third, login, discipline in teachers:
                    cur.execute("""INSERT INTO employees(surname,name,third_name,login,password,role_id)
                        SELECT %s,%s,%s,%s,%s,%s WHERE NOT EXISTS
                        (SELECT 1 FROM employees WHERE login=%s)""",
                        (surname, name, third, login, "teacher123", role_id, login))
                    cur.execute("SELECT employee_id FROM employees WHERE login=%s", (login,))
                    eid = cur.fetchone()[0]
                    cur.execute("SELECT discipline_id FROM disciplines WHERE name=%s", (discipline,))
                    did_row = cur.fetchone()
                    cur.execute("SELECT group_id FROM groups WHERE name=%s",
                                ("Группа " + str(int(login.replace('teacher','')) + 2),))
                    gid_row = cur.fetchone()
                    if gid_row and did_row:
                        cur.execute("""INSERT INTO curators(employee_id,group_id,discipline_id)
                            SELECT %s,%s,%s WHERE NOT EXISTS (
                            SELECT 1 FROM curators WHERE employee_id=%s AND group_id=%s AND discipline_id=%s)""",
                            (eid,gid_row[0],did_row[0],eid,gid_row[0],did_row[0]))
                # Учебные аккаунты не создаются автоматически: администратор выдаёт их ученикам.

    @property
    def is_student(self):
        return bool(self.employee and self.employee[5] == "Ученик")

    @property
    def is_admin(self):
        return bool(self.employee and self.employee[5] == "Администратор")

    def allowed(self, key, operation="view"):
        if not self.employee:
            return False
        if key in REPORTS:
            if key in ("Финансовый отчёт", "Долги по оплате"):
                return operation == "view" and self.is_admin
            return operation == "view" and not self.is_student
        if key in VIEWS:
            return operation == "view"
        if key not in TABLES:
            return False
        if self.is_admin:
            return True
        if self.is_student:
            return operation == "view" and key in ("Оценки", "Посещаемость", "Занятия")
        if operation == "view":
            return key not in ("Доступ учеников", "Оплата обучения")
        return key in ("Оценки", "Посещаемость")

    def show_login(self):
        self.clear()
        card = tk.Frame(self.root, bg=WHITE, padx=48, pady=32,
                        highlightbackground="#D7DFEC", highlightthickness=1)
        card.place(relx=.5, rely=.5, anchor="center")
        tk.Label(card, text="ХУДОЖЕСТВЕННАЯ ШКОЛА", font=("Arial", 20, "bold"),
                 bg=WHITE, fg=NAVY).pack(pady=(0, 12))
        tk.Label(card, text="Тип входа", bg=WHITE, fg=NAVY).pack(anchor="w")
        kind = ttk.Combobox(card, values=["Сотрудник", "Ученик"], state="readonly", width=34)
        kind.current(0)
        kind.pack(pady=(4, 12), ipady=3)
        tk.Label(card, text="Логин", bg=WHITE, fg=NAVY).pack(anchor="w")
        username = ttk.Entry(card, width=37)
        username.pack(pady=(4, 12), ipady=4)
        tk.Label(card, text="Пароль", bg=WHITE, fg=NAVY).pack(anchor="w")
        password = ttk.Entry(card, width=37, show="*")
        password.pack(pady=(4, 18), ipady=4)

        def login():
            if not username.get().strip() or not password.get():
                messagebox.showwarning("Вход", "Введите логин и пароль.", parent=self.root)
                return
            try:
                with self.conn.cursor() as cur:
                    if kind.get() == "Ученик":
                        cur.execute("""SELECT s.student_id,s.surname,s.name,s.third_name,
                                              NULL,'Ученик' FROM student_accounts a
                                       JOIN students s ON s.student_id=a.student_id
                                       WHERE a.login=%s AND a.password=%s""",
                                    (username.get().strip(), password.get()))
                    else:
                        cur.execute("""SELECT e.employee_id,e.surname,e.name,e.third_name,
                                              e.role_id,r.name FROM employees e
                                       LEFT JOIN roles r ON r.role_id=e.role_id
                                       WHERE e.login=%s AND e.password=%s""",
                                    (username.get().strip(), password.get()))
                    self.employee = cur.fetchone()
                if not self.employee:
                    messagebox.showerror("Вход", "Неверный логин или пароль.", parent=self.root)
                    return
                self.show_main()
            except Exception as exc:
                self.error("Ошибка входа", exc)
        ttk.Button(card, text="ВОЙТИ", command=login).pack(fill="x")
        tk.Label(card, text="Демо: администратор — admin / admin123; преподаватель — teacher1 / teacher123",
                 bg=WHITE, fg=MUTED, font=("Arial", 8)).pack(pady=(14, 0))
        username.focus_set()
        self.root.bind("<Return>", lambda _e: login())

    def show_main(self):
        self.clear()
        self.header("ХУДОЖЕСТВЕННАЯ ШКОЛА")
        body = tk.Frame(self.root, bg=BG, padx=28, pady=18)
        body.pack(fill="both", expand=True)
        tk.Label(body, text="Главное меню", bg=BG, fg=NAVY,
                 font=("Arial", 23, "bold")).pack(anchor="w")
        keys = [k for k in list(TABLES) + list(VIEWS) + list(REPORTS) if self.allowed(k)]
        grid = tk.Frame(body, bg=BG)
        grid.pack(fill="both", expand=True, pady=12)
        for i, key in enumerate(keys):
            tk.Button(grid, text=key, bg=WHITE, fg=NAVY, relief="flat",
                      font=("Arial", 11, "bold"), cursor="hand2",
                      command=lambda k=key: self.open_section(k)).grid(
                          row=i // 4, column=i % 4, padx=6, pady=6, sticky="nsew")
        for i in range(4):
            grid.columnconfigure(i, weight=1)
        for i in range((len(keys)+3)//4):
            grid.rowconfigure(i, weight=1)
        ttk.Button(body, text="Выйти из системы", command=self.logout).pack(anchor="e")

    def open_section(self, key):
        if key in REPORTS:
            return self.open_report(key)
        return super().open_section(key)

    def load_table(self):
        key = self.current_key
        if not self.allowed(key):
            return
        table = TABLES[key][0] if key in TABLES else VIEWS[key]
        try:
            with self.conn.cursor() as cur:
                query = sql.SQL("SELECT * FROM {}").format(sql.Identifier(table))
                params = ()
                if self.is_student:
                    sid = self.employee[0]
                    if key == "Оценки":
                        query = sql.SQL("SELECT * FROM grades WHERE student_id=%s")
                        params = (sid,)
                    elif key == "Посещаемость":
                        query = sql.SQL("SELECT * FROM attendance WHERE student_id=%s")
                        params = (sid,)
                    elif key == "Занятия":
                        query = sql.SQL("""SELECT l.* FROM lessons l
                            JOIN students s ON s.group_id=l.group_id WHERE s.student_id=%s""")
                        params = (sid,)
                    elif key == "Расписание":
                        # Представления прежних версий могут иметь другие колонки.
                        query = sql.SQL("""SELECT l.lesson_date,l.lesson_time,l.classroom,
                            g.name AS group_name,concat_ws(' ',e.surname,e.name) AS teacher_name,
                            d.name AS discipline_name FROM lessons l
                            JOIN students s ON s.group_id=l.group_id
                            LEFT JOIN groups g ON g.group_id=l.group_id
                            LEFT JOIN employees e ON e.employee_id=l.teacher_id
                            LEFT JOIN disciplines d ON d.discipline_id=l.discipline_id
                            WHERE s.student_id=%s""")
                        params = (sid,)
                    elif key == "Оценки учеников":
                        query = sql.SQL("""SELECT d.name AS discipline_name, gr.grade_date,gr.value
                            FROM grades gr LEFT JOIN disciplines d ON d.discipline_id=gr.discipline_id
                            WHERE gr.student_id=%s""")
                        params = (sid,)
                    elif key == "Отчёт по посещаемости":
                        query = sql.SQL("""SELECT coalesce(a.attendance_date,l.lesson_date) AS attendance_date,
                            l.lesson_time,a.mark FROM attendance a
                            JOIN lessons l ON l.lesson_id=a.lesson_id WHERE a.student_id=%s""")
                        params = (sid,)
                cur.execute(query, params)
                self.all_rows = cur.fetchall()
                self.columns = [d[0] for d in cur.description]
            self.tree["columns"] = self.columns
            for col in self.columns:
                self.tree.heading(col, text=LABELS.get(col, col.replace('_',' ').capitalize()),
                                  command=lambda c=col: self.sort_column(c))
                self.tree.column(col, width=170, minwidth=85, stretch=True)
            self.visible_rows = list(self.all_rows)
            self.render_rows(self.all_rows)
        except Exception as exc:
            self.error("Ошибка загрузки", exc)

    def foreign_options(self, kind):
        # В списке отображаются полные ФИО и сведения о занятиях.
        return super().foreign_options(kind)

    def open_form(self, key, operation, record_id):
        # Базовая форма поддерживает все дополнительные таблицы.
        return super().open_form(key, operation, record_id)

    def report_query(self, key):
        reports = {
            "Сводка посещаемости": """SELECT concat_ws(' ',s.surname,s.name,s.third_name) AS student_name,
                g.name AS group_name, COUNT(l.lesson_id) AS total_lessons,
                COUNT(a.attendance_id) FILTER(WHERE a.mark IN ('Отсутствовал','Уважительная причина')) AS missed,
                CASE WHEN COUNT(l.lesson_id)=0 THEN 0 ELSE
                ROUND(100.0 * (COUNT(l.lesson_id)-COUNT(a.attendance_id)
                FILTER(WHERE a.mark IN ('Отсутствовал','Уважительная причина')))
                / COUNT(l.lesson_id),1) END AS attendance_percent
                FROM students s LEFT JOIN groups g ON g.group_id=s.group_id
                LEFT JOIN lessons l ON l.group_id=s.group_id AND l.lesson_date<=CURRENT_DATE
                LEFT JOIN attendance a ON a.lesson_id=l.lesson_id AND a.student_id=s.student_id
                GROUP BY s.student_id,s.surname,s.name,s.third_name,g.name ORDER BY g.name,s.surname""",
            "Ведомость успеваемости": """SELECT concat_ws(' ',s.surname,s.name,s.third_name) AS student_name,
                g.name AS group_name,d.name AS discipline_name,COUNT(gr.grade_id) AS grade_count,
                ROUND(AVG(gr.value),2) AS average_grade
                FROM students s LEFT JOIN groups g ON g.group_id=s.group_id
                LEFT JOIN grades gr ON gr.student_id=s.student_id
                LEFT JOIN disciplines d ON d.discipline_id=gr.discipline_id
                GROUP BY s.student_id,s.surname,s.name,s.third_name,g.name,d.name
                ORDER BY g.name,s.surname,d.name""",
            "Финансовый отчёт": """SELECT concat_ws(' ',s.surname,s.name,s.third_name) AS student_name,
                g.name AS group_name,p.period,COUNT(p.payment_id) AS payments_count,
                SUM(p.amount) AS paid FROM payments p JOIN students s ON s.student_id=p.student_id
                LEFT JOIN groups g ON g.group_id=s.group_id
                GROUP BY s.student_id,s.surname,s.name,s.third_name,g.name,p.period
                ORDER BY p.period DESC,g.name,s.surname""",
            "Долги по оплате": """SELECT concat_ws(' ',s.surname,s.name,s.third_name) AS student_name,
                g.name AS group_name,COUNT(l.lesson_id) AS lessons_count,
                COALESCE(SUM(d.price),0) AS expected,
                COALESCE((SELECT SUM(p.amount) FROM payments p WHERE p.student_id=s.student_id),0) AS paid,
                GREATEST(COALESCE(SUM(d.price),0)-COALESCE((SELECT SUM(p.amount)
                    FROM payments p WHERE p.student_id=s.student_id),0),0) AS debt
                FROM students s LEFT JOIN groups g ON g.group_id=s.group_id
                LEFT JOIN lessons l ON l.group_id=s.group_id AND l.lesson_date<=CURRENT_DATE
                LEFT JOIN disciplines d ON d.discipline_id=l.discipline_id
                GROUP BY s.student_id,s.surname,s.name,s.third_name,g.name
                ORDER BY debt DESC,s.surname""",
            "Нагрузка преподавателей": """SELECT concat_ws(' ',e.surname,e.name,e.third_name) AS teacher_name,
                COUNT(l.lesson_id) AS lessons_count,
                COUNT(DISTINCT l.group_id) AS groups_count
                FROM employees e LEFT JOIN lessons l ON l.teacher_id=e.employee_id
                GROUP BY e.employee_id,e.surname,e.name,e.third_name
                ORDER BY lessons_count DESC""",
            "Состав групп": """SELECT g.name AS group_name, g.year,
                concat_ws(' ',e.surname,e.name,e.third_name) AS teacher_name,
                COUNT(s.student_id) AS students_count FROM groups g
                LEFT JOIN employees e ON e.employee_id=g.teacher_id
                LEFT JOIN students s ON s.group_id=g.group_id
                GROUP BY g.group_id,g.name,g.year,e.surname,e.name,e.third_name
                ORDER BY g.name""",
            "Список кураторов": """SELECT concat_ws(' ',e.surname,e.name,e.third_name) AS curator_name,
                g.name AS group_name,d.name AS discipline_name
                FROM curators c LEFT JOIN employees e ON e.employee_id=c.employee_id
                LEFT JOIN groups g ON g.group_id=c.group_id
                LEFT JOIN disciplines d ON d.discipline_id=c.discipline_id
                ORDER BY g.name,e.surname""",
        }
        return reports[key]

    def open_report(self, key):
        if not self.allowed(key):
            messagebox.showerror("Доступ", "Недостаточно прав.", parent=self.root)
            return
        self.current_key = key
        self.clear()
        self.header("Отчёт: " + key)
        body = tk.Frame(self.root, bg=BG, padx=20, pady=18)
        body.pack(fill="both", expand=True)
        bar = tk.Frame(body, bg=BG)
        bar.pack(fill="x", pady=(0, 12))
        ttk.Label(bar, text="Выберите отчёт:").pack(side="left")
        combo = ttk.Combobox(bar, state="readonly", width=35,
                             values=[k for k in REPORTS if self.allowed(k)])
        combo.set(key)
        combo.pack(side="left", padx=8)
        combo.bind("<<ComboboxSelected>>", lambda _e: self.open_report(combo.get()))
        holder = tk.Frame(body)
        holder.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(holder, show="headings")
        ys = ttk.Scrollbar(holder, orient="vertical", command=self.tree.yview)
        xs = ttk.Scrollbar(holder, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=ys.set, xscrollcommand=xs.set)
        self.tree.grid(row=0,column=0,sticky="nsew")
        ys.grid(row=0,column=1,sticky="ns")
        xs.grid(row=1,column=0,sticky="ew")
        holder.columnconfigure(0,weight=1)
        holder.rowconfigure(0,weight=1)
        self.tree.tag_configure("odd",background="#F3F6FB")
        footer = tk.Frame(body, bg=BG)
        footer.pack(fill="x", pady=12)
        ttk.Button(footer,text="Обновить",command=self.load_report).pack(side="left")
        ttk.Button(footer,text="Сохранить в CSV",command=self.export_report).pack(side="left",padx=8)
        ttk.Button(footer,text="Назад",command=self.show_main).pack(side="right")
        ttk.Label(footer,textvariable=self.status).pack(side="right",padx=20)
        self.load_report()

    def load_report(self):
        try:
            with self.conn.cursor() as cur:
                cur.execute(self.report_query(self.current_key))
                self.all_rows=cur.fetchall()
                self.columns=[d[0] for d in cur.description]
            self.tree["columns"]=self.columns
            for col in self.columns:
                self.tree.heading(col,text=LABELS.get(col,col.replace('_',' ').capitalize()))
                self.tree.column(col,width=170,minwidth=100)
            self.render_rows(self.all_rows)
        except Exception as exc:
            self.error("Ошибка отчёта",exc)

    def export_report(self):
        path=filedialog.asksaveasfilename(parent=self.root,defaultextension=".csv",
                                          filetypes=[("Таблица CSV","*.csv")],
                                          initialfile=self.current_key+".csv")
        if not path:
            return
        try:
            with open(path,"w",encoding="utf-8-sig",newline="") as f:
                writer=csv.writer(f,delimiter=";")
                writer.writerow([LABELS.get(c,c.replace('_',' ').capitalize()) for c in self.columns])
                writer.writerows(self.all_rows)
            messagebox.showinfo("Готово","Отчёт сохранён.",parent=self.root)
        except OSError as exc:
            messagebox.showerror("Ошибка экспорта",str(exc),parent=self.root)

# Дополнительная версия: русскоязычные связанные разделы, фильтры и заполнение.
import calendar
from datetime import timedelta

LABELS.update({"teacher_id":"Преподаватель", "students_count":"Учеников", "groups_count":"Групп",
 "payments_count":"Платежей", "hours_count":"Часов", "duration_hours":"Длительность, ч",
 "classroom_name":"Аудитория", "period":"Период", "paid":"Оплачено, ₽",
 "expected":"Начислено, ₽", "debt":"Задолженность, ₽", "average_grade":"Средний балл",
 "attendance_percent":"Посещаемость, %", "total_lessons":"Всего занятий",
 "missed":"Пропусков", "grade_count":"Оценок", "lessons_count":"Занятий",
 "curator_name":"Куратор", "teacher_name":"Преподаватель", "discipline_name":"Дисциплина",
 "student_name":"ФИО ученика", "group_name":"Группа", "role_name":"Должность",
 "account_id":"№ доступа", "payment_id":"№ платежа", "curator_id":"№ записи",
 "lesson_id":"№ занятия", "grade_id":"№ оценки", "attendance_id":"№ отметки",
 "employee_id":"№ сотрудника", "student_id":"№ ученика", "discipline_id":"№ дисциплины",
 "group_id":"№ группы", "method":"Способ оплаты", "note":"Примечание"})
TABLES["Группы"][2].append(("curator_id", "Куратор", "employees"))
TABLES["Дисциплины"][2].extend([("teacher_id", "Преподаватель", "employees"),
                                 ("classroom", "Аудитория", "text")])
TABLES["Занятия"][2].append(("duration_hours", "Продолжительность, ч", "decimal"))

class CompleteSchoolApp(ExtendedSchoolApp):
    def prepare_database(self):
        super().prepare_database()
        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute("ALTER TABLE groups ADD COLUMN IF NOT EXISTS curator_id INTEGER REFERENCES employees(employee_id)")
                cur.execute("ALTER TABLE disciplines ADD COLUMN IF NOT EXISTS teacher_id INTEGER REFERENCES employees(employee_id)")
                cur.execute("ALTER TABLE disciplines ADD COLUMN IF NOT EXISTS classroom VARCHAR(100)")
                cur.execute("ALTER TABLE lessons ADD COLUMN IF NOT EXISTS duration_hours NUMERIC(5,2) DEFAULT 2")
                cur.execute("SELECT role_id FROM roles WHERE name='Преподаватель'")
                role = cur.fetchone()[0]
                surnames = ['Иванов','Соколова','Морозов','Кузнецова','Васильев','Орлова','Фёдоров','Белова','Крылов','Захарова','Тихонов','Егорова','Павлов','Громова','Макаров','Сидорова','Беляев','Рыбакова','Комаров','Данилова','Лебедев','Тарасова','Киселёв','Воронова']
                names = ['Иван','Елена','Андрей','Мария','Павел','Наталья','Дмитрий','Татьяна','Сергей','Ольга','Михаил','Анна','Алексей','Ирина','Николай','Светлана','Виктор','Юлия','Роман','Екатерина','Артём','Полина','Константин','Вера']
                for i in range(1,25):
                    login = f'teacher{i}'
                    cur.execute('SELECT 1 FROM employees WHERE login=%s', (login,))
                    if not cur.fetchone():
                        cur.execute('INSERT INTO employees(surname,name,third_name,login,password,role_id) VALUES (%s,%s,%s,%s,%s,%s)',
                                    (surnames[i-1],names[i-1],'Александрович' if i%2 else 'Сергеевна',login,'teacher123',role))
                cur.execute("SELECT employee_id FROM employees WHERE role_id=%s ORDER BY employee_id", (role,))
                teachers = [r[0] for r in cur.fetchall()]
                cur.execute('SELECT group_id,name FROM groups ORDER BY group_id')
                groups = cur.fetchall()
                for i,(gid,gname) in enumerate(groups):
                    cur.execute('UPDATE groups SET teacher_id=COALESCE(teacher_id,%s),curator_id=COALESCE(curator_id,%s) WHERE group_id=%s',
                                (teachers[i%len(teachers)],teachers[(i+3)%len(teachers)],gid))
                cur.execute('SELECT discipline_id FROM disciplines ORDER BY discipline_id')
                disciplines = [r[0] for r in cur.fetchall()]
                for i,did in enumerate(disciplines):
                    cur.execute('UPDATE disciplines SET teacher_id=COALESCE(teacher_id,%s), classroom=COALESCE(classroom,%s) WHERE discipline_id=%s',
                                (teachers[i%len(teachers)],f'Аудитория {i%12+1}',did))
                # Создаём дополнительные группы и заполняем каждую учениками, если это демонстрационная база.
                for i in range(1,26):
                    group = f'Учебная группа {i:02d}'
                    cur.execute('SELECT group_id FROM groups WHERE name=%s', (group,))
                    result = cur.fetchone()
                    if result:
                        gid = result[0]
                    else:
                        cur.execute('INSERT INTO groups(name,year,teacher_id,curator_id) VALUES (%s,%s,%s,%s) RETURNING group_id',
                                    (group,2026,teachers[(i-1)%len(teachers)],teachers[(i+2)%len(teachers)]))
                        gid = cur.fetchone()[0]
                    # Заполняем только недостающих учеников до 15 в каждой демонстрационной группе.
                    cur.execute('SELECT count(*) FROM students WHERE group_id=%s', (gid,))
                    count = cur.fetchone()[0]
                    for j in range(count+1,16):
                        surname = surnames[(i*7+j)%len(surnames)]
                        name = names[(i*3+j)%len(names)]
                        phone = f'+7900{i:03d}{j:04d}'
                        cur.execute('SELECT 1 FROM students WHERE phone=%s', (phone,))
                        if cur.fetchone():
                            continue
                        cur.execute('INSERT INTO students(surname,name,third_name,birth_date,phone,group_id) VALUES (%s,%s,%s,%s,%s,%s)',
                                    (surname,name,'Александрович' if j%2 else 'Сергеевна',date(2010+j%5,1+j%12,1+j%25),phone,gid))
                cur.execute('SELECT group_id,teacher_id,curator_id FROM groups ORDER BY group_id')
                groups = cur.fetchall()
                # Для каждой группы назначаем кураторов по дисциплинам.
                for i,(gid,tid,cid) in enumerate(groups):
                    did = disciplines[i%len(disciplines)]
                    cur.execute('SELECT 1 FROM curators WHERE group_id=%s', (gid,))
                    if not cur.fetchone():
                        cur.execute('INSERT INTO curators(employee_id,group_id,discipline_id) VALUES (%s,%s,%s)', (cid or tid,gid,did))
                # Согласованные занятия на 8 недель для каждой группы.
                start = date(2026,9,1)
                for i,(gid,tid,cid) in enumerate(groups):
                    for week in range(8):
                        for day_offset in (0,2):
                            day = start + timedelta(days=7*week+day_offset)
                            did = disciplines[(i+week+day_offset)%len(disciplines)]
                            cur.execute('SELECT teacher_id,classroom FROM disciplines WHERE discipline_id=%s',(did,))
                            teacher,room = cur.fetchone()
                            hour = 9+(i%5)*2
                            cur.execute('SELECT lesson_id FROM lessons WHERE group_id=%s AND lesson_date=%s AND lesson_time=%s',
                                        (gid,day,f'{hour:02d}:00'))
                            if not cur.fetchone():
                                cur.execute('INSERT INTO lessons(lesson_date,lesson_time,classroom,group_id,teacher_id,discipline_id,duration_hours) VALUES (%s,%s,%s,%s,%s,%s,2)',
                                            (day,f'{hour:02d}:00',room,gid,teacher,did))
                # Для каждого ученика — вход, оценки, посещаемость и демонстрационная оплата.
                cur.execute('SELECT student_id,group_id FROM students ORDER BY student_id')
                students = cur.fetchall()
                for sid,gid in students:
                    cur.execute('SELECT 1 FROM student_accounts WHERE student_id=%s',(sid,))
                    if not cur.fetchone():
                        login = f'student{sid}'
                        cur.execute('SELECT 1 FROM student_accounts WHERE login=%s',(login,))
                        if not cur.fetchone():
                            cur.execute('INSERT INTO student_accounts(student_id,login,password) VALUES (%s,%s,%s)',(sid,login,'student123'))
                    cur.execute('SELECT lesson_id,lesson_date,discipline_id FROM lessons WHERE group_id=%s ORDER BY lesson_date,lesson_time LIMIT 12',(gid,))
                    lessons = cur.fetchall()
                    for k,(lid,ldate,did) in enumerate(lessons):
                        cur.execute('SELECT 1 FROM attendance WHERE student_id=%s AND lesson_id=%s',(sid,lid))
                        if not cur.fetchone():
                            mark = 'Отсутствовал' if (sid+k)%9==0 else 'Присутствовал'
                            cur.execute('INSERT INTO attendance(lesson_id,student_id,mark,attendance_date) VALUES (%s,%s,%s,%s)',(lid,sid,mark,ldate))
                        if k%2==0:
                            cur.execute('SELECT 1 FROM grades WHERE student_id=%s AND discipline_id=%s AND grade_date=%s',(sid,did,ldate))
                            if not cur.fetchone():
                                cur.execute('INSERT INTO grades(student_id,discipline_id,grade_date,value) VALUES (%s,%s,%s,%s)',(sid,did,ldate,3+(sid+k)%3))
                    for month in ('2026-09','2026-10'):
                        cur.execute('SELECT 1 FROM payments WHERE student_id=%s AND period=%s',(sid,month))
                        if not cur.fetchone():
                            cur.execute('INSERT INTO payments(student_id,payment_date,period,amount,method,note) VALUES (%s,%s,%s,%s,%s,%s)',
                                        (sid,date.fromisoformat(month+'-10'),month,3500+(sid%4)*500,'Банковская карта','Демонстрационная оплата'))

                cur.execute('SELECT student_id FROM students ORDER BY student_id LIMIT 1')
                first_student=cur.fetchone()
                if first_student:
                    cur.execute("SELECT 1 FROM student_accounts WHERE login='demo_student'")
                    if not cur.fetchone():
                        cur.execute("INSERT INTO student_accounts(student_id,login,password) VALUES (%s,'demo_student','student123')",(first_student[0],))

    def show_login(self):
        super().show_login()
        tk.Label(self.root,text='Вход ученика: тип «Ученик», логин demo_student, пароль student123',
                 bg=BG,fg=NAVY,font=('Arial',10)).place(relx=0.5,rely=0.91,anchor='center')

    def section_query(self,key):
        # Первый столбец таблиц для редактирования — первичный ключ.
        q = {
          'Ученики': """SELECT s.student_id,s.surname,s.name,s.third_name,s.birth_date,s.phone,g.name AS group_name
                          FROM students s LEFT JOIN groups g ON g.group_id=s.group_id ORDER BY s.surname,s.name,s.student_id""",
          'Сотрудники': """SELECT e.employee_id,e.surname,e.name,e.third_name,e.phone,e.email,e.login,
                              e.password,r.name AS role_name FROM employees e LEFT JOIN roles r ON r.role_id=e.role_id
                              ORDER BY e.surname,e.name,e.employee_id""",
          'Группы': """SELECT g.group_id,g.name,g.year,concat_ws(' ',e.surname,e.name,e.third_name) AS teacher_name,
                           concat_ws(' ',c.surname,c.name,c.third_name) AS curator_name,
                           (SELECT count(*) FROM students s WHERE s.group_id=g.group_id) AS students_count
                           FROM groups g LEFT JOIN employees e ON e.employee_id=g.teacher_id
                           LEFT JOIN employees c ON c.employee_id=g.curator_id ORDER BY g.name""",
          'Дисциплины': """SELECT d.discipline_id,d.name,d.price,
                               concat_ws(' ',e.surname,e.name,e.third_name) AS teacher_name,d.classroom
                               FROM disciplines d LEFT JOIN employees e ON e.employee_id=d.teacher_id ORDER BY d.name""",
          'Занятия': """SELECT l.lesson_id,l.lesson_date,l.lesson_time,g.name AS group_name,
                             d.name AS discipline_name,concat_ws(' ',e.surname,e.name,e.third_name) AS teacher_name,
                             l.classroom,l.duration_hours FROM lessons l
                             LEFT JOIN groups g ON g.group_id=l.group_id
                             LEFT JOIN disciplines d ON d.discipline_id=l.discipline_id
                             LEFT JOIN employees e ON e.employee_id=l.teacher_id
                             ORDER BY l.lesson_date,l.lesson_time,g.name""",
          'Оценки': """SELECT gr.grade_id,concat_ws(' ',s.surname,s.name,s.third_name) AS student_name,
                           g.name AS group_name,d.name AS discipline_name,gr.grade_date,gr.value FROM grades gr
                           JOIN students s ON s.student_id=gr.student_id
                           LEFT JOIN groups g ON g.group_id=s.group_id
                           LEFT JOIN disciplines d ON d.discipline_id=gr.discipline_id
                           ORDER BY g.name,s.surname,s.name,gr.grade_date""",
          'Посещаемость': """SELECT a.attendance_id,concat_ws(' ',s.surname,s.name,s.third_name) AS student_name,
                                 g.name AS group_name,d.name AS discipline_name,
                                 coalesce(a.attendance_date,l.lesson_date) AS attendance_date,a.mark
                                 FROM attendance a JOIN students s ON s.student_id=a.student_id
                                 JOIN lessons l ON l.lesson_id=a.lesson_id
                                 LEFT JOIN groups g ON g.group_id=s.group_id
                                 LEFT JOIN disciplines d ON d.discipline_id=l.discipline_id
                                 ORDER BY g.name,s.surname,a.attendance_date""",
          'Кураторы': """SELECT c.curator_id,concat_ws(' ',e.surname,e.name,e.third_name) AS curator_name,
                              g.name AS group_name,d.name AS discipline_name,d.classroom
                              FROM curators c LEFT JOIN employees e ON e.employee_id=c.employee_id
                              LEFT JOIN groups g ON g.group_id=c.group_id
                              LEFT JOIN disciplines d ON d.discipline_id=c.discipline_id ORDER BY g.name""",
          'Оплата обучения': """SELECT p.payment_id,concat_ws(' ',s.surname,s.name,s.third_name) AS student_name,
                                     g.name AS group_name,p.payment_date,p.period,p.amount,p.method,p.note
                                     FROM payments p JOIN students s ON s.student_id=p.student_id
                                     LEFT JOIN groups g ON g.group_id=s.group_id ORDER BY g.name,s.surname,p.payment_date""",
          'Доступ учеников': """SELECT a.account_id,concat_ws(' ',s.surname,s.name,s.third_name) AS student_name,
                                     g.name AS group_name,a.login,a.password FROM student_accounts a
                                     JOIN students s ON s.student_id=a.student_id
                                     LEFT JOIN groups g ON g.group_id=s.group_id ORDER BY g.name,s.surname""",
          'Расписание': """SELECT l.lesson_date,l.lesson_time,g.name AS group_name,d.name AS discipline_name,
                               concat_ws(' ',e.surname,e.name,e.third_name) AS teacher_name,l.classroom,l.duration_hours
                               FROM lessons l LEFT JOIN groups g ON g.group_id=l.group_id
                               LEFT JOIN disciplines d ON d.discipline_id=l.discipline_id
                               LEFT JOIN employees e ON e.employee_id=l.teacher_id
                               ORDER BY l.lesson_date,l.lesson_time,g.name""",
          'Оценки учеников': """SELECT concat_ws(' ',s.surname,s.name,s.third_name) AS student_name,
                                   g.name AS group_name,d.name AS discipline_name,gr.grade_date,gr.value
                                   FROM grades gr JOIN students s ON s.student_id=gr.student_id
                                   LEFT JOIN groups g ON g.group_id=s.group_id
                                   LEFT JOIN disciplines d ON d.discipline_id=gr.discipline_id
                                   ORDER BY g.name,s.surname,s.name,gr.grade_date""",
          'Отчёт по посещаемости': """SELECT concat_ws(' ',s.surname,s.name,s.third_name) AS student_name,
                                         g.name AS group_name,d.name AS discipline_name,
                                         coalesce(a.attendance_date,l.lesson_date) AS attendance_date,a.mark
                                         FROM attendance a JOIN students s ON s.student_id=a.student_id
                                         JOIN lessons l ON l.lesson_id=a.lesson_id
                                         LEFT JOIN groups g ON g.group_id=s.group_id
                                         LEFT JOIN disciplines d ON d.discipline_id=l.discipline_id
                                         ORDER BY g.name,s.surname,a.attendance_date""",
        }
        return q[key]

    def load_table(self):
        try:
            query=self.section_query(self.current_key)
            params=[]
            if self.is_student:
                sid=self.employee[0]
                if self.current_key in ('Оценки','Оценки учеников','Посещаемость','Отчёт по посещаемости'):
                    query=f'SELECT * FROM ({query}) AS visible WHERE student_name=(SELECT concat_ws(\' \',surname,name,third_name) FROM students WHERE student_id=%s)'
                    params=[sid]
                elif self.current_key in ('Занятия','Расписание'):
                    query=f'SELECT * FROM ({query}) AS visible WHERE group_name=(SELECT g.name FROM students s JOIN groups g ON g.group_id=s.group_id WHERE s.student_id=%s)'
                    params=[sid]
            with self.conn.cursor() as cur:
                cur.execute(query,params)
                self.all_rows=cur.fetchall()
                self.columns=[d[0] for d in cur.description]
            self.tree['columns']=self.columns
            for col in self.columns:
                self.tree.heading(col,text=LABELS.get(col,col.replace('_',' ').capitalize()),
                                  command=lambda c=col:self.sort_column(c))
                self.tree.column(col,width=175,minwidth=95,stretch=True)
            self.visible_rows=list(self.all_rows)
            self.apply_filters()
        except Exception as exc:
            self.error('Ошибка загрузки',exc)

    def render_rows(self,rows):
        self.tree.delete(*self.tree.get_children())
        for i,row in enumerate(rows):
            values=['••••••••' if col=='password' else ('' if v is None else str(v))
                    for col,v in zip(self.columns,row)]
            self.tree.insert('', 'end', iid=str(i),values=values,tags=('odd',) if i%2 else ())
        self.status.set(f'Записей: {len(rows)}')

    def apply_filters(self):
        rows=list(self.all_rows)
        for column,widget in getattr(self,'filters',{}).items():
            val=widget.get()
            if val and val!='Все':
                idx=self.columns.index(column) if column in self.columns else -1
                if idx>=0:
                    rows=[r for r in rows if str(r[idx])==val]
        search=getattr(self,'search_box',None)
        if search:
            q=search.get().strip().casefold()
            if q:
                rows=[r for r in rows if any(q in str(v).casefold() for c,v in zip(self.columns,r)
                                                 if v is not None and c!='password')]
        self.visible_rows=rows
        self.render_rows(rows)

    def open_section(self,key):
        if key in REPORTS:
            return self.open_report(key)
        if not self.allowed(key):
            messagebox.showerror('Доступ','Нет прав для просмотра раздела.',parent=self.root)
            return
        self.current_key=key
        self.clear()
        self.header(key)
        body=tk.Frame(self.root,bg=BG,padx=18,pady=14)
        body.pack(fill='both',expand=True)
        controls=tk.Frame(body,bg=BG)
        controls.pack(fill='x',pady=(0,10))
        self.search_box=tk.StringVar()
        tk.Label(controls,text='Поиск:',bg=BG,fg=NAVY).pack(side='left')
        search=ttk.Entry(controls,textvariable=self.search_box,width=25)
        search.pack(side='left',padx=6)
        self.filters={}
        # Фильтры заполняются после чтения строк.
        holder=tk.Frame(body)
        holder.pack(fill='both',expand=True)
        self.tree=ttk.Treeview(holder,show='headings',selectmode='browse')
        ys=ttk.Scrollbar(holder,orient='vertical',command=self.tree.yview)
        xs=ttk.Scrollbar(holder,orient='horizontal',command=self.tree.xview)
        self.tree.configure(yscrollcommand=ys.set,xscrollcommand=xs.set)
        self.tree.grid(row=0,column=0,sticky='nsew')
        ys.grid(row=0,column=1,sticky='ns')
        xs.grid(row=1,column=0,sticky='ew')
        holder.rowconfigure(0,weight=1)
        holder.columnconfigure(0,weight=1)
        self.tree.tag_configure('odd',background='#F3F6FB')
        self.load_table()
        for col,title in [('group_name','Группа'),('discipline_name','Дисциплина'),
                          ('student_name','Ученик'),('teacher_name','Преподаватель')]:
            if col not in self.columns:
                continue
            tk.Label(controls,text=title+':',bg=BG).pack(side='left',padx=(10,2))
            options=sorted({str(r[self.columns.index(col)]) for r in self.all_rows if r[self.columns.index(col)]})
            combo=ttk.Combobox(controls,state='readonly',width=17,values=['Все']+options)
            combo.set('Все')
            combo.pack(side='left',padx=3)
            combo.bind('<<ComboboxSelected>>',lambda _e:self.apply_filters())
            self.filters[col]=combo
        self.search_box.trace_add('write',lambda *_:self.apply_filters())
        actions=tk.Frame(body,bg=BG)
        actions.pack(fill='x',pady=10)
        if key in TABLES and self.allowed(key,'edit'):
            for label,op in [('Добавить','add'),('Редактировать','edit'),('Удалить','delete')]:
                ttk.Button(actions,text=label,command=lambda x=op:self.manage_record(key,x)).pack(side='left',padx=3)
            self.tree.bind('<Double-1>',lambda _e:self.manage_record(key,'edit'))
        if key in ('Сотрудники','Доступ учеников') and self.is_admin:
            ttk.Button(actions,text='Показать пароль выбранного',command=self.show_password).pack(side='left',padx=5)
        ttk.Button(actions,text='Обновить',command=self.load_table).pack(side='left',padx=5)
        ttk.Button(actions,text='Назад',command=self.show_main).pack(side='right')
        ttk.Label(actions,textvariable=self.status).pack(side='right',padx=15)

    def show_password(self):
        if not self.is_admin or self.current_key not in ('Сотрудники','Доступ учеников'):
            return
        selection=self.tree.selection()
        if not selection:
            messagebox.showwarning('Выбор','Выберите запись.',parent=self.root)
            return
        record_id=self.selected_id()
        table,pk,_=TABLES[self.current_key]
        with self.conn.cursor() as cur:
            cur.execute(sql.SQL('SELECT password FROM {} WHERE {}=%s').format(sql.Identifier(table),sql.Identifier(pk)),(record_id,))
            result=cur.fetchone()
        messagebox.showinfo('Пароль выбранной записи',result[0] if result else 'Запись не найдена',parent=self.root)

    def foreign_options(self,kind):
        if kind=='lessons':
            with self.conn.cursor() as cur:
                cur.execute('''SELECT l.lesson_id,concat(l.lesson_date,' ',l.lesson_time,' — ',g.name,' — ',d.name)
                               FROM lessons l LEFT JOIN groups g ON g.group_id=l.group_id
                               LEFT JOIN disciplines d ON d.discipline_id=l.discipline_id
                               ORDER BY l.lesson_date DESC,l.lesson_time''')
                return cur.fetchall()
        return super().foreign_options(kind)

    def open_form(self,key,operation,record_id):
        # Для оценок и посещаемости выбор группы ограничивает список учеников и занятий.
        if key not in ('Оценки','Посещаемость'):
            return super().open_form(key,operation,record_id)
        table,pk,fields=TABLES[key]
        existing={}
        try:
            with self.conn.cursor() as cur:
                if operation=='edit':
                    cur.execute(sql.SQL('SELECT * FROM {} WHERE {}=%s').format(sql.Identifier(table),sql.Identifier(pk)),(record_id,))
                    row=cur.fetchone()
                    if not row:
                        return
                    existing=dict(zip([d[0] for d in cur.description],row))
                cur.execute('SELECT group_id,name FROM groups ORDER BY name')
                groups=cur.fetchall()
        except Exception as exc:
            self.error('Ошибка формы',exc)
            return
        win=tk.Toplevel(self.root)
        win.title('Оценка' if key=='Оценки' else 'Посещаемость')
        win.geometry('530x570')
        win.transient(self.root)
        win.grab_set()
        panel=tk.Frame(win,padx=25,pady=20)
        panel.pack(fill='both',expand=True)
        tk.Label(panel,text='Выберите группу, ученика и '+('дисциплину' if key=='Оценки' else 'занятие'),font=('Arial',13,'bold')).pack(pady=10)
        def field(label,options):
            tk.Label(panel,text=label).pack(anchor='w',pady=(9,2))
            c=ttk.Combobox(panel,state='readonly',values=options)
            c.pack(fill='x')
            return c
        gc=field('Группа',[f'{gid} — {name}' for gid,name in groups])
        sc=field('Ученик',[])
        dc=field('Дисциплина' if key=='Оценки' else 'Занятие',[])
        tk.Label(panel,text='Дата (ГГГГ-ММ-ДД)').pack(anchor='w',pady=(9,2))
        date_entry=ttk.Entry(panel)
        date_entry.insert(0,str(existing.get('grade_date') or existing.get('attendance_date') or date.today()))
        date_entry.pack(fill='x')
        vc=field('Оценка' if key=='Оценки' else 'Отметка',
                 ['1','2','3','4','5'] if key=='Оценки' else ['Присутствовал','Отсутствовал','Опоздал','Уважительная причина'])
        vc.set(str(existing.get('value') or existing.get('mark') or ('5' if key=='Оценки' else 'Присутствовал')))
        students=[]
        options=[]
        def group_changed(_e=None):
            nonlocal students,options
            if gc.current()<0:
                return
            gid=groups[gc.current()][0]
            with self.conn.cursor() as cur:
                cur.execute("SELECT student_id,concat_ws(' ',surname,name,third_name) FROM students WHERE group_id=%s ORDER BY surname,name",(gid,))
                students=cur.fetchall()
                if key=='Оценки':
                    cur.execute('SELECT discipline_id,name FROM disciplines ORDER BY name')
                else:
                    cur.execute('''SELECT l.lesson_id,concat(l.lesson_date,' ',l.lesson_time,' — ',d.name)
                                   FROM lessons l LEFT JOIN disciplines d ON d.discipline_id=l.discipline_id
                                   WHERE l.group_id=%s ORDER BY l.lesson_date DESC,l.lesson_time''',(gid,))
                options=cur.fetchall()
            sc['values']=[f'{i} — {n}' for i,n in students]
            dc['values']=[f'{i} — {n}' for i,n in options]
            if students:
                sc.current(next((i for i,r in enumerate(students) if r[0]==existing.get('student_id')),0))
            if options:
                target=existing.get('discipline_id' if key=='Оценки' else 'lesson_id')
                dc.current(next((i for i,r in enumerate(options) if r[0]==target),0))
        gc.bind('<<ComboboxSelected>>',group_changed)
        with self.conn.cursor() as cur:
            cur.execute('SELECT group_id FROM students WHERE student_id=%s',(existing.get('student_id'),))
            found=cur.fetchone()
        target_gid=found[0] if found else (groups[0][0] if groups else None)
        if target_gid is not None:
            gc.current(next((i for i,g in enumerate(groups) if g[0]==target_gid),0))
            group_changed()
        def save():
            try:
                if sc.current()<0 or dc.current()<0:
                    raise ValueError('Выберите ученика и дисциплину/занятие')
                sid=students[sc.current()][0]
                did=options[dc.current()][0]
                day=date.fromisoformat(date_entry.get().strip())
                value=int(vc.get()) if key=='Оценки' else vc.get()
                if key=='Оценки' and value not in range(1,6):
                    raise ValueError('Оценка от 1 до 5')
                if key=='Посещаемость':
                    with self.conn.cursor() as cur:
                        cur.execute('SELECT lesson_date FROM lessons WHERE lesson_id=%s',(did,))
                        lesson_day=cur.fetchone()[0]
                    if day!=lesson_day:
                        raise ValueError('Дата посещения должна совпадать с датой выбранного занятия')
                cols=['student_id','discipline_id','grade_date','value'] if key=='Оценки' else ['student_id','lesson_id','attendance_date','mark']
                vals=[sid,did,day,value]
                with self.conn:
                    with self.conn.cursor() as cur:
                        if operation=='add':
                            cur.execute(sql.SQL('INSERT INTO {} ({}) VALUES ({})').format(sql.Identifier(table),
                                sql.SQL(',').join(map(sql.Identifier,cols)),sql.SQL(',').join(sql.Placeholder() for _ in cols)),vals)
                        else:
                            cur.execute(sql.SQL('UPDATE {} SET {} WHERE {}=%s').format(sql.Identifier(table),
                                sql.SQL(',').join(sql.SQL('{}=%s').format(sql.Identifier(c)) for c in cols),sql.Identifier(pk)),vals+[record_id])
                win.destroy()
                self.load_table()
            except Exception as exc:
                self.error('Ошибка сохранения',exc,win)
        ttk.Button(panel,text='Сохранить',command=save).pack(side='left',pady=20)
        ttk.Button(panel,text='Отмена',command=win.destroy).pack(side='left',padx=10,pady=20)

    def report_query(self,key):
        if key=='Нагрузка преподавателей':
            return """SELECT concat_ws(' ',e.surname,e.name,e.third_name) AS teacher_name,
                      string_agg(DISTINCT d.name,', ' ORDER BY d.name) AS discipline_name,
                      COUNT(l.lesson_id) AS lessons_count,COUNT(DISTINCT l.group_id) AS groups_count,
                      COALESCE(SUM(l.duration_hours),0) AS hours_count
                      FROM employees e LEFT JOIN lessons l ON l.teacher_id=e.employee_id
                      LEFT JOIN disciplines d ON d.discipline_id=l.discipline_id
                      WHERE EXISTS(SELECT 1 FROM roles r WHERE r.role_id=e.role_id AND r.name='Преподаватель')
                      GROUP BY e.employee_id ORDER BY e.surname,e.name"""
        if key=='Список кураторов':
            return """SELECT concat_ws(' ',e.surname,e.name,e.third_name) AS curator_name,
                      g.name AS group_name,d.name AS discipline_name,d.classroom
                      FROM curators c LEFT JOIN employees e ON e.employee_id=c.employee_id
                      LEFT JOIN groups g ON g.group_id=c.group_id
                      LEFT JOIN disciplines d ON d.discipline_id=c.discipline_id ORDER BY g.name"""
        return super().report_query(key)

    def open_report(self,key):
        super().open_report(key)
        if not self.allowed(key):
            return
        # Добавляем фильтры для всех отчётов, где присутствуют соответствующие столбцы.
        top=self.tree.master.master
        controls=tk.Frame(top,bg=BG)
        controls.pack(before=self.tree.master,fill='x',pady=(0,8))
        self.report_filters={}
        for col,title in [('group_name','Группа'),('discipline_name','Дисциплина'),('student_name','Ученик')]:
            if col not in self.columns:
                continue
            tk.Label(controls,text=title+':',bg=BG).pack(side='left',padx=5)
            idx=self.columns.index(col)
            opts=sorted({str(row[idx]) for row in self.all_rows if row[idx] is not None})
            cb=ttk.Combobox(controls,values=['Все']+opts,state='readonly',width=22)
            cb.set('Все')
            cb.pack(side='left',padx=4)
            cb.bind('<<ComboboxSelected>>',lambda _e:self.filter_report())
            self.report_filters[col]=cb

    def filter_report(self):
        rows=list(self.all_rows)
        for col,cb in self.report_filters.items():
            if cb.get()!='Все' and col in self.columns:
                idx=self.columns.index(col)
                rows=[r for r in rows if str(r[idx])==cb.get()]
        self.visible_rows=rows
        self.render_rows(rows)

    def export_report(self):
        # Экспортируем выбранную выборку, а не все скрытые фильтром строки.
        all_rows=self.all_rows
        self.all_rows=getattr(self,'visible_rows',self.all_rows)
        try:
            super().export_report()
        finally:
            self.all_rows=all_rows


# ==========================================================
# Версия 4: вход без отдельного окна БД, расписание на неделю,
# безопасная работа с существующими данными.
# ==========================================================
import os
import calendar

class SchoolV4(CompleteSchoolApp):
    def __init__(self, root):
        # Не запускаем старое окно подключения.
        self.root = root
        self.root.title("АИС художественной школы")
        self.root.geometry("1250x750")
        self.root.minsize(940, 580)
        self.root.configure(bg=BG)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.conn = None
        self.employee = None
        self.current_key = None
        self.tree = None
        self.all_rows = []
        self.visible_rows = []
        self.columns = []
        self.status = tk.StringVar(value="")
        self.setup_style()
        self.root.after(30, self.start)

    def start(self):
        # Пароль БД задаётся в переменной окружения ART_SCHOOL_DB_PASSWORD.
        # Не отображаем отдельный диалог и не сохраняем пароль в коде.
        try:
            self.conn = psycopg2.connect(
                dbname=os.getenv("ART_SCHOOL_DB_NAME", "art_school"),
                user=os.getenv("ART_SCHOOL_DB_USER", "postgres"),
                password=os.getenv("ART_SCHOOL_DB_PASSWORD", "1"),
                host=os.getenv("ART_SCHOOL_DB_HOST", "localhost"),
                port=os.getenv("ART_SCHOOL_DB_PORT", "5432"),
                connect_timeout=5,
            )
            self.prepare_database()
            self.show_login()
        except Exception as exc:
            self.error("Ошибка подключения к базе данных", exc)
            self.clear()
            tk.Label(self.root, text="Не удалось подключиться к PostgreSQL",
                     bg=BG, fg=NAVY, font=("Arial", 16, "bold")).pack(pady=35)
            tk.Label(self.root, text="Укажите пароль в переменной окружения "
                     "ART_SCHOOL_DB_PASSWORD и перезапустите программу.",
                     bg=BG, fg=NAVY).pack(pady=12)
            ttk.Button(self.root, text="Повторить подключение",
                       command=self.start).pack(pady=12)

    def prepare_database(self):
        # ВАЖНО: старые генераторы сотен случайных учеников НЕ вызываются.
        # Никакие ученики, оценки или оплаты автоматически не удаляются.
        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute("""CREATE TABLE IF NOT EXISTS weekly_schedule (
                    schedule_id SERIAL PRIMARY KEY,
                    group_id INTEGER NOT NULL REFERENCES groups(group_id),
                    weekday INTEGER NOT NULL CHECK (weekday BETWEEN 1 AND 7),
                    lesson_time TIME NOT NULL,
                    discipline_id INTEGER REFERENCES disciplines(discipline_id),
                    teacher_id INTEGER REFERENCES employees(employee_id),
                    classroom VARCHAR(100),
                    duration_hours NUMERIC(5,2) NOT NULL DEFAULT 2,
                    UNIQUE(group_id,weekday,lesson_time)
                )""")
                # Если расписания ещё нет, создаём для существующих групп
                # демонстрационный недельный план Пн–Сб.
                cur.execute("SELECT COUNT(*) FROM weekly_schedule")
                if cur.fetchone()[0] == 0:
                    cur.execute("SELECT group_id,teacher_id FROM groups ORDER BY group_id")
                    groups = cur.fetchall()
                    cur.execute("""SELECT discipline_id,teacher_id,classroom
                                   FROM disciplines ORDER BY name,discipline_id""")
                    disciplines = cur.fetchall()
                    if disciplines:
                        for gi, (gid, teacher) in enumerate(groups):
                            for weekday in range(1, 7):
                                did, assigned_teacher, room = disciplines[
                                    (gi * 3 + weekday - 1) % len(disciplines)]
                                cur.execute("""INSERT INTO weekly_schedule
                                    (group_id,weekday,lesson_time,discipline_id,
                                     teacher_id,classroom,duration_hours)
                                    VALUES (%s,%s,%s,%s,%s,%s,2)
                                    ON CONFLICT(group_id,weekday,lesson_time) DO NOTHING""",
                                    (gid,weekday,f"{9 + (gi % 4)*2:02d}:00",
                                     did,assigned_teacher or teacher,
                                     room or f"Аудитория {(gi % 12)+1}"))
                # Индивидуальные учётные записи для учеников, у которых их нет.
                cur.execute("SELECT student_id FROM students ORDER BY student_id")
                for (sid,) in cur.fetchall():
                    cur.execute("SELECT 1 FROM student_accounts WHERE student_id=%s", (sid,))
                    if not cur.fetchone():
                        login = f"student{sid}"
                        cur.execute("SELECT 1 FROM student_accounts WHERE login=%s", (login,))
                        if not cur.fetchone():
                            cur.execute("""INSERT INTO student_accounts
                                (student_id,login,password) VALUES (%s,%s,%s)""",
                                (sid,login,f"school{sid}"))
                # Отчёт о повторяющихся ФИО без рискованного удаления записей.
                cur.execute("""CREATE TABLE IF NOT EXISTS data_quality_notes (
                    note_id SERIAL PRIMARY KEY, category VARCHAR(100),
                    description TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""")

    def show_login(self):
        # Используем готовую форму с выбором «Сотрудник / Ученик»,
        # но без публичных подсказок с паролями.
        ExtendedSchoolApp.show_login(self)
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, tk.Label) and "Демо:" in child.cget("text"):
                        child.destroy()

    def show_main(self):
        super().show_main()
        if self.employee:
            name = self.employee[2]
            patronymic = self.employee[3] or ""
            tk.Label(self.root,
                     text=f"{name} {patronymic}, добро пожаловать!",
                     font=("Arial", 12, "bold"), fg=NAVY, bg=BG).pack(
                         side="bottom", pady=6)

    def section_query(self, key):
        if key == "Расписание":
            return """SELECT
                CASE w.weekday
                    WHEN 1 THEN 'Понедельник' WHEN 2 THEN 'Вторник'
                    WHEN 3 THEN 'Среда' WHEN 4 THEN 'Четверг'
                    WHEN 5 THEN 'Пятница' WHEN 6 THEN 'Суббота'
                    ELSE 'Воскресенье' END AS weekday,
                w.lesson_time, g.name AS group_name,
                d.name AS discipline_name,
                concat_ws(' ',e.surname,e.name,e.third_name) AS teacher_name,
                w.classroom,w.duration_hours
                FROM weekly_schedule w
                JOIN groups g ON g.group_id=w.group_id
                LEFT JOIN disciplines d ON d.discipline_id=w.discipline_id
                LEFT JOIN employees e ON e.employee_id=w.teacher_id
                ORDER BY w.weekday,w.lesson_time,g.name"""
        return super().section_query(key)

    def open_section(self, key):
        super().open_section(key)
        if key == "Расписание" and getattr(self,"tree",None):
            # Упорядоченные дни недели + фильтр, как и для других разделов.
            if "weekday" in self.columns:
                holder = self.tree.master.master
                if isinstance(holder, tk.Frame):
                    controls = next((x for x in holder.winfo_children()
                                     if isinstance(x, tk.Frame)
                                     and any(isinstance(c, ttk.Entry)
                                             for c in x.winfo_children())),None)
                    if controls:
                        tk.Label(controls,text="День недели:",bg=BG).pack(side="left",padx=4)
                        days = ["Все","Понедельник","Вторник","Среда",
                                "Четверг","Пятница","Суббота","Воскресенье"]
                        combo = ttk.Combobox(controls,state="readonly",values=days,width=16)
                        combo.current(0)
                        combo.pack(side="left",padx=3)
                        self.filters["weekday"] = combo
                        combo.bind("<<ComboboxSelected>>",lambda _e:self.apply_filters())

    def report_query(self,key):
        if key == "Нагрузка преподавателей":
            return """SELECT
                concat_ws(' ',e.surname,e.name,e.third_name) AS teacher_name,
                COALESCE(string_agg(DISTINCT d.name, ', ' ORDER BY d.name)
                         FILTER (WHERE d.name IS NOT NULL),'Не назначена') AS discipline_name,
                COUNT(DISTINCT w.group_id) AS groups_count,
                COUNT(w.schedule_id) AS lessons_count,
                COALESCE(SUM(w.duration_hours),0) AS hours_count
                FROM employees e JOIN roles r ON r.role_id=e.role_id
                LEFT JOIN weekly_schedule w ON w.teacher_id=e.employee_id
                LEFT JOIN disciplines d ON d.discipline_id=w.discipline_id
                WHERE r.name='Преподаватель'
                GROUP BY e.employee_id,e.surname,e.name,e.third_name
                ORDER BY e.surname,e.name"""
        return super().report_query(key)


LABELS.update({
    "weekday":"День недели","discipline_name":"Дисциплина",
    "lesson_time":"Время","duration_hours":"Часов",
    "hours_count":"Часов в неделю","lessons_count":"Занятий в неделю",
    "groups_count":"Групп","teacher_name":"Преподаватель",
    "group_name":"Группа","student_name":"Ученик",
})


# ==========================================================
# Исправление индивидуальной авторизации и приветствия
# ==========================================================
import secrets
import string
from collections import Counter

class SchoolV5(SchoolV4):
    def prepare_database(self):
        super().prepare_database()
        alphabet = string.ascii_letters + string.digits
        def password():
            return "".join(secrets.choice(alphabet) for _ in range(12))

        with self.conn:
            with self.conn.cursor() as cur:
                # В предыдущих версиях многим ученикам выдавался один пароль.
                # Обновляем только совпадающие пароли; существующие уникальные
                # пароли не меняем.
                cur.execute("""SELECT account_id, student_id, login, password
                               FROM student_accounts ORDER BY account_id""")
                accounts = cur.fetchall()
                counts = Counter(row[3] for row in accounts)
                used_logins = set()
                used_passwords = set()
                for aid, sid, login, pw in accounts:
                    if sid is None:
                        continue
                    new_login = login
                    if not new_login or new_login in used_logins or new_login == "demo_student":
                        new_login = f"student{sid}"
                        suffix = 2
                        while new_login in used_logins or any(
                            r[2] == new_login and r[0] != aid for r in accounts
                        ):
                            new_login = f"student{sid}_{suffix}"
                            suffix += 1
                    new_password = pw
                    if not pw or counts[pw] > 1 or pw in used_passwords or pw == "student123":
                        new_password = password()
                        while new_password in used_passwords:
                            new_password = password()
                    if new_login != login or new_password != pw:
                        cur.execute("""UPDATE student_accounts
                                       SET login=%s,password=%s WHERE account_id=%s""",
                                    (new_login,new_password,aid))
                    used_logins.add(new_login)
                    used_passwords.add(new_password)

                # Разные сотрудники также не должны иметь одинаковые пароли.
                cur.execute("""SELECT employee_id,login,password FROM employees
                               ORDER BY employee_id""")
                employees = cur.fetchall()
                counts = Counter(row[2] for row in employees)
                used_logins = set()
                used_passwords = set()
                for eid, login, pw in employees:
                    new_login = login
                    if not login or login in used_logins:
                        new_login = f"teacher{eid}"
                        suffix = 2
                        while new_login in used_logins or any(
                            r[1] == new_login and r[0] != eid for r in employees
                        ):
                            new_login = f"teacher{eid}_{suffix}"
                            suffix += 1
                    new_pw = pw
                    if (not pw or pw in used_passwords or
                        (counts[pw] > 1 and login != "admin")):
                        new_pw = password()
                        while new_pw in used_passwords:
                            new_pw = password()
                    if new_login != login or new_pw != pw:
                        cur.execute("""UPDATE employees SET login=%s,password=%s
                                       WHERE employee_id=%s""",(new_login,new_pw,eid))
                    used_logins.add(new_login)
                    used_passwords.add(new_pw)

    def show_login(self):
        # Прямой вызов базовой формы: без рекламируемых тестовых паролей.
        ExtendedSchoolApp.show_login(self)
        for widget in self.root.winfo_children():
            for child in widget.winfo_children():
                if isinstance(child, tk.Label) and "Демо:" in child.cget("text"):
                    child.destroy()
        self.root.unbind("<Return>")

    def show_main(self):
        # Не показываем "системы" из служебной записи администратора.
        # Используем реальное имя пользователя или роль для админа.
        CompleteSchoolApp.show_main(self)
        if self.employee:
            surname, name, patronymic = self.employee[1:4]
            role = self.employee[5]
            if role == "Администратор" and (
                (name or "").strip().lower() in ("системы","система","system")
            ):
                greeting = "Администратор, добро пожаловать!"
            else:
                greeting = f"{name or ''} {patronymic or ''}, добро пожаловать!".strip()
            tk.Label(self.root,text=greeting,bg=BG,fg=NAVY,
                     font=("Arial",13,"bold")).pack(side="bottom",pady=6)



# ==========================================================
# Исправленная авторизация: простые РАЗНЫЕ пароли, один раз.
# ==========================================================
class SchoolV6(SchoolV4):
    def prepare_database(self):
        SchoolV4.prepare_database(self)
        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute("""CREATE TABLE IF NOT EXISTS school_migrations
                               (migration_key VARCHAR(100) PRIMARY KEY)""")
                cur.execute("""SELECT 1 FROM school_migrations
                               WHERE migration_key='simple_accounts_v6'""")
                if cur.fetchone():
                    return
                # У каждого ученика один логин student<ID>, пароль u<ID>26.
                # Сохраняем все карточки и оценки, меняем только данные входа.
                cur.execute("SELECT student_id FROM students ORDER BY student_id")
                for (sid,) in cur.fetchall():
                    login, pw = f"student{sid}", f"u{sid}26"
                    cur.execute("""SELECT account_id FROM student_accounts
                                   WHERE student_id=%s ORDER BY account_id LIMIT 1""",(sid,))
                    row=cur.fetchone()
                    if row:
                        cur.execute("""UPDATE student_accounts SET login=%s,password=%s
                                       WHERE account_id=%s""",(login,pw,row[0]))
                        # Устаревшие дубли аккаунтов одного ученика отключаем
                        # без удаления: их логины не совпадают с рабочим.
                        cur.execute("""UPDATE student_accounts
                                       SET login='архив_'||account_id::text,
                                           password='отключено_'||account_id::text
                                       WHERE student_id=%s AND account_id<>%s""",(sid,row[0]))
                    else:
                        cur.execute("""INSERT INTO student_accounts
                                       (student_id,login,password) VALUES (%s,%s,%s)""",
                                    (sid,login,pw))
                # Администратор остаётся с текущим паролем.
                # Для каждого преподавателя простая индивидуальная комбинация.
                cur.execute("""SELECT e.employee_id,e.login,r.name
                               FROM employees e LEFT JOIN roles r ON r.role_id=e.role_id
                               ORDER BY e.employee_id""")
                for eid,login,role in cur.fetchall():
                    if role == "Администратор" or login == "admin":
                        continue
                    cur.execute("""UPDATE employees SET login=%s,password=%s
                                   WHERE employee_id=%s""",
                                (f"teacher{eid}",f"t{eid}26",eid))
                cur.execute("""INSERT INTO school_migrations(migration_key)
                               VALUES ('simple_accounts_v6')""")

    def show_login(self):
        # Не вызываем старую форму с общим тестовым паролем.
        ExtendedSchoolApp.show_login(self)
        for parent in self.root.winfo_children():
            for child in parent.winfo_children():
                if isinstance(child, tk.Label) and "Демо:" in child.cget("text"):
                    child.destroy()
        for child in self.root.winfo_children():
            if isinstance(child, tk.Label) and "Вход ученика:" in child.cget("text"):
                child.destroy()

    def show_main(self):
        # Сначала строим меню, затем выводим персональное приветствие.
        CompleteSchoolApp.show_main(self)
        if self.employee:
            _id,surname,name,patronymic,_role_id,role=self.employee
            if role == "Администратор" and (name or "").lower() in ("системы","система"):
                greeting="Администратор, добро пожаловать!"
            else:
                greeting=f"{name or ''} {patronymic or ''}, добро пожаловать!"
            tk.Label(self.root,text=greeting,fg=NAVY,bg=BG,
                     font=("Arial",13,"bold")).pack(side="bottom",pady=8)



class SchoolV7(SchoolV6):
    def prepare_database(self):
        # Не вызываем миграцию V6, в которой возможны конфликты логинов.
        SchoolV4.prepare_database(self)
        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute("""CREATE TABLE IF NOT EXISTS school_migrations
                    (migration_key VARCHAR(100) PRIMARY KEY)""")
                cur.execute("""SELECT 1 FROM school_migrations
                    WHERE migration_key='safe_accounts_v7'""")
                if cur.fetchone():
                    return
                # Двухэтапное переименование: сначала освобождаем ВСЕ старые
                # логины, затем назначаем новые. Это устраняет конфликты UNIQUE.
                cur.execute("SELECT account_id,student_id FROM student_accounts ORDER BY account_id")
                accounts=cur.fetchall()
                cur.execute("SELECT employee_id,login FROM employees ORDER BY employee_id")
                employees=cur.fetchall()
                import uuid
                token=uuid.uuid4().hex[:12]
                for aid,sid in accounts:
                    cur.execute("UPDATE student_accounts SET login=%s WHERE account_id=%s",
                                (f'_migration_{token}_{aid}',aid))
                for eid,login in employees:
                    if login != 'admin':
                        cur.execute("UPDATE employees SET login=%s WHERE employee_id=%s",
                                    (f'_migration_{token}_{eid}',eid))
                # Если у ученика несколько аккаунтов, только первый активен.
                primary={}
                for aid,sid in accounts:
                    if sid is not None and sid not in primary:
                        primary[sid]=aid
                for aid,sid in accounts:
                    if sid is not None and primary.get(sid)==aid:
                        login,pw=f'student{sid}',f'u{sid}26'
                    else:
                        login,pw=f'archive{aid}',f'disabled{aid}'
                    cur.execute("""UPDATE student_accounts SET login=%s,password=%s
                                   WHERE account_id=%s""",(login,pw,aid))
                cur.execute("SELECT student_id FROM students ORDER BY student_id")
                for (sid,) in cur.fetchall():
                    if sid not in primary:
                        cur.execute("""INSERT INTO student_accounts(student_id,login,password)
                                       VALUES (%s,%s,%s)""",(sid,f'student{sid}',f'u{sid}26'))
                for eid,login in employees:
                    if login=='admin':
                        continue
                    cur.execute("""UPDATE employees SET login=%s,password=%s
                                   WHERE employee_id=%s""",(f'teacher{eid}',f't{eid}26',eid))
                cur.execute("""INSERT INTO school_migrations(migration_key)
                               VALUES ('safe_accounts_v7') ON CONFLICT DO NOTHING""")



class SchoolV8(SchoolV4):
    """Однократная выдача проверяемых индивидуальных учётных данных."""
    def prepare_database(self):
        SchoolV4.prepare_database(self)
        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute("""CREATE TABLE IF NOT EXISTS school_migrations
                               (migration_key VARCHAR(100) PRIMARY KEY)""")
                cur.execute("""SELECT 1 FROM school_migrations
                               WHERE migration_key='working_login_v8'""")
                if cur.fetchone():
                    return
                # Сначала освобождаем ВСЕ логины учеников, не трогая связанные данные.
                cur.execute("SELECT account_id,student_id FROM student_accounts ORDER BY account_id")
                accounts = cur.fetchall()
                import uuid
                token = uuid.uuid4().hex
                for aid, sid in accounts:
                    cur.execute("UPDATE student_accounts SET login=%s WHERE account_id=%s",
                                (f'_tmp_v8_{token}_{aid}', aid))
                first = {}
                for aid, sid in accounts:
                    if sid is not None and sid not in first:
                        first[sid] = aid
                for aid, sid in accounts:
                    if sid is not None and first.get(sid) == aid:
                        login, password = f'student{sid}', f'u{sid}26'
                    else:
                        login, password = f'archive{aid}', f'blocked{aid}'
                    cur.execute("""UPDATE student_accounts SET login=%s,password=%s
                                   WHERE account_id=%s""", (login, password, aid))
                cur.execute('SELECT student_id FROM students ORDER BY student_id')
                for (sid,) in cur.fetchall():
                    if sid not in first:
                        cur.execute("""INSERT INTO student_accounts(student_id,login,password)
                                       VALUES (%s,%s,%s)""",
                                    (sid, f'student{sid}', f'u{sid}26'))
                # Преподавателей перенумеровываем без конфликта уникальности.
                cur.execute("""SELECT e.employee_id,e.login,COALESCE(r.name,'')
                               FROM employees e LEFT JOIN roles r ON r.role_id=e.role_id
                               ORDER BY e.employee_id""")
                employees = cur.fetchall()
                for eid, login, role in employees:
                    if login != 'admin' and role != 'Администратор':
                        cur.execute('UPDATE employees SET login=%s WHERE employee_id=%s',
                                    (f'_tmp_v8_{token}_{eid}', eid))
                for eid, login, role in employees:
                    if login != 'admin' and role != 'Администратор':
                        cur.execute('UPDATE employees SET login=%s,password=%s WHERE employee_id=%s',
                                    (f'teacher{eid}', f't{eid}26', eid))
                # Проверяем реальные пары через ТОТ ЖЕ SQL, что использует окно входа.
                cur.execute("""SELECT COUNT(*) FROM student_accounts a
                               JOIN students s ON s.student_id=a.student_id
                               WHERE a.login='student'||s.student_id::text
                                 AND a.password='u'||s.student_id::text||'26'""")
                valid_students = cur.fetchone()[0]
                cur.execute('SELECT COUNT(*) FROM students')
                total_students = cur.fetchone()[0]
                if valid_students != total_students:
                    raise RuntimeError(f'Проверка входа учеников: {valid_students} из {total_students}. '
                                       'Изменения отменены, обратитесь к администратору БД.')
                cur.execute("""INSERT INTO school_migrations(migration_key)
                               VALUES ('working_login_v8')""")

    def show_login(self):
        self.clear()
        card = tk.Frame(self.root,bg=WHITE,padx=45,pady=30,
                        highlightbackground='#D7DFEC',highlightthickness=1)
        card.place(relx=.5,rely=.5,anchor='center')
        tk.Label(card,text='ХУДОЖЕСТВЕННАЯ ШКОЛА',bg=WHITE,fg=NAVY,
                 font=('Arial',20,'bold')).pack(pady=(0,18))
        tk.Label(card,text='Тип входа',bg=WHITE,fg=NAVY).pack(anchor='w')
        kind=ttk.Combobox(card,values=['Ученик','Сотрудник'],state='readonly',width=34)
        kind.set('Ученик');kind.pack(pady=(4,12))
        tk.Label(card,text='Логин',bg=WHITE,fg=NAVY).pack(anchor='w')
        username=ttk.Entry(card,width=37);username.pack(pady=(4,12),ipady=4)
        tk.Label(card,text='Пароль',bg=WHITE,fg=NAVY).pack(anchor='w')
        password=ttk.Entry(card,width=37,show='*');password.pack(pady=(4,15),ipady=4)
        def login():
            user=username.get().strip()
            pw=password.get().strip()
            if not user or not pw:
                messagebox.showwarning('Вход','Введите логин и пароль.',parent=self.root)
                return
            try:
                with self.conn.cursor() as cur:
                    if kind.get()=='Ученик':
                        cur.execute("""SELECT s.student_id,s.surname,s.name,s.third_name,
                                              NULL,'Ученик'
                                       FROM student_accounts a JOIN students s
                                         ON s.student_id=a.student_id
                                       WHERE a.login=%s AND a.password=%s
                                       LIMIT 1""",(user,pw))
                    else:
                        cur.execute("""SELECT e.employee_id,e.surname,e.name,e.third_name,
                                              e.role_id,r.name FROM employees e
                                       LEFT JOIN roles r ON r.role_id=e.role_id
                                       WHERE e.login=%s AND e.password=%s
                                       LIMIT 1""",(user,pw))
                    account=cur.fetchone()
                if account is None:
                    messagebox.showerror('Вход','Неверный логин или пароль. Проверьте тип входа.\n'
                                         'Ученики: student<номер ID> / u<номер ID>26.\n'
                                         'Преподаватели: teacher<номер ID> / t<номер ID>26.',
                                         parent=self.root)
                    return
                self.employee=account
                self.root.unbind('<Return>')
                self.show_main()
            except Exception as exc:
                self.error('Ошибка авторизации',exc)
        ttk.Button(card,text='ВОЙТИ',command=login).pack(fill='x')
        tk.Label(card,text='Используйте данные из раздела «Доступ учеников»\n'
                 'или «Сотрудники» у администратора.',bg=WHITE,fg=MUTED,
                 font=('Arial',9)).pack(pady=(14,0))
        username.focus_set()
        self.root.bind('<Return>',lambda event:login())

    def show_main(self):
        CompleteSchoolApp.show_main(self)
        if self.employee:
            _,surname,name,patronymic,_,role=self.employee
            if role=='Администратор' and (name or '').strip().lower() in ('система','системы'):
                greeting='Администратор, добро пожаловать!'
            else:
                greeting=f'{name or ""} {patronymic or ""}, добро пожаловать!'
            tk.Label(self.root,text=greeting,bg=BG,fg=NAVY,
                     font=('Arial',12,'bold')).pack(side='bottom',pady=6)


def main():
    root=tk.Tk()
    SchoolV8(root)
    root.mainloop()

if __name__=='__main__':
    main()
