import streamlit as st
import pandas as pd
from controllers.admin_controller import AdminController
from controllers.auth_controller import AuthController

def render_admin_ui(user):
    ctrl = AdminController()
    auth = AuthController()

    if "admin_nav" not in st.session_state: st.session_state.admin_nav = "Dashboard"
    def navigate(page): st.session_state.admin_nav = page
    def logout(): 
        st.session_state.user = None
        st.session_state.admin_nav = "Dashboard"

    st.sidebar.title("🛠️ Admin Portal")
    options = ["Dashboard", "Tài khoản (UC13, 14)", "Học kỳ", "Môn học", "Lớp học phần", "Khung chương trình", "Đổi mật khẩu"]
    
    try:
        idx = options.index(st.session_state.admin_nav)
    except ValueError: idx = 0
        
    menu = st.sidebar.radio("Quản lý", options, index=idx, key="admin_menu_radio")
    
    if menu != st.session_state.admin_nav:
        st.session_state.admin_nav = menu
        st.rerun()

    st.sidebar.button("Đăng xuất", on_click=logout)

    # --- 1. DASHBOARD ---
    if menu == "Dashboard":
        st.title("🚀 Admin Dashboard")
        stats = ctrl.get_stats()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Tổng User", stats["users"])
        c2.metric("Tổng Môn", stats["courses"])
        c3.metric("Lớp HP", stats["sections"])
        c4.metric("Học kỳ", stats["semesters"])
        
        st.divider()
        st.subheader("⚡ Truy cập nhanh")
        c1, c2, c3 = st.columns(3)
        c1.button("👥 Tài khoản", on_click=navigate, args=("Tài khoản (UC13, 14)",), use_container_width=True)
        c2.button("🏫 Lớp học phần", on_click=navigate, args=("Lớp học phần",), use_container_width=True)
        c3.button("📘 Khung CT", on_click=navigate, args=("Khung chương trình",), use_container_width=True)

    # --- 2. QUẢN LÝ TÀI KHOẢN ---
    elif menu == "Tài khoản (UC13, 14)":
        st.title("👥 Quản lý Tài khoản")
        tab1, tab2 = st.tabs(["📥 Import (UC13)", "🔒 Khóa tài khoản (UC14)"])
        with tab1:
            uploaded = st.file_uploader("Chọn file Excel/CSV", type=['xlsx', 'csv'])
            if uploaded:
                df = ctrl.preview_import_users(uploaded)
                if df is not None:
                    st.dataframe(df.head())
                    if st.button("Lưu vào hệ thống"):
                        ok, msg = ctrl.save_import_users(df)
                        st.success(msg) if ok else st.error(msg)
        with tab2:
            search = st.text_input("Nhập mã số hoặc tên để tìm kiếm:").strip()
            if search:
                results = ctrl.get_users_filtered(search)
                if not results: st.warning("Không tìm thấy kết quả.")
                else:
                    opts = {u.userID: f"{u.userID} - {u.fullName} ({u.role})" for u in results}
                    sid = st.selectbox("Chọn tài khoản:", list(opts.keys()), format_func=lambda x: opts[x])
                    target = next((u for u in results if u.userID == sid), None)
                    if target:
                        st.divider()
                        st.write(f"### 👤 {target.fullName}")
                        if target.status:
                            st.success("Trạng thái: ✅ Hoạt động")
                            with st.form("lock_f"):
                                reason = st.text_input("Lý do khóa (Bắt buộc):")
                                if st.form_submit_button("🔒 Khóa tài khoản"):
                                    ok, msg = ctrl.lock_user(target.userID, reason)
                                    if ok: st.success(msg); st.rerun()
                                    else: st.error(msg)
                        else:
                            st.error("Trạng thái: 🔒 Đã khóa")
                            if st.button("🔓 Mở khóa tài khoản"):
                                ok, msg = ctrl.unlock_user(target.userID)
                                if ok: st.success(msg); st.rerun()

    # --- 3. QUẢN LÝ HỌC KỲ ---
    elif menu == "Học kỳ":
        st.title("📅 Quản lý Học kỳ")
        t1, t2 = st.tabs(["Danh sách", "Thêm mới"])
        with t1:
            sems = ctrl.get_all_semesters()
            if sems:
                data = [{"Mã": s.semesterID, "Tên": s.name, "Bắt đầu": s.startDate, "Kết thúc": s.endDate} for s in sems]
                st.dataframe(data, use_container_width=True)
        with t2:
            with st.form("add_sem"):
                sid = st.text_input("Mã HK")
                name = st.text_input("Tên HK")
                c1, c2 = st.columns(2)
                d1, d2 = c1.date_input("Bắt đầu"), c2.date_input("Kết thúc")
                if st.form_submit_button("Lưu"):
                    ok, msg = ctrl.add_semester(sid, name, d1, d2)
                    if ok: st.success(msg); st.rerun()
                    else: st.error(msg)

    # --- 4. QUẢN LÝ MÔN HỌC ---
    elif menu == "Môn học":
        st.title("📚 Quản lý Môn học")
        t1, t2 = st.tabs(["Danh sách", "Thêm mới"])
        courses = ctrl.get_all_courses()
        with t1:
            if courses:
                df = pd.DataFrame([vars(c) for c in courses.values()])
                st.dataframe(df[['courseID', 'courseName', 'credits', 'majorID']], use_container_width=True)
                sel_del = st.selectbox("Chọn môn để xóa", list(courses.keys()))
                if st.button("🗑️ Xóa môn học"):
                    ok, msg = ctrl.delete_course(sel_del)
                    if ok: st.success(msg); st.rerun()
            else: st.info("Trống.")
        with t2:
            majors = ctrl.get_all_majors()
            with st.form("add_c"):
                cid = st.text_input("Mã môn")
                cname = st.text_input("Tên môn")
                cre = st.number_input("Tín chỉ", 1, 10, 3)
                mid = st.selectbox("Thuộc ngành", [m.majorID for m in majors])
                if st.form_submit_button("Thêm môn"):
                    ok, msg = ctrl.add_course(cid, cname, cre, mid)
                    if ok: st.success(msg); st.rerun()

    # --- 5. LỚP HỌC PHẦN ---
    # --- UC 17: LỚP HỌC PHẦN ---
    elif menu == "Lớp học phần":
        # 👇 Layout tiêu đề + Nút quay về (giống bên Student/Lecturer)
        c1, c2 = st.columns([5, 1])
        with c1: 
            st.title("🏫 Quản lý Lớp học phần")
        with c2: 
            # Nút này giúp quay về Dashboard khi bị kẹt
            st.button("⬅️ Trang chủ", on_click=navigate, args=("Dashboard",)) 
        
        tab1, tab2 = st.tabs(["Danh sách lớp", "Mở lớp (Auto Enroll)"])
        
        with tab1:
            secs = ctrl.get_all_sections() # Hàm này giờ đã trả về data đẹp (có giờ)
            if secs:
                df = pd.DataFrame(secs)
                # Hiển thị bảng full chiều rộng
                st.dataframe(df, use_container_width=True)
                
                st.divider()
                # Logic xóa lớp
                all_ids = [s['Mã lớp'] for s in secs]
                if all_ids:
                    sid = st.selectbox("Chọn lớp để hủy:", all_ids)
                    if st.button("❌ Hủy lớp này"):
                        ok, msg = ctrl.cancel_section(sid)
                        if ok: 
                            st.success(msg)
                            st.rerun()
                        else: 
                            st.error(msg)
            else: 
                st.info("Hiện chưa có lớp học phần nào.")

        with tab2:
            st.subheader("Mở lớp & Tự động xếp SV")
            
            # Lấy dữ liệu cho dropdown
            courses = ctrl.get_all_courses()
            sems = ctrl.get_all_semesters()
            lecturers = ctrl.get_all_lecturers()
            majors = ctrl.get_all_majors()

            with st.form("auto_sec"):
                c1, c2 = st.columns(2)
                # Dropdown chọn Môn và GV
                cid = c1.selectbox("Môn học", list(courses.keys()), format_func=lambda x: f"{x} - {courses[x].courseName}")
                lid = c2.selectbox("Giảng viên", [l.lecturerID for l in lecturers], format_func=lambda x: f"{x} - {[l.fullName for l in lecturers if l.lecturerID==x][0]}")
                
                c3, c4 = st.columns(2)
                sem = c3.selectbox("Học kỳ", [s.semesterID for s in sems])
                room = c4.text_input("Phòng học (Bắt buộc)") # <--- Nhập phòng
                
                c5, c6 = st.columns(2)
                day = c5.selectbox("Thứ", ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7"])
                
                # Chọn tiết học
                col_p1, col_p2 = c6.columns(2)
                p1 = col_p1.number_input("Tiết BĐ", 1, 15, 1)
                p2 = col_p2.number_input("Tiết KT", 1, 15, 3)
                
                st.divider()
                st.write("Cấu hình tự động xếp lớp:")
                
                # Chọn ngành để auto enroll
                target_maj = st.selectbox("Sinh viên ngành nào?", [m.majorID for m in majors])
                mx = st.number_input("Sĩ số tối đa", 10, 100, 30)
                sid = st.text_input("Mã lớp (VD: SE01_L01) - Bắt buộc") # <--- Nhập mã lớp
                
                if st.form_submit_button("🚀 Mở lớp ngay"):
                    # Gọi hàm create_section_auto_enroll (đã thêm validate ở trên)
                    ok, msg = ctrl.create_section_auto_enroll(sid, cid, lid, sem, room, day, p1, p2, mx, target_maj)
                    if ok: 
                        st.success(msg)
                        st.rerun()
                    else: 
                        st.error(msg)
    # ---- 5. KHUNG CHƯƠNG TRÌNH ---------
    elif menu == "Khung chương trình":
        majors = ctrl.get_all_majors()
        sel_m = st.selectbox("Chọn ngành", [m.majorID for m in majors])
        
        df = ctrl.get_curriculum(sel_m)
        if not df.empty:
            total_credits = df['credits'].sum() # Tự động tính tổng tín chỉ
            st.success(f"Khung đào tạo ngành {sel_m}: {total_credits} / 120 tín chỉ")
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("Ngành này chưa có môn học nào.")

    # --- 7. ĐỔI MẬT KHẨU ---
    elif menu == "Đổi mật khẩu":
        st.title("🔐 Đổi mật khẩu")
        with st.form("cp"):
            o, n, c = st.text_input("MK cũ", type="password"), st.text_input("MK mới", type="password"), st.text_input("Xác nhận", type="password")
            if st.form_submit_button("Lưu thay đổi"):
                ok, msg = auth.change_password(user.userID, o, n, c)
                st.success(msg) if ok else st.error(msg)