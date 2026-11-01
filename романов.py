import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "dbname": "furniture",
    "user": "postgres",
    "password": "1234567890"
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("АИС Мебельного комбината")
        self.root.geometry("1100x700")
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        self.tabs = {}
        self.create_client_tab()
        self.create_employee_tab()
        self.create_supplier_tab()
        self.create_material_tab()
        self.create_supply_tab()
        self.create_product_tab()
        self.create_order_tab()

    def execute_query(self, query, params=None, fetch=True):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(query, params or ())
        if fetch:
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description]
        else:
            conn.commit()
            rows, cols = None, None
        cur.close()
        conn.close()
        return rows, cols

    def build_crud_tab(self, title, table, columns, column_names,
                       insert_fields, update_fields):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=title)
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill="both", expand=True, padx=5, pady=5)
        tree = ttk.Treeview(tree_frame, columns=columns,
                            show="headings", height=20)
        for col, name in zip(columns, column_names):
            tree.heading(col, text=name)
            tree.column(col, width=130, anchor="w")
        scroll = ttk.Scrollbar(tree_frame, orient="vertical",
                               command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", padx=5, pady=5)

        def load():
            for i in tree.get_children():
                tree.delete(i)
            rows, _ = self.execute_query(
                f"SELECT {','.join(columns)} FROM {table} ORDER BY 1")
            for r in rows:
                tree.insert("", "end", values=r)

        def get_selected():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Внимание", "Выберите запись")
                return None
            return tree.item(sel[0])["values"]

        def add():
            self.field_dialog(
                f"Добавление: {title}", insert_fields,
                lambda vals: self._insert(table, insert_fields, vals, load))

        def edit():
            vals = get_selected()
            if vals is None:
                return
            initial = dict(zip([f[0] for f in update_fields], vals[1:]))
            self.field_dialog(
                f"Изменение: {title}", update_fields,
                lambda new: self._update(table, columns[0], vals[0],
                                         update_fields, new, load),
                initial=initial)

        def delete():
            vals = get_selected()
            if vals is None:
                return
            if not messagebox.askyesno("Подтверждение",
                                       "Удалить запись?"):
                return
            try:
                self.execute_query(
                    f"DELETE FROM {table} WHERE {columns[0]} = %s",
                    (vals[0],), fetch=False)
                load()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        ttk.Button(btn_frame, text="Добавить",
                   command=add).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Изменить",
                   command=edit).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Удалить",
                   command=delete).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Обновить",
                   command=load).pack(side="left", padx=2)
        load()
        self.tabs[title] = {"tree": tree, "load": load}

    def _insert(self, table, fields, vals, callback):
        names = [f[0] for f in fields]
        placeholders = ",".join(["%s"] * len(names))
        try:
            self.execute_query(
                f"INSERT INTO {table} ({','.join(names)}) "
                f"VALUES ({placeholders})",
                [v for _, v in vals], fetch=False)
            callback()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _update(self, table, pk_col, pk_val, fields, vals, callback):
        sets = ",".join([f"{f[0]}=%s" for f in fields])
        try:
            self.execute_query(
                f"UPDATE {table} SET {sets} WHERE {pk_col}=%s",
                [v for _, v in vals] + [pk_val], fetch=False)
            callback()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def field_dialog(self, title, fields, on_ok, initial=None):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("400x350")
        entries = {}
        for i, (fname, label) in enumerate(fields):
            ttk.Label(win, text=label).grid(
                row=i, column=0, padx=5, pady=3, sticky="e")
            e = ttk.Entry(win, width=30)
            e.grid(row=i, column=1, padx=5, pady=3)
            if initial and fname in initial:
                e.insert(0, str(initial[fname]))
            entries[fname] = e

        def ok():
            vals = [(k, entries[k].get()) for k, _ in fields]
            win.destroy()
            on_ok(vals)

        ttk.Button(win, text="OK", command=ok).grid(
            row=len(fields), column=0, columnspan=2, pady=10)

    def create_client_tab(self):
        self.build_crud_tab(
            "Клиенты", "client",
            ["client_id", "last_name", "first_name", "middle_name",
             "phone", "email"],
            ["ID", "Фамилия", "Имя", "Отчество", "Телефон", "Почта"],
            [("last_name", "Фамилия"), ("first_name", "Имя"),
             ("middle_name", "Отчество"), ("phone", "Телефон"),
             ("email", "Почта")],
            [("last_name", "Фамилия"), ("first_name", "Имя"),
             ("middle_name", "Отчество"), ("phone", "Телефон"),
             ("email", "Почта")])

    def create_employee_tab(self):
        self.build_crud_tab(
            "Сотрудники", "employee",
            ["employee_id", "last_name", "first_name", "middle_name",
             "position", "phone", "email"],
            ["ID", "Фамилия", "Имя", "Отчество", "Должность",
             "Телефон", "Почта"],
            [("last_name", "Фамилия"), ("first_name", "Имя"),
             ("middle_name", "Отчество"),
             ("position", "Должность (товаровед/менеджер/технолог)"),
             ("phone", "Телефон"), ("email", "Почта")],
            [("last_name", "Фамилия"), ("first_name", "Имя"),
             ("middle_name", "Отчество"), ("position", "Должность"),
             ("phone", "Телефон"), ("email", "Почта")])

    def create_supplier_tab(self):
        self.build_crud_tab(
            "Поставщики", "supplier",
            ["supplier_id", "company_name", "phone", "address", "email"],
            ["ID", "Компания", "Телефон", "Адрес", "Почта"],
            [("company_name", "Название"), ("phone", "Телефон"),
             ("address", "Адрес"), ("email", "Почта")],
            [("company_name", "Название"), ("phone", "Телефон"),
             ("address", "Адрес"), ("email", "Почта")])

    def create_material_tab(self):
        self.build_crud_tab(
            "Материалы", "material",
            ["material_id", "supplier_id", "name", "material_type",
             "unit", "price"],
            ["ID", "Поставщик", "Название", "Тип", "Ед. изм.", "Цена"],
            [("supplier_id", "ID поставщика"), ("name", "Название"),
             ("material_type", "Тип"), ("unit", "Ед. изм."),
             ("price", "Цена")],
            [("supplier_id", "ID поставщика"), ("name", "Название"),
             ("material_type", "Тип"), ("unit", "Ед. изм."),
             ("price", "Цена")])

    def create_supply_tab(self):
        self.build_crud_tab(
            "Поставки", "supply",
            ["supply_id", "supplier_id", "supply_date"],
            ["ID", "Поставщик", "Дата"],
            [("supplier_id", "ID поставщика"),
             ("supply_date", "Дата (ГГГГ-ММ-ДД)")],
            [("supplier_id", "ID поставщика"), ("supply_date", "Дата")])

    def create_product_tab(self):
        self.build_crud_tab(
            "Продукция", "product",
            ["product_id", "name", "furniture_type", "price"],
            ["ID", "Название", "Тип мебели", "Цена"],
            [("name", "Название"), ("furniture_type", "Тип мебели"),
             ("price", "Цена")],
            [("name", "Название"), ("furniture_type", "Тип мебели"),
             ("price", "Цена")])

    def create_order_tab(self):
        self.build_crud_tab(
            "Заказы", "orders",
            ["order_id", "client_id", "employee_id", "order_date",
             "due_date", "status", "total_cost"],
            ["ID", "Клиент", "Сотрудник", "Дата заказа",
             "Дата выполнения", "Статус", "Стоимость"],
            [("client_id", "ID клиента"), ("employee_id", "ID сотрудника"),
             ("order_date", "Дата заказа"),
             ("due_date", "Дата выполнения"),
             ("status", "Статус (новый/в_работе/выполнен/отменён)"),
             ("total_cost", "Стоимость")],
            [("client_id", "ID клиента"), ("employee_id", "ID сотрудника"),
             ("order_date", "Дата заказа"),
             ("due_date", "Дата выполнения"), ("status", "Статус"),
             ("total_cost", "Стоимость")])

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()