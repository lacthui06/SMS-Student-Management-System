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

    # --- Helper hiển thị thông tin (GIỮ NGUYÊN) ---
    st.markdown("""
        <style>
        .profile-row { font-size: 15px; margin-bottom: 8px; }
        .profile-label { font-weight: bold; color: #31333F; }
        .profile-val { color: #000; }
        </style>
    """, unsafe_allow_html=True)
    def row(label, value):
        st.markdown(f"<div class='profile-row'><span class='profile-label'>{label}:</span> <span class='profile-val'>{value}</span></div>", unsafe_allow_html=True)

    # --- 1. DASHBOARD (GIỮ NGUYÊN) ---
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

    # --- 2. HỒ SƠ (GIỮ NGUYÊN) ---
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
                    # Controller đã có logic validate
                    ok, msg = ctrl.update_contact_info(ph, em, ad)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    # --- 3. LỊCH DẠY (GIỮ NGUYÊN) ---
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

    # --- 4. NHẬP ĐIỂM (CẬP NHẬT LOGIC UC10/UC11) ---
    elif menu == "Nhập điểm":
        c1, c2 = st.columns([4, 1])
        c1.title("📝 Quản lý Điểm")
        c2.button("⬅️ Trang chủ", key="back_grade", on_click=navigate, args=("Dashboard",))

        opts = ctrl.get_my_sections()
        if not opts: 
            st.warning("Không có lớp nào được phân công.")
        else:
            sel = st.selectbox("Chọn lớp", [f"{i} - {n}" for i, n in opts])
            sec_id = sel.split(" - ")[0]
            data = ctrl.get_students_in_section(sec_id)
            
            # --- Logic mới: Kiểm tra chế độ Nhập (UC10) hay Sửa (UC11) ---
            has_grades = any(row['Điểm CK'] is not None for row in data)
            
            if has_grades:
                st.info("ℹ️ Lớp đã có điểm. Chế độ: **Cập nhật (UC11)**")
            else:
                st.success("🆕 Lớp chưa có điểm. Chế độ: **Nhập mới (UC10)**")
            
            # Bảng nhập liệu (Giữ cấu hình column của bạn)
            edited = st.data_editor(
                data, 
                num_rows="fixed", 
                use_container_width=True,
                column_config={
                    "MSSV": st.column_config.TextColumn(disabled=True),
                    "Họ tên": st.column_config.TextColumn(disabled=True),
                    "Điểm QT": st.column_config.NumberColumn("Điểm QT", step=0.1, format="%.1f"),
                    "Điểm CK": st.column_config.NumberColumn("Điểm CK", step=0.1, format="%.1f")
                }
            )
            
            with st.form("save_grades"):
                # Nếu là Update (UC11), thêm ô nhập Lý do
                reason = ""
                if has_grades:
                    st.markdown("**Lý do chỉnh sửa (Bắt buộc cho UC11):**")
                    reason = st.text_input("Lý do", placeholder="VD: Nhập sai sót, Phúc khảo...", label_visibility="collapsed")
                
                if st.form_submit_button("💾 Lưu bảng điểm"):
                    # Validate lý do ở tầng View
                    if has_grades and not reason.strip():
                        st.error("❌ Vui lòng nhập lý do chỉnh sửa điểm.")
                    else:
                        # Gọi controller kèm reason
                        ok, msg = ctrl.save_grades(sec_id, edited, reason)
                        if ok: 
                            st.success(msg)
                        else: 
                            st.error(msg)

    # --- 5. DUYỆT PHÚC KHẢO (CẬP NHẬT GIAO DIỆN UC12) ---
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
                        reply = st.text_input("Phản hồi của GV", value=r.reply, key=f"r_{r.requestID}")
                        
                        # Thay Selectbox bằng Radio cho đúng flow Accept/Reject
                        action = st.radio("Quyết định", ["Chưa xử lý", "Chấp nhận (Accept)", "Từ chối (Reject)"], key=f"rad_{r.requestID}")
                        
                        if st.form_submit_button("Xác nhận"):
                            if action == "Chưa xử lý":
                                st.warning("Vui lòng chọn kết quả.")
                            else:
                                stt = "Approved" if action == "Chấp nhận (Accept)" else "Rejected"
                                ok, msg = ctrl.process_review(r.requestID, stt, reply)
                                if ok: 
                                    st.success(msg)
                                    st.rerun()
                                else: st.error(msg)

    # --- 6. ĐỔI MẬT KHẨU (GIỮ NGUYÊN) ---
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