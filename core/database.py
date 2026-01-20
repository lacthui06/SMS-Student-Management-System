# core/database.py
import streamlit as st
from core.models import Account, Student, Lecturer, Major, Course, Section, GradeReport, GradeReviewRequest

class MockDatabase:
    def __init__(self):
        if 'db_init' not in st.session_state:
            self._init_data()
            st.session_state['db_init'] = True

    def _init_data(self):
        # 1. Majors
        majors = {
            "SE": Major("SE", "Kỹ thuật Phần mềm", 150, "IT"),
            "IS": Major("IS", "Hệ thống Thông tin", 145, "IT"),
        }

        # 2. Users 
        # --- QUAN TRỌNG: Thêm email cho Admin để test UC3 ---
        admins = {
            "admin": Account(userID="admin", password="123", role="Admin", email="superstudentmanagementsystem@gmail.com") 
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

        # 3. Courses
        courses = {
            "SE101": Course("SE101", "Nhập môn CNPM", 3),
            "DB201": Course("DB201", "Cơ sở dữ liệu", 4),
            "MATH1": Course("MATH1", "Đại số tuyến tính", 3),
        }

        # 4. Sections
        sections = [
            Section("SE101.N11", "SE101", "gv01", "HK1_2024", "C201", "Thứ 2", 1, 3),
            Section("DB201.N12", "DB201", "gv01", "HK1_2024", "B102", "Thứ 4", 7, 9),
        ]

        # 5. Grades
        grades = [
            GradeReport("sv01", "SE101.N11", 8.0, 8.5),
            GradeReport("sv01", "DB201.N12", 7.5, None),
            GradeReport("sv02", "SE101.N11", 6.0, 7.0),
        ]

        # 6. Requests
        requests = [
            GradeReviewRequest("REQ001", "sv01", "SE101.N11", "Em nghĩ bài thi em làm tốt hơn 8.5", "Pending", "", "2024-01-15")
        ]

        # Lưu vào Session
        st.session_state['majors'] = majors
        # GỘP USER
        st.session_state['users'] = {**admins, **students, **lecturers} 
        st.session_state['courses'] = courses
        st.session_state['sections'] = sections
        st.session_state['grades'] = grades
        st.session_state['requests'] = requests
    
    # ... (Các hàm helper giữ nguyên như cũ) ...
    def get_user(self, user_id): return st.session_state['users'].get(user_id)
    def get_student_grades(self, student_id): return [g for g in st.session_state['grades'] if g.studentID == student_id]
    def get_course_by_id(self, course_id): return st.session_state['courses'].get(course_id)
    def get_section_by_id(self, section_id):
        for s in st.session_state['sections']:
            if s.sectionID == section_id: return s
        return None
    def get_major(self, major_id): return st.session_state['majors'].get(major_id)