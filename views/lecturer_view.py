import streamlit as st
import pandas as pd
from controllers.lecturer_controller import LecturerController
from controllers.auth_controller import AuthController

def render_lecturer_ui(user):
    ctrl = LecturerController(user.userID)
    auth = AuthController() # Import AuthController để đổi mật khẩu
    
    st.sidebar.title(f"👨‍🏫 GV: {user.fullName}")
    
    # --- ĐIỀU HƯỚNG ---
    options = ["Dashboard", "Hồ sơ", "Lịch dạy", "Nhập điểm", "Duyệt phúc khảo", "Đổi mật khẩu"]
    if 'lec_nav' not in st.session_state: st.session_state['lec_nav'] = "Dashboard"
    
    def navigate(page): st.session_state['lec_nav'] = page
    def logout(): 
        st.session_state['user'] = None
        st.session_state['lec_nav'] = "Dashboard"

    menu = st.sidebar.radio("Menu", options, key="lec_nav")
    st.sidebar.button("Đăng xuất", on_click=logout)

    # --- Helper hiển thị thông tin ---
    st.markdown("""
        <style>
        .profile-row { font-size: 15px; margin-bottom: 8px; }
        .profile-label { font-weight: bold; color: #31333F; }
        .profile-val { color: #000; }
        </style>
    """, unsafe_allow_html=True)
    def row(label, value):
        st.markdown(f"<div class='profile-row'><span class='profile-label'>{label}:</span> <span class='profile-val'>{value}</span></div>", unsafe_allow_html=True)

    # --- 1. DASHBOARD ---
    if menu == "Dashboard":
        st.title("🏠 Trang chủ Giảng viên")
        
        with st.container(border=True):
            st.subheader("📌 Thông tin Giảng viên")
            c1, c2 = st.columns(2)
            with c1:
                row("Mã GV", user.userID)
                row("Họ tên", user.fullName)
                row("Học vị", user.degree)
            with c2:
                row("Chức vụ", user.position)
                row("Email", user.email)
                row("SĐT", user.phone)

        st.markdown("### 🚀 Truy cập nhanh")
        
        # Hàng 1
        c1, c2, c3 = st.columns(3)
        with c1:
            st.button("📅 Xem Lịch dạy", use_container_width=True, on_click=navigate, args=("Lịch dạy",))
        with c2:
            st.button("📝 Nhập điểm", use_container_width=True, on_click=navigate, args=("Nhập điểm",))
        with c3:
            st.button("📩 Duyệt phúc khảo", use_container_width=True, on_click=navigate, args=("Duyệt phúc khảo",))
        
        # Hàng 2
        st.markdown("")
        c4, c5 = st.columns(2)
        with c4:
             st.button("👤 Cập nhật hồ sơ", use_container_width=True, on_click=navigate, args=("Hồ sơ",))
        with c5:
             st.button("🔐 Đổi mật khẩu", use_container_width=True, on_click=navigate, args=("Đổi mật khẩu",))

    # --- 2. HỒ SƠ ---
    elif menu == "Hồ sơ":
        c1, c2 = st.columns([4, 1])
        c1.title("Hồ sơ Giảng viên")
        c2.button("⬅️ Trang chủ", key="back_dash", on_click=navigate, args=("Dashboard",))

        tab1, tab2 = st.tabs(["👁️ Thông tin chi tiết", "✏️ Cập nhật liên hệ"])
        with tab1:
            st.subheader("Thông tin cá nhân")
            c1, c2 = st.columns(2)
            with c1:
                row("Mã GV", user.userID)
                row("Họ tên", user.fullName)
                row("Ngày sinh", user.dob)
                row("Nơi sinh", user.pob)
            with c2:
                row("Giới tính", user.gender)
                row("CCCD", user.citizenID)
                row("Học vị", user.degree)
                row("Chức vụ", user.position)
            st.divider()
            st.subheader("Thông tin liên hệ")
            row("Email", user.email)
            row("SĐT", user.phone)
            row("Địa chỉ", user.address)
            
        with tab2:
            st.info("Cập nhật thông tin liên hệ:")
            with st.form("edit_lec"):
                ph = st.text_input("Số điện thoại", user.phone)
                em = st.text_input("Email", user.email)
                ad = st.text_input("Địa chỉ", user.address)
                if st.form_submit_button("Lưu thay đổi"):
                    ctrl.update_contact_info(ph, em, ad)
                    st.success("Đã cập nhật!")
                    st.rerun()

    # --- 3. LỊCH DẠY ---
    elif menu == "Lịch dạy":
        c1, c2 = st.columns([4, 1])
        c1.title("📅 Lịch giảng dạy")
        c2.button("⬅️ Trang chủ", key="back_sch", on_click=navigate, args=("Dashboard",))

        sch = ctrl.get_teaching_schedule()
        if sch:
            df = pd.DataFrame(sch).sort_values(by=["_d", "_s"]).drop(columns=["_d", "_s"])
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("Hiện chưa có lịch dạy.")

    # --- 4. NHẬP ĐIỂM ---
    elif menu == "Nhập điểm":
        c1, c2 = st.columns([4, 1])
        c1.title("📝 Nhập điểm Sinh viên")
        c2.button("⬅️ Trang chủ", key="back_grade", on_click=navigate, args=("Dashboard",))

        opts = ctrl.get_my_sections()
        if not opts: 
            st.warning("Không có lớp nào được phân công.")
        else:
            sel = st.selectbox("Chọn lớp", [f"{i} - {n}" for i, n in opts])
            sec_id = sel.split(" - ")[0]
            data = ctrl.get_students_in_section(sec_id)
            
            st.info("Nhập điểm trực tiếp vào bảng (Thang điểm 10):")
            
            # --- CẤU HÌNH GIAO DIỆN (BỎ chặn Min/Max để cho phép nhập sai) ---
            edited = st.data_editor(
                data, 
                num_rows="fixed", 
                use_container_width=True,
                column_config={
                    "MSSV": st.column_config.TextColumn(disabled=True),
                    "Họ tên": st.column_config.TextColumn(disabled=True),
                    "Điểm QT": st.column_config.NumberColumn(
                        "Điểm QT",
                        step=0.1,
                        format="%.1f"
                        # ĐÃ BỎ min_value, max_value ĐỂ TRÁNH TỰ SỬA THÀNH 10
                    ),
                    "Điểm CK": st.column_config.NumberColumn(
                        "Điểm CK",
                        step=0.1,
                        format="%.1f"
                        # ĐÃ BỎ min_value, max_value ĐỂ TRÁNH TỰ SỬA THÀNH 10
                    )
                }
            )
            
            if st.button("💾 Lưu bảng điểm"):
                ok, msg = ctrl.save_grades(sec_id, edited)
                if ok: 
                    st.success(msg)
                else: 
                    # HIỆN LỖI ĐỎ NẾU NHẬP SAI
                    st.error(msg)

    # --- 5. DUYỆT PHÚC KHẢO ---
    elif menu == "Duyệt phúc khảo":
        c1, c2 = st.columns([4, 1])
        c1.title("📩 Duyệt yêu cầu phúc khảo")
        c2.button("⬅️ Trang chủ", key="back_req", on_click=navigate, args=("Dashboard",))

        reqs = ctrl.get_pending_reviews()
        if not reqs:
            st.info("Không có yêu cầu nào cần xử lý.")
        else:
            for r in reqs:
                label = f"📌 {r.sectionID} - SV: {r.studentID} ({r.createDate})"
                with st.expander(label, expanded=True):
                    st.markdown(f"**Lý do:** {r.reason}")
                    st.markdown(f"**Trạng thái hiện tại:** `{r.status}`")
                    
                    with st.form(key=f"f_{r.requestID}"):
                        c1, c2 = st.columns(2)
                        new_stt = c1.selectbox("Trạng thái", ["Pending", "Approved", "Rejected"], index=["Pending", "Approved", "Rejected"].index(r.status), key=f"s_{r.requestID}")
                        reply = c2.text_input("Phản hồi", value=r.reply, key=f"r_{r.requestID}")
                        
                        if st.form_submit_button("Cập nhật"):
                            ctrl.process_review(r.requestID, new_stt, reply)
                            st.success("Đã xử lý xong!")
                            st.rerun()

    # --- 6. ĐỔI MẬT KHẨU (UC2) ---
    elif menu == "Đổi mật khẩu":
        c1, c2 = st.columns([4, 1])
        c1.title("🔐 Đổi mật khẩu")
        c2.button("⬅️ Trang chủ", on_click=navigate, args=("Dashboard",))

        with st.form("change_pass_lec"):
            o = st.text_input("Mật khẩu cũ", type="password")
            n = st.text_input("Mật khẩu mới", type="password")
            c = st.text_input("Xác nhận mật khẩu mới", type="password")
            if st.form_submit_button("Lưu thay đổi"):
                ok, msg = auth.change_password(user.userID, o, n, c)
                if ok: st.success(msg)
                else: st.error(msg)