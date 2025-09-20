import json

class Database:
    def __init__(self, filepath='data.json'):
        self.filepath = filepath
        self.data = self._load_data()

    def _load_data(self):
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: ไม่พบไฟล์ {self.filepath}")
            return {"users": [], "students":[], "subjects": [], "subject_structure":[],"registered_subjects": []}
        except json.JSONDecodeError:
            print(f"Error: ไฟล์ {self.filepath} มีรูปแบบไม่ถูกต้อง")
            return {"users": [], "students":[], "subjects": [], "subject_structure":[],"registered_subjects": []}
    
    def save_data(self):
        with open(self.filepath,'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def get_table(self, name):
        return self.data.get(name, [])
    
    def add_record(self, table_name, record):
        if table_name in self.data:
            self.data[table_name].append(record)
            self.save_data()
            return True
        return False
    
    def update_grade(self, student_id, subject_id, grade):
        for reg in self.data['registered_subjects']:
            if reg['student_id'] == student_id and reg['subject_id'] == subject_id:
                reg['grade'] = grade
                self.save_data()
                return True
        return False
    
    def get_student_by_id(self, student_id):
        return next((s for s in self.data['students'] if s['student_id'] == student_id), None)

    def get_subject_by_id(self, subject_id):
        return next((s for s in self.data['subjects'] if s['subject_id'] == subject_id), None)
    
    def get_registered_subjects_by_student(self, student_id):
        return [r for r in self.data['registered_subjects'] if r['student_id'] == student_id]

    def get_students_registered_in_subject(self, subject_id):
        regs = [r for r in self.data['registered_subjects'] if r['subject_id'] == subject_id]
        out = []
        for r in regs:
            s = self.get_student_by_id(r['student_id'])
            if s:
                out.append({
                    "student_id": s['student_id'],
                    "full_name": f"{s['title']}{s['first_name']} {s['last_name']}",
                    "grade": r.get('grade')
                })
        return out
    
    # def count_registered(self, subject_id):
    #     return sum(1 for r in self.data['registered_subjects'] if r['subject_id'] == subject_id)
    
    # def has_grade(self, student_id, subject_id):
    #     reg = next((r for r in self.data['registered_subjects']
    #             if r['student_id'] == student_id and r['subject_id'] == subject_id), None)
    # return bool(reg and (reg.get('grade') is not None) and (reg.get('grade') != ""))

    # def batch_update_grades(self, subject_id, updates):