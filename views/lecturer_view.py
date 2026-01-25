import streamlit as st
import pandas as pd
from controllers.lecturer_controller import LecturerController
from controllers.auth_controller import AuthController

def render_lecturer_ui(user_account):
    ctrl = LecturerController(user_account.userID)
    lecturer_info = ctrl.get_lecturer_info()
    auth = AuthController()

    if not lecturer_info:
        st.error("⚠️ Lỗi: Không tìm thấy hồ sơ giảng viên.")
        return

    # --- 1. QUẢN LÝ STATE (Chuẩn Callback) ---
    if 'lec_nav' not in st.session_state: 
        st.session_state['lec_nav'] = "Dashboard"
    
    # Hàm callback: Chỉ đổi state, KHÔNG rerun (Streamlit tự lo)
    def set_nav(page):
        st.session_state['lec_nav'] = page

    def logout(): 
        st.session_state['user'] = None
        st.session_state['lec_nav'] = "Dashboard"
        st.rerun()

    # --- SIDEBAR ---
    st.sidebar.title(f"👨‍🏫 GV: {lecturer_info.fullName}")
    
    options = ["Dashboard", "Hồ sơ", "Lịch dạy", "Nhập điểm", "Cập nhật điểm", "Duyệt phúc khảo", "Đổi mật khẩu"]
    
    # Xác định index
    try: idx = options.index(st.session_state['lec_nav'])
    except: idx = 0
        
    # Hàm sync sidebar
    def on_sidebar_change():
        st.session_state['lec_nav'] = st.session_state['lec_sidebar_key']

    st.sidebar.radio(
        "Menu", 
        options, 
        index=idx, 
        key="lec_sidebar_key", 
        on_change=on_sidebar_change
    )

    if st.sidebar.button("Đăng xuất", key="btn_lec_logout"): 
        logout()

    # --- HEADER HELPER ---
    def render_header(title):
        c1, c2 = st.columns([5, 1])
        c1.title(title)
        # Nút Back dùng callback
        c2.button("⬅️ Trang chủ", key=f"bk_{title}", on_click=set_nav, args=("Dashboard",))
        st.divider()

    # Lấy menu hiện tại
    menu = st.session_state['lec_nav']

    # ========================================================
    # NỘI DUNG CHÍNH
    # ========================================================

    # --- 1. DASHBOARD ---
    if menu == "Dashboard":
        st.title("🏠 Trang chủ Giảng viên")
        
        # 👇 ĐÃ KHÔI PHỤC HIỂN THỊ HỌC VỊ & CHỨC VỤ
        with st.container(border=True):
            st.subheader("📌 Thông tin cá nhân")
            c1, c2 = st.columns(2)
            c1.write(f"**Mã GV:** {lecturer_info.lecturerID}")
            c1.write(f"**Họ tên:** {lecturer_info.fullName}")
            
            # Lấy thông tin an toàn
            degree = getattr(lecturer_info, 'degree', '')
            position = getattr(lecturer_info, 'position', '')
            
            c1.write(f"**Học vị:** {degree}")
            c2.write(f"**Chức vụ:** {position}")
            c2.write(f"**Email:** {lecturer_info.email}")
            c2.write(f"**SĐT:** {lecturer_info.phone}")
            
        st.subheader("🚀 Truy cập nhanh")
        
        # 👇 BUTTON FIX: Dùng on_click=set_nav (Hoạt động 100%)
        c1, c2, c3 = st.columns(3)
        c1.button("👤 Hồ sơ cá nhân", use_container_width=True, key="QA_HOSO", on_click=set_nav, args=("Hồ sơ",))
        c2.button("📅 Xem Lịch dạy", use_container_width=True, key="QA_LICH", on_click=set_nav, args=("Lịch dạy",))
        c3.button("📝 Nhập điểm", use_container_width=True, key="QA_NHAP", on_click=set_nav, args=("Nhập điểm",))
            
        c4, c5, c6 = st.columns(3)
        c4.button("✏️ Cập nhật điểm", use_container_width=True, key="QA_SUA", on_click=set_nav, args=("Cập nhật điểm",))
        c5.button("📩 Duyệt phúc khảo", use_container_width=True, key="QA_PK", on_click=set_nav, args=("Duyệt phúc khảo",))
        c6.button("🔐 Đổi mật khẩu", use_container_width=True, key="QA_MK", on_click=set_nav, args=("Đổi mật khẩu",))

    # --- 2. HỒ SƠ ---
    elif menu == "Hồ sơ":
        render_header("Hồ sơ Giảng viên")
        tab1, tab2 = st.tabs(["Thông tin", "Cập nhật"])
        with tab1:
            c1, c2 = st.columns(2)
            c1.markdown(f"**Mã GV:** `{lecturer_info.lecturerID}`")
            c1.markdown(f"**Họ tên:** {lecturer_info.fullName}")
            
            # Hiển thị đầy đủ thông tin
            dob = getattr(lecturer_info, 'dob', '')
            gender = getattr(lecturer_info, 'gender', None)
            degree = getattr(lecturer_info, 'degree', '')
            position = getattr(lecturer_info, 'position', '')
            
            c1.markdown(f"**Ngày sinh:** {dob}")
            c1.markdown(f"**Giới tính:** {'Nam' if gender else 'Nữ'}")
            
            c2.markdown(f"**Học vị:** {degree}")
            c2.markdown(f"**Chức vụ:** {position}")
            c2.markdown(f"**Email:** {lecturer_info.email}")
            st.divider()
            st.write(f"**Địa chỉ:** {lecturer_info.address}")
            st.write(f"**SĐT:** {lecturer_info.phone}")
            
        with tab2:
            with st.form("edit_lec_form"):
                ph = st.text_input("SĐT", lecturer_info.phone)
                em = st.text_input("Email", lecturer_info.email)
                ad = st.text_input("Địa chỉ", lecturer_info.address)
                if st.form_submit_button("Lưu thay đổi"):
                    ok, msg = ctrl.update_contact_info(ph, em, ad)
                    if ok: st.success(msg); st.rerun()
                    else: st.error(msg)

    # --- 3. LỊCH DẠY ---
    elif menu == "Lịch dạy":
        render_header("📅 Lịch giảng dạy")
        sch = ctrl.get_teaching_schedule()
        if sch:
            df = pd.DataFrame(sch)
            # Sắp xếp và ẩn cột phụ
            if '_d' in df.columns: 
                df = df.sort_values(by=["_d", "_s"]).drop(columns=["_d", "_s"])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Hiện không có lịch dạy.")

    # --- 4. NHẬP ĐIỂM (UC10) ---
    elif menu == "Nhập điểm":
        render_header("📝 Nhập điểm")
        opts = ctrl.get_my_sections()
        
        if not opts:
            st.warning("Bạn chưa được phân công lớp nào.")
        else:
            sel = st.selectbox("Chọn lớp:", [f"{i} - {n}" for i, n in opts])
            sec_id = sel.split(" - ")[0]
            data = ctrl.get_students_in_section(sec_id)
            
            # Kiểm tra nếu đã có điểm
            has_grade = False
            for row in data:
                if row.get('Điểm CK') is not None or row.get('Điểm QT') is not None:
                    has_grade = True
                    break
            if has_grade: st.info("ℹ️ Lớp này đã có điểm.")
            
            # Cho phép nhập trống (None)
            edited = st.data_editor(
                data, 
                num_rows="fixed", 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "MSSV": st.column_config.TextColumn(disabled=True),
                    "Họ tên": st.column_config.TextColumn(disabled=True),
                    "Điểm QT": st.column_config.NumberColumn(min_value=0, max_value=10, step=0.1, format="%.1f"),
                    "Điểm CK": st.column_config.NumberColumn(min_value=0, max_value=10, step=0.1, format="%.1f")
                }
            )
            
            if st.button("💾 Lưu bảng điểm", type="primary"):
                ok, msg = ctrl.enter_grades(sec_id, edited)
                if ok: st.success(msg)
                else: st.error(msg)

    # --- 5. CẬP NHẬT ĐIỂM (UC11) ---
    elif menu == "Cập nhật điểm":
        render_header("✏️ Cập nhật điểm")
        opts = ctrl.get_my_sections()
        
        if not opts:
            st.warning("Bạn chưa được phân công lớp nào.")
        else:
            # === LOGIC GIỮ TRẠNG THÁI LỚP (PERSISTENCE) ===
            if 'uc11_idx' not in st.session_state: st.session_state['uc11_idx'] = 0

            # Xử lý chuyển trang từ Phúc Khảo
            if 'target_section' in st.session_state:
                tid = str(st.session_state.pop('target_section')).strip()
                for i, (sid, _) in enumerate(opts):
                    if str(sid).strip() == tid:
                        st.session_state['uc11_idx'] = i
                        break
                st.toast(f"Đã chuyển đến lớp {tid}", icon="✅")

            # Validate index
            if st.session_state['uc11_idx'] >= len(opts): st.session_state['uc11_idx'] = 0

            # Render Selectbox
            sel = st.selectbox(
                "Chọn lớp cần sửa điểm:", 
                options=[f"{i} - {n}" for i, n in opts], 
                index=st.session_state['uc11_idx'],
                key="uc11_sb"
            )
            
            # Cập nhật ngược lại state
            curr_idx = [f"{i} - {n}" for i, n in opts].index(sel)
            st.session_state['uc11_idx'] = curr_idx

            sec_id = sel.split(" - ")[0]
            data = ctrl.get_students_in_section(sec_id)
            
            edited = st.data_editor(
                data, 
                num_rows="fixed", 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "MSSV": st.column_config.TextColumn(disabled=True),
                    "Họ tên": st.column_config.TextColumn(disabled=True),
                    "Điểm QT": st.column_config.NumberColumn(min_value=0, max_value=10, step=0.1, format="%.1f"),
                    "Điểm CK": st.column_config.NumberColumn(min_value=0, max_value=10, step=0.1, format="%.1f")
                }
            )
            
            st.write("---")
            with st.form("upd_form"):
                reason = st.text_input("Lý do chỉnh sửa (Bắt buộc):")
                if st.form_submit_button("💾 Cập nhật"):
                    if not reason: st.error("Vui lòng nhập lý do!")
                    else:
                        ok, msg = ctrl.update_grades(sec_id, edited, reason)
                        if ok: st.success(msg)
                        else: st.error(msg)

    # --- 6. DUYỆT PHÚC KHẢO ---
    elif menu == "Duyệt phúc khảo":
        render_header("📩 Duyệt yêu cầu phúc khảo")
        reqs = ctrl.get_pending_reviews_detailed()
        
        if not reqs:
            st.info("Không có yêu cầu nào.")
        else:
            for item in reqs:
                r = item['request']
                with st.expander(f"📌 {item['student_name']} - {item['course_name']}", expanded=True):
                    st.write(f"**Lý do:** {item['reason']}")
                    with st.form(f"rv_{r.requestID}"):
                        reply = st.text_input("Phản hồi:")
                        act = st.radio("Quyết định:", ["Chưa xử lý", "Chấp nhận", "Từ chối"], horizontal=True)
                        if st.form_submit_button("Xác nhận"):
                            if act == "Chấp nhận":
                                ctrl.process_review(r.requestID, 1, reply)
                                st.success("Đã duyệt. Chuyển trang...")
                                st.session_state['lec_nav'] = "Cập nhật điểm (UC11)"
                                st.session_state['target_section'] = item['section_id']
                                st.rerun()
                            elif act == "Từ chối":
                                ctrl.process_review(r.requestID, 2, reply)
                                st.success("Đã từ chối."); st.rerun()

    # --- 7. ĐỔI MẬT KHẨU ---
    elif menu == "Đổi mật khẩu":
        render_header("🔐 Đổi mật khẩu")
        with st.form("cp_lec"):
            o = st.text_input("Mật khẩu cũ", type="password")
            n = st.text_input("Mật khẩu mới", type="password")
            c = st.text_input("Xác nhận", type="password")
            if st.form_submit_button("Lưu thay đổi"):
                ok, msg = auth.change_password(user_account.userID, o, n, c)
                if ok: st.success(msg); st.rerun()
                else: st.error(msg)