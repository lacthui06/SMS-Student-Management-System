import streamlit as st
import pandas as pd
from controllers.admin_controller import AdminController
from controllers.auth_controller import AuthController

def render_admin_ui(user):
    ctrl = AdminController()
    auth = AuthController() # Để đổi mật khẩu Admin
    
    st.sidebar.title("🛠️ Admin Portal")
    
    # Danh sách chức năng
    options = ["Dashboard", "Học kỳ", "Môn học", "Lớp học phần", "Đổi mật khẩu"]
    if 'admin_nav' not in st.session_state: st.session_state['admin_nav'] = "Dashboard"
    
    def navigate(page): st.session_state['admin_nav'] = page
    def logout(): 
        st.session_state['user'] = None
        st.session_state['admin_nav'] = "Dashboard"

    menu = st.sidebar.radio("Quản lý", options, key="admin_nav")
    st.sidebar.button("Đăng xuất", on_click=logout)

    # --- 1. DASHBOARD ---
    if menu == "Dashboard":
        st.title("🚀 Admin Dashboard")
        
        # Thống kê tổng quan
        stats = ctrl.get_stats()
        with st.container(border=True):
            st.subheader("Thống kê hệ thống")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Tổng User", stats['users'])
            c2.metric("Môn học", stats['courses'])
            c3.metric("Lớp học phần", stats['sections'])
            c4.metric("Học kỳ", stats['semesters'])

        st.divider()
        st.markdown("### ⚡ Quản lý nhanh")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.button("📅 Quản lý Học kỳ", use_container_width=True, on_click=navigate, args=("Học kỳ",))
        with c2:
            st.button("📚 Quản lý Môn học", use_container_width=True, on_click=navigate, args=("Môn học",))
        with c3:
            st.button("🏫 Quản lý Lớp học phần", use_container_width=True, on_click=navigate, args=("Lớp học phần",))
        
        st.markdown("")
        st.button("🔐 Đổi mật khẩu Admin", use_container_width=True, on_click=navigate, args=("Đổi mật khẩu",))

    # --- 2. QUẢN LÝ HỌC KỲ ---
    elif menu == "Học kỳ":
        c1, c2 = st.columns([4,1])
        c1.title("📅 Quản lý Học kỳ")
        c2.button("⬅️ Trang chủ", on_click=navigate, args=("Dashboard",))

        tab1, tab2 = st.tabs(["Danh sách", "Thêm mới"])
        with tab1: st.dataframe(ctrl.db.semesters, use_container_width=True, hide_index=True)
        with tab2:
            with st.form("add_sem"):
                sid = st.text_input("Mã HK (VD: HK2_2024)")
                name = st.text_input("Tên HK")
                d1 = st.date_input("Bắt đầu")
                d2 = st.date_input("Kết thúc")
                if st.form_submit_button("Thêm Học kỳ"):
                    ok, msg = ctrl.add_semester(sid, name, d1, d2)
                    if ok: st.success(msg); st.rerun()
                    else: st.error(msg)

    # --- 3. QUẢN LÝ MÔN HỌC ---
    elif menu == "Môn học":
        c1, c2 = st.columns([4,1])
        c1.title("📚 Quản lý Môn học")
        c2.button("⬅️ Trang chủ", on_click=navigate, args=("Dashboard",))

        tab1, tab2 = st.tabs(["Danh sách", "Thêm mới"])
        with tab1: st.dataframe(ctrl.db.courses, use_container_width=True)
        with tab2:
            with st.form("add_course"):
                cid = st.text_input("Mã Môn").upper()
                cname = st.text_input("Tên Môn")
                cre = st.number_input("Tín chỉ", 1, 10, 3)
                if st.form_submit_button("Thêm Môn"):
                    ok, msg = ctrl.add_course(cid, cname, cre)
                    if ok: st.success(msg); st.rerun()
                    else: st.error(msg)

    # --- 4. QUẢN LÝ LỚP HỌC PHẦN ---
    elif menu == "Lớp học phần":
        c1, c2 = st.columns([4,1])
        c1.title("🏫 Quản lý Lớp học phần")
        c2.button("⬅️ Trang chủ", on_click=navigate, args=("Dashboard",))

        tab1, tab2 = st.tabs(["Danh sách lớp", "Mở lớp mới"])
        with tab1: 
            st.dataframe(pd.DataFrame(ctrl.db.sections), use_container_width=True)

        with tab2:
            courses = ctrl.db.courses
            users = ctrl.db.users
            lecs = {uid: u for uid, u in users.items() if u.role == 'Lecturer'}
            
            with st.form("open_sec"):
                st.subheader("Thông tin lớp học")
                if not courses or not lecs:
                    st.warning("Cần có dữ liệu Môn học và Giảng viên trước.")
                    st.form_submit_button("Mở Lớp", disabled=True)
                else:
                    c_opt = [f"{c.courseID} - {c.courseName}" for c in courses.values()]
                    l_opt = [f"{l.userID} - {l.fullName}" for l in lecs.values()]
                    
                    c1, c2 = st.columns(2)
                    sel_c = c1.selectbox("Môn học", c_opt)
                    sel_l = c2.selectbox("Giảng viên", l_opt)
                    
                    c3, c4 = st.columns(2)
                    room = c3.text_input("Phòng học", "C101")
                    day = c4.selectbox("Thứ", ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7"])
                    
                    c5, c6 = st.columns(2)
                    p1 = c5.number_input("Tiết BĐ", 1, 12, 1)
                    p2 = c6.number_input("Tiết KT", 1, 12, 3)
                    
                    cid = sel_c.split(" - ")[0]
                    lid = sel_l.split(" - ")[0]
                    suggest_id = f"{cid}.N{len(ctrl.db.sections)+1:02d}"
                    sid = st.text_input("Mã Lớp (Tự sinh)", suggest_id)
                    
                    if st.form_submit_button("Mở Lớp"):
                        cname = sel_c.split(" - ")[1]
                        ok, msg = ctrl.add_section(sid, cid, cname, lid, room, day, p1, p2)
                        if ok: st.success(msg); st.rerun()
                        else: st.error(msg)
    
    # --- 5. ĐỔI MẬT KHẨU (UC2) ---
    elif menu == "Đổi mật khẩu":
        c1, c2 = st.columns([4, 1])
        c1.title("🔐 Đổi mật khẩu Admin")
        c2.button("⬅️ Trang chủ", on_click=navigate, args=("Dashboard",))

        with st.form("change_pass_admin"):
            o = st.text_input("Mật khẩu cũ", type="password")
            n = st.text_input("Mật khẩu mới", type="password")
            c = st.text_input("Xác nhận mật khẩu mới", type="password")
            if st.form_submit_button("Lưu thay đổi"):
                ok, msg = auth.change_password(user.userID, o, n, c)
                if ok: st.success(msg)
                else: st.error(msg)