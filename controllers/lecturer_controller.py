import re
from sqlalchemy import desc
from core.database import Session
# 👇 IMPORT TỪ UTILS
from core.utils import calculate_total, to_letter_grade, get_time_string
from core.models_orm import Lecturer, CourseSection, Student, GradeReport, Course, GradeReviewRequest

class LecturerController:
    def __init__(self, user_id):
        self.session = Session()
        self.user_id = user_id
        # Lấy object Giảng viên
        self.lecturer = self.session.query(Lecturer).filter(Lecturer.userID == user_id).first()

    def __del__(self):
        self.session.close()

    def get_lecturer_info(self):
        return self.lecturer

    # --- UC: UPDATE PROFILE ---
    def update_contact_info(self, phone, email, address):
        if not phone or not email or not address: 
            return False, "❌ Vui lòng điền đầy đủ thông tin."

        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email): 
            return False, "❌ Email không đúng định dạng."
        
        if not phone.isdigit():
            return False, "❌ Số điện thoại chỉ được chứa chữ số."
        if len(phone) < 10 or len(phone) > 11:
            return False, "❌ Số điện thoại phải có 10 hoặc 11 số."
        
        try:
            self.lecturer.phone = phone
            self.lecturer.email = email
            self.lecturer.address = address
            self.session.commit()
            return True, "✅ Cập nhật hồ sơ thành công!"
        except Exception as e:
            self.session.rollback()
            return False, f"Lỗi DB: {e}"

    # --- UC: VIEW SCHEDULE ---
    def get_teaching_schedule(self):
        if not self.lecturer: return []

        results = self.session.query(CourseSection, Course)\
            .join(Course, CourseSection.courseID == Course.courseID)\
            .filter(CourseSection.lecturerID == self.lecturer.lecturerID).all()

        data = []
        for sec, course in results:
            data.append({
                "Mã Lớp": sec.sectionID,
                "Môn học": course.courseName,
                "Thứ": sec.dayOfWeek,
                "Phòng": sec.room,
                # 👇 SỬ DỤNG HÀM TỪ UTILS
                "Thời gian": get_time_string(sec.startPeriod, sec.endPeriod),
                "_d": sec.dayOfWeek, 
                "_s": sec.startPeriod
            })
        return data

    def get_my_sections(self):
        if not self.lecturer: return []

        results = self.session.query(CourseSection, Course)\
            .join(Course, CourseSection.courseID == Course.courseID)\
            .filter(CourseSection.lecturerID == self.lecturer.lecturerID).all()
        
        return [(sec.sectionID, course.courseName) for sec, course in results]

    # --- UC: MANAGE GRADES ---
    def get_students_in_section(self, section_id):
        results = self.session.query(GradeReport, Student)\
            .join(Student, GradeReport.studentID == Student.studentID)\
            .filter(GradeReport.sectionID == section_id).all()

        data = []
        for grade, student in results:
            data.append({
                "MSSV": student.studentID,
                "Họ tên": student.fullName,
                "Điểm QT": grade.midterm if grade.midterm is not None else 0.0, 
                "Điểm CK": grade.final if grade.final is not None else 0.0
            })
        return data

    def enter_grades(self, section_id, new_data_list):
        return self._process_grades(section_id, new_data_list, is_update=False)

    def update_grades(self, section_id, new_data_list, reason):
        if not reason: return False, "❌ Cần nhập lý do chỉnh sửa."
        return self._process_grades(section_id, new_data_list, is_update=True, reason=reason)

    def _process_grades(self, section_id, new_data_list, is_update=False, reason=""):
        try:
            count = 0
            for row in new_data_list:
                grade_entry = self.session.query(GradeReport).filter_by(
                    sectionID=section_id,
                    studentID=row['MSSV']
                ).first()

                if grade_entry:
                    new_mid = float(row['Điểm QT']) if row['Điểm QT'] is not None else 0.0
                    new_final = float(row['Điểm CK']) if row['Điểm CK'] is not None else 0.0
                    
                    # Check validation 0-10
                    if not (0 <= new_mid <= 10) or not (0 <= new_final <= 10):
                        return False, f"❌ Lỗi: Điểm của sinh viên {row['MSSV']} không hợp lệ (Phải từ 0 đến 10)!"

                    current_mid = grade_entry.midterm if grade_entry.midterm is not None else 0.0
                    current_final = grade_entry.final if grade_entry.final is not None else 0.0

                    if current_mid != new_mid or current_final != new_final:
                        grade_entry.midterm = new_mid
                        grade_entry.final = new_final
                        
                        # 👇 SỬ DỤNG HÀM TỪ UTILS ĐỂ TÍNH TỔNG & ĐIỂM CHỮ
                        grade_entry.total = calculate_total(new_mid, new_final)
                        grade_entry.letterGrade = to_letter_grade(grade_entry.total)
                        
                        count += 1
            
            if count > 0:
                self.session.commit()
                msg = f"✅ Đã lưu thành công {count} sinh viên."
                if reason: msg += f" (Lý do: {reason})"
                return True, msg
            
            return True, "⚠️ Không có dữ liệu nào thay đổi."

        except ValueError:
            return False, "❌ Lỗi: Dữ liệu điểm không hợp lệ (phải là số)."
        except Exception as e:
            self.session.rollback()
            return False, f"❌ Lỗi hệ thống: {e}"

    # --- UC 12: REVIEW GRADE REQUEST ---
    def get_pending_reviews_detailed(self):
        if not self.lecturer: return []

        results = self.session.query(GradeReviewRequest, CourseSection, Course, Student)\
            .join(CourseSection, GradeReviewRequest.sectionID == CourseSection.sectionID)\
            .join(Course, CourseSection.courseID == Course.courseID)\
            .join(Student, GradeReviewRequest.studentID == Student.studentID)\
            .filter(
                CourseSection.lecturerID == self.lecturer.lecturerID,
                GradeReviewRequest.status == 0 
            ).all()

        detailed_list = []
        for req, sec, course, student in results:
            detailed_list.append({
                "request": req,
                "request_id": req.requestID,
                "student_name": student.fullName,
                "student_id": student.studentID,
                "course_name": course.courseName,
                "section_id": sec.sectionID,
                "reason": req.studentComment,
                "date": req.createDate
            })
        return detailed_list

    def process_review(self, request_id, new_status_code, reply_msg):
        try:
            req = self.session.query(GradeReviewRequest).get(request_id)
            if not req: return False, "❌ Không tìm thấy yêu cầu."
            
            req.status = new_status_code
            req.lecturerReply = reply_msg
            
            self.session.commit()
            return True, "✅ Đã cập nhật trạng thái."
        except Exception as e:
            self.session.rollback()
            return False, f"❌ Lỗi: {e}"