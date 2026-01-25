from sqlalchemy import desc
import pandas as pd
import re
from datetime import date
import time # Import time ở đây để dùng chung
from core.database import Session
from core.utils import get_time_string 
from core.models_orm import (
    Student, Major, GradeReport, 
    CourseSection, Course, Lecturer, GradeReviewRequest, Semester
)

class StudentController:
    def __init__(self, student_id=None):
        self.db = Session() # Giữ nguyên biến self.db
        self.student_id = student_id

    def __del__(self):
        self.db.close() # Chỉ đóng kết nối khi tắt class

    # =================================================================
    # 👇👇👇 PHẦN SỬA LẠI CHO ĐÚNG ĐẶC TẢ (VIEW GRADES) 👇👇👇
    # =================================================================

    # 1. Lấy danh sách Học kỳ sinh viên đã học (Để làm Dropdown)
    def get_student_semesters(self):
        results = self.db.query(Semester.semesterID, Semester.name)\
            .join(CourseSection, Semester.semesterID == CourseSection.semesterID)\
            .join(GradeReport, CourseSection.sectionID == GradeReport.sectionID)\
            .filter(GradeReport.studentID == self.student_id)\
            .distinct().all()
        return results

    # 2. Tính GPA, CPA và lấy Bảng điểm chi tiết
    def get_academic_results(self, selected_sem_id):
        # A. LẤY TOÀN BỘ ĐIỂM (Để tính CPA Tích lũy)
        all_records = self.db.query(
            Course.credits, GradeReport.total, CourseSection.semesterID
        ).join(CourseSection, GradeReport.sectionID == CourseSection.sectionID)\
         .join(Course, CourseSection.courseID == Course.courseID)\
         .filter(GradeReport.studentID == self.student_id).all()

        # Tính CPA (Tích lũy toàn khóa)
        valid_cpa = [r for r in all_records if r.total is not None]
        total_pts = sum(r.total * r.credits for r in valid_cpa)
        total_cre = sum(r.credits for r in valid_cpa)
        cpa = round(total_pts / total_cre, 2) if total_cre > 0 else 0.0

        # Tính GPA (Học kỳ đang chọn)
        sem_records = [r for r in valid_cpa if r.semesterID == selected_sem_id]
        sem_pts = sum(r.total * r.credits for r in sem_records)
        sem_cre = sum(r.credits for r in sem_records)
        gpa = round(sem_pts / sem_cre, 2) if sem_cre > 0 else 0.0

        # B. LẤY CHI TIẾT BẢNG ĐIỂM CHO HỌC KỲ ĐÓ
        details = self.db.query(
            Course.courseID, Course.courseName, Course.credits,
            GradeReport.midterm, GradeReport.final, GradeReport.total, GradeReport.letterGrade
        ).join(CourseSection, GradeReport.sectionID == CourseSection.sectionID)\
         .join(Course, CourseSection.courseID == Course.courseID)\
         .filter(
             GradeReport.studentID == self.student_id, 
             CourseSection.semesterID == selected_sem_id
         ).all()

        df = pd.DataFrame(details, columns=[
            "Mã MH", "Tên Môn Học", "TC", 
            "Điểm QT", "Điểm CK", "Tổng Kết", "Điểm Chữ"
        ])
        
        # Xử lý dữ liệu trống (Theo đặc tả: Not updated)
        df = df.fillna("Not updated")
        
        return df, gpa, cpa

    # 2. LẤY LỊCH HỌC
    def get_timetable(self):
        try:
            classes = self.db.query(CourseSection, Course)\
                .join(GradeReport, GradeReport.sectionID == CourseSection.sectionID)\
                .join(Course, CourseSection.courseID == Course.courseID)\
                .filter(GradeReport.studentID == self.student_id).all()
            
            data = []
            for sec, course in classes:
                real_time = get_time_string(sec.startPeriod, sec.endPeriod)
                period_str = f"Tiết {sec.startPeriod} - {sec.endPeriod}"
                
                data.append({
                    "Mã Lớp": sec.sectionID,
                    "Môn Học": course.courseName,
                    "Thứ": sec.dayOfWeek,
                    "Ca/Tiết": period_str,
                    "Giờ học": real_time,
                    "Phòng": sec.room,
                    "Giảng viên": sec.lecturerID,
                    "_day_sort": sec.dayOfWeek,
                    "_start_sort": sec.startPeriod
                })
            return data
        finally:
            self.db.close()

    # 3. LẤY TIẾN ĐỘ HỌC TẬP
    def get_progress_data(self):
        try:
            student = self.db.query(Student).filter_by(studentID=self.student_id).first()
            if not student:
                return {"accumulated": 0, "required": 150, "details": []}

            major = self.db.query(Major).filter_by(majorID=student.majorID).first()
            
            all_graded_courses = self.db.query(Course.courseName, Course.credits, GradeReport.total)\
                .join(CourseSection, GradeReport.sectionID == CourseSection.sectionID)\
                .join(Course, CourseSection.courseID == Course.courseID)\
                .filter(GradeReport.studentID == self.student_id)\
                .filter(GradeReport.total != None).all()
            
            accumulated_credits = 0
            details = []

            for pc in all_graded_courses:
                is_passed = pc.total >= 4.0
                status = "✅ Đạt" if is_passed else "❌ Không đạt"
                
                if is_passed:
                    accumulated_credits += pc.credits

                details.append({
                    "Môn học": pc.courseName,
                    "Số tín chỉ": pc.credits,
                    "Điểm": pc.total,
                    "Trạng thái": status
                })
                
            return {
                "accumulated": accumulated_credits,
                "required": major.requiredCredits if major else 0,
                "details": details
            }
        finally:
            self.db.close()

    # 4. CẬP NHẬT THÔNG TIN LIÊN HỆ
    def update_contact_info(self, phone, email, address):
        if not phone or not email or not address:
            return False, "⚠️ Vui lòng điền đầy đủ thông tin!"

        email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(email_pattern, email):
            return False, "⚠️ Định dạng Email không hợp lệ!"

        if not phone.isdigit() or len(phone) < 10 or len(phone) > 11:
            return False, "⚠️ Số điện thoại không hợp lệ!"
        
        try:
            student = self.db.query(Student).filter_by(studentID=self.student_id).first()
            if student:
                student.phone = phone
                student.email = email
                student.address = address
                self.db.commit()
                return True, "✅ Cập nhật thành công!"
            return False, "❌ Không tìm thấy hồ sơ."
        except Exception as e:
            self.db.rollback()
            return False, f"Lỗi: {str(e)}"
        finally:
            self.db.close()

    # 5. LẤY BẢNG ĐIỂM (Dict)
    def get_grade_table(self):
        df = self.get_grade_report(self.student_id)
        if df is not None:
            return df.to_dict('records')
        return []

    # 6. LẤY MÔN ĐỦ ĐIỀU KIỆN PHÚC KHẢO
    def get_reviewable_courses(self):
        try:
            courses = self.db.query(CourseSection.sectionID, Course.courseName)\
                .join(GradeReport, GradeReport.sectionID == CourseSection.sectionID)\
                .join(Course, CourseSection.courseID == Course.courseID)\
                .filter(GradeReport.studentID == self.student_id).all()
            return courses
        finally:
            self.db.close()

    # 7. TẠO YÊU CẦU PHÚC KHẢO
    def create_review_request(self, section_id, reason):
        if not reason or len(reason.strip()) < 10:
            return False, "⚠️ Lý do phúc khảo phải dài hơn 10 ký tự!"

        try:
            existing_req = self.db.query(GradeReviewRequest)\
                .filter(GradeReviewRequest.studentID == self.student_id)\
                .filter(GradeReviewRequest.sectionID == section_id).first()
            
            if existing_req:
                return False, f"⚠️ Bạn đã gửi yêu cầu phúc khảo cho môn này rồi! (Mã đơn: {existing_req.requestID})"

            new_id = f"RQ{int(time.time()) % 1000000}" 
            
            new_req = GradeReviewRequest(
                requestID=new_id,
                studentID=self.student_id,
                sectionID=section_id,
                studentComment=reason,
                status=0,
                createDate=date.today()
            )
            self.db.add(new_req)
            self.db.commit()
            return True, "✅ Đã gửi yêu cầu thành công!"
        except Exception as e:
            self.db.rollback()
            return False, f"Lỗi: {str(e)}"
        finally:
            self.db.close()

    # 8. LẤY LỊCH SỬ PHÚC KHẢO (Đã sửa self.session -> self.db)
    def get_review_history(self, student_id):
        try:
            # Dùng self.db thay vì self.session
            reqs = self.db.query(GradeReviewRequest).filter_by(studentID=student_id).all()
            
            data = []
            for r in reqs:
                sec = self.db.query(CourseSection).get(r.sectionID)
                c_name = "Unknown"
                if sec:
                    course = self.db.query(Course).get(sec.courseID)
                    if course: c_name = course.courseName
                
                status_map = {0: "Chưa xử lý", 1: "Đã duyệt", 2: "Từ chối"}
                
                data.append({
                    "requestID": r.requestID,
                    "sectionID": r.sectionID,
                    "courseName": c_name,
                    "date": r.createDate,
                    "reason": r.studentComment,
                    "status": status_map.get(r.status, "Khác"),
                    "reply": r.lecturerReply
                })
            return data
        except Exception as e:
            print(f"Lỗi history: {e}")
            return []
        finally:
            self.db.close()
            
    # 9. HỦY ĐƠN (Đã sửa self.session -> self.db)
    def cancel_review_request(self, request_id):
        try:
            # Dùng self.db thay vì self.session
            req = self.db.query(GradeReviewRequest).get(request_id)
            if req and req.status == 0: 
                self.db.delete(req)
                self.db.commit()
                return True, "✅ Đã hủy yêu cầu thành công."
            return False, "❌ Không thể hủy (Đơn không tồn tại hoặc GV đã duyệt)."
        except Exception as e:
            self.db.rollback()
            return False, str(e)
        finally:
            self.db.close()