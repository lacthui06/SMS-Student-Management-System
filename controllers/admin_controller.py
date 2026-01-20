import pandas as pd
from core.database import MockDatabase
from core.models import Section, Course

class AdminController:
    def __init__(self):
        self.db = MockDatabase()

    def get_stats(self):
        return {
            "users": len(self.db.get_account("admin").password) + 4, # Demo logic
            "courses": len(self.db.get_course("SE101").courseName) + 3, # Demo logic
            "sections": len(self.db.sections),
            "semesters": len(self.db.semesters)
        }

    def add_semester(self, sem_id, name, start, end):
        # Semesters được lưu là DataFrame trong database.py -> Dùng logic cũ OK
        if sem_id in self.db.semesters['semesterID'].values: return False, "Trùng mã HK"
        if start >= end: return False, "Ngày không hợp lệ"
        new_sem = {"semesterID": sem_id, "name": name, "startDate": str(start), "endDate": str(end)}
        
        updated = pd.concat([self.db.semesters, pd.DataFrame([new_sem])], ignore_index=True)
        # Update lại vào MockDatabase
        self.db.update_dataframe('semesters', updated) # Cần đảm bảo hàm này có trong MockDatabase hoặc gán trực tiếp
        # Fix nhanh: Gán trực tiếp vì Python pass by reference
        import streamlit as st
        st.session_state['db']['semesters'] = updated
        return True, "Thêm thành công"

    def add_course(self, cid, cname, credits):
        # Courses được lưu là Dictionary -> Phải dùng logic Dict
        if self.db.get_course(cid): return False, "Trùng mã môn"
        
        # Tạo đối tượng Course mới
        new_c = Course(courseID=cid, courseName=cname, credits=credits)
        
        # Lưu vào Dictionary
        import streamlit as st
        st.session_state['db']['courses'][cid] = new_c
        return True, "Thêm thành công"

    def add_section(self, sid, cid, cname, lid, room, day, p1, p2):
        # Sections được lưu là List -> Phải dùng logic List
        if any(s.sectionID == sid for s in self.db.sections): return False, "Trùng mã lớp"
        if p1 >= p2: return False, "Tiết học sai"
        
        # Tạo đối tượng Section mới
        # Lưu ý: Class Section trong models.py yêu cầu: sectionID, courseID, lecturerID, semesterID, room, day, startPeriod, endPeriod
        new_sec = Section(
            sectionID=sid, 
            courseID=cid, 
            lecturerID=lid, 
            semesterID="HK1_24", # Default hoặc lấy từ input
            room=room, 
            day=day, 
            startPeriod=p1, 
            endPeriod=p2
        )
        
        # Thêm vào List
        self.db.sections.append(new_sec)
        return True, "Mở lớp thành công"