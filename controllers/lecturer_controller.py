import streamlit as st
import re # <--- Import thư viện Regex để kiểm tra chuỗi
from core.database import MockDatabase
from core.utils import get_time_string

class LecturerController:
    def __init__(self, lecturer_id):
        self.db = MockDatabase()
        self.lecturer = self.db.get_user(lecturer_id)

    # --- UC5: Update Profile (ĐÃ BỔ SUNG VALIDATION) ---
    def update_contact_info(self, phone, email, address):
        # 1. Kiểm tra rỗng
        if not phone or not email or not address:
            return False, "❌ Vui lòng điền đầy đủ thông tin (SĐT, Email, Địa chỉ)."

        # 2. Kiểm tra định dạng Email (VD: abc@domain.com)
        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_pattern, email):
            return False, "❌ Định dạng Email không hợp lệ."

        # 3. Kiểm tra số điện thoại (Chỉ chứa số, độ dài từ 9-11 số)
        if not phone.isdigit() or len(phone) < 9 or len(phone) > 11:
            return False, "❌ Số điện thoại phải là dãy số từ 9-11 chữ số."

        # 4. Nếu tất cả hợp lệ thì mới lưu vào DB
        self.lecturer.phone = phone
        self.lecturer.email = email
        self.lecturer.address = address
        return True, "✅ Cập nhật hồ sơ thành công!"

    # ... (Các hàm bên dưới giữ nguyên logic cũ) ...

    def get_teaching_schedule(self):
        all_sections = st.session_state['sections']
        my_sections = [s for s in all_sections if s.lecturerID == self.lecturer.userID]
        
        data = []
        for sec in my_sections:
            course = self.db.get_course_by_id(sec.courseID)
            data.append({
                "Mã Lớp": sec.sectionID,
                "Môn học": course.courseName,
                "Thứ": sec.dayOfWeek,
                "Phòng": sec.room,
                "Thời gian": get_time_string(sec.startPeriod, sec.endPeriod),
                "_d": sec.dayOfWeek, "_s": sec.startPeriod
            })
        return data

    def get_my_sections(self):
        all_sections = st.session_state['sections']
        my_sections = [s for s in all_sections if s.lecturerID == self.lecturer.userID]
        return [(s.sectionID, self.db.get_course_by_id(s.courseID).courseName) for s in my_sections]

    def get_students_in_section(self, section_id):
        all_grades = st.session_state['grades']
        class_grades = [g for g in all_grades if g.sectionID == section_id]
        
        data = []
        for g in class_grades:
            sv = self.db.get_user(g.studentID)
            data.append({
                "MSSV": sv.userID,
                "Họ tên": sv.fullName,
                "Điểm QT": g.componentGrade,
                "Điểm CK": g.finalScore
            })
        return data

    def save_grades(self, section_id, new_data_list, reason=""):
        all_grades = st.session_state['grades']
        count = 0
        
        # 1. Validation 0-10
        for row in new_data_list:
            mssv = row['MSSV']
            qt = row['Điểm QT']
            ck = row['Điểm CK']
            if qt is not None and (qt < 0 or qt > 10):
                return False, f"❌ Lỗi: Điểm QT của SV {mssv} là {qt} (Phải từ 0 đến 10)."
            if ck is not None and (ck < 0 or ck > 10):
                return False, f"❌ Lỗi: Điểm CK của SV {mssv} là {ck} (Phải từ 0 đến 10)."

        # 2. Logic Lưu
        for row in new_data_list:
            for g in all_grades:
                if g.studentID == row['MSSV'] and g.sectionID == section_id:
                    if g.componentGrade != row['Điểm QT'] or g.finalScore != row['Điểm CK']:
                        g.componentGrade = row['Điểm QT']
                        g.finalScore = row['Điểm CK']
                        count += 1
        
        if count > 0:
            msg = f"✅ Đã lưu thành công điểm cho {count} sinh viên."
            if reason: msg += f" (Lý do: {reason})"
            return True, msg
        else:
            return True, "⚠️ Không có thay đổi nào cần lưu."

    def get_pending_reviews(self):
        my_section_ids = [s.sectionID for s in st.session_state['sections'] if s.lecturerID == self.lecturer.userID]
        all_reqs = st.session_state['requests']
        # Chỉ lấy đơn Pending
        my_reqs = [r for r in all_reqs if r.sectionID in my_section_ids and r.status == "Pending"]
        return my_reqs

    def process_review(self, request_id, new_status, reply_msg):
        for r in st.session_state['requests']:
            if r.requestID == request_id:
                r.status = new_status
                r.reply = reply_msg
                return True, f"✅ Đã xử lý đơn: {new_status}"
        return False, "❌ Không tìm thấy yêu cầu."