import pandas as pd
import streamlit as st
from core.database import MockDatabase
from core.models import Section, Course, Semester, GradeReviewRequest # Import đủ

class AdminController:
    def __init__(self):
        self.db = MockDatabase()

    def get_stats(self):
        users = st.session_state.get('users', {})
        courses = st.session_state.get('courses', {})
        sections = st.session_state.get('sections', [])
        semesters = st.session_state.get('semesters', [])
        
        return {
            "users": len(users),
            "courses": len(courses),
            "sections": len(sections),
            "semesters": len(semesters)
        }

    # --- HÀM HỖ TRỢ VIEW ---
    def get_all_semesters(self):
        # Trả về list object để view xử lý
        return st.session_state.get('semesters', [])

    def get_all_sections(self):
        # Convert list object thành list dict để hiển thị bảng
        sections = st.session_state.get('sections', [])
        if not sections: return []
        return [vars(s) for s in sections]
    
    def get_all_users(self):
        return st.session_state.get('users', {}).values()

    def get_all_courses(self):
        return st.session_state.get('courses', {})

    # -------- UC: MANAGE SEMESTER ----------
    def add_semester(self, sem_id, name, start, end):
        if not sem_id or not name: return False, "Thiếu thông tin"
        
        current_sems = st.session_state.get('semesters', [])
        
        # Kiểm tra trùng ID (Dùng cú pháp Object .semesterID)
        if any(s.semesterID == sem_id for s in current_sems):
            return False, "Trùng mã HK"
            
        new_sem = Semester(sem_id, name, str(start), str(end))
        current_sems.append(new_sem)
        return True, "Thêm thành công"

    def update_semester(self, sem_id, start, end):
        semesters = st.session_state.get('semesters', [])
        for s in semesters:
            # Sửa lỗi: Truy cập bằng .semesterID thay vì ['semesterID']
            if s.semesterID == sem_id:
                s.startDate = str(start)
                s.endDate = str(end)
                return True, "Cập nhật học kỳ thành công"
        return False, "Không tìm thấy học kỳ"

    def delete_semester(self, sem_id):
        semesters = st.session_state.get('semesters', [])
        for i, s in enumerate(semesters):
            if s.semesterID == sem_id:
                del semesters[i]
                return True, "Xóa học kỳ thành công"
        return False, "Không tìm thấy học kỳ"

    # -------- UC: MANAGE COURSE ----------
    def add_course(self, cid, cname, credits):
        courses = st.session_state.get('courses', {})
        if cid in courses: return False, "Trùng mã môn"
        new_c = Course(cid, cname, credits)
        st.session_state['courses'][cid] = new_c
        return True, "Thêm môn thành công"

    def update_course(self, cid, name=None, credits=None):
        courses = st.session_state.get('courses', {})
        if cid not in courses:
            return False, "Không tìm thấy môn học"

        course = courses[cid]
        if name is not None:
            course.courseName = name # Sửa attribute name cho khớp model
        if credits is not None:
            course.credits = credits

        return True, "Cập nhật môn học thành công"

    def delete_course(self, cid):
        courses = st.session_state.get('courses', {})
        if cid not in courses:
            return False, "Không tìm thấy môn học"
        del courses[cid]
        return True, "Xóa môn học thành công"

    # -------- UC: MANAGE SECTION ----------
    def add_section(self, sid, cid, lid, sem_id, room, day, p1, p2):
        # Hàm này dùng chung logic tạo section
        return self.create_section_with_semester(sid, cid, lid, sem_id, room, day, p1, p2)

    def create_section_with_semester(self, sid, cid, lid, semester_id, room, day, p1, p2):
        sections = st.session_state.get('sections', [])
        if any(s.sectionID == sid for s in sections):
            return False, "Trùng mã lớp học phần"
        
        # Tạo object Section thay vì dict
        new_sec = Section(sid, cid, lid, semester_id, room, day, p1, p2)
        sections.append(new_sec)
        return True, "Tạo lớp học phần thành công"

    def update_section(self, section_id, room=None, day=None, p1=None, p2=None):
        sections = st.session_state.get('sections', [])
        for s in sections:
            if s.sectionID == section_id:
                if room is not None: s.room = room
                if day is not None: s.dayOfWeek = day # Sửa lại cho khớp model (dayOfWeek)
                if p1 is not None: s.startPeriod = p1 # Sửa lại cho khớp model
                if p2 is not None: s.endPeriod = p2   # Sửa lại cho khớp model
                return True, "Cập nhật lớp học phần thành công"
        return False, "Không tìm thấy lớp học phần"

    def cancel_section(self, section_id):
        sections = st.session_state.get('sections', [])
        for s in sections:
            if s.sectionID == section_id:
                # Lưu ý: Class Section trong model chưa có thuộc tính status
                # Cần đảm bảo model Section có field này hoặc thêm động
                s.status = "CANCELED" 
                return True, "Hủy lớp thành công"
        return False, "Không tìm thấy lớp học phần"

    # -------- UC: LOCK / UNLOCK USER ----------
    def lock_user(self, user_id, reason):
        users = st.session_state.get('users', {})
        if user_id not in users:
            return False, "Không tìm thấy người dùng"
        
        # Sửa lỗi: Truy cập attribute object thay vì dict ['key']
        users[user_id].status = False # False = Locked
        # users[user_id].lock_reason = reason # (Model chưa có field này, tạm ẩn để không lỗi)
        return True, "Khóa tài khoản thành công"

    def unlock_user(self, user_id):
        users = st.session_state.get('users', {})
        if user_id not in users:
            return False, "Không tìm thấy người dùng"
        
        users[user_id].status = True # True = Active
        return True, "Mở khóa tài khoản thành công"

    # -------- UC: MANAGE CURRICULUM ----------
    def add_curriculum_item(self, major, course_id, semester_no, required=True):
        curriculum = st.session_state.get('curriculum', [])
        curriculum.append({
            "major": major,
            "courseID": course_id,
            "semester": semester_no,
            "required": required
        })
        st.session_state['curriculum'] = curriculum
        return True, "Thêm môn vào khung chương trình thành công"

    def get_curriculum(self, major=None):
        curriculum = st.session_state.get('curriculum', [])
        if major:
            curriculum = [c for c in curriculum if c['major'] == major]
        return pd.DataFrame(curriculum)

    def remove_curriculum_item(self, major, course_id):
        curriculum = st.session_state.get('curriculum', [])
        for c in curriculum:
            if c['major'] == major and c['courseID'] == course_id:
                curriculum.remove(c)
                return True, "Xóa môn khỏi khung chương trình thành công"
        return False, "Không tìm thấy môn trong khung chương trình"

    # -------- EXTENSION: IMPORT BATCH ----------
    def import_users_batch(self, df):
        # Demo function
        return True, "Import (Demo) thành công"