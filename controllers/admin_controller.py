import pandas as pd
import streamlit as st
from core.database import MockDatabase
from core.models import Section, Course

class AdminController:
    def __init__(self):
        self.db = MockDatabase()

    def get_stats(self):
        # Lấy số liệu an toàn từ Session State
        users = st.session_state.get('users', {})
        courses = st.session_state.get('courses', {})
        sections = st.session_state.get('sections', [])
        semesters = st.session_state.get('semesters', [])
        
        return {
            "users": len(users),
            "courses": len(courses),
            "sections": len(sections),
            "semesters": len(semesters) if isinstance(semesters, list) else len(semesters)
        }

    # --- HÀM MỚI ĐỂ FIX LỖI VIEW ---
    def get_all_semesters(self):
        # Trả về DataFrame hoặc List từ Session
        data = st.session_state.get('semesters', [])
        if isinstance(data, list):
            return pd.DataFrame(data)
        return data

    def get_all_sections(self):
        # Trả về danh sách section dưới dạng DataFrame đẹp
        sections = st.session_state.get('sections', [])
        if not sections:
            return []
        # Convert object to dict list
        return [vars(s) for s in sections]

    # ... (Các hàm add_semester, add_course, add_section... giữ nguyên logic cũ) ...
    def add_semester(self, sem_id, name, start, end):
        # Logic cũ của bạn
        if not sem_id or not name: return False, "Thiếu thông tin"
        
        current_sems = st.session_state.get('semesters', [])
        # Nếu là DataFrame
        if isinstance(current_sems, pd.DataFrame):
            if sem_id in current_sems['semesterID'].values: return False, "Trùng mã HK"
            new_sem = {"semesterID": sem_id, "name": name, "startDate": str(start), "endDate": str(end)}
            updated = pd.concat([current_sems, pd.DataFrame([new_sem])], ignore_index=True)
            st.session_state['semesters'] = updated
        else:
            # Nếu là List
            new_sem = {"semesterID": sem_id, "name": name, "startDate": str(start), "endDate": str(end)}
            st.session_state['semesters'].append(new_sem)
            
        return True, "Thêm thành công"

    def add_course(self, cid, cname, credits):
        courses = st.session_state.get('courses', {})
        if cid in courses: return False, "Trùng mã môn"
        new_c = Course(cid, cname, credits)
        st.session_state['courses'][cid] = new_c
        return True, "Thêm môn thành công"

    def add_section(self, sid, cid, cname, lid, room, day, p1, p2):
        sections = st.session_state.get('sections', [])
        if any(s.sectionID == sid for s in sections): return False, "Trùng mã lớp"
        new_sec = Section(sid, cid, lid, "HK1_24", room, day, p1, p2)
        st.session_state['sections'].append(new_sec)
        return True, "Mở lớp thành công"
        
    def import_users_batch(self, df):
        return True, "Import (Demo) thành công"
    
        

    # -------- UC 14: LOCK / UNLOCK USER ----------
    def lock_user(self, user_id, reason):
        users = st.session_state.get('users', {})
        if user_id not in users:
            return False, "Không tìm thấy người dùng"
        users[user_id]['status'] = 'LOCKED'
        users[user_id]['lock_reason'] = reason
        return True, "Khóa tài khoản thành công"

    def unlock_user(self, user_id):
        users = st.session_state.get('users', {})
        if user_id not in users:
            return False, "Không tìm thấy người dùng"
        users[user_id]['status'] = 'ACTIVE'
        users[user_id].pop('lock_reason', None)
        return True, "Mở khóa tài khoản thành công"

    # -------- UC 15: MANAGE SEMESTER ----------
    def update_semester(self, sem_id, start, end):
        semesters = st.session_state.get('semesters', [])
        for s in semesters:
            if s['semesterID'] == sem_id:
                s['startDate'] = str(start)
                s['endDate'] = str(end)
                return True, "Cập nhật học kỳ thành công"
        return False, "Không tìm thấy học kỳ"

    def delete_semester(self, sem_id):
        semesters = st.session_state.get('semesters', [])
        for s in semesters:
            if s['semesterID'] == sem_id:
                semesters.remove(s)
                return True, "Xóa học kỳ thành công"
        return False, "Không tìm thấy học kỳ"
    
        # -------- UC 16: MANAGE COURSE ----------
    def update_course(self, cid, name=None, credits=None):
        courses = st.session_state.get('courses', {})
        if cid not in courses:
            return False, "Không tìm thấy môn học"

        course = courses[cid]
        if name is not None:
            course.name = name
        if credits is not None:
            course.credits = credits

        return True, "Cập nhật môn học thành công"


    # -------- UC 17: MANAGE SECTION ----------
    def update_section(self, section_id, room=None, day=None, p1=None, p2=None):
        sections = st.session_state.get('sections', [])
        for s in sections:
            if s.sectionID == section_id:
                if room is not None: s.room = room
                if day is not None: s.day = day
                if p1 is not None: s.periodStart = p1
                if p2 is not None: s.periodEnd = p2
                return True, "Cập nhật lớp học phần thành công"
        return False, "Không tìm thấy lớp học phần"

    # -------- UC 19: CREATE SECTION (EXTENDED) ----------
    def create_section_with_semester(self, sid, cid, lid, semester_id, room, day, p1, p2):
        sections = st.session_state.get('sections', [])
        if any(s.sectionID == sid for s in sections):
            return False, "Trùng mã lớp học phần"
        new_sec = Section(sid, cid, lid, semester_id, room, day, p1, p2)
        sections.append(new_sec)
        return True, "Tạo lớp học phần thành công"

    
        
    # -------- UC 18: MANAGE CURRICULUM ----------
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


    # -------- UC 20: CANCEL SECTION ----------
    def cancel_section(self, section_id):
        sections = st.session_state.get('sections', [])
        for s in sections:
            if s.sectionID == section_id:
                s.status = "CANCELED"
                return True, "Hủy lớp thành công"
        return False, "Không tìm thấy lớp học phần"

    # -------- UC 21 / 22: DELETE COURSE ----------
    def delete_course(self, cid):
        courses = st.session_state.get('courses', {})
        if cid not in courses:
            return False, "Không tìm thấy môn học"
        del courses[cid]
        return True, "Xóa môn học thành công"
