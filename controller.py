from datetime import datetime
from model import Database
from view import View

class Controller:
    def __init__(self, root):
        self.db = Database()
        self.view = View(root, self)
        self.current_user = None
        
        self.view.create_login_page()

    def handle_login(self, username, password):
        users = self.db.get_table('users')
        for user in users:
            if user['username'] == username and user['password'] == password:
                self.current_user = user
                
                if self.current_user['role'] == 'admin':
                    self.show_admin_dashboard()
                elif self.current_user['role'] == 'student':
                    self.show_student_dashboard()
                return
            
        self.view.show_error("Login Failed", "Username หรือ Password ไม่ถูกต้อง!")

    def handle_logout(self):
        "ออกจากระบบ"
        self.current_user = None
        self.view.create_login_page()

    def show_admin_dashboard(self):
        "หน้าจอหลักของ Admin"
        all_students = self.db.get_table('students')
        self.view.create_admin_dashboard(all_students)

    def show_student_dashboard(self):
        "หน้าจอหลักของนักเรียน"
        student_id = self.current_user['username']
        student_info = next((s for s in self.db.get_table('students') if s['student_id'] == student_id), None)
        
        if not student_info:
            self.view.show_error("Error", "ไม่พบข้อมูลนักเรียน")
            self.handle_logout()
            return
        
        all_registered = self.db.get_table('registered_subjects')
        student_registered_ids = [r for r in all_registered if r['student_id'] == student_id]
        
        all_subjects = self.db.get_table('subjects')

        registered_subjects_details = []
        for reg in student_registered_ids:
            subject_detail = next((s for s in all_subjects if s['subject_id'] == reg['subject_id']), None)
            if subject_detail:
                registered_subjects_details.append({
                    **subject_detail,
                    'grade': reg['grade']
                })
        
        self.view.create_student_dashboard(student_info, registered_subjects_details)

    def show_registration_page(self):
    
        student_id = self.current_user['username']
        student_info = next((s for s in self.db.get_table('students') if s['student_id'] == student_id), None)

        age = self.calculate_age(student_info['birth_date'])
        if age < 15:
            self.view.show_error("ลงทะเบียนไม่ได้", "อายุของคุณไม่ถึง 15 ปี")
            return

        program_id = student_info['program_id']
        all_subjects = self.db.get_table('subjects')
        all_registered = self.db.get_table('registered_subjects')
        structure = self.db.get_table('subject_structure')

        program_subjects_ids = [s['subject_id'] for s in structure if s['program_id'] == program_id]
        student_registered_ids = [r['subject_id'] for r in all_registered if r['student_id'] == student_id]
        unregistered_ids = [sid for sid in program_subjects_ids if sid not in student_registered_ids]
        
        available_subjects = []
        for subject_id in unregistered_ids:
            subject_detail = next((s for s in all_subjects if s['subject_id'] == subject_id), None)
            if not subject_detail: continue

        
            prereq_key = 'prerequisite_id' if 'prerequisite_id' in subject_detail else 'รหัสวิชาบังคับก่อน'
            prerequisite_id = subject_detail.get(prereq_key)
            if prerequisite_id:
                prereq_reg = next(
                    (r for r in all_registered
                    if r['student_id'] == student_id and r['subject_id'] == prerequisite_id), 
                    None
                )
                if not prereq_reg or prereq_reg.get('grade'):
                    continue
            
            available_subjects.append(subject_detail)

        self.view.create_registration_window(available_subjects)

    def handle_registration_selection(self, selected_subject):

        student_id = self.current_user['username']
    
        new_registration = {
            "student_id": student_id,
            "subject_id": selected_subject['subject_id'],
            "grade": None
        }
        
        self.db.add_record('registered_subjects', new_registration)
        
        self.view.show_message("สำเร็จ", f"ลงทะเบียนวิชา {selected_subject['name']} เรียบร้อยแล้ว")
        
    
        self.show_student_dashboard()


    def calculate_age(self, birth_date_str):
        birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d")
        today = datetime.now()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age
    
    def show_grade_page(self, subject_id=None):
        subjects = self.db.get_table('subjects')
        if subject_id is None:

            self.view.create_grade_subject_picker(subjects)
            return

        regs = [r for r in self.db.get_table('registered_subjects') if r['subject_id'] == subject_id]
        students = self.db.get_table('students')
        rows = []
        for r in regs:
            s = next((st for st in students if st['student_id'] == r['student_id']), None)
            if s:
                rows.append({
                    "student_id": s['student_id'],
                    "full_name": f"{s['title']}{s['first_name']} {s['last_name']}",
                    "grade": r.get('grade')
                })
        self.view.create_grade_page(subject_id, rows, len(rows))

    def handle_grade_save(self, subject_id, updates):

        allowed = {"A","B+","B","C+","C","D+","D","F"}
        for sid, grade in updates:
            if grade in allowed:
                self.db.update_grade(sid, subject_id, grade)
        self.view.show_message("สำเร็จ", "บันทึกเกรดเรียบร้อย")
        self.show_grade_page(subject_id)


    def open_student_profile(self, student_id):
        student = next((s for s in self.db.get_table('students') if s['student_id'] == student_id), None)
        if not student:
            self.view.show_error("Error", "ไม่พบข้อมูลนักเรียน")
            return
        regs = [r for r in self.db.get_table('registered_subjects') if r['student_id'] == student_id]
        subjects = self.db.get_table('subjects')
        details = []
        for r in regs:
            sub = next((s for s in subjects if s['subject_id'] == r['subject_id']), None)
            if sub:
                details.append({**sub, "grade": r.get('grade')})
        self.view.create_student_dashboard(student, details)

    def show_grade_page(self, subject_id=None):
        subjects = self.db.get_table('subjects')
        if subject_id is None:
            self.view.create_grade_subject_picker(subjects)
            return
        regs = [r for r in self.db.get_table('registered_subjects') if r['subject_id'] == subject_id]
        students = self.db.get_table('students')
        rows = []
        for r in regs:
            s = next((st for st in students if st['student_id'] == r['student_id']), None)
            if s:
                rows.append({
                    "student_id": s['student_id'],
                    "full_name": f"{s['title']}{s['first_name']} {s['last_name']}",
                    "grade": r.get('grade')
                })
        self.view.create_grade_page(subject_id, rows, len(rows))

    def handle_grade_save(self, subject_id, updates):
        allowed = {"A", "B+", "B", "C+", "C", "D+", "D", "F"}
        for sid, grade in updates:
            if grade in allowed:
                self.db.update_grade(sid, subject_id, grade)
        self.view.show_message("สำเร็จ", "บันทึกเกรดเรียบร้อย")
        self.show_grade_page(subject_id)