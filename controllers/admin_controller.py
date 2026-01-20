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