import streamlit as st
import pandas as pd
import time  # 👈 BẮT BUỘC ĐỂ HIỆN THÔNG BÁO
from controllers.admin_controller import AdminController
from controllers.auth_controller import AuthController

def render_admin_ui(user):
    ctrl = AdminController()
    auth = AuthController()

    # --- 1. CẤU HÌNH NAV ---
    if "admin_nav" not in st.session_state: 
        st.session_state['admin_nav'] = "Dashboard"
    
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
        if c2.button("⬅️ Trang chủ", key=f"bk_{title}"):
            navigate("Dashboard")
        st.divider()

    # ========================================================
    # NỘI DUNG CHÍNH
    # ========================================================

    # --- 1. DASHBOARD ---
    if menu == "Dashboard":
        st.title("🚀 Admin Dashboard")
        try:
            stats = ctrl.get_stats() if hasattr(ctrl, 'get_stats') else {}
        except: stats = {}

        with st.container(border=True):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Tổng User", stats.get("users", 0), "👤")
            c2.metric("Tổng Môn", stats.get("courses", 0), "📚")
            c3.metric("Lớp HP", stats.get("sections", 0), "🏫")
            c4.metric("Học kỳ", stats.get("semesters", 0), "📅")
        
        st.subheader("⚡ Truy cập nhanh")
        c1, c2, c3 = st.columns(3)
        with c1: 
            if st.button("👥 Tài khoản", use_container_width=True): navigate("Tài khoản")
        with c2: 
            if st.button("📅 Quản lý Học kỳ", use_container_width=True): navigate("Học kỳ")
        with c3: 
            if st.button("📚 Quản lý Môn học", use_container_width=True): navigate("Môn học")
            
        c4, c5, c6 = st.columns(3)
        with c4: 
            if st.button("🏫 Lớp học phần", use_container_width=True): navigate("Lớp học phần")
        with c5: 
            if st.button("🎓 Khung chương trình", use_container_width=True): navigate("Khung chương trình")
        with c6: 
            if st.button("🔐 Đổi mật khẩu", use_container_width=True): navigate("Đổi mật khẩu")

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
                        count, errors = ctrl.save_import_users(df)
                        if count > 0:
                            st.success(f"✅ Đã import thành công {count} tài khoản mới!")
                        else:
                            st.warning("⚠️ Không có tài khoản mới nào được thêm.")
                        
                        if errors:
                            st.error(f"❌ Có {len(errors)} dòng lỗi:")
                            with st.expander("Xem chi tiết lỗi", expanded=True):
                                for err in errors: st.write(f"- {err}")
        with tab2:
            search = st.text_input("🔍 Tìm kiếm User:")
            if search:
                results = ctrl.get_users_filtered(search)
                if not results: 
                    st.warning("Không tìm thấy.")
                else:
                    opts = {u.userID: f"{u.userID} (Quyền: {u.role})" for u in results}
                    sid = st.selectbox("Chọn tài khoản:", list(opts.keys()), format_func=lambda x: opts[x])
                    target = next((u for u in results if u.userID == sid), None)
                    if target:
                        st.markdown(f"**Trạng thái:** {'✅ Active' if target.status else '🔒 Locked'}")
                        if target.status:
                            with st.form("lock_u"):
                                r = st.text_input("Lý do khóa:")
                                if st.form_submit_button("🔒 Khóa ngay"):
                                    ok, m = ctrl.lock_user(target.userID, r)
                                    if ok: 
                                        st.success(m)
                                        time.sleep(1)
                                        st.rerun()
                                    else: st.error(m)
                        else:
                            if st.button("🔓 Mở khóa"):
                                ok, m = ctrl.unlock_user(target.userID)
                                if ok: 
                                    st.success(m)
                                    time.sleep(1)
                                    st.rerun()

    # --- 3. HỌC KỲ (ĐÃ CÓ NÚT XÓA) ---
    elif menu == "Học kỳ":
        render_header("📅 Quản lý Học kỳ")
        t1, t2 = st.tabs(["Danh sách & Xóa", "Thêm mới"])
        
        with t1:
            sems = ctrl.get_all_semesters()
            if sems:
                data = [{"Mã": s.semesterID, "Tên": s.name, "Bắt đầu": s.startDate, "Kết thúc": s.endDate} for s in sems]
                st.dataframe(data, use_container_width=True)
                
                # 👇 PHẦN BỔ SUNG NÚT XÓA HỌC KỲ Ở ĐÂY
                st.divider()
                with st.expander("🗑️ Xóa Học Kỳ (Nguy hiểm)", expanded=True):
                    st.warning("Chỉ có thể xóa học kỳ khi chưa có Lớp học phần nào được mở trong học kỳ đó.")
                    del_sid = st.selectbox("Chọn HK muốn xóa:", [s.semesterID for s in sems])
                    if st.button("Xác nhận Xóa HK"):
                        ok, msg = ctrl.delete_semester(del_sid)
                        if ok:
                            st.success(msg)
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(msg)
            else: 
                st.info("Trống")

        with t2:
            with st.form("add_sem_form"):
                st.write("Thêm Học Kỳ Mới")
                sid = st.text_input("Mã HK (VD: HK1_2025)")
                name = st.text_input("Tên HK (Bắt buộc)")
                d1 = st.date_input("Bắt đầu")
                d2 = st.date_input("Kết thúc")
                
                if st.form_submit_button("Lưu Học Kỳ"):
                    ok, msg = ctrl.add_semester(sid, name, d1, d2)
                    if ok:
                        st.success(msg)
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(msg)

    # --- 4. MÔN HỌC ---
    elif menu == "Môn học":
        render_header("📚 Quản lý Môn học")
        t1, t2 = st.tabs(["Danh sách", "Thêm mới"])
        with t1:
            courses = ctrl.get_all_courses()
            if courses:
                c_list = [{"Mã": c.courseID, "Tên": c.courseName, "Tín chỉ": c.credits, "Ngành": c.majorID} for c in courses.values()]
                st.dataframe(c_list, use_container_width=True)
                
                with st.expander("Xóa môn học"):
                    sel_del = st.selectbox("Chọn môn xóa:", list(courses.keys()))
                    if st.button("🗑️ Xóa môn"):
                        ok, msg = ctrl.delete_course(sel_del)
                        if ok: 
                            st.success(msg)
                            time.sleep(1)
                            st.rerun()
                        else: st.error(msg)
            else: st.info("Chưa có môn học nào.")

        with t2:
            majors = ctrl.get_all_majors()
            if not majors:
                st.error("⚠️ Vui lòng thêm Ngành học trước (Trong DB).")
            else:
                with st.form("add_c_form"):
                    st.write("### Thêm Môn Học Mới")
                    c1, c2 = st.columns(2)
                    cid = c1.text_input("Mã môn (VD: CS001)")
                    cname = c2.text_input("Tên môn học")
                    
                    c3, c4 = st.columns(2)
                    cre = c3.number_input("Tín chỉ", 1, 10, 3)
                    major_ids = [m.majorID for m in majors]
                    mid = c4.selectbox("Thuộc Ngành", major_ids)
                    
                    if st.form_submit_button("Lưu Môn Học"):
                        ok, msg = ctrl.add_course(cid, mid, cname, cre)
                        if ok:
                            st.success(msg)
                            time.sleep(1.5)
                            st.rerun()
                        else:
                            st.error(msg)

    # --- 5. LỚP HỌC PHẦN ---
    elif menu == "Lớp học phần":
        render_header("🏫 Quản lý Lớp học phần")
        tab1, tab2 = st.tabs(["Danh sách & Hủy", "Mở lớp mới"])
        
        with tab1:
            secs = ctrl.get_all_sections()
            if secs:
                st.dataframe(secs, use_container_width=True)
                
                st.divider()
                st.write("❌ **Hủy Lớp Học Phần**")
                all_ids = [s['Mã lớp'] for s in secs]
                sid_del = st.selectbox("Chọn lớp hủy:", all_ids)
                
                st.info("ℹ️ Nếu lớp đã có sinh viên nhưng chưa nhập điểm: Hệ thống sẽ xóa danh sách đăng ký và hủy lớp.")
                
                if st.button("Xác nhận Hủy lớp"):
                    ok, msg = ctrl.cancel_section(sid_del)
                    if ok: 
                        st.success(msg)
                        time.sleep(1.5)
                        st.rerun()
                    else: st.error(msg)
            else:
                st.info("Chưa có lớp học phần nào.")

        with tab2:
            st.subheader("Mở lớp (Auto Enroll)")
            courses = ctrl.get_all_courses()
            sems = ctrl.get_all_semesters()
            lecturers = ctrl.get_all_lecturers()
            majors = ctrl.get_all_majors()
            
            if not courses or not sems or not lecturers or not majors:
                st.warning("⚠️ Thiếu dữ liệu (Môn/HK/GV/Ngành) để mở lớp.")
            else:
                with st.form("auto_enroll_form"):
                    c1, c2 = st.columns(2)
                    cid = c1.selectbox("Môn học", list(courses.keys()), format_func=lambda x: f"{x} - {courses[x].courseName}")
                    
                    l_dict = {l.lecturerID: l.fullName for l in lecturers}
                    lid = c2.selectbox("Giảng viên", list(l_dict.keys()), format_func=lambda x: f"{x} - {l_dict[x]}")
                    
                    c3, c4 = st.columns(2)
                    sem = c3.selectbox("Học kỳ", [s.semesterID for s in sems])
                    room = c4.text_input("Phòng học (VD: B102)")
                    
                    c5, c6, c7 = st.columns(3)
                    day = c5.selectbox("Thứ", ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật"])
                    p1 = c6.number_input("Tiết BĐ", 1, 15, 1)
                    p2 = c7.number_input("Tiết KT", 1, 15, 3)
                    
                    c8, c9, c10 = st.columns(3)
                    target_maj = c8.selectbox("Ngành SV", [m.majorID for m in majors])
                    mx = c9.number_input("Max SV", 10, 100, 30)
                    sid_input = c10.text_input("Mã Lớp (VD: CS001_01)")
                    
                    if st.form_submit_button("🚀 Mở lớp ngay"):
                        ok, msg = ctrl.create_section_auto_enroll(sid_input, cid, lid, sem, room, day, p1, p2, mx, target_maj)
                        if ok:
                            st.success(msg)
                            time.sleep(1.5)
                            st.rerun()
                        else:
                            st.error(msg)

    # --- 6. KHUNG CHƯƠNG TRÌNH ---
    elif menu == "Khung chương trình":
        render_header("🎓 Thiết lập Khung chương trình")
        majors = ctrl.get_all_majors()
        if not majors:
            st.warning("Chưa có dữ liệu Ngành.")
        else:
            m_opts = {m.majorID: m.majorName for m in majors}
            sel_m = st.selectbox("Chọn Ngành:", list(m_opts.keys()), format_func=lambda x: f"{x} - {m_opts[x]}")
            
            courses = ctrl.get_curriculum(sel_m)
            st.write(f"**Tổng tín chỉ:** {sum(c.credits for c in courses)}")
            
            if courses:
                df = [{"Mã": c.courseID, "Tên": c.courseName, "TC": c.credits} for c in courses]
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("Chưa có môn nào trong khung.")
            
            st.divider()
            t1, t2, t3 = st.tabs(["➕ Thêm", "✏️ Sửa", "🗑️ Xóa"])
            
            with t1:
                with st.form("add_kct"):
                    st.write("Thêm môn vào Khung:")
                    c1, c2, c3 = st.columns([1,2,1])
                    nc = c1.text_input("Mã môn")
                    nn = c2.text_input("Tên môn")
                    ncr = c3.number_input("TC", 1, 10, 3)
                    if st.form_submit_button("Lưu"):
                        ok, m = ctrl.add_course_to_curriculum(nc, sel_m, nn, ncr)
                        if ok: 
                            st.success(m)
                            time.sleep(1)
                            st.rerun()
                        else: st.error(m)
            
            with t2:
                if courses:
                    c_opts = {c.courseID: c.courseName for c in courses}
                    ec = st.selectbox("Chọn môn sửa:", list(c_opts.keys()))
                    cur_c = next(c for c in courses if c.courseID == ec)
                    with st.form("edit_kct"):
                        enn = st.text_input("Tên mới", value=cur_c.courseName)
                        ecr = st.number_input("TC mới", 1, 10, value=cur_c.credits)
                        if st.form_submit_button("Cập nhật"):
                            ok, m = ctrl.update_course(ec, enn, ecr)
                            if ok: 
                                st.success(m)
                                time.sleep(1)
                                st.rerun()
                            else: st.error(m)
                else: st.write("Không có môn để sửa.")
            
            with t3:
                if courses:
                    dc = st.selectbox("Chọn môn xóa:", [c.courseID for c in courses])
                    st.warning("Cẩn thận: Xóa môn sẽ ảnh hưởng đến dữ liệu cũ.")
                    if st.button("Xác nhận Xóa"):
                        ok, m = ctrl.remove_course_from_curriculum(dc)
                        if ok: 
                            st.success(m)
                            time.sleep(1)
                            st.rerun()
                        else: st.error(m)
                else: st.write("Không có môn để xóa.")

    # --- 7. ĐỔI MẬT KHẨU ---
    elif menu == "Đổi mật khẩu":
        render_header("🔐 Đổi mật khẩu")
        with st.form("adm_cp"):
            o = st.text_input("Mật khẩu cũ", type="password")
            n = st.text_input("Mật khẩu mới", type="password")
            c = st.text_input("Xác nhận", type="password")
            if st.form_submit_button("Lưu thay đổi"):
                ok, msg = auth.change_password(user.userID, o, n, c)
                if ok: 
                    st.success(msg)
                    time.sleep(1)
                    st.rerun()
                else: st.error(msg)