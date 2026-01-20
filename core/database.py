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
            "admin": Admin(userID="admin", password="123", role="Admin", email="superstudentmanagementsystem@gmail.com") 
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