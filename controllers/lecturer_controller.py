import pandas as pd
import re
from core.database import Session
from core.models_orm import Lecturer, CourseSection, Student, GradeReport, Course, GradeReviewRequest
from core.utils import calculate_total, to_letter_grade, get_time_string

class LecturerController:
    def __init__(self, user_id):
        self.session = Session()
        self.user_id = user_id
        self.lecturer = self.session.query(Lecturer).filter(Lecturer.userID == user_id).first()

    def __del__(self):
        self.session.close()

    def get_lecturer_info(self):
        return self.lecturer

    # --- UPDATE PROFILE ---
    def update_contact_info(self, phone, email, address):
        if not phone or not email or not address: return False, "❌ Thiếu thông tin."
        try:
            self.lecturer.phone = phone; self.lecturer.email = email; self.lecturer.address = address
            self.session.commit()
            return True, "✅ Cập nhật thành công!"
        except Exception as e: return False, str(e)

    # --- SCHEDULE ---
    def get_teaching_schedule(self):
        if not self.lecturer: return []
        results = self.session.query(CourseSection, Course)\
            .join(Course, CourseSection.courseID == Course.courseID)\
            .filter(CourseSection.lecturerID == self.lecturer.lecturerID).all()
        data = []
        for sec, course in results:
            data.append({
                "Mã Lớp": sec.sectionID, "Môn học": course.courseName,
                "Thứ": sec.dayOfWeek, "Phòng": sec.room,
                "Thời gian": get_time_string(sec.startPeriod, sec.endPeriod),
                "_d": sec.dayOfWeek, "_s": sec.startPeriod
            })
        return data

    def get_my_sections(self):
        if not self.lecturer: return []
        results = self.session.query(CourseSection, Course)\
            .join(Course, CourseSection.courseID == Course.courseID)\
            .filter(CourseSection.lecturerID == self.lecturer.lecturerID).all()
        return [(sec.sectionID, course.courseName) for sec, course in results]

    # --- GRADES ---
    def get_students_in_section(self, section_id):
        results = self.session.query(GradeReport, Student)\
            .join(Student, GradeReport.studentID == Student.studentID)\
            .filter(GradeReport.sectionID == section_id).all()
        data = []
        for grade, student in results:
            data.append({
                "MSSV": student.studentID, "Họ tên": student.fullName,
                "Điểm QT": grade.midterm, "Điểm CK": grade.final # Để None nếu null
            })
        return data

    def enter_grades(self, section_id, new_data_list):
        return self._process_grades(section_id, new_data_list, reason="")

    def update_grades(self, section_id, new_data_list, reason):
        if not reason: return False, "❌ Cần nhập lý do."
        return self._process_grades(section_id, new_data_list, reason=reason)

    def _process_grades(self, section_id, new_data_list, reason=""):
        try:
            count = 0
            for row in new_data_list:
                # Helper validate từng điểm
                def validate_score(val):
                    # Chấp nhận None, chuỗi rỗng, hoặc NaN (cho phép để trống)
                    if val is None or val == "" or pd.isna(val): return None 
                    try:
                        s = float(val)
                        if 0 <= s <= 10: return s
                        return False # Sai range (trả về False để báo lỗi)
                    except: return False # Sai format

                # Lấy giá trị từ dict (row là dict)
                new_mid = validate_score(row.get('Điểm QT'))
                new_final = validate_score(row.get('Điểm CK'))

                # Nếu trả về False tức là vi phạm 0-10 (còn None là hợp lệ)
                if new_mid is False or new_final is False:
                    return False, f"❌ Lỗi: Điểm SV {row['MSSV']} không hợp lệ (Phải từ 0-10 hoặc để trống)."

                grade = self.session.query(GradeReport).filter_by(sectionID=section_id, studentID=row['MSSV']).first()
                if grade:
                    # Chỉ update nếu khác giá trị cũ
                    # Lưu ý: Cần so sánh kỹ với None để tránh lỗi logic
                    old_mid = grade.midterm
                    old_final = grade.final
                    
                    has_change = False
                    if (new_mid != old_mid): has_change = True
                    if (new_final != old_final): has_change = True

                    if has_change:
                        grade.midterm = new_mid
                        grade.final = new_final
                        
                        # Tính tổng (Chỉ tính khi có đủ 2 điểm số thực, nếu có None thì Total = None)
                        if new_mid is not None and new_final is not None:
                            grade.total = calculate_total(new_mid, new_final)
                            grade.letterGrade = to_letter_grade(grade.total)
                        else:
                            # Nếu xóa điểm thành phần -> Xóa luôn tổng kết
                            grade.total = None
                            grade.letterGrade = None
                        count += 1
            
            if count > 0:
                self.session.commit()
                return True, f"✅ Đã lưu thành công {count} sinh viên."
            return True, "⚠️ Không có thay đổi nào."
            
        except Exception as e:
            self.session.rollback()
            return False, f"Lỗi hệ thống: {e}"

    # --- REVIEWS ---
    def get_pending_reviews_detailed(self):
        if not self.lecturer: return []
        results = self.session.query(GradeReviewRequest, CourseSection, Course, Student)\
            .join(CourseSection, GradeReviewRequest.sectionID == CourseSection.sectionID)\
            .join(Course, CourseSection.courseID == Course.courseID)\
            .join(Student, GradeReviewRequest.studentID == Student.studentID)\
            .filter(CourseSection.lecturerID == self.lecturer.lecturerID, GradeReviewRequest.status == 0).all() # 0: Chưa xử lý

        data = []
        for req, sec, cour, stu in results:
            data.append({
                "request": req, "student_name": stu.fullName, "student_id": stu.studentID,
                "course_name": cour.courseName, "section_id": sec.sectionID,
                "reason": req.studentComment, "date": req.createDate
            })
        return data

    def process_review(self, request_id, status_code, reply):
        try:
            req = self.session.query(GradeReviewRequest).get(request_id)
            if req:
                req.status = status_code # 1: Duyệt, 2: Từ chối
                req.lecturerReply = reply
                self.session.commit()
                return True, "Thành công."
            return False, "Lỗi."
        except Exception as e: return False, str(e)