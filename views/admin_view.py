import streamlit as st
import pandas as pd
from controllers.admin_controller import AdminController
from controllers.auth_controller import AuthController

def render_admin_ui(user):
    ctrl = AdminController()
    auth = AuthController() # Để đổi mật khẩu Admin
    
    st.sidebar.title("🛠️ Admin Portal")
    
    # --- CẬP NHẬT MENU: Thêm "Tài khoản" (UC 13) ---
    options = ["Dashboard", "Tài khoản", "Học kỳ", "Môn học", "Lớp học phần", "Đổi mật khẩu"]
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
        
        # Cập nhật thêm nút Quản lý Tài khoản vào Dashboard
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.button("👥 QL Tài khoản", use_container_width=True, on_click=navigate, args=("Tài khoản",))
        with c2:
            st.button("📅 QL Học kỳ", use_container_width=True, on_click=navigate, args=("Học kỳ",))
        with c3:
            st.button("📚 QL Môn học", use_container_width=True, on_click=navigate, args=("Môn học",))
        with c4:
            st.button("🏫 QL Lớp HP", use_container_width=True, on_click=navigate, args=("Lớp học phần",))
        
        st.markdown("")
        st.button("🔐 Đổi mật khẩu Admin", use_container_width=True, on_click=navigate, args=("Đổi mật khẩu",))

    # --- 2. QUẢN LÝ TÀI KHOẢN (UC 13: Import User) ---
    elif menu == "Tài khoản":
        c1, c2 = st.columns([4,1])
        c1.title("👥 Quản lý Tài khoản")
        c2.button("⬅️ Trang chủ", on_click=navigate, args=("Dashboard",))

        tab1, tab2 = st.tabs(["Danh sách User", "Import từ Excel (UC13)"])
        
        with tab1:
            # Hiển thị danh sách user hiện có
            if hasattr(ctrl.db, 'users'):
                # Chuyển đổi dict users thành list để hiển thị
                users_data = [
                    {"ID": u.userID, "Họ tên": u.fullName, "Vai trò": u.role, "Email": u.email} 
                    for u in ctrl.db.users.values()
                ]
                st.dataframe(pd.DataFrame(users_data), use_container_width=True)
            else:
                st.info("Chưa có dữ liệu người dùng.")

        with tab2:
            st.subheader("Import User Accounts (Batch) - UC13")
            st.markdown("Tải lên file Excel/CSV chứa danh sách tài khoản. Cấu trúc file cần có các cột: `UserID`, `FullName`, `Role`, `Email`.")
            
            uploaded_file = st.file_uploader("Chọn file", type=['csv', 'xlsx'])
            
            if uploaded_file is not None:
                try:
                    if uploaded_file.name.endswith('.csv'):
                        df = pd.read_csv(uploaded_file)
                    else:
                        df = pd.read_excel(uploaded_file)
                    
                    st.write("Xem trước dữ liệu:")
                    st.dataframe(df.head())
                    
                    if st.button("🚀 Thực hiện Import"):
                        # Gọi hàm import từ controller (Đảm bảo AdminController đã có hàm này)
                        if hasattr(ctrl, 'import_users_batch'):
                            ok, msg = ctrl.import_users_batch(df)
                            if ok: 
                                st.success(msg)
                                st.rerun()
                            else: st.error(msg)
                        else:
                            st.error("Lỗi: AdminController chưa cập nhật hàm 'import_users_batch'.")
                except Exception as e:
                    st.error(f"Lỗi đọc file: {e}")

    elif menu == "Học kỳ":
        c1, c2 = st.columns([4,1])
        c1.title("📅 Quản lý Học kỳ")
        c2.button("⬅️ Trang chủ", on_click=navigate, args=("Dashboard",))

        tab1, tab2 = st.tabs(["Danh sách", "Thêm mới"])
        
        with tab1: 
            # --- FIX LỖI Ở ĐÂY: Dùng hàm get_all_semesters() ---
            df_sem = ctrl.get_all_semesters()
            st.dataframe(df_sem, use_container_width=True, hide_index=True)
            
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

    # --- 4. QUẢN LÝ MÔN HỌC (Giữ nguyên) ---
    elif menu == "Môn học":
        # ... (Code cũ của bạn) ...
        pass # Placeholder

    # --- 5. QUẢN LÝ LỚP HỌC PHẦN ---
    elif menu == "Lớp học phần":
        c1, c2 = st.columns([4,1])
        c1.title("🏫 Quản lý Lớp học phần")
        c2.button("⬅️ Trang chủ", on_click=navigate, args=("Dashboard",))

        tab1, tab2 = st.tabs(["Danh sách lớp", "Mở lớp mới"])
        with tab1: 
            # --- FIX: Dùng hàm get_all_sections() ---
            data_sec = ctrl.get_all_sections()
            if data_sec:
                 st.dataframe(pd.DataFrame(data_sec), use_container_width=True)
            else:
                 st.info("Chưa có lớp nào.")

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
    
    # --- 6. ĐỔI MẬT KHẨU ---
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