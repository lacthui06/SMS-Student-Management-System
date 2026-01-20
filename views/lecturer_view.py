import streamlit as st
import pandas as pd
from controllers.lecturer_controller import LecturerController
from controllers.auth_controller import AuthController

def render_lecturer_ui(user):
    ctrl = LecturerController(user.userID)
    auth = AuthController()
    
    st.sidebar.title(f"👨‍🏫 GV: {user.fullName}")
    
    # --- CẤU HÌNH MENU ĐIỀU HƯỚNG ---
    options = ["Dashboard", "Hồ sơ", "Lịch dạy", "Nhập điểm (UC10)", "Cập nhật điểm (UC11)", "Duyệt phúc khảo", "Đổi mật khẩu"]
    
    if 'lec_nav' not in st.session_state: 
        st.session_state['lec_nav'] = "Dashboard"
    
    if st.session_state['lec_nav'] not in options:
        st.session_state['lec_nav'] = "Dashboard"

    current_index = options.index(st.session_state['lec_nav'])

    # Hiển thị Menu
    selected_menu = st.sidebar.radio("Menu", options, index=current_index)

    if selected_menu != st.session_state['lec_nav']:
        st.session_state['lec_nav'] = selected_menu
        st.rerun()

    menu = st.session_state['lec_nav']

    # --- SỬA LỖI Ở ĐÂY: Bỏ st.rerun() trong các hàm callback ---
    def navigate(page): 
        st.session_state['lec_nav'] = page
        # Đã xóa st.rerun() vì on_click tự động rerun
        
    def logout(): 
        st.session_state['user'] = None
        st.session_state['lec_nav'] = "Dashboard"
        # Đã xóa st.rerun() vì on_click tự động rerun

    st.sidebar.button("Đăng xuất", on_click=logout)

    # --- 1. DASHBOARD ---
    if menu == "Dashboard":
        st.title("🏠 Trang chủ Giảng viên")
        with st.container(border=True):
            st.subheader("📌 Thông tin Giảng viên")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**Mã GV:** {user.userID}")
                st.markdown(f"**Họ tên:** {user.fullName}")
                st.markdown(f"**Học vị:** {user.degree}")
            with c2:
                st.markdown(f"**Chức vụ:** {user.position}")
                st.markdown(f"**Email:** {user.email}")
                st.markdown(f"**SĐT:** {user.phone}")
        st.markdown("### 🚀 Truy cập nhanh")
        c1, c2, c3 = st.columns(3)
        with c1: st.button("📅 Xem Lịch dạy", use_container_width=True, on_click=lambda: navigate("Lịch dạy"))
        with c2: st.button("📝 Nhập điểm", use_container_width=True, on_click=lambda: navigate("Nhập điểm (UC10)"))
        with c3: st.button("📩 Duyệt phúc khảo", use_container_width=True, on_click=lambda: navigate("Duyệt phúc khảo"))

    # --- 2. HỒ SƠ ---
    elif menu == "Hồ sơ":
        c1, c2 = st.columns([4, 1])
        c1.title("Hồ sơ Giảng viên")
        c2.button("⬅️ Trang chủ", on_click=lambda: navigate("Dashboard"))
        tab1, tab2 = st.tabs(["👁️ Thông tin", "✏️ Cập nhật"])
        with tab1:
            st.subheader("Thông tin cá nhân")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**Mã GV:** {user.userID}")
                st.markdown(f"**Họ tên:** {user.fullName}")
                st.markdown(f"**Ngày sinh:** {user.dob}")
            with c2:
                st.markdown(f"**Giới tính:** {user.gender}")
                st.markdown(f"**CCCD:** {user.citizenID}")
                st.markdown(f"**Học vị:** {user.degree}")
            st.divider()
            st.markdown(f"📧 **Email:** {user.email}")
            st.markdown(f"📞 **SĐT:** {user.phone}")
            st.markdown(f"📍 **Địa chỉ:** {user.address}")
        with tab2:
            st.info("Cập nhật thông tin liên hệ")
            with st.form("edit_lec"):
                ph = st.text_input("Số điện thoại", user.phone)
                em = st.text_input("Email", user.email)
                ad = st.text_input("Địa chỉ", user.address)
                if st.form_submit_button("Lưu thay đổi"):
                    ok, msg = ctrl.update_contact_info(ph, em, ad)
                    if ok: st.success(msg); st.rerun()
                    else: st.error(msg)

    # --- 3. LỊCH DẠY ---
    elif menu == "Lịch dạy":
        c1, c2 = st.columns([4, 1])
        c1.title("📅 Lịch giảng dạy")
        c2.button("⬅️ Trang chủ", on_click=lambda: navigate("Dashboard"))
        sch = ctrl.get_teaching_schedule()
        if sch:
            df = pd.DataFrame(sch).sort_values(by=["_d", "_s"]).drop(columns=["_d", "_s"])
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("Chưa có lịch dạy.")

    # --- 4. NHẬP ĐIỂM (UC 10) ---
    elif menu == "Nhập điểm (UC10)":
        c1, c2 = st.columns([4, 1])
        c1.title("📝 Nhập điểm (UC10)")
        c2.button("⬅️ Trang chủ", on_click=lambda: navigate("Dashboard"))

        opts = ctrl.get_my_sections()
        if not opts:
            st.warning("Bạn chưa được phân công lớp nào.")
        else:
            sel = st.selectbox("Chọn lớp để nhập điểm", [f"{i} - {n}" for i, n in opts])
            sec_id = sel.split(" - ")[0]
            data = ctrl.get_students_in_section(sec_id)
            
            if any(row['Điểm CK'] is not None for row in data):
                st.warning("⚠️ Lớp này đã có điểm. Vui lòng chuyển sang menu 'Cập nhật điểm (UC11)' để chỉnh sửa.")
            
            edited = st.data_editor(
                data, num_rows="fixed", use_container_width=True,
                column_config={
                    "MSSV": st.column_config.TextColumn(disabled=True),
                    "Họ tên": st.column_config.TextColumn(disabled=True),
                    "Điểm QT": st.column_config.NumberColumn(step=0.1, format="%.1f"),
                    "Điểm CK": st.column_config.NumberColumn(step=0.1, format="%.1f")
                }
            )
            if st.button("💾 Lưu điểm"):
                ok, msg = ctrl.enter_grades(sec_id, edited)
                if ok: st.success(msg)
                else: st.error(msg)

    # --- 5. CẬP NHẬT ĐIỂM (UC 11) ---
    elif menu == "Cập nhật điểm (UC11)":
        c1, c2 = st.columns([4, 1])
        c1.title("✏️ Cập nhật điểm (UC11)")
        c2.button("⬅️ Trang chủ", on_click=lambda: navigate("Dashboard"))

        opts = ctrl.get_my_sections()
        if not opts:
            st.warning("Bạn chưa được phân công lớp nào.")
        else:
            # Logic: Kiểm tra xem có yêu cầu chuyển hướng từ tab Phúc khảo không
            default_index = 0
            if 'target_section' in st.session_state:
                target_id = st.session_state['target_section']
                for i, (sid, sname) in enumerate(opts):
                    if sid == target_id:
                        default_index = i
                        break
                del st.session_state['target_section']
                st.toast(f"Đã chuyển đến lớp {target_id} theo yêu cầu phúc khảo.", icon="✅")

            sel = st.selectbox(
                "Chọn lớp cần sửa điểm", 
                [f"{i} - {n}" for i, n in opts], 
                index=default_index
            )
            sec_id = sel.split(" - ")[0]
            data = ctrl.get_students_in_section(sec_id)
            
            edited = st.data_editor(
                data, num_rows="fixed", use_container_width=True,
                column_config={
                    "MSSV": st.column_config.TextColumn(disabled=True),
                    "Họ tên": st.column_config.TextColumn(disabled=True),
                    "Điểm QT": st.column_config.NumberColumn(step=0.1, format="%.1f"),
                    "Điểm CK": st.column_config.NumberColumn(step=0.1, format="%.1f")
                }
            )
            
            with st.form("update_grade_form"):
                st.markdown("**Lý do chỉnh sửa (Bắt buộc):**")
                reason = st.text_input("Lý do", placeholder="VD: Nhập sai, Phúc khảo...", label_visibility="collapsed")
                
                if st.form_submit_button("💾 Cập nhật"):
                    ok, msg = ctrl.update_grades(sec_id, edited, reason)
                    if ok: st.success(msg)
                    else: st.error(msg)

    # --- 6. DUYỆT PHÚC KHẢO (UC 12) ---
    elif menu == "Duyệt phúc khảo":
        c1, c2 = st.columns([4, 1])
        c1.title("📩 Duyệt yêu cầu phúc khảo")
        c2.button("⬅️ Trang chủ", on_click=lambda: navigate("Dashboard"))

        reqs = ctrl.get_pending_reviews_detailed()
        
        if not reqs:
            st.info("Không có yêu cầu nào cần xử lý.")
        else:
            st.write(f"Có **{len(reqs)}** yêu cầu đang chờ xử lý:")
            
            for item in reqs:
                r = item['request']
                label = f"📌 {item['student_name']} - {item['course_name']} ({item['section_id']})"
                
                with st.expander(label, expanded=True):
                    c_a, c_b = st.columns(2)
                    c_a.markdown(f"**Mã SV:** `{item['student_id']}`")
                    c_a.markdown(f"**Ngày gửi:** {item['date']}")
                    c_b.markdown(f"**Môn học:** {item['course_name']}")
                    st.markdown("---")
                    st.markdown(f"🗣️ **Lý do sinh viên:** {item['reason']}")
                    
                    with st.form(key=f"rv_{r.requestID}"):
                        reply = st.text_input("Phản hồi của GV", value=r.reply, placeholder="Nhập lý do...")
                        
                        action = st.radio("Quyết định", ["Chưa xử lý", "Chấp nhận (Accept)", "Từ chối (Reject)"], horizontal=True)
                        
                        if st.form_submit_button("Xác nhận xử lý"):
                            if action == "Chưa xử lý":
                                st.warning("Vui lòng chọn Chấp nhận hoặc Từ chối.")
                            else:
                                if action == "Chấp nhận (Accept)":
                                    ok, msg = ctrl.process_review(r.requestID, "Approved", reply)
                                    if ok:
                                        st.success(f"{msg}. Đang chuyển sang màn hình sửa điểm...")
                                        # CHUYỂN HƯỚNG SANG UC11
                                        st.session_state['lec_nav'] = "Cập nhật điểm (UC11)"
                                        st.session_state['target_section'] = item['section_id']
                                        st.rerun()
                                else:
                                    ok, msg = ctrl.process_review(r.requestID, "Rejected", reply)
                                    if ok: 
                                        st.success(msg)
                                        st.rerun()
                                    else: st.error(msg)

    # --- 7. ĐỔI MẬT KHẨU ---
    elif menu == "Đổi mật khẩu":
        c1, c2 = st.columns([4, 1])
        c1.title("🔐 Đổi mật khẩu")
        c2.button("⬅️ Trang chủ", on_click=lambda: navigate("Dashboard"))
        with st.form("cp"):
            o = st.text_input("Mật khẩu cũ", type="password")
            n = st.text_input("Mật khẩu mới", type="password")
            c = st.text_input("Xác nhận", type="password")
            if st.form_submit_button("Lưu"):
                ok, msg = auth.change_password(user.userID, o, n, c)
                if ok: st.success(msg)
                else: st.error(msg)