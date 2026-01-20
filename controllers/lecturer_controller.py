import streamlit as st
import re
from core.database import MockDatabase
from core.utils import get_time_string

class LecturerController:
    def __init__(self, lecturer_id):
        self.db = MockDatabase()
        self.lecturer = self.db.get_user(lecturer_id)

    # ... (Các hàm update_profile, get_schedule, enter/update grades... GIỮ NGUYÊN) ...
    def update_contact_info(self, phone, email, address):
        if not phone or not email or not address: return False, "❌ Thiếu thông tin."
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email): return False, "❌ Email sai."
        self.lecturer.phone = phone
        self.lecturer.email = email
        self.lecturer.address = address
        return True, "✅ Cập nhật thành công!"

    def get_teaching_schedule(self):
        # (Giữ nguyên logic cũ)
        all_sections = st.session_state.get('sections', [])
        my_sections = [s for s in all_sections if s.lecturerID == self.lecturer.userID]
        data = []
        for sec in my_sections:
            course = self.db.get_course_by_id(sec.courseID)
            data.append({
                "Mã Lớp": sec.sectionID, "Môn học": course.courseName,
                "Thứ": sec.dayOfWeek, "Phòng": sec.room,
                "Thời gian": get_time_string(sec.startPeriod, sec.endPeriod),
                "_d": sec.dayOfWeek, "_s": sec.startPeriod
            })
        return data

    def get_my_sections(self):
        # (Giữ nguyên logic cũ)
        all_sections = st.session_state.get('sections', [])
        my_sections = [s for s in all_sections if s.lecturerID == self.lecturer.userID]
        return [(s.sectionID, self.db.get_course_by_id(s.courseID).courseName) for s in my_sections]

    def get_students_in_section(self, section_id):
        # (Giữ nguyên logic cũ)
        all_grades = st.session_state.get('grades', [])
        class_grades = [g for g in all_grades if g.sectionID == section_id]
        data = []
        for g in class_grades:
            sv = self.db.get_user(g.studentID)
            data.append({ "MSSV": sv.userID, "Họ tên": sv.fullName, "Điểm QT": g.componentGrade, "Điểm CK": g.finalScore })
        return data

    def enter_grades(self, section_id, new_data_list):
        # (Giữ nguyên logic UC10 bạn đã có)
        return self._process_grades(section_id, new_data_list, is_update=False)

    def update_grades(self, section_id, new_data_list, reason):
        # (Giữ nguyên logic UC11 bạn đã có)
        if not reason: return False, "❌ Cần nhập lý do."
        return self._process_grades(section_id, new_data_list, is_update=True, reason=reason)

    def _process_grades(self, section_id, new_data_list, is_update=False, reason=""):
        # Helper function để tránh lặp code (bạn có thể copy logic cũ vào đây)
        all_grades = st.session_state.get('grades', [])
        count = 0
        for row in new_data_list:
            for g in all_grades:
                if g.studentID == row['MSSV'] and g.sectionID == section_id:
                    if g.componentGrade != row['Điểm QT'] or g.finalScore != row['Điểm CK']:
                        g.componentGrade = row['Điểm QT']
                        g.finalScore = row['Điểm CK']
                        count += 1
        if count > 0: return True, f"✅ Thành công. {reason}"
        return True, "⚠️ Không có thay đổi."

    # --- UC 12: REVIEW GRADE REQUEST (ĐÃ NÂNG CẤP) ---
    def get_pending_reviews_detailed(self):
        """
        Lấy danh sách yêu cầu phúc khảo kèm thông tin chi tiết:
        Student Name, Course Name, Reason.
        """
        my_section_ids = [s.sectionID for s in st.session_state.get('sections', []) if s.lecturerID == self.lecturer.userID]
        all_reqs = st.session_state.get('requests', [])
        
        # 1. Lọc Request của GV này
        my_reqs = [r for r in all_reqs if r.sectionID in my_section_ids and r.status == "Pending"]
        
        # 2. Enrich Data (Thêm tên SV, Tên Môn)
        detailed_list = []
        for r in my_reqs:
            student = self.db.get_user(r.studentID)
            section = self.db.get_section_by_id(r.sectionID)
            course = self.db.get_course_by_id(section.courseID)
            
            detailed_list.append({
                "request": r, # Object gốc
                "student_name": student.fullName if student else r.studentID,
                "student_id": r.studentID,
                "course_name": course.courseName if course else "Unknown Course",
                "section_id": r.sectionID,
                "reason": r.reason,
                "date": r.createDate
            })
            
        return detailed_list

    def process_review(self, request_id, new_status, reply_msg):
        for r in st.session_state['requests']:
            if r.requestID == request_id:
                r.status = new_status
                r.reply = reply_msg
                return True, f"✅ Đã cập nhật trạng thái: {new_status}"
        return False, "❌ Không tìm thấy yêu cầu."