import streamlit as st
from views.login_view import render_login
from views.student_view import render_student_ui
from views.lecturer_view import render_lecturer_ui
from views.admin_view import render_admin_ui

# Config trang
st.set_page_config(page_title="EduSoft LMS", layout="wide", page_icon="🏫")

def main():
    if 'user' not in st.session_state or st.session_state['user'] is None:
        render_login()
    else:
        user = st.session_state['user']
        if user.role == "Student":
            render_student_ui(user)
        elif user.role == "Lecturer":
            render_lecturer_ui(user)
        elif user.role == 'Admin':
            # --- SỬA LỖI Ở ĐÂY ---
            # Code cũ của bạn có thể đang là: st.warning("Admin Portal chưa nằm trong phạm vi...")
            # Hãy thay bằng dòng này:
            render_admin_ui(user) 
        else:
            st.error("Vai trò không hợp lệ.")

if __name__ == "__main__":
    main()