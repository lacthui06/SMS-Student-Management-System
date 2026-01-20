import streamlit as st
import re
from core.database import MockDatabase
from core.models import GradeReviewRequest
from core.utils import calculate_total, to_letter_grade, get_time_string
from datetime import date

class StudentController:
    def __init__(self, student_id):
        self.db = MockDatabase()
        self.student = self.db.get_user(student_id)

    # ... (Các hàm update_contact_info, v.v. giữ nguyên) ...
    def update_contact_info(self, phone, email, address):
        if not phone or not email or not address:
            return False, "❌ Vui lòng điền đầy đủ thông tin."
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
            return False, "❌ Định dạng Email không hợp lệ."
        if not phone.isdigit() or len(phone) < 9 or len(phone) > 11:
            return False, "❌ Số điện thoại phải là dãy số từ 9-11 chữ số."

        self.student.phone = phone
        self.student.email = email
        self.student.address = address
        return True, "✅ Cập nhật hồ sơ thành công!"

    # UC6: View Academic Progress (ĐÃ CẬP NHẬT THÊM MÃ HP & SECTION ID)
    def get_progress_data(self):
        major = self.db.get_major(self.student.majorID)
        grades = self.db.get_student_grades(self.student.userID)
        
        accumulated = 0
        passed_courses = []
        
        for g in grades:
            total = calculate_total(g.componentGrade, g.finalScore)
            # Môn học được tính là Đạt nếu điểm >= 4.0
            if total is not None and total >= 4.0:
                sec = self.db.get_section_by_id(g.sectionID)
                course = self.db.get_course_by_id(sec.courseID)
                accumulated += course.credits
                
                passed_courses.append({
                    "Mã HP": course.courseID,   # <--- Thêm Course Code (theo đặc tả)
                    "Mã Lớp": sec.sectionID,    # <--- Thêm Section ID (theo yêu cầu của bạn)
                    "Tên môn": course.courseName,
                    "Tín chỉ": course.credits,
                    "Điểm": total,
                    "Kết quả": "Đạt"
                })
                
        return {
            "accumulated": accumulated,
            "required": major.requiredCredits if major else 150,
            "percent": min(accumulated / (major.requiredCredits if major else 150), 1.0),
            "details": passed_courses
        }

    # ... (Các hàm get_timetable, get_grade_table, ... giữ nguyên không đổi) ...
    def get_timetable(self):
        grades = self.db.get_student_grades(self.student.userID)
        section_ids = [g.sectionID for g in grades]
        
        schedule = []
        for sec_id in section_ids:
            sec = self.db.get_section_by_id(sec_id)
            if sec:
                course = self.db.get_course_by_id(sec.courseID)
                lecturer = self.db.get_user(sec.lecturerID)
                
                schedule.append({
                    "Mã Lớp": sec.sectionID,
                    "Môn học": course.courseName,
                    "Giảng viên": lecturer.fullName,
                    "Thứ": sec.dayOfWeek,
                    "Phòng": sec.room,
                    "Ca/Tiết": get_time_string(sec.startPeriod, sec.endPeriod),
                    "_day_sort": sec.dayOfWeek,
                    "_start_sort": sec.startPeriod
                })
        return schedule

    def get_grade_table(self):
        raw_grades = self.db.get_student_grades(self.student.userID)
        data = []
        for g in raw_grades:
            sec = self.db.get_section_by_id(g.sectionID)
            course = self.db.get_course_by_id(sec.courseID)
            total = calculate_total(g.componentGrade, g.finalScore)
            
            data.append({
                "Học kỳ": sec.semesterID,
                "Mã HP": sec.sectionID,
                "Tên môn": course.courseName,
                "Tín chỉ": course.credits,
                "Điểm QT": g.componentGrade,
                "Điểm CK": g.finalScore,
                "Tổng kết": total,
                "Điểm chữ": to_letter_grade(total)
            })
        return data

    def get_reviewable_courses(self):
        grades = self.db.get_student_grades(self.student.userID)
        my_requests = [r.sectionID for r in st.session_state['requests'] if r.studentID == self.student.userID]
        
        eligible = []
        for g in grades:
            if g.finalScore is not None and g.sectionID not in my_requests:
                sec = self.db.get_section_by_id(g.sectionID)
                course = self.db.get_course_by_id(sec.courseID)
                eligible.append(f"{g.sectionID} - {course.courseName}")
        return eligible

    def create_review_request(self, section_str, reason):
        section_id = section_str.split(" - ")[0]
        req_id = f"REQ{len(st.session_state['requests']) + 1:03d}"
        new_req = GradeReviewRequest(
            requestID=req_id,
            studentID=self.student.userID,
            sectionID=section_id,
            reason=reason,
            createDate=str(date.today()),
            status="Pending",
            reply=""
        )
        st.session_state['requests'].append(new_req)
        return True, "Gửi yêu cầu thành công!"
    
    def get_my_requests(self):
        return [r for r in st.session_state['requests'] if r.studentID == self.student.userID]