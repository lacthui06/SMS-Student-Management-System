import streamlit as st
from views.login_view import render_login
from views.student_view import render_student_ui
from views.lecturer_view import render_lecturer_ui

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
        # Admin view (chưa implement trong 10 UC này)
        else:
            st.warning("Admin Portal chưa nằm trong phạm vi 10 UC đầu tiên.")
            if st.button("Đăng xuất"):
                st.session_state['user'] = None
                st.rerun()

if __name__ == "__main__":
    main()