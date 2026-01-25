import streamlit as st
import pandas as pd
from controllers.admin_controller import AdminController
from controllers.auth_controller import AuthController

def render_admin_ui(user):
    ctrl = AdminController()
    auth = AuthController()

    # --- 1. CẤU HÌNH NAV ---
    if "admin_nav" not in st.session_state: 
        st.session_state['admin_nav'] = "Dashboard"
    
    # Hàm điều hướng trực tiếp
    def navigate(page): 
        st.session_state['admin_nav'] = page
        st.rerun()
        
    def logout(): 
        st.session_state['user'] = None
        st.session_state['admin_nav'] = "Dashboard"
        st.rerun()

    # --- SIDEBAR ---
    st.sidebar.title("🛠️ Admin Portal")
    st.sidebar.write(f"Xin chào, {user.userID}")
    
    options = ["Dashboard", "Tài khoản", "Học kỳ", "Môn học", "Lớp học phần", "Khung chương trình", "Đổi mật khẩu"]
    
    try: idx = options.index(st.session_state['admin_nav'])
    except: idx = 0
        
    menu = st.sidebar.radio("Quản lý", options, index=idx)
    
    # Logic đồng bộ
    if menu != st.session_state['admin_nav']:
        st.session_state['admin_nav'] = menu
        st.rerun()

    if st.sidebar.button("Đăng xuất"): logout()

    # --- HEADER HELPER ---
    def render_header(title):
        c1, c2 = st.columns([5, 1])
        c1.title(title)
        # Nút Back dùng if st.button
        if c2.button("⬅️ Trang chủ", key=f"bk_{title}"):
            navigate("Dashboard")
        st.divider()

    # ========================================================
    # NỘI DUNG CHÍNH
    # ========================================================

    # --- 1. DASHBOARD ---
    if menu == "Dashboard":
        st.title("🚀 Admin Dashboard")
        
        # Stats
        try:
            if hasattr(ctrl, 'get_stats'): stats = ctrl.get_stats()
            else: stats = {"users": 0, "courses": 0, "sections": 0, "semesters": 0}
        except: stats = {"users": 0, "courses": 0, "sections": 0, "semesters": 0}

        with st.container(border=True):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Tổng User", stats.get("users", 0), "👤")
            c2.metric("Tổng Môn", stats.get("courses", 0), "📚")
            c3.metric("Lớp HP", stats.get("sections", 0), "🏫")
            c4.metric("Học kỳ", stats.get("semesters", 0), "📅")
        
        st.subheader("⚡ Truy cập nhanh")
        
        # 👇 SỬA LẠI THEO PHONG CÁCH STUDENT (IF ST.BUTTON)
        c1, c2, c3 = st.columns(3)
        with c1: 
            if st.button("👥 Tài khoản", use_container_width=True, key="qa_acc"): navigate("Tài khoản (UC13, 14)")
        with c2: 
            if st.button("📅 Quản lý Học kỳ", use_container_width=True, key="qa_sem"): navigate("Học kỳ")
        with c3: 
            if st.button("📚 Quản lý Môn học", use_container_width=True, key="qa_cou"): navigate("Môn học")
            
        c4, c5, c6 = st.columns(3)
        with c4: 
            if st.button("🏫 Lớp học phần", use_container_width=True, key="qa_sec"): navigate("Lớp học phần")
        with c5: 
            if st.button("🎓 Khung chương trình", use_container_width=True, key="qa_cur"): navigate("Khung chương trình")
        with c6: 
            if st.button("🔐 Đổi mật khẩu", use_container_width=True, key="qa_pass"): navigate("Đổi mật khẩu")

    # --- 2. TÀI KHOẢN ---
    elif menu == "Tài khoản":
        render_header("👥 Quản lý Tài khoản")
        tab1, tab2 = st.tabs(["📥 Import", "🔒 Khóa tài khoản"])
        
        with tab1:
            st.info("Hỗ trợ file Excel/CSV.")
            uploaded = st.file_uploader("Upload danh sách User", type=['xlsx', 'csv'])
            if uploaded:
                df = ctrl.preview_import_users(uploaded)
                if df is not None:
                    st.dataframe(df.head(), use_container_width=True)
                    if st.button("Lưu vào hệ thống", type="primary"):
                        # Gọi hàm mới (nhận về count và errors)
                        count, errors = ctrl.save_import_users(df)
                        
                        # 1. Thông báo thành công
                        if count > 0:
                            st.success(f"✅ Đã import thành công {count} tài khoản mới!")
                        else:
                            st.warning("⚠️ Không có tài khoản mới nào được thêm.")

                        # 2. HIỂN THỊ DANH SÁCH LỖI (Quan trọng)
                        if errors:
                            st.error(f"❌ Có {len(errors)} dòng bị lỗi/trùng lặp (đã bỏ qua):")
                            # Hiện danh sách lỗi trong khung cho dễ nhìn
                            with st.expander("Xem chi tiết lỗi", expanded=True):
                                for err in errors:
                                    st.write(f"- {err}")
        with tab2:
            search = st.text_input("🔍 Tìm kiếm User:")
            if search:
                results = ctrl.get_users_filtered(search)
                if not results: st.warning("Không tìm thấy.")
                else:
                    opts = {u.userID: f"{u.userID} - {u.fullName} ({u.role})" for u in results}
                    sid = st.selectbox("Chọn tài khoản:", list(opts.keys()), format_func=lambda x: opts[x])
                    target = next((u for u in results if u.userID == sid), None)
                    if target:
                        st.markdown(f"**Trạng thái:** {'✅ Active' if target.status else '🔒 Locked'}")
                        if target.status:
                            with st.form("lock_u"):
                                r = st.text_input("Lý do khóa:")
                                if st.form_submit_button("🔒 Khóa ngay"):
                                    ok, m = ctrl.lock_user(target.userID, r)
                                    if ok: st.success(m); st.rerun()
                                    else: st.error(m)
                        else:
                            if st.button("🔓 Mở khóa"):
                                ok, m = ctrl.unlock_user(target.userID)
                                if ok: st.success(m); st.rerun()

    # --- 3. HỌC KỲ ---
    elif menu == "Học kỳ":
        render_header("📅 Quản lý Học kỳ")
        t1, t2 = st.tabs(["Danh sách", "Thêm mới"])
        with t1:
            sems = ctrl.get_all_semesters()
            if sems:
                data = [{"Mã": s.semesterID, "Tên": s.name, "Bắt đầu": s.startDate, "Kết thúc": s.endDate} for s in sems]
                st.dataframe(data, use_container_width=True)
            else: st.info("Trống")
        with t2:
            with st.form("add_s"):
                sid = st.text_input("Mã HK"); name = st.text_input("Tên HK")
                d1 = st.date_input("Bắt đầu"); d2 = st.date_input("Kết thúc")
                if st.form_submit_button("Lưu"):
                    ctrl.add_semester(sid, name, d1, d2); st.rerun()

    # --- 4. MÔN HỌC ---
    elif menu == "Môn học":
        render_header("📚 Quản lý Môn học")
        t1, t2 = st.tabs(["Danh sách", "Thêm mới"])
        with t1:
            courses = ctrl.get_all_courses()
            if courses:
                c_list = [{"Mã": c.courseID, "Tên": c.courseName, "Tín chỉ": c.credits, "Ngành": c.majorID} for c in courses.values()]
                st.dataframe(c_list, use_container_width=True)
                sel_del = st.selectbox("Chọn môn xóa:", list(courses.keys()))
                if st.button("🗑️ Xóa môn"):
                    ctrl.delete_course(sel_del); st.rerun()
        with t2:
            majors = ctrl.get_all_majors()
            with st.form("add_c"):
                cid = st.text_input("Mã môn"); cname = st.text_input("Tên môn")
                cre = st.number_input("Tín chỉ", 1, 10, 3)
                mid = st.selectbox("Ngành", [m.majorID for m in majors])
                if st.form_submit_button("Thêm"):
                    ctrl.add_course(cid, mid, cname, cre); st.rerun()

    # --- 5. LỚP HỌC PHẦN ---
    elif menu == "Lớp học phần":
        render_header("🏫 Quản lý Lớp học phần")
        tab1, tab2 = st.tabs(["Danh sách", "Mở lớp"])
        with tab1:
            st.dataframe(ctrl.get_all_sections(), use_container_width=True)
            secs = ctrl.get_all_sections()
            if secs:
                all_ids = [s['Mã lớp'] for s in secs]
                sid_del = st.selectbox("Chọn lớp hủy:", all_ids)
                if st.button("❌ Hủy lớp"):
                    ok, msg = ctrl.cancel_section(sid_del)
                    if ok: st.success(msg); st.rerun()
                    else: st.error(msg)

        with tab2:
            st.subheader("Mở lớp (Auto Enroll)")
            courses = ctrl.get_all_courses()
            sems = ctrl.get_all_semesters()
            lecturers = ctrl.get_all_lecturers()
            majors = ctrl.get_all_majors()
            with st.form("auto_s"):
                c1, c2 = st.columns(2)
                cid = c1.selectbox("Môn", list(courses.keys()))
                lid = c2.selectbox("GV", [l.lecturerID for l in lecturers])
                sem = st.selectbox("HK", [s.semesterID for s in sems])
                room = st.text_input("Phòng")
                c3, c4 = st.columns(2)
                day = c3.selectbox("Thứ", ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7"])
                p1 = c4.number_input("Tiết BĐ", 1, 15, 1); p2 = c4.number_input("Tiết KT", 1, 15, 3)
                target_maj = st.selectbox("Ngành SV", [m.majorID for m in majors])
                mx = st.number_input("Max SV", 10, 100, 30)
                sid_input = st.text_input("Mã Lớp")
                if st.form_submit_button("🚀 Mở lớp"):
                    ok, msg = ctrl.create_section_auto_enroll(sid_input, cid, lid, sem, room, day, p1, p2, mx, target_maj)
                    if ok: st.success(msg); st.rerun()
                    else: st.error(msg)

    # --- 6. KHUNG CHƯƠNG TRÌNH ---
    elif menu == "Khung chương trình":
        render_header("🎓 Khung chương trình")
        majors = ctrl.get_all_majors()
        m = st.selectbox("Chọn ngành", [x.majorID for x in majors])
        df = ctrl.get_curriculum(m)
        if not df.empty:
            st.success(f"Tổng tín chỉ: {df['credits'].sum()}")
            st.dataframe(df, use_container_width=True)
        else: st.warning("Chưa có môn.")

    # --- 7. ĐỔI MẬT KHẨU ---
    elif menu == "Đổi mật khẩu":
        render_header("🔐 Đổi mật khẩu")
        with st.form("adm_cp"):
            o = st.text_input("Mật khẩu cũ", type="password")
            n = st.text_input("Mật khẩu mới", type="password")
            c = st.text_input("Xác nhận", type="password")
            if st.form_submit_button("Lưu thay đổi"):
                ok, msg = auth.change_password(user.userID, o, n, c)
                if ok: st.success(msg); st.rerun()
                else: st.error(msg)