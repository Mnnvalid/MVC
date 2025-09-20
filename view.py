import tkinter as tk
from tkinter import ttk,messagebox

class View:

    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.root.title("ระบบลงทะเบียนเรียน")
        self.root.geometry("600x600")

        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def create_login_page(self):
        self.clear_main_frame()
        
        login_frame = ttk.Frame(self.main_frame, padding="20")
        login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        ttk.Label(login_frame, text="ระบบลงทะเบียนเรียน", font=("Helvetica", 16)).pack(pady=10)

        ttk.Label(login_frame, text="Username:").pack(pady=5)
        username_entry = ttk.Entry(login_frame, width=30)
        username_entry.pack()
        username_entry.insert(0, "admin")


        ttk.Label(login_frame, text="Password:").pack(pady=5)
        password_entry = ttk.Entry(login_frame, show="*", width=30)
        password_entry.pack()
        password_entry.insert(0, "123")
        
        login_button = ttk.Button(
            login_frame,
            text="Login",
            command=lambda: self.controller.handle_login(username_entry.get(), password_entry.get())
        )
        login_button.pack(pady=20)

    def create_admin_dashboard(self, students):
        self.clear_main_frame()
        admin = ttk.Frame(self.main_frame, padding="10")
        admin.pack(fill=tk.BOTH, expand=True)
        ttk.Label(admin, text="Admin Dashboard", font=("Helvetica", 16)).pack(pady=10)
        bar = ttk.Frame(admin)
        bar.pack(fill=tk.X, pady=5)
        self._adm_search = tk.StringVar()
        ttk.Entry(bar, textvariable=self._adm_search, width=30).pack(side=tk.LEFT, padx=4)
        schools = sorted({s['school'] for s in students})
        self._adm_school = tk.StringVar(value="(ทั้งหมด)")
        school_cb = ttk.Combobox(bar, textvariable=self._adm_school, values=["(ทั้งหมด)"]+schools, state="readonly", width=24)
        school_cb.pack(side=tk.LEFT, padx=4)
        ttk.Button(bar, text="ค้นหา/กรอง", command=lambda: refresh()).pack(side=tk.LEFT, padx=4)
        ttk.Button(bar, text="กรอกเกรดรายวิชา", command=self.controller.show_grade_page).pack(side=tk.LEFT, padx=10)
        cols = ("student_id", "full_name", "school")
        tree = ttk.Treeview(admin, columns=cols, show="headings")
        tree.heading("student_id", text="รหัสนักเรียน", command=lambda: sort_by("student_id"))
        tree.heading("full_name", text="ชื่อ-สกุล", command=lambda: sort_by("full_name"))
        tree.heading("school", text="โรงเรียน", command=lambda: sort_by("school"))
        tree.column("student_id", width=120, anchor="w")
        tree.column("full_name", width=300, anchor="w")
        tree.column("school", width=240, anchor="w")
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._adm_all = [{"student_id": s["student_id"], "full_name": f"{s['title']}{s['first_name']} {s['last_name']}", "school": s["school"]} for s in students]
        _sort = {"key": "student_id", "reverse": False}
        def set_rows(rows):
            tree.delete(*tree.get_children())
            for r in rows:
                tree.insert("", tk.END, values=(r["student_id"], r["full_name"], r["school"]))
        def refresh():
            q = self._adm_search.get().strip().lower()
            sc = self._adm_school.get()
            rows = [r for r in self._adm_all if (q in r["student_id"].lower() or q in r["full_name"].lower() or q in r["school"].lower()) and (sc == "(ทั้งหมด)" or r["school"] == sc)]
            rows.sort(key=lambda x: x[_sort["key"]], reverse=_sort["reverse"])
            set_rows(rows)
        def sort_by(key):
            if _sort["key"] == key:
                _sort["reverse"] = not _sort["reverse"]
            else:
                _sort["key"], _sort["reverse"] = key, False
            refresh()
        def on_dbl(_evt):
            sel = tree.selection()
            if sel:
                sid = tree.item(sel[0], "values")[0]
                self.controller.open_student_profile(sid)
        tree.bind("<Double-1>", on_dbl)
        refresh()

    def create_grade_subject_picker(self, subjects):
        self.clear_main_frame()
        f = ttk.Frame(self.main_frame, padding="10")
        f.pack(fill=tk.BOTH, expand=True)
        ttk.Label(f, text="เลือกวิชาสำหรับกรอกเกรด", font=("Helvetica", 16)).pack(pady=10)
        var = tk.StringVar()
        pairs = [(s['subject_id'], f"{s['subject_id']} - {s['name']}") for s in subjects]
        cb = ttk.Combobox(f, textvariable=var, values=[p[1] for p in pairs], state="readonly", width=60)
        cb.pack(pady=10)
        def go_next():
            idx = cb.current()
            if idx < 0:
                self.show_error("ข้อผิดพลาด", "กรุณาเลือกวิชา")
                return
            self.controller.show_grade_page(subject_id=pairs[idx][0])
        ttk.Button(f, text="ถัดไป", command=go_next).pack(pady=5)

    def create_grade_page(self, subject_id, rows, total):
        self.clear_main_frame()
        f = ttk.Frame(self.main_frame, padding="10")
        f.pack(fill=tk.BOTH, expand=True)
        ttk.Label(f, text=f"กรอกเกรดสำหรับวิชา {subject_id}", font=("Helvetica", 16)).pack(pady=10)
        ttk.Label(f, text=f"จำนวนผู้ลงทะเบียน: {total} คน").pack(pady=5)
        form = ttk.Frame(f)
        form.pack(fill=tk.BOTH, expand=True, pady=10)
        inputs = []
        for r in rows:
            rowf = ttk.Frame(form)
            rowf.pack(fill=tk.X, pady=2)
            ttk.Label(rowf, text=f"{r['student_id']} - {r['full_name']}", width=50).pack(side=tk.LEFT)
            v = tk.StringVar(value=r.get('grade') or "")
            cb = ttk.Combobox(rowf, textvariable=v, values=["A","B+","B","C+","C","D+","D","F"], width=5, state="readonly")
            cb.pack(side=tk.LEFT)
            inputs.append((r['student_id'], v))
        def on_save():
            updates = [(sid, var.get()) for sid, var in inputs]
            self.controller.handle_grade_save(subject_id, updates)
        btns = ttk.Frame(f)
        btns.pack(pady=10)
        ttk.Button(btns, text="บันทึกเกรด", command=on_save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btns, text="กลับ", command=self.controller.show_admin_dashboard).pack(side=tk.LEFT, padx=5)



    def show_message(self, title, text):
        messagebox.showinfo(title, text)

    def show_error(self, title, text):
        messagebox.showerror(title, text)

    def create_student_dashboard(self, student_info, registered_subjects_details):
        self.clear_main_frame()
        rootf = ttk.Frame(self.main_frame, padding="10")
        rootf.pack(fill=tk.BOTH, expand=True)

        ttk.Label(rootf, text=f"Student Dashboard", font=("Helvetica", 16)).pack(pady=6)
        ttk.Label(rootf, text=f"{student_info['title']}{student_info['first_name']} {student_info['last_name']}  |  รหัส {student_info['student_id']}").pack(pady=2)

        cols = ("subject_id", "name", "credits", "grade")
        tree = ttk.Treeview(rootf, columns=cols, show="headings", height=12)
        tree.heading("subject_id", text="รหัสวิชา")
        tree.heading("name", text="ชื่อวิชา")
        tree.heading("credits", text="หน่วยกิต")
        tree.heading("grade", text="เกรด")
        tree.column("subject_id", width=110, anchor="w")
        tree.column("name", width=280, anchor="w")
        tree.column("credits", width=80, anchor="center")
        tree.column("grade", width=80, anchor="center")
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for s in registered_subjects_details:
            tree.insert("", tk.END, values=(s["subject_id"], s["name"], s["credits"], s.get("grade") or ""))

        btns = ttk.Frame(rootf)
        btns.pack(pady=6)
        ttk.Button(btns, text="ลงทะเบียนวิชา", command=self.controller.show_registration_page).pack(side=tk.LEFT, padx=5)
        ttk.Button(btns, text="ออกจากระบบ", command=self.controller.handle_logout).pack(side=tk.LEFT, padx=5)

    def create_registration_window(self, available_subjects):
        self.clear_main_frame()
        f = ttk.Frame(self.main_frame, padding="10")
        f.pack(fill=tk.BOTH, expand=True)

        ttk.Label(f, text="ลงทะเบียนวิชา", font=("Helvetica", 16)).pack(pady=8)

        cols = ("subject_id", "name", "credits")
        tree = ttk.Treeview(f, columns=cols, show="headings", height=12)
        tree.heading("subject_id", text="รหัสวิชา")
        tree.heading("name", text="ชื่อวิชา")
        tree.heading("credits", text="หน่วยกิต")
        tree.column("subject_id", width=120, anchor="w")
        tree.column("name", width=340, anchor="w")
        tree.column("credits", width=80, anchor="center")
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for s in available_subjects:
            tree.insert("", tk.END, values=(s["subject_id"], s["name"], s["credits"]))

        def confirm_register():
            sel = tree.selection()
            if not sel:
                self.show_error("ข้อผิดพลาด", "กรุณาเลือกวิชา")
                return
            sid = tree.item(sel[0], "values")[0]
            sub = next((x for x in available_subjects if x["subject_id"] == sid), None)
            if not sub:
                self.show_error("ข้อผิดพลาด", "ไม่พบข้อมูลวิชา")
                return
            self.controller.handle_registration_selection(sub)

        btns = ttk.Frame(f)
        btns.pack(pady=6)
        ttk.Button(btns, text="ยืนยันลงทะเบียน", command=confirm_register).pack(side=tk.LEFT, padx=5)
        ttk.Button(btns, text="กลับ", command=self.controller.show_student_dashboard).pack(side=tk.LEFT, padx=5)
