import streamlit as st
import pandas as pd
from controllers.admin_controller import AdminController
from controllers.auth_controller import AuthController


def render_admin_ui(user):
    ctrl = AdminController()
    auth = AuthController()

    # ================== SIDEBAR ==================
    st.sidebar.title("🛠️ Admin Portal")

    options = [
        "Dashboard",
        "Tài khoản",
        "Học kỳ",
        "Môn học",
        "Lớp học phần",
        "Khung chương trình",
        "Đổi mật khẩu"
    ]

    if "admin_nav" not in st.session_state:
        st.session_state.admin_nav = "Dashboard"

    def navigate(page):
        st.session_state.admin_nav = page

    def logout():
        st.session_state.user = None
        st.session_state.admin_nav = "Dashboard"

    menu = st.sidebar.radio("Quản lý", options, key="admin_nav")
    st.sidebar.button("Đăng xuất", on_click=logout)

    # ================== DASHBOARD ==================
    if menu == "Dashboard":
        st.title("🚀 Admin Dashboard")

        stats = ctrl.get_stats()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Users", stats["users"])
        c2.metric("Courses", stats["courses"])
        c3.metric("Sections", stats["sections"])
        c4.metric("Semesters", stats["semesters"])

        st.divider()
        st.subheader("⚡ Truy cập nhanh")
        a, b, c, d = st.columns(4)
        a.button("👥 Tài khoản", use_container_width=True, on_click=navigate, args=("Tài khoản",))
        b.button("📅 Học kỳ", use_container_width=True, on_click=navigate, args=("Học kỳ",))
        c.button("📚 Môn học", use_container_width=True, on_click=navigate, args=("Môn học",))
        d.button("🏫 Lớp HP", use_container_width=True, on_click=navigate, args=("Lớp học phần",))

    # ================== UC14: TÀI KHOẢN ==================
    elif menu == "Tài khoản":
        st.title("👥 Quản lý Tài khoản")

        users = ctrl.db.users

        data = [{
            "UserID": u.userID,
            "Họ tên": u.fullName,
            "Vai trò": u.role,
            "Email": u.email,
            "Trạng thái": "Hoạt động" if getattr(u, "status", True) else "Khóa"
        } for u in users.values()]

        st.dataframe(pd.DataFrame(data), use_container_width=True)

        st.divider()
        st.subheader("🔒 Lock / Unlock User")

        uid = st.selectbox("Chọn User", list(users.keys()))
        reason = st.text_input("Lý do khóa (nếu Lock)")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔒 Lock"):
                ok, msg = ctrl.lock_user(uid, reason)
                st.success(msg) if ok else st.error(msg)
                if ok: st.rerun()

        with c2:
            if st.button("🔓 Unlock"):
                ok, msg = ctrl.unlock_user(uid)
                st.success(msg) if ok else st.error(msg)
                if ok: st.rerun()

    # ================== UC15: HỌC KỲ ==================
    elif menu == "Học kỳ":
        st.title("📅 Quản lý Học kỳ")

        tab1, tab2 = st.tabs(["Danh sách", "Thêm mới"])

        with tab1:
            semesters = ctrl.get_all_semesters()
            if semesters:
                st.dataframe(pd.DataFrame([vars(s) for s in semesters]), use_container_width=True)
            else:
                st.info("Chưa có học kỳ")

        with tab2:
            with st.form("add_semester"):
                sid = st.text_input("Mã học kỳ")
                name = st.text_input("Tên học kỳ")
                d1 = st.date_input("Ngày bắt đầu")
                d2 = st.date_input("Ngày kết thúc")

                if st.form_submit_button("Thêm"):
                    ok, msg = ctrl.add_semester(sid, name, d1, d2)
                    st.success(msg) if ok else st.error(msg)
                    if ok: st.rerun()

    # ================== UC16 + UC21 + UC22: MÔN HỌC ==================
    elif menu == "Môn học":
        st.title("📚 Quản lý Môn học")

        tab1, tab2 = st.tabs(["Danh sách / Xóa", "Thêm môn"])

        with tab1:
            courses = ctrl.get_all_courses()
            df = pd.DataFrame([{
                "Mã môn": c.courseID,
                "Tên môn": c.courseName,
                "Tín chỉ": c.credits
            } for c in courses.values()])
            st.dataframe(df, use_container_width=True)

            st.divider()
            cid = st.selectbox("Chọn môn cần xóa", list(courses.keys()))
            if st.button("🗑️ Xóa môn học"):
                ok, msg = ctrl.delete_course(cid)
                st.success(msg) if ok else st.error(msg)
                if ok: st.rerun()

        with tab2:
            with st.form("add_course"):
                cid = st.text_input("Mã môn")
                cname = st.text_input("Tên môn")
                credits = st.number_input("Số tín chỉ", 1, 6, 3)

                if st.form_submit_button("Thêm"):
                    ok, msg = ctrl.add_course(cid, cname, credits)
                    st.success(msg) if ok else st.error(msg)
                    if ok: st.rerun()

    # ================== UC17 + UC19 + UC20: LỚP HỌC PHẦN ==================
    elif menu == "Lớp học phần":
        st.title("🏫 Quản lý Lớp học phần")

        tab1, tab2 = st.tabs(["Danh sách / Hủy lớp", "Mở lớp mới"])

        with tab1:
            sections = ctrl.get_all_sections()
            if sections:
                df = pd.DataFrame(sections)
                st.dataframe(df, use_container_width=True)

                st.divider()
                sid = st.selectbox("Chọn lớp để hủy", df["sectionID"])
                if st.button("❌ Hủy lớp học phần"):
                    ok, msg = ctrl.cancel_section(sid)
                    st.success(msg) if ok else st.error(msg)
                    if ok: st.rerun()
            else:
                st.info("Chưa có lớp học phần")

        with tab2:
            courses = ctrl.db.courses
            semesters = ctrl.db.semesters
            lecturers = {k: v for k, v in ctrl.db.users.items() if v.role == "Lecturer"}

            with st.form("add_section"):
                cid = st.selectbox("Môn học", list(courses.keys()))
                lid = st.selectbox("Giảng viên", list(lecturers.keys()))
                sem = st.selectbox("Học kỳ", [s.semesterID for s in semesters])
                room = st.text_input("Phòng học")
                day = st.selectbox("Thứ", ["Thứ 2","Thứ 3","Thứ 4","Thứ 5","Thứ 6"])
                p1 = st.number_input("Tiết bắt đầu", 1, 12, 1)
                p2 = st.number_input("Tiết kết thúc", 1, 12, 3)

                sid = f"{cid}.N{len(ctrl.db.sections)+1:02d}"

                if st.form_submit_button("Mở lớp"):
                    ok, msg = ctrl.add_section(sid, cid, lid, sem, room, day, p1, p2)
                    st.success(msg) if ok else st.error(msg)
                    if ok: st.rerun()

    # ================== UC18: KHUNG CHƯƠNG TRÌNH ==================
    elif menu == "Khung chương trình":
        st.title("📘 Quản lý Khung chương trình")

        majors = ctrl.db.majors
        courses = ctrl.db.courses

        tab1, tab2 = st.tabs(["Xem khung", "Thêm môn"])

        with tab1:
            mid = st.selectbox("Ngành", list(majors.keys()))
            df = ctrl.get_curriculum(mid)
            if not df.empty:
                st.dataframe(df, use_container_width=True)
            else:
                st.info("Chưa có dữ liệu")

        with tab2:
            with st.form("add_curriculum"):
                mid = st.selectbox("Ngành", list(majors.keys()))
                cid = st.selectbox("Môn học", list(courses.keys()))
                sem_no = st.number_input("Học kỳ", 1, 10, 1)
                req = st.checkbox("Bắt buộc", True)

                if st.form_submit_button("Thêm"):
                    ok, msg = ctrl.add_curriculum_item(mid, cid, sem_no, req)
                    st.success(msg) if ok else st.error(msg)
                    if ok: st.rerun()

    # ================== ĐỔI MẬT KHẨU ==================
    elif menu == "Đổi mật khẩu":
        st.title("🔐 Đổi mật khẩu Admin")

        with st.form("change_pass"):
            old = st.text_input("Mật khẩu cũ", type="password")
            new = st.text_input("Mật khẩu mới", type="password")
            confirm = st.text_input("Xác nhận mật khẩu mới", type="password")

            if st.form_submit_button("Lưu"):
                ok, msg = auth.change_password(user.userID, old, new, confirm)
                st.success(msg) if ok else st.error(msg)
