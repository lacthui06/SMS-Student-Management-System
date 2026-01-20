import streamlit as st
import pandas as pd
from controllers.student_controller import StudentController
from controllers.auth_controller import AuthController

def render_student_ui(user):
    ctrl = StudentController(user.userID)
    auth = AuthController()
    
    st.sidebar.title(f"🎓 {user.fullName}")
    
    # --- ĐIỀU HƯỚNG (NAVIGATION) ---
    # Danh sách chức năng đầy đủ
    options = ["Dashboard", "Hồ sơ", "Lịch học", "Kết quả học tập", "Tiến độ học tập", "Đổi mật khẩu"]
    
    if 'student_nav' not in st.session_state:
        st.session_state['student_nav'] = "Dashboard"

    def navigate(page):
        st.session_state['student_nav'] = page

    def logout():
        st.session_state['user'] = None
        st.session_state['student_nav'] = "Dashboard"

    menu = st.sidebar.radio("Menu", options, key="student_nav")
    st.sidebar.button("Đăng xuất", on_click=logout)

    # --- 1. DASHBOARD ---
    if menu == "Dashboard":
        st.title("🏠 Trang chủ Sinh viên")
        
        # Khung thông tin sinh viên
        with st.container(border=True):
            st.subheader("📌 Thông tin sinh viên")
            
            # Hàng 1
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"**MSSV:** {user.userID}")
            c2.markdown(f"**Họ tên:** {user.fullName}")
            c3.markdown(f"**Giới tính:** {user.gender}")
            
            st.divider() 
            
            # Hàng 2
            c4, c5, c6 = st.columns(3)
            c4.markdown(f"**Ngành:** {user.majorID}")
            c5.markdown(f"**Khoa:** {user.facultyID}")
            c6.markdown(f"**Khóa học:** 2024")
            
            st.divider()

            # Hàng 3
            c7, c8, c9 = st.columns(3)
            c7.markdown(f"**Ngày sinh:** {user.dob}")
            c8.markdown(f"**Email:** {user.email}")
            c9.markdown(f"**SĐT:** {user.phone}")

        # --- KHU VỰC TRUY CẬP NHANH (QUICK ACCESS) ---
        st.markdown("### 🚀 Truy cập nhanh")
        
        # Hàng 1: Các chức năng học tập chính (3 cột)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.button("📅 Xem Lịch học", use_container_width=True, on_click=navigate, args=("Lịch học",))
        with col2:
            st.button("📊 Xem Tiến độ", use_container_width=True, on_click=navigate, args=("Tiến độ học tập",))
        with col3:
            st.button("📑 Xem Kết quả", use_container_width=True, on_click=navigate, args=("Kết quả học tập",))
        
        st.markdown("") # Khoảng cách nhỏ

        # Hàng 2: Các chức năng cá nhân (2 cột)
        col4, col5 = st.columns(2)
        with col4:
            st.button("👤 Hồ sơ cá nhân", use_container_width=True, on_click=navigate, args=("Hồ sơ",))
        with col5:
            st.button("🔐 Đổi mật khẩu", use_container_width=True, on_click=navigate, args=("Đổi mật khẩu",))

    # --- 2. HỒ SƠ ---
    elif menu == "Hồ sơ":
        c1, c2 = st.columns([4, 1])
        c1.title("Hồ sơ sinh viên")
        c2.button("⬅️ Trang chủ", key="back_prof", on_click=navigate, args=("Dashboard",))

        tab1, tab2 = st.tabs(["👁️ Thông tin chi tiết", "✏️ Cập nhật liên hệ"])
        with tab1:
            st.subheader("Thông tin cơ bản")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**MSSV:** {user.userID}")
                st.markdown(f"**Họ tên:** {user.fullName}")
                st.markdown(f"**Ngày sinh:** {user.dob}")
                st.markdown(f"**Nơi sinh:** {user.pob}")
                st.markdown(f"**Ngành:** {user.majorID}")
            with col2:
                st.markdown(f"**Khóa học:** 2024")
                st.markdown(f"**Giới tính:** {user.gender}")
                st.markdown(f"**CCCD:** {user.citizenID}")
                st.markdown(f"**Hệ đào tạo:** Chính quy")
                st.markdown(f"**Khoa:** {user.facultyID}")
            
            st.divider()
            st.subheader("Thông tin liên hệ")
            st.markdown(f"📍 **Địa chỉ:** {user.address}")
            st.markdown(f"📞 **SĐT:** {user.phone}")
            st.markdown(f"📧 **Email:** {user.email}")

        with tab2:
            st.info("Cập nhật thông tin liên lạc")
            with st.form("edit"):
                ph = st.text_input("Số điện thoại", user.phone)
                em = st.text_input("Email", user.email)
                ad = st.text_input("Địa chỉ", user.address)
                
                # --- SỬA ĐOẠN NÀY ---
                if st.form_submit_button("Lưu thay đổi"):
                    # Nhận kết quả từ Controller
                    ok, msg = ctrl.update_contact_info(ph, em, ad)
                    
                    if ok:
                        st.success(msg) # Hiện thông báo thành công
                        st.rerun()      # Chỉ reload trang khi thành công
                    else:
                        st.error(msg)   # Hiện thông báo lỗi màu đỏ nếu sai (không reload)

    # --- 3. LỊCH HỌC ---
    elif menu == "Lịch học":
        c1, c2 = st.columns([4, 1])
        c1.title("📅 Lịch học cá nhân")
        c2.button("⬅️ Trang chủ", key="back_tt", on_click=navigate, args=("Dashboard",))

        data = ctrl.get_timetable()
        if data:
            df = pd.DataFrame(data).sort_values(by=["_day_sort", "_start_sort"]).drop(columns=["_day_sort", "_start_sort"])
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("Hiện tại chưa có lịch học.")

    # --- 4. TIẾN ĐỘ HỌC TẬP ---
    elif menu == "Tiến độ học tập":
        c1, c2 = st.columns([4, 1])
        c1.title("📊 Tiến độ học tập")
        c2.button("⬅️ Trang chủ", key="back_prog", on_click=navigate, args=("Dashboard",))

        prog = ctrl.get_progress_data()
        
        st.metric("Tín chỉ tích lũy", f"{prog['accumulated']} / {prog['required']}")
        
        st.divider()
        st.subheader("Danh sách các môn đã hoàn thành")
        if prog['details']:
            st.dataframe(
                pd.DataFrame(prog['details']), 
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Chưa có môn học nào hoàn thành.")

    # --- 5. KẾT QUẢ HỌC TẬP ---
    elif menu == "Kết quả học tập":
        c1, c2 = st.columns([4, 1])
        c1.title("📑 Bảng điểm & Phúc khảo")
        c2.button("⬅️ Trang chủ", key="back_res", on_click=navigate, args=("Dashboard",))

        # 1. Bảng điểm
        grades = ctrl.get_grade_table()
        st.dataframe(pd.DataFrame(grades), use_container_width=True)
        
        st.divider()

        # 2. --- THÊM PHẦN NÀY: LỊCH SỬ PHÚC KHẢO ---
        st.subheader("Lịch sử yêu cầu phúc khảo")
        my_reqs = ctrl.get_my_requests()
        if my_reqs:
            req_data = []
            for r in my_reqs:
                req_data.append({
                    "Mã môn": r.sectionID,
                    "Ngày gửi": r.createDate,
                    "Lý do": r.reason,
                    "Trạng thái": r.status, # Pending/Approved/Rejected
                    "Phản hồi GV": r.reply
                })
            # Hiển thị bảng lịch sử
            st.dataframe(pd.DataFrame(req_data), use_container_width=True, hide_index=True)
        else:
            st.info("Bạn chưa gửi yêu cầu phúc khảo nào.")

        st.divider()
        
        # 3. Form gửi yêu cầu (Giữ nguyên)
        st.subheader("Gửi yêu cầu Phúc khảo mới (UC9)")
        st.caption("Lưu ý: Chỉ được phúc khảo môn đã có điểm Tổng kết và chưa gửi yêu cầu trước đó.")
        
        eligible_courses = ctrl.get_reviewable_courses()
        
        with st.form("pk_form"):
            if not eligible_courses:
                st.warning("Bạn không có môn học nào đủ điều kiện phúc khảo (hoặc đã gửi yêu cầu hết rồi).")
                st.form_submit_button("Gửi yêu cầu", disabled=True)
            else:
                sel = st.selectbox("Chọn môn học", eligible_courses)
                reason = st.text_area("Lý do phúc khảo (ghi rõ mong muốn)")
                if st.form_submit_button("Gửi yêu cầu"):
                    ctrl.create_review_request(sel, reason)
                    st.success("Đã gửi yêu cầu thành công!")
                    st.rerun()

    # --- 6. ĐỔI MẬT KHẨU ---
    elif menu == "Đổi mật khẩu":
        c1, c2 = st.columns([4, 1])
        c1.title("🔐 Đổi mật khẩu")
        c2.button("⬅️ Trang chủ", key="back_pass", on_click=navigate, args=("Dashboard",))

        with st.form("change_pass_form"):
            o = st.text_input("Mật khẩu cũ", type="password")
            n = st.text_input("Mật khẩu mới", type="password")
            c = st.text_input("Xác nhận mật khẩu mới", type="password")
            if st.form_submit_button("Lưu thay đổi"):
                ok, msg = auth.change_password(user.userID, o, n, c)
                if ok: st.success(msg)
                else: st.error(msg)