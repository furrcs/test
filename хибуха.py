import psycopg2
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

DB_PARAMS = {
    'dbname': 'school',
    'user': 'postgres',
    'password': '1234567890',
    'host': 'localhost',
    'port': '5432'
}

def connect_db():
    try:
        return psycopg2.connect(**DB_PARAMS)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Подключение:\n{e}")
        return None

def execute_query(q, p=None):
    conn = connect_db()
    if not conn:
        return []
    cur = None
    try:
        cur = conn.cursor()
        cur.execute(q, p or ())
        return cur.fetchall()
    except Exception as e:
        messagebox.showerror("Ошибка", f"{e}")
        return []
    finally:
        if cur:
            cur.close()
        conn.close()

def execute_update(q, p=None):
    conn = connect_db()
    if not conn:
        return False
    cur = None
    try:
        cur = conn.cursor()
        cur.execute(q, p or ())
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Ошибка", f"{e}")
        return False
    finally:
        if cur:
            cur.close()
        conn.close()

def sync_sequence(table, pk):
    conn = connect_db()
    if not conn:
        return
    cur = None
    try:
        cur = conn.cursor()
        cur.execute("SELECT pg_get_serial_sequence(%s, %s)", (table, pk))
        seq = cur.fetchone()
        if seq and seq[0]:
            cur.execute(
                f'SELECT setval(%s, COALESCE((SELECT MAX("{pk}") FROM "{table}"), 1), true)',
                (seq[0],)
            )
        conn.commit()
    except Exception:
        pass
    finally:
        if cur:
            cur.close()
        conn.close()


def sync_all():
    for t, meta in tables.items():
        sync_sequence(t, meta[0][0])

def get_id_by_name(table, name_col, name_val, pk_col="id"):
    if not name_val:
        return None
    q = f'SELECT "{pk_col}" FROM "{table}" WHERE "{name_col}" = %s'
    r = execute_query(q, (name_val,))
    return r[0][0] if r else None

def get_name_by_id(table, pk_col, name_col, id_val):
    if not id_val:
        return ""
    q = f'SELECT "{name_col}" FROM "{table}" WHERE "{pk_col}" = %s'
    r = execute_query(q, (id_val,))
    return r[0][0] if r else str(id_val)

def get_teaching_label(tid):
    r = execute_query('''
        SELECT t.last_name, s.name, c.name
        FROM teachings te
        JOIN teachers t ON t.teacher_id = te.teacher_id
        JOIN subjects s ON s.subject_id = te.subject_id
        JOIN classes c ON c.class_id = te.class_id
        WHERE te.teaching_id = %s
    ''', (tid,))
    return f"{r[0][0]} - {r[0][1]} - {r[0][2]}" if r else str(tid)

tables = {
    "classes": (
        ["class_id", "name"],
        ["ID", "Класс"],
        ["students", "schedule"]
    ),
    "subjects": (
        ["subject_id", "name"],
        ["ID", "Предмет"],
        ["teachings", "schedule"]
    ),
    "teachers": (
        ["teacher_id", "last_name", "first_name", "middle_name", "phone", "email"],
        ["ID", "Фамилия", "Имя", "Отчество", "Телефон", "Почта"],
        ["teachings", "schedule"]
    ),
    "students": (
        ["student_id", "last_name", "first_name", "middle_name",
         "birth_date", "phone", "email", "class_id"],
        ["ID", "Фамилия", "Имя", "Отчество", "Дата рожд.", "Телефон", "Почта", "Класс"],
        ["grades", "classes"]
    ),
    "teachings": (
        ["teaching_id", "teacher_id", "subject_id", "class_id"],
        ["ID", "Учитель", "Предмет", "Класс"],
        ["grades"]
    ),
    "lessons": (
        ["lesson_number", "start_time", "end_time"],
        ["Номер", "Начало", "Окончание"],
        ["schedule"]
    ),
    "schedule": (
        ["schedule_id", "class_id", "subject_id", "teacher_id",
         "week_day", "lesson_number"],
        ["ID", "Класс", "Предмет", "Учитель", "День", "Урок"],
        ["classes", "subjects", "teachers", "lessons"]
    ),
    "grades": (
        ["grade_id", "student_id", "teaching_id", "grade", "grade_date"],
        ["ID", "Ученик", "Преподавание", "Оценка", "Дата"],
        ["students", "teachings"]
    ),
}

SECTION_TITLES = {
    "classes":   "Классы",
    "subjects":  "Предметы",
    "teachers":  "Учителя",
    "students":  "Ученики",
    "teachings": "Преподавание",
    "lessons":   "Уроки",
    "schedule":  "Расписание",
    "grades":    "Оценки",
}

def create_table(frame, phys_cols, disp_cols, table_name, related=None):
    col_ids = [f"c{i}" for i in range(len(disp_cols))]

    tree = ttk.Treeview(frame, columns=col_ids, show="headings")
    for cid, name in zip(col_ids, disp_cols):
        tree.heading(cid, text=name)
        tree.column(cid, width=140, anchor="w")
    tree.pack(fill=BOTH, expand=1)

    sb = ttk.Scrollbar(frame, command=tree.yview)
    sb.pack(side=RIGHT, fill=Y)
    tree.configure(yscrollcommand=sb.set)

    # ---------- Загрузка данных ----------
    def load():
        tree.delete(*tree.get_children())
        cols = ', '.join(f'"{c}"' for c in phys_cols)
        data = execute_query(
            f'SELECT {cols} FROM "{table_name}" ORDER BY "{phys_cols[0]}"'
        )
        for row in data:
            r = list(row)
            # Подмена внешних ключей на читаемые значения
            if table_name == "students":
                r[7] = get_name_by_id("classes", "class_id", "name", row[7])
            elif table_name == "teachings":
                r[1] = get_name_by_id("teachers", "teacher_id", "last_name", row[1])
                r[2] = get_name_by_id("subjects", "subject_id", "name", row[2])
                r[3] = get_name_by_id("classes", "class_id", "name", row[3])
            elif table_name == "schedule":
                r[1] = get_name_by_id("classes", "class_id", "name", row[1])
                r[2] = get_name_by_id("subjects", "subject_id", "name", row[2])
                r[3] = get_name_by_id("teachers", "teacher_id", "last_name", row[3])
            elif table_name == "grades":
                r[1] = get_name_by_id("students", "student_id", "last_name", row[1])
                r[2] = get_teaching_label(row[2])
            tree.insert("", "end", values=r)

    load()

    # ---------- Поля ввода ----------
    f = ttk.Frame(frame)
    f.pack(pady=10)
    entries = {}
    for i, name in enumerate(disp_cols[1:]):
        ttk.Label(f, text=name).grid(row=0, column=i, padx=5)
        e = ttk.Entry(f, width=18)
        e.grid(row=1, column=i, padx=5)
        entries[name] = e

    # ---------- Добавление записи ----------
    def add():
        vals = [e.get().strip() for e in entries.values()]
        if not all(vals):
            messagebox.showwarning("", "Заполните все поля!")
            return

        ins = []
        for i, (p_col, d_col) in enumerate(zip(phys_cols[1:], disp_cols[1:])):
            val = vals[i]

            # --- Разрешение внешних ключей по названию ---
            if table_name == "students" and d_col == "Класс":
                id_val = get_id_by_name("classes", "name", val, "class_id")
                if id_val is None:
                    messagebox.showerror("", f"Класс '{val}' не найден!")
                    return
                ins.append(id_val)
            elif table_name == "teachings" and d_col == "Учитель":
                id_val = get_id_by_name("teachers", "last_name", val, "teacher_id")
                if id_val is None:
                    messagebox.showerror("", f"Учитель '{val}' не найден!")
                    return
                ins.append(id_val)
            elif table_name == "teachings" and d_col == "Предмет":
                id_val = get_id_by_name("subjects", "name", val, "subject_id")
                if id_val is None:
                    messagebox.showerror("", f"Предмет '{val}' не найден!")
                    return
                ins.append(id_val)
            elif table_name == "teachings" and d_col == "Класс":
                id_val = get_id_by_name("classes", "name", val, "class_id")
                if id_val is None:
                    messagebox.showerror("", f"Класс '{val}' не найден!")
                    return
                ins.append(id_val)
            elif table_name == "schedule" and d_col == "Класс":
                id_val = get_id_by_name("classes", "name", val, "class_id")
                if id_val is None:
                    messagebox.showerror("", f"Класс '{val}' не найден!")
                    return
                ins.append(id_val)
            elif table_name == "schedule" and d_col == "Предмет":
                id_val = get_id_by_name("subjects", "name", val, "subject_id")
                if id_val is None:
                    messagebox.showerror("", f"Предмет '{val}' не найден!")
                    return
                ins.append(id_val)
            elif table_name == "schedule" and d_col == "Учитель":
                id_val = get_id_by_name("teachers", "last_name", val, "teacher_id")
                if id_val is None:
                    messagebox.showerror("", f"Учитель '{val}' не найден!")
                    return
                ins.append(id_val)
            elif table_name == "schedule" and d_col == "Урок":
                # Проверка существования урока в справочнике lessons
                r = execute_query(
                    'SELECT 1 FROM "lessons" WHERE "lesson_number" = %s', (val,)
                )
                if not r:
                    messagebox.showerror("", f"Урок №{val} не найден!")
                    return
                ins.append(int(val))
            elif table_name == "grades" and d_col == "Ученик":
                id_val = get_id_by_name("students", "last_name", val, "student_id")
                if id_val is None:
                    messagebox.showerror("", f"Ученик '{val}' не найден!")
                    return
                ins.append(id_val)
            elif table_name == "grades" and d_col == "Преподавание":
                id_val = get_id_by_name("teachings", "teaching_id", val, "teaching_id")
                if id_val is None:
                    messagebox.showerror("", f"Преподавание '{val}' не найдено!")
                    return
                ins.append(id_val)
            else:
                # Числовые поля
                try:
                    if p_col in ("lesson_number", "week_day", "grade"):
                        ins.append(int(val))
                    else:
                        ins.append(val)
                except ValueError:
                    messagebox.showerror("", f"Неверный формат: {d_col}")
                    return

        # --- Вставка записи ---
        try:
            placeholders = ", ".join(["%s"] * len(ins))
            cols = ", ".join(f'"{c}"' for c in phys_cols[1:])
            q = f'INSERT INTO "{table_name}" ({cols}) VALUES ({placeholders})'
            if execute_update(q, tuple(ins)):
                load()
                for e in entries.values():
                    e.delete(0, END)
        except Exception as e:
            messagebox.showerror("", str(e))

    # ---------- Удаление записи ----------
    def delete():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("", "Выберите запись для удаления!")
            return
        pk_val = tree.item(sel[0])["values"][0]
        if not messagebox.askyesno("", "Удалить запись?"):
            return
        q = f'DELETE FROM "{table_name}" WHERE "{phys_cols[0]}" = %s'
        if execute_update(q, (pk_val,)):
            load()

    # ---------- Кнопки ----------
    btn_frame = ttk.Frame(frame)
    btn_frame.pack(pady=5)

    ttk.Button(btn_frame, text="Добавить", command=add).pack(side=LEFT, padx=5)
    ttk.Button(btn_frame, text="Удалить", command=delete).pack(side=LEFT, padx=5)

    # Кнопки перехода к связанным таблицам
    if related:
        for rel in related:
            if rel in tables:
                r_phys, r_disp, r_rel = tables[rel]
                ttk.Button(
                    btn_frame,
                    text=f"Открыть {SECTION_TITLES.get(rel, rel).lower()}",
                    command=lambda rp=r_phys, rd=r_disp, rn=rel, rr=r_rel:
                        create_table(Toplevel(frame), rp, rd, rn, rr)
                ).pack(side=LEFT, padx=5)



root = Tk()
root.title("Школа — Учёт")
root.geometry("700x650")

f = ttk.Frame(root, padding=30)
f.pack(fill=BOTH, expand=1)

ttk.Label(f, text="Выберите раздел:", font="Arial 14").pack(pady=20)

for table_name, (phys, disp, rel) in tables.items():
    ttk.Button(
        f,
        text=SECTION_TITLES.get(table_name, table_name),
        command=lambda p=phys, d=disp, n=table_name, r=rel:
            create_table(Toplevel(root), p, d, n, r)
    ).pack(pady=5, fill=X)

sync_all()
root.mainloop()