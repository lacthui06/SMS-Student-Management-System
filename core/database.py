import streamlit as st
from core.models import * # <--- Dùng * để import đủ 11 class (Admin, Faculty, Semester...)

class MockDatabase:
    def __init__(self):
        if 'db_init' not in st.session_state:
            self._init_data()
            st.session_state['db_init'] = True
        
        # --- Mapping các biến từ Session State ra để Controller dùng ---
        self.users = st.session_state.get('users', {})
        self.courses = st.session_state.get('courses', {})
        self.sections = st.session_state.get('sections', [])
        self.grades = st.session_state.get('grades', [])
        self.requests = st.session_state.get('requests', [])
        self.majors = st.session_state.get('majors', {})
        
        # --- BỔ SUNG MAPPING CHO CLASS MỚI ---
        self.faculties = st.session_state.get('faculties', [])
        self.semesters = st.session_state.get('semesters', [])

    def _init_data(self):
        # 1. Faculties (KHOA - MỚI)
        faculties = [
            Faculty("IT", "Công nghệ Thông tin"),
            Faculty("BA", "Quản trị Kinh doanh")
        ]

        # 2. Majors (NGÀNH)
        majors = {
            "SE": Major("SE", "Kỹ thuật Phần mềm", 150, "IT"),
            "IS": Major("IS", "Hệ thống Thông tin", 145, "IT"),
        }

        # 3. Semesters (HỌC KỲ - MỚI)
        semesters = [
            Semester("HK1_2024", "Học kỳ 1 Năm 2024", "2024-09-05", "2025-01-15")
        ]

        # 4. Users 
        # --- Sửa: Dùng class Admin thay vì Account ---
        admins = {
            "admin": Admin(userID="admin", password="123", role="Admin", fullName="Quản trị viên", email="superstudentmanagementsystem@gmail.com") 
        }

        students = {
            "sv01": Student(
                userID="sv01", password="123", role="Student",
                fullName="Nguyễn Văn An", dob="2003-05-20", pob="TP.HCM",
                citizenID="079203000001", gender="Nam",
                address="123 Nguyễn Văn Cừ, Q5", phone="0909123456", email="thaianhlac06@gmail.com",
                majorID="SE", facultyID="IT"
            ),
            "sv02": Student(
                userID="sv02", password="123", role="Student",
                fullName="Trần Thị Bích", dob="2003-08-15", pob="Đồng Nai",
                citizenID="079203000002", gender="Nữ",
                address="456 Lê Văn Việt, Q9", phone="0909888999", email="bich.tran@sv.edu.vn",
                majorID="IS", facultyID="IT"
            )
        }

        lecturers = {
            "gv01": Lecturer(
                userID="gv01", password="123", role="Lecturer",
                fullName="TS. Lê Văn Chiêu", dob="1980-01-01", pob="Hà Nội",
                citizenID="001080000001", gender="Nam",
                address="Biệt thự số 1, Thảo Điền", phone="0913000111", email="chieu.le@edu.vn",
                degree="Tiến sĩ", position="Trưởng khoa"
            )
        }

        # 5. Courses
        courses = {
            "SE101": Course("SE101", "Nhập môn CNPM", 3),
            "DB201": Course("DB201", "Cơ sở dữ liệu", 4),
            "MATH1": Course("MATH1", "Đại số tuyến tính", 3),
        }

        # 6. Sections
        sections = [
            Section("SE101.N11", "SE101", "gv01", "HK1_2024", "C201", "Thứ 2", 1, 3),
            Section("DB201.N12", "DB201", "gv01", "HK1_2024", "B102", "Thứ 4", 7, 9),
        ]

        # 7. Grades
        grades = [
            GradeReport("sv01", "SE101.N11", 8.0, 8.5),
            GradeReport("sv01", "DB201.N12", 7.5, None),
            GradeReport("sv02", "SE101.N11", 6.0, 7.0),
        ]

        # 8. Requests
        requests = [
            GradeReviewRequest("REQ001", "sv01", "SE101.N11", "Em nghĩ bài thi em làm tốt hơn 8.5", "Pending", "", "2024-01-15")
        ]

        # --- LƯU VÀO SESSION STATE ---
        st.session_state['faculties'] = faculties # <--- Mới
        st.session_state['majors'] = majors
        st.session_state['semesters'] = semesters # <--- Mới
        st.session_state['users'] = {**admins, **students, **lecturers} 
        st.session_state['courses'] = courses
        st.session_state['sections'] = sections
        st.session_state['grades'] = grades
        st.session_state['requests'] = requests
    
    # --- Helper Methods ---
    def get_user(self, user_id): return self.users.get(user_id)
    def get_student_grades(self, student_id): return [g for g in self.grades if g.studentID == student_id]
    def get_course_by_id(self, course_id): return self.courses.get(course_id)
    def get_section_by_id(self, section_id):
        for s in self.sections:
            if s.sectionID == section_id: return s
        return None
    def get_major(self, major_id): return self.majors.get(major_id)
       
       
    # -------- UC 14: LOCK / UNLOCK USER ----------
    def lock_user(self, user_id, reason):
        user = self.users.get(user_id)
        if not user:
            return False, "Không tìm thấy người dùng"
        user.status = "LOCKED"
        user.lock_reason = reason
        return True, "Khóa tài khoản thành công"

    def unlock_user(self, user_id):
        user = self.users.get(user_id)
        if not user:
            return False, "Không tìm thấy người dùng"
        user.status = "ACTIVE"
        if hasattr(user, 'lock_reason'):
            delattr(user, 'lock_reason')
        return True, "Mở khóa tài khoản thành công"

    # -------- UC 15: MANAGE SEMESTER ----------
    def add_semester(self, semester: Semester):
        if any(s.semesterID == semester.semesterID for s in self.semesters):
            return False, "Trùng mã học kỳ"
        self.semesters.append(semester)
        st.session_state['semesters'] = self.semesters
        return True, "Thêm học kỳ thành công"

    def update_semester(self, sem_id, start, end):
        for s in self.semesters:
            if s.semesterID == sem_id:
                s.startDate = start
                s.endDate = end
                return True, "Cập nhật học kỳ thành công"
        return False, "Không tìm thấy học kỳ"

    def delete_semester(self, sem_id):
        for s in self.semesters:
            if s.semesterID == sem_id:
                self.semesters.remove(s)
                return True, "Xóa học kỳ thành công"
        return False, "Không tìm thấy học kỳ"

    # -------- UC 16: MANAGE COURSE ----------
    def update_course(self, course_id, name=None, credits=None):
        course = self.courses.get(course_id)
        if not course:
            return False, "Không tìm thấy môn học"
        if name is not None:
            course.name = name
        if credits is not None:
            course.credits = credits
        return True, "Cập nhật môn học thành công"

    # -------- UC 17: MANAGE SECTION ----------
    def update_section(self, section_id, room=None, day=None, p1=None, p2=None):
        section = self.get_section_by_id(section_id)
        if not section:
            return False, "Không tìm thấy lớp học phần"
        if room is not None:
            section.room = room
        if day is not None:
            section.day = day
        if p1 is not None:
            section.periodStart = p1
        if p2 is not None:
            section.periodEnd = p2
        return True, "Cập nhật lớp học phần thành công"

    # -------- UC 18: CURRICULUM ----------
    def add_curriculum_item(self, major_id, course_id, semester_no, required=True):
        curriculum = st.session_state.get('curriculum', [])
        curriculum.append({
            "majorID": major_id,
            "courseID": course_id,
            "semester": semester_no,
            "required": required
        })
        st.session_state['curriculum'] = curriculum
        return True, "Thêm vào khung chương trình thành công"

    def get_curriculum(self, major_id=None):
        curriculum = st.session_state.get('curriculum', [])
        if major_id:
            curriculum = [c for c in curriculum if c['majorID'] == major_id]
        return curriculum

    # -------- UC 19: CREATE SECTION ----------
    def create_section(self, section: Section):
        if any(s.sectionID == section.sectionID for s in self.sections):
            return False, "Trùng mã lớp học phần"
        self.sections.append(section)
        st.session_state['sections'] = self.sections
        return True, "Tạo lớp học phần thành công"

    # -------- UC 20: CANCEL SECTION ----------
    def cancel_section(self, section_id):
        section = self.get_section_by_id(section_id)
        if not section:
            return False, "Không tìm thấy lớp học phần"
        section.status = "CANCELED"
        return True, "Hủy lớp thành công"

    # -------- UC 21 / 22: COURSE CREATE / DELETE ----------
    def delete_course(self, course_id):
        if course_id not in self.courses:
            return False, "Không tìm thấy môn học"
        del self.courses[course_id]
        st.session_state['courses'] = self.courses
        return True, "Xóa môn học thành công"
