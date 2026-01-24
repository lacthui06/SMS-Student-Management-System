import pandas as pd
from sqlalchemy import or_
from core.database import Session
from core.models_orm import (
    Account, Student, Lecturer, Admin, 
    Semester, Major, Course, CourseSection, GradeReport
)
from core.utils import get_time_string

class AdminController:
    def __init__(self):
        self.session = Session()

    def __del__(self):
        self.session.close()

    def get_stats(self):
        try:
            return {
                "users": self.session.query(Account).count(),
                "courses": self.session.query(Course).count(),
                "sections": self.session.query(CourseSection).count(),
                "semesters": self.session.query(Semester).count()
            }
        except Exception:
            return {"users": 0, "courses": 0, "sections": 0, "semesters": 0}

    # --- UC 13: IMPORT USERS ---
    def preview_import_users(self, uploaded_file):
        if uploaded_file is None: return None
        try:
            if uploaded_file.name.endswith('.csv'): df = pd.read_csv(uploaded_file)
            else: df = pd.read_excel(uploaded_file)
            return df
        except Exception: return None

    def save_import_users(self, df):
        count = 0
        try:
            for index, row in df.iterrows():
                uid = str(row['UserID'])
                existing_user = self.session.query(User).filter_by(userID=uid).first()
                if existing_user: continue

                new_u = None
                if row['Role'] == 'Student':
                    new_u = Student(userID=uid, password=str(row['Password']), fullName=row['FullName'], email=row['Email'])
                elif row['Role'] == 'Lecturer':
                    new_u = Lecturer(userID=uid, password=str(row['Password']), fullName=row['FullName'], email=row['Email'])
                
                if new_u:
                    self.session.add(new_u)
                    count += 1
            self.session.commit()
            return True, f"Import thành công {count} tài khoản."
        except Exception as e:
            self.session.rollback()
            return False, f"Lỗi Import: {str(e)}"

    # --- UC 14: LOCK USER ---
    def get_users_filtered(self, search_term=""):
        query = self.session.query(User)
        if search_term:
            term = f"%{search_term.strip()}%"
            query = query.filter(or_(User.userID.like(term), User.fullName.like(term)))
        return query.all()

    def lock_user(self, user_id, reason):
        if not reason or not reason.strip(): return False, "Vui lòng nhập lý do."
        try:
            user = self.session.query(User).get(user_id)
            if user:
                user.status = False
                self.session.commit()
                return True, "Đã khóa tài khoản."
            return False, "Không tìm thấy user."
        except Exception as e:
            return False, str(e)

    def unlock_user(self, user_id):
        try:
            user = self.session.query(User).get(user_id)
            if user:
                user.status = True
                self.session.commit()
                return True, "Đã mở khóa."
            return False, "Không tìm thấy."
        except Exception as e:
            return False, str(e)

    # --- QUẢN LÝ HỌC KỲ ---
    def get_all_semesters(self):
        return self.session.query(Semester).all()

    def add_semester(self, sem_id, name, start, end):
        if start >= end: return False, "Ngày kết thúc phải sau ngày bắt đầu."
        try:
            if self.session.query(Semester).get(sem_id): return False, "Mã HK đã tồn tại."
            new_sem = Semester(semesterID=sem_id, name=name, startDate=start, endDate=end)
            self.session.add(new_sem)
            self.session.commit()
            return True, "Thêm học kỳ thành công."
        except Exception as e:
            return False, str(e)

    # --- QUẢN LÝ MÔN HỌC & NGÀNH ---
    def get_all_courses(self):
        courses = self.session.query(Course).all()
        return {c.courseID: c for c in courses}

    def get_all_majors(self):
        return self.session.query(Major).all()
    
    def get_all_lecturers(self):
        return self.session.query(Lecturer).all()

    def add_course(self, cid, cname, credits, major_id):
        # 👇 THÊM CÁC DÒNG KIỂM TRA NÀY
        if not cid or len(cid.strip()) == 0:
            return False, "❌ Mã môn học không được để trống!"
        if not cname or len(cname.strip()) == 0:
            return False, "❌ Tên môn học không được để trống!"
        if credits <= 0:
            return False, "❌ Số tín chỉ phải lớn hơn 0!"
            
        try:
            if self.session.query(Course).get(cid): 
                return False, "❌ Mã môn học đã tồn tại!"
            
            new_c = Course(courseID=cid, courseName=cname, credits=credits, majorID=major_id)
            self.session.add(new_c)
            self.session.commit()
            return True, "✅ Thêm môn học thành công!"
        except Exception as e:
            self.session.rollback()
            return False, str(e)

    def delete_course(self, cid):
        try:
            c = self.session.query(Course).get(cid)
            if c:
                self.session.delete(c)
                self.session.commit()
                return True, "Đã xóa môn học thành công."
            return False, "Không tìm thấy môn học."
        except Exception:
            return False, "Không thể xóa do có dữ liệu liên quan (lớp học phần/điểm)."

    # --- QUẢN LÝ LỚP HỌC PHẦN ---
    def get_all_sections(self):
        secs = self.session.query(CourseSection).all()
        data = []
        for s in secs:
            # Convert sang dict và format lại dữ liệu cho View
            data.append({
                "Mã lớp": s.sectionID,
                "Môn học": s.courseID,
                "Giảng viên": s.lecturerID,
                "Phòng": s.room,
                "Thứ": s.dayOfWeek,
                # Gọi hàm get_time_string để hiện giờ thay vì tiết số
                "Thời gian": get_time_string(s.startPeriod, s.endPeriod) 
            })
        return data

    def cancel_section(self, sid):
        try:
            s = self.session.query(CourseSection).get(sid)
            if s:
                self.session.delete(s)
                self.session.commit()
                return True, "Đã hủy lớp học phần thành công."
            return False, "Không tìm thấy lớp học phần."
        except Exception as e:
            return False, str(e)

    def create_section_auto_enroll(self, sid, cid, lid, sem, room, day, p1, p2, max_slot, target_major):
        # 1. VALIDATION CƠ BẢN
        if not sid or not sid.strip(): return False, "❌ Mã lớp trống!"
        if not room or not room.strip(): return False, "❌ Phòng trống!"
        if p1 >= p2: return False, "❌ Tiết BĐ phải nhỏ hơn Tiết KT!"

        try:
            # 2. KIỂM TRA TRÙNG MÃ LỚP
            if self.session.query(CourseSection).get(sid): 
                return False, f"❌ Lỗi: Mã lớp '{sid}' đã tồn tại."

            # 3. 👇 CHECK TRÙNG LỊCH HỌC (QUAN TRỌNG)
            # Tìm các lớp cùng Học kỳ, cùng Phòng, cùng Thứ
            conflicts = self.session.query(CourseSection).filter(
                CourseSection.semesterID == sem,
                CourseSection.room == room,
                CourseSection.dayOfWeek == day
            ).all()

            for c in conflicts:
                # Công thức check giao nhau: (StartA <= EndB) và (EndA >= StartB)
                if (p1 <= c.endPeriod) and (p2 >= c.startPeriod):
                    return False, f"❌ Trùng lịch! Phòng {room} đã có lớp {c.sectionID} học tiết {c.startPeriod}-{c.endPeriod}."

            # 4. KIỂM TRA SỐ LƯỢNG SINH VIÊN TRƯỚC
            candidates = self.session.query(Student)\
                .filter_by(majorID=target_major)\
                .order_by(Student.fullName.asc())\
                .limit(max_slot).all()

            if not candidates:
                return False, f"⚠️ Không tìm thấy sinh viên nào thuộc ngành '{target_major}' để xếp lớp! Vui lòng kiểm tra lại Data."

            # 5. TẠO LỚP (Nếu mọi thứ OK)
            new_sec = CourseSection(
                sectionID=sid, courseID=cid, lecturerID=lid, semesterID=sem,
                room=room, dayOfWeek=day, startPeriod=p1, endPeriod=p2, maxSlot=max_slot,
                currentSlot=len(candidates), status=1
            )
            self.session.add(new_sec)
            
            # 6. XẾP SINH VIÊN VÀO
            count = 0
            for stu in candidates:
                reg = GradeReport(studentID=stu.studentID, sectionID=sid, midterm=0, final=0)
                self.session.add(reg)
                count += 1
            
            self.session.commit()
            return True, f"✅ Thành công! Tạo lớp {sid} và xếp {count} SV ngành {target_major}."

        except Exception as e:
            self.session.rollback()
            return False, f"Lỗi hệ thống: {str(e)}"

    # --- UC 18: KHUNG CHƯƠNG TRÌNH (CÁCH A: LẤY TỪ COURSE) ---
    def get_curriculum(self, major_id):
        # Lấy môn học trực tiếp từ bảng Course dựa trên majorID
        data = self.session.query(Course).filter_by(majorID=major_id).all()
        # Chuyển đổi thành DataFrame để hiển thị
        result = []
        for c in data:
            result.append({
                "courseID": c.courseID,
                "courseName": c.courseName,
                "credits": c.credits,
                "required": True
            })
        return pd.DataFrame(result)