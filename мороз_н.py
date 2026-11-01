from __future__ import annotations
import configparser
import datetime as dt
import json
import os
import re
import tkinter as tk
from tkinter import ttk, messagebox

try:
    import psycopg2
    from psycopg2 import sql
except ImportError:
    psycopg2 = None
    sql = None

import hashlib
import os
import base64


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 310_000)
    return "pbkdf2_sha256$310000$%s$%s" % (
        base64.urlsafe_b64encode(salt).decode().rstrip("="),
        base64.urlsafe_b64encode(digest).decode().rstrip("="),
    )


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, iterations, salt_text, digest_text = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        pad = lambda value: value + "=" * (-len(value) % 4)
        salt = base64.urlsafe_b64decode(pad(salt_text))
        expected = base64.urlsafe_b64decode(pad(digest_text))
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, int(iterations))
        return actual == expected
    except (ValueError, TypeError):
        return False


DEFAULT_PASSWORDS = {
    "admin": "admin123",
    "manager": "manager123",
    "pto": "pto123",
    "omts": "omts123",
    "garage": "garage123",
    "client1": "client123",
}


APP_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(APP_DIR, "config.ini")

TABLES = {
    "departments": ("Отделы", [("name","Название","text"),("description","Описание","text")]),
    "employees": ("Сотрудники", [("last_name","Фамилия","text"),("first_name","Имя","text"),("middle_name","Отчество","text"),("title","Должность","text"),("hire_date","Дата приёма (ГГГГ-ММ-ДД)","date"),("salary","Оклад","decimal"),("department_id","ID отдела","int"),("phone","Телефон","phone"),("email","Email","email"),("is_active","Активен (true/false)","bool")]),
    "clients": ("Клиенты", [("company_name","Компания","text"),("contact_name","Контактное лицо","text"),("phone","Телефон","phone"),("email","Email","email"),("address","Адрес","text"),("city","Город","text"),("country","Страна","text")]),
    "suppliers": ("Поставщики", [("company_name","Компания","text"),("contact_name","Контактное лицо","text"),("phone","Телефон","phone"),("email","Email","email"),("address","Адрес","text"),("country","Страна","text")]),
    "materials": ("Материалы", [("material_name","Материал","text"),("unit","Единица измерения","text"),("unit_price","Цена за единицу","decimal"),("stock_quantity","Остаток","decimal"),("min_stock","Минимальный остаток","decimal")]),
    "projects": ("Проекты", [("project_name","Название проекта","text"),("start_date","Дата начала (ГГГГ-ММ-ДД)","date"),("end_date","Дата окончания (ГГГГ-ММ-ДД)","date_optional"),("status","Статус","project_status"),("manager_id","ID менеджера","int_optional")]),
    "construction_objects": ("Объекты строительства", [("address","Адрес","text"),("city","Город","text"),("object_type","Тип объекта","text"),("area","Площадь, м²","decimal"),("floors","Этажность","int"),("project_id","ID проекта","int")]),
    "contracts": ("Договоры", [("contract_number","Номер договора","text"),("contract_date","Дата договора (ГГГГ-ММ-ДД)","date"),("total_amount","Сумма договора","decimal"),("client_id","ID клиента","int"),("project_id","ID проекта","int"),("status","Статус","contract_status")]),
    "project_employees": ("Сотрудники проектов", [("project_id","ID проекта","int"),("employee_id","ID сотрудника","int"),("role","Роль на проекте","text")]),
    "supplies": ("Поставки", [("project_id","ID проекта","int"),("material_id","ID материала","int"),("supplier_id","ID поставщика","int_optional"),("supply_date","Дата поставки (ГГГГ-ММ-ДД)","date"),("quantity","Количество","decimal"),("price","Стоимость","decimal"),("status","Статус","supply_status")]),
    "orders": ("Заказы материалов", [("order_number","Номер заказа","text"),("project_id","ID проекта","int"),("material_id","ID материала","int"),("supplier_id","ID поставщика","int"),("quantity","Количество","decimal"),("unit","Единица измерения","text"),("unit_price","Цена за единицу","decimal"),("order_date","Дата заказа (ГГГГ-ММ-ДД)","date"),("planned_delivery_date","Плановая дата доставки (ГГГГ-ММ-ДД)","date"),("status","Статус","order_status"),("comment","Комментарий","text_optional")]),
    "vehicles": ("Транспорт", [("plate_number","Госномер","text"),("vehicle_type","Тип транспорта","text"),("brand","Марка","text"),("capacity_tons","Грузоподъёмность, т","decimal"),("status","Статус","vehicle_status")]),
    "drivers": ("Водители", [("employee_id","ID сотрудника","int"),("license_number","Номер водительского удостоверения","text"),("phone","Телефон","phone"),("status","Статус","driver_status")]),
    "deliveries": ("Доставки", [("delivery_number","Номер доставки","text"),("order_id","ID заказа","int"),("vehicle_id","ID транспорта","int_optional"),("driver_id","ID водителя","int_optional"),("from_address","Откуда","text"),("to_address","Куда","text"),("planned_date","Дата доставки (ГГГГ-ММ-ДД)","date"),("planned_time","Время (ЧЧ:ММ)","time"),("actual_date","Фактическая дата (ГГГГ-ММ-ДД)","date_optional"),("status","Статус","delivery_status"),("comment","Комментарий","text_optional")]),
    "routes": ("Маршруты", [("delivery_id","ID доставки","int"),("sequence_no","Порядок остановки","int"),("address","Адрес остановки","text"),("planned_arrival","Плановое время (ЧЧ:ММ)","time_optional"),("status","Статус","route_status")]),
    "users": ("Пользователи", [("username","Логин","text"),("password_hash","Пароль (при создании обязателен)","password"),("role_name","Роль","role"),("employee_id","ID сотрудника","int_optional"),("client_id","ID клиента","int_optional"),("is_active","Активен (true/false)","bool")]),
    "user_logs": ("Журнал действий", [("user_id","ID пользователя","int_optional"),("action","Действие","text"),("entity_name","Таблица/объект","text_optional"),("entity_id","ID записи","int_optional"),("details","Подробности","text_optional")]),
}

ROLE_TABLES = {
    "Администратор": list(TABLES.keys()),
    "Менеджер": ["clients", "contracts", "projects", "construction_objects"],
    "Сотрудник ПТО": ["projects", "construction_objects", "project_employees", "employees"],
    "Сотрудник ОМТС": ["materials", "suppliers", "orders", "supplies", "projects"],
    "Диспетчер гаража": ["vehicles", "drivers", "deliveries", "routes", "orders"],
    "Клиент": ["contracts", "projects"],
}
READ_ONLY_ROLES = {"Клиент"}
CHOICES = {
    "project_status": ["Проектирование", "В работе", "Приостановлен", "Завершён"],
    "contract_status": ["Черновик", "Действует", "Исполнен", "Расторгнут"],
    "supply_status": ["Ожидается", "В пути", "Получена", "Частично получена", "Отменена"],
    "order_status": ["Создан", "Согласован", "Заказан", "В пути", "Доставлен", "Отменён"],
    "vehicle_status": ["Свободен", "Назначен", "В рейсе", "На обслуживании"],
    "driver_status": ["Доступен", "Назначен", "В рейсе", "Недоступен"],
    "delivery_status": ["Запланирована", "Назначен транспорт", "В пути", "Доставлена", "Отменена"],
    "route_status": ["Ожидает", "Пройден", "Пропущен"],
    "role": ["Администратор", "Менеджер", "Сотрудник ПТО", "Сотрудник ОМТС", "Диспетчер гаража", "Клиент"],
}






class Database:
    def __init__(self):
        if psycopg2 is None:
            raise RuntimeError("Не установлен psycopg2-binary. Выполните: python -m pip install -r requirements.txt")
        self.conn = psycopg2.connect(host="localhost", port="5432", database="construction_company", user="postgres", password="1234567890")
        self.conn.autocommit = False
        self.prepare_seed_users()

    def prepare_seed_users(self):
        with self.conn.cursor() as cur:
            cur.execute("SELECT username, password_hash FROM users WHERE username = ANY(%s)", (list(DEFAULT_PASSWORDS),))
            rows = cur.fetchall()
            for username, stored in rows:
                if stored == "RESET_ON_FIRST_LOGIN":
                    cur.execute("UPDATE users SET password_hash=%s WHERE username=%s", (hash_password(DEFAULT_PASSWORDS[username]), username))
        self.conn.commit()

    def log(self, user_id, action, entity=None, entity_id=None, details=None):
        try:
            with self.conn.cursor() as cur:
                cur.execute("INSERT INTO user_logs(user_id, action, entity_name, entity_id, details) VALUES (%s,%s,%s,%s,%s)", (user_id, action, entity, entity_id, details))
            self.conn.commit()
        except Exception:
            self.conn.rollback()

    def close(self):
        self.conn.close()


def validate_value(value, kind, label):
    value = value.strip() if isinstance(value, str) else value
    if kind in ("text", "date", "decimal", "int", "phone", "email", "bool", "project_status", "contract_status", "supply_status", "order_status", "vehicle_status", "driver_status", "delivery_status", "route_status", "role", "password") and value == "":
        raise ValueError(f"Поле «{label}» обязательно для заполнения.")
    if kind in ("text_optional", "date_optional", "int_optional", "time_optional") and value == "":
        return None
    if kind == "text_optional":
        return value or None
    if kind == "password":
        return hash_password(value)
    if kind in ("text", "phone", "email", "project_status", "contract_status", "supply_status", "order_status", "vehicle_status", "driver_status", "delivery_status", "route_status", "role"):
        if kind == "phone" and not re.fullmatch(r"[+()\d\-\s]{6,30}", value):
            raise ValueError(f"Поле «{label}»: проверьте формат телефона.")
        if kind == "email" and value and not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
            raise ValueError(f"Поле «{label}»: укажите корректный email.")
        if kind in CHOICES and value not in CHOICES[kind]:
            raise ValueError(f"Выберите допустимое значение для поля «{label}».")
        return value or None
    if kind in ("date", "date_optional"):
        try:
            return dt.date.fromisoformat(value)
        except ValueError:
            raise ValueError(f"Поле «{label}»: дата должна быть в формате ГГГГ-ММ-ДД.")
    if kind in ("time", "time_optional"):
        try:
            return dt.time.fromisoformat(value)
        except ValueError:
            raise ValueError(f"Поле «{label}»: время должно быть в формате ЧЧ:ММ.")
    if kind in ("int", "int_optional"):
        try:
            number = int(value)
        except (ValueError, TypeError):
            raise ValueError(f"Поле «{label}» должно содержать целое число.")
        if number < 1 and kind == "int":
            raise ValueError(f"Поле «{label}» должно быть положительным числом.")
        return number
    if kind == "decimal":
        try:
            number = float(value.replace(",", "."))
        except (ValueError, AttributeError):
            raise ValueError(f"Поле «{label}» должно содержать число.")
        if number < 0:
            raise ValueError(f"Поле «{label}» не может быть отрицательным.")
        return number
    if kind == "bool":
        low = value.lower()
        if low in ("true", "да", "1", "yes"):
            return True
        if low in ("false", "нет", "0", "no"):
            return False
        raise ValueError(f"Поле «{label}»: введите true/false или да/нет.")
    return value


class MainWindow(tk.Tk):
    def __init__(self, db, user):
        super().__init__()
        self.db, self.user = db, user
        self.title(f"АИС строительной компании — {user['role']}")
        self.geometry("1240x760")
        self.minsize(1000, 620)
        self.protocol("WM_DELETE_WINDOW", self.close_app)
        self.current_table = None
        self.current_rows = []
        self._build()
        self.show_dashboard()

    def _build(self):
        top = ttk.Frame(self, padding=(12, 10))
        top.pack(fill="x")
        ttk.Label(top, text="АИС СТРОИТЕЛЬНОЙ КОМПАНИИ", font=("Segoe UI", 16, "bold")).pack(side="left")
        ttk.Label(top, text=f"{self.user['username']}  |  {self.user['role']}").pack(side="right", padx=10)
        ttk.Button(top, text="Закрыть", command=self.close_app).pack(side="right")
        body = ttk.Frame(self)
        body.pack(fill="both", expand=True, padx=10, pady=(0,10))
        self.sidebar = ttk.Frame(body, width=225, padding=8)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        ttk.Button(self.sidebar, text="Главная", command=self.show_dashboard).pack(fill="x", pady=3)
        ttk.Separator(self.sidebar).pack(fill="x", pady=7)
        for table in TABLES.keys():
            label = TABLES[table][0]
            ttk.Button(self.sidebar, text=label, command=lambda t=table: self.show_table(t)).pack(fill="x", pady=2)
        self.content = ttk.Frame(body, padding=10)
        self.content.pack(side="left", fill="both", expand=True)

    def clear_content(self):
        for child in self.content.winfo_children():
            child.destroy()

    def show_dashboard(self):
        self.current_table = None
        self.clear_content()
        ttk.Label(self.content, text="Главная панель", font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(0,12))
        ttk.Label(self.content, text="Сводная информация по строительным проектам, снабжению и доставкам.").pack(anchor="w", pady=(0,15))
        cards = ttk.Frame(self.content)
        cards.pack(fill="x")
        metrics = [("Клиенты","SELECT COUNT(*) FROM clients"),("Договоры","SELECT COUNT(*) FROM contracts"),("Проекты","SELECT COUNT(*) FROM projects"),("Заказы","SELECT COUNT(*) FROM orders"),("Доставки","SELECT COUNT(*) FROM deliveries"),("Материалы","SELECT COUNT(*) FROM materials")]
        for i, (label, query) in enumerate(metrics):
            value = "—"
            try:
                with self.db.conn.cursor() as cur:
                    cur.execute(query)
                    value = str(cur.fetchone()[0])
                self.db.conn.commit()
            except Exception:
                self.db.conn.rollback()
            card = ttk.LabelFrame(cards, text=label, padding=18)
            card.grid(row=i//3, column=i%3, padx=8, pady=8, sticky="nsew")
            ttk.Label(card, text=value, font=("Segoe UI", 22, "bold")).pack()
        for col in range(3): cards.columnconfigure(col, weight=1)
        ttk.Label(self.content, text="Режим администратора: доступны все разделы системы.", foreground="#555").pack(anchor="w", pady=18)
        if self.user["role"] == "Администратор":
            ttk.Button(self.content, text="Открыть журнал действий", command=lambda: self.show_table("user_logs")).pack(anchor="w")

    def show_table(self, table):
        self.current_table = table
        self.clear_content()
        title, fields = TABLES[table]
        heading = ttk.Frame(self.content)
        heading.pack(fill="x", pady=(0,8))
        ttk.Label(heading, text=title, font=("Segoe UI", 17, "bold")).pack(side="left")
        ttk.Button(heading, text="Обновить", command=lambda: self.refresh_table(table)).pack(side="right", padx=3)
        searchrow = ttk.Frame(self.content)
        searchrow.pack(fill="x", pady=(0,8))
        ttk.Label(searchrow, text="Поиск по отображаемым данным:").pack(side="left")
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(searchrow, textvariable=self.search_var, width=35)
        search_entry.pack(side="left", padx=8)
        ttk.Button(searchrow, text="Найти", command=lambda: self.refresh_table(table, self.search_var.get().strip())).pack(side="left")
        columns = ["id"] + [f[0] for f in fields if not (table == "users" and f[0] == "password_hash")]
        self.tree = ttk.Treeview(self.content, columns=columns, show="headings", selectmode="browse")
        for col in columns:
            if col == "id": label = "ID"
            else: label = next((x[1] for x in fields if x[0] == col), col)
            self.tree.heading(col, text=label)
            self.tree.column(col, width=115 if col != "id" else 55, minwidth=50, stretch=True)
        yscroll = ttk.Scrollbar(self.content, orient="vertical", command=self.tree.yview)
        xscroll = ttk.Scrollbar(self.content, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        self.tree.pack(fill="both", expand=True, side="top")
        xscroll.pack(fill="x")
        yscroll.place(relx=1.0, rely=0.28, relheight=0.6, anchor="ne")
        buttons = ttk.Frame(self.content)
        buttons.pack(fill="x", pady=10)
        read_only = self.user["role"] in READ_ONLY_ROLES or table == "user_logs"
        if not read_only:
            ttk.Button(buttons, text="Добавить", command=lambda: self.open_form(table)).pack(side="left", padx=3)
            ttk.Button(buttons, text="Изменить выбранную", command=lambda: self.edit_selected(table)).pack(side="left", padx=3)
            ttk.Button(buttons, text="Удалить выбранную", command=lambda: self.delete_selected(table)).pack(side="left", padx=3)
        ttk.Label(buttons, text="Для связей указывайте ID связанных записей.", foreground="#666").pack(side="right")
        self.refresh_table(table)

    def refresh_table(self, table, search=""):
        if table != self.current_table or not hasattr(self, "tree"):
            return
        for item in self.tree.get_children(): self.tree.delete(item)
        fields = TABLES[table][1]
        columns = ["id"] + [f[0] for f in fields if not (table == "users" and f[0] == "password_hash")]
        try:
            where = ""
            params = []
            if table == "contracts" and self.user["role"] == "Клиент":
                where = " WHERE client_id=%s"
                params.append(self.user["client_id"])
            elif table == "projects" and self.user["role"] == "Клиент":
                where = " WHERE id IN (SELECT project_id FROM contracts WHERE client_id=%s)"
                params.append(self.user["client_id"])
            if search:
                searchable = [c for c in columns if c != "id" and c != "password_hash"]
                if searchable:
                    condition = " OR ".join(f"CAST({c} AS TEXT) ILIKE %s" for c in searchable)
                    where += (" AND " if where else " WHERE ") + "(" + condition + ")"
                    params.extend([f"%{search}%"] * len(searchable))
            query = sql.SQL("SELECT {} FROM {}{} ORDER BY id DESC LIMIT 1000").format(
                sql.SQL(", ").join(map(sql.Identifier, columns)), sql.Identifier(table), sql.SQL(where)
            )
            with self.db.conn.cursor() as cur:
                cur.execute(query, params)
                rows = cur.fetchall()
            self.db.conn.commit()
            self.current_rows = rows
            for row in rows:
                values = ["" if v is None else str(v) for v in row]
                self.tree.insert("", "end", values=values)
        except Exception as exc:
            self.db.conn.rollback()
            messagebox.showerror("Ошибка чтения", str(exc))

    def selected_id(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Выбор записи", "Сначала выберите запись в таблице.")
            return None
        return int(self.tree.item(selected[0], "values")[0])

    def edit_selected(self, table):
        record_id = self.selected_id()
        if record_id is None: return
        fields = TABLES[table][1]
        columns = [f[0] for f in fields]
        try:
            with self.db.conn.cursor() as cur:
                cur.execute(sql.SQL("SELECT {} FROM {} WHERE id=%s").format(sql.SQL(", ").join(map(sql.Identifier, columns)), sql.Identifier(table)), (record_id,))
                row = cur.fetchone()
            self.db.conn.commit()
            if row is None:
                messagebox.showerror("Запись не найдена", "Обновите таблицу и попробуйте ещё раз.")
                return
            initial = dict(zip(columns, row))
            if table == "users": initial["password_hash"] = ""
            self.open_form(table, record_id, initial)
        except Exception as exc:
            self.db.conn.rollback()
            messagebox.showerror("Ошибка", str(exc))

    def open_form(self, table, record_id=None, initial=None):
        title, fields = TABLES[table]
        form = tk.Toplevel(self)
        form.title(("Изменение: " if record_id else "Добавление: ") + title.lower())
        form.geometry("600x700")
        form.minsize(500, 420)
        form.transient(self)
        form.grab_set()
        outer = ttk.Frame(form, padding=14)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text=("Изменение записи" if record_id else "Новая запись"), font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0,10))
        canvas = tk.Canvas(outer, highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        inner = ttk.Frame(canvas)
        inner.bind("<Configure>", lambda _e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        controls = {}
        for i, (col, label, kind) in enumerate(fields):
            ttk.Label(inner, text=label).grid(row=i, column=0, sticky="w", padx=(0,12), pady=5)
            if kind in CHOICES:
                control = ttk.Combobox(inner, values=CHOICES[kind], state="readonly", width=38)
            elif kind == "bool":
                control = ttk.Combobox(inner, values=["true", "false"], state="readonly", width=38)
            else:
                control = ttk.Entry(inner, width=42, show="●" if kind == "password" else "")
            value = (initial or {}).get(col)
            if value is not None:
                if kind == "bool": value = "true" if value else "false"
                elif isinstance(value, (dt.date, dt.time)): value = value.isoformat()
                elif kind == "password": value = ""
                else: value = str(value)
                control.insert(0, value) if isinstance(control, ttk.Entry) else control.set(value)
            elif kind in ("date", "date_optional") and not record_id:
                if kind == "date": control.insert(0, dt.date.today().isoformat())
            elif kind in ("time", "time_optional") and not record_id:
                if kind == "time": control.insert(0, "10:00")
            elif kind == "bool" and not record_id:
                control.set("true")
            controls[col] = control
            control.grid(row=i, column=1, sticky="ew", pady=5)
        inner.columnconfigure(1, weight=1)
        ttk.Label(outer, text="Даты: ГГГГ-ММ-ДД. Время: ЧЧ:ММ. Для связи используйте ID записи.", foreground="#555").pack(anchor="w", pady=8)
        footer = ttk.Frame(outer)
        footer.pack(fill="x", pady=(4,0))

        def save():
            try:
                values = {}
                for col, label, kind in fields:
                    raw = controls[col].get()
                    if kind == "password" and record_id and raw.strip() == "":
                        continue
                    values[col] = validate_value(raw, kind, label)
                if table == "projects":
                    start = values.get("start_date")
                    end = values.get("end_date")
                    if start and end and end < start:
                        raise ValueError("Дата окончания проекта не может быть раньше даты начала.")
                if table == "deliveries" and values.get("planned_date") and values.get("actual_date") and values["actual_date"] < values["planned_date"]:
                    # Фактическая дата может быть раньше плановой только при изменении графика; предупредим, но не блокируем.
                    if not messagebox.askyesno("Проверка даты", "Фактическая дата раньше плановой. Всё равно сохранить?"):
                        return
                with self.db.conn.cursor() as cur:
                    if record_id:
                        assignments = sql.SQL(", ").join(sql.SQL("{}=%s").format(sql.Identifier(c)) for c in values)
                        cur.execute(sql.SQL("UPDATE {} SET {} WHERE id=%s").format(sql.Identifier(table), assignments), list(values.values()) + [record_id])
                        action = "Изменение записи"
                    else:
                        cols = list(values)
                        cur.execute(sql.SQL("INSERT INTO {} ({}) VALUES ({}) RETURNING id").format(sql.Identifier(table), sql.SQL(", ").join(map(sql.Identifier, cols)), sql.SQL(", ").join(sql.Placeholder() for _ in cols)), list(values.values()))
                        record_id_new = cur.fetchone()[0]
                        record_id = record_id_new
                        action = "Добавление записи"
                self.db.conn.commit()
                self.db.log(self.user["id"], action, table, record_id, f"{TABLES[table][0]}: запись ID {record_id}")
                form.destroy()
                self.refresh_table(table, self.search_var.get().strip() if hasattr(self, "search_var") else "")
                messagebox.showinfo("Готово", "Данные успешно сохранены.")
            except Exception as exc:
                self.db.conn.rollback()
                messagebox.showerror("Не удалось сохранить", f"Проверьте значения полей и связи с другими записями.\n\n{exc}")
        ttk.Button(footer, text="Сохранить", command=save).pack(side="left", padx=(0,8))
        ttk.Button(footer, text="Отмена", command=form.destroy).pack(side="left")

    def delete_selected(self, table):
        record_id = self.selected_id()
        if record_id is None: return
        if not messagebox.askyesno("Подтверждение удаления", f"Удалить запись ID {record_id}?\nЕсли на неё ссылаются другие записи, база запретит удаление."):
            return
        try:
            with self.db.conn.cursor() as cur:
                cur.execute(sql.SQL("DELETE FROM {} WHERE id=%s").format(sql.Identifier(table)), (record_id,))
            self.db.conn.commit()
            self.db.log(self.user["id"], "Удаление записи", table, record_id, f"Удалена запись ID {record_id}")
            self.refresh_table(table)
            messagebox.showinfo("Готово", "Запись удалена.")
        except Exception as exc:
            self.db.conn.rollback()
            messagebox.showerror("Удаление невозможно", f"Запись может использоваться в других таблицах.\n\n{exc}")

    def close_app(self):
        try:
            self.db.log(self.user.get("id"), "Закрытие приложения", "users", self.user.get("id"), "Приложение закрыто без авторизации")
        except Exception:
            pass
        try:
            self.db.conn.close()
        except Exception:
            pass
        self.destroy()


if __name__ == "__main__":
    try:
        database = Database()
        # Авторизация отключена: приложение открывается сразу в режиме администратора.
        admin_user = {"id": None, "username": "admin", "role": "Администратор", "employee_id": None, "client_id": None}
        MainWindow(database, admin_user).mainloop()
    except Exception as exc:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Ошибка запуска",
            "Не удалось подключиться к PostgreSQL или открыть приложение.\n\n"
            f"{exc}\n\nПроверьте config.ini и убедитесь, что database.sql выполнен в нужной базе."
        )
        root.destroy()
