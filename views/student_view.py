import streamlit as st
import pandas as pd
import time
from controllers.student_controller import StudentController
from controllers.auth_controller import AuthController
from core.database import Session
from core.models_orm import Student
from datetime import datetime

def render_student_ui(user):
    # --- 1. LẤY THÔNG TIN SINH VIÊN ---
    session = Session()
    current_student = session.query(Student).filter_by(userID=user.userID).first()
    session.close()

    if not current_student:
        st.error("⚠️ Lỗi: Tài khoản này chưa được liên kết với hồ sơ Sinh viên nào!")
        return

    ctrl = StudentController(current_student.studentID)
    auth = AuthController()
    
    # --- SIDEBAR ---
    st.sidebar.title(f"🎓 {current_student.fullName}")
    st.sidebar.write(f"MSSV: {current_student.studentID}")
    
    options = ["Dashboard", "Hồ sơ", "Lịch học", "Kết quả học tập", "Tiến độ học tập", "Đổi mật khẩu"]
    
    # Khởi tạo state điều hướng
    if 'student_nav' not in st.session_state:
        st.session_state['student_nav'] = "Dashboard"

    # Hàm điều hướng an toàn (tránh lỗi StreamlitAPIException)
    def navigate(page):
        st.session_state['student_nav'] = page

    # Xác định index hiện tại cho Radio button
    try:
        current_index = options.index(st.session_state['student_nav'])
    except ValueError:
        current_index = 0

    # 👇 SỬA LỖI Ở ĐÂY: Không dùng key trực tiếp vào state, dùng logic cập nhật
    selected = st.sidebar.radio("Menu", options, index=current_index)
    
    # Nếu người dùng bấm Radio thay đổi -> Cập nhật state
    if selected != st.session_state['student_nav']:
        st.session_state['student_nav'] = selected
        st.rerun()

    if st.sidebar.button("Đăng xuất"):
        st.session_state['user'] = None
        st.session_state['student_nav'] = "Dashboard"
        st.rerun()

    # --- NỘI DUNG TRANG ---
    page = st.session_state['student_nav']

    # === TRANG 1: DASHBOARD ===
    if page == "Dashboard":
        st.title("🏠 Trang chủ Sinh viên")

        # Hàm xử lý ngày tháng cho đẹp (Bỏ giờ phút giây thừa thãi)
        def format_date(d):
            if not d: return "..."
            # Nếu là chuỗi thì trả về luôn, nếu là datetime thì format lại
            return d.strftime("%d/%m/%Y") if hasattr(d, "strftime") else str(d)

        with st.container(border=True):
            st.subheader("📌 Thông tin sinh viên")
            
            # --- DÒNG 1: THÔNG TIN ĐỊNH DANH (3 Cột) ---
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"**🆔 MSSV:** {current_student.studentID}")
            c2.markdown(f"**👤 Họ tên:** {current_student.fullName}")
            c3.markdown(f"**⚧ Giới tính:** {'Nam' if current_student.gender else 'Nữ'}")
            
            st.divider() # Một đường kẻ duy nhất ở giữa cho thoáng
            
            # --- DÒNG 2: THÔNG TIN CHI TIẾT (3 Cột) ---
            # Đưa "Ngành" xuống đây để lấp đầy khoảng trống
            c4, c5, c6 = st.columns(3)
            
            c4.markdown(f"**🎓 Ngành:** {current_student.majorID}")
            c5.markdown(f"**🎂 Ngày sinh:** {format_date(current_student.dob)}")
            c6.markdown(f"**📱 SĐT:** {current_student.phone}")
            st.divider()
            # --- DÒNG 3: EMAIL (Riêng 1 dòng hoặc ghép vào nếu muốn) ---
            st.markdown(f"**📧 Email:** {current_student.email}")

        st.markdown("### 🚀 Truy cập nhanh")
        col1, col2, col3 = st.columns(3)
        # Các nút này gọi hàm navigate -> cập nhật state -> Rerun -> Radio tự nhảy theo index
        with col1: st.button("📅 Xem Lịch học", use_container_width=True, on_click=navigate, args=("Lịch học",))
        with col2: st.button("📊 Xem Tiến độ", use_container_width=True, on_click=navigate, args=("Tiến độ học tập",))
        with col3: st.button("📑 Xem Kết quả", use_container_width=True, on_click=navigate, args=("Kết quả học tập",))
        
        st.markdown("")
        col4, col5 = st.columns(2)
        with col4: st.button("👤 Hồ sơ cá nhân", use_container_width=True, on_click=navigate, args=("Hồ sơ",))
        with col5: st.button("🔐 Đổi mật khẩu", use_container_width=True, on_click=navigate, args=("Đổi mật khẩu",))

    # === TRANG 2: HỒ SƠ ===
    elif page == "Hồ sơ":
        c1, c2 = st.columns([4, 1])
        c1.title("Hồ sơ sinh viên")
        c2.button("⬅️ Trang chủ", key="back_prof", on_click=navigate, args=("Dashboard",))

        tab1, tab2 = st.tabs(["👁️ Thông tin chi tiết", "✏️ Cập nhật liên hệ"])
        with tab1:
            st.subheader("Thông tin cơ bản")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**MSSV:** {current_student.studentID}")
                st.markdown(f"**Họ tên:** {current_student.fullName}")
                st.markdown(f"**Ngày sinh:** {current_student.dob}")
                st.markdown(f"**Nơi sinh:** {current_student.pob}")
                st.markdown(f"**Ngành:** {current_student.majorID}")
            with col2:
                st.markdown(f"**Khóa học:** 2024")
                st.markdown(f"**Giới tính:** {'Nam' if current_student.gender else 'Nữ'}")
                st.markdown(f"**CCCD:** {current_student.citizenID}")
                st.markdown(f"**Hệ đào tạo:** Chính quy")
            st.divider()
            st.subheader("Thông tin liên hệ")
            st.markdown(f"📍 **Địa chỉ:** {current_student.address}")
            st.markdown(f"📞 **SĐT:** {current_student.phone}")
            st.markdown(f"📧 **Email:** {current_student.email}")

        with tab2:
            st.info("Cập nhật thông tin liên lạc")
            with st.form("edit"):
                ph = st.text_input("Số điện thoại", current_student.phone)
                em = st.text_input("Email", current_student.email)
                ad = st.text_input("Địa chỉ", current_student.address)
                
                if st.form_submit_button("Lưu thay đổi"):
                    ok, msg = ctrl.update_contact_info(ph, em, ad)
                    if ok:
                        st.success(msg)
                        time.sleep(1.5)
                        st.rerun()
                    else:
                        st.error(msg)

    # === TRANG 3: LỊCH HỌC ===
    elif page == "Lịch học":
        c1, c2 = st.columns([4, 1])
        c1.title("📅 Lịch học cá nhân")
        c2.button("⬅️ Trang chủ", key="back_tt", on_click=navigate, args=("Dashboard",))

        data = ctrl.get_timetable()
        if data:
            df = pd.DataFrame(data)
            if not df.empty and '_day_sort' in df.columns:
                 df = df.sort_values(by=["_day_sort", "_start_sort"]).drop(columns=["_day_sort", "_start_sort"])
            
            # Sắp xếp cột
            column_order = ["Mã Lớp", "Môn Học", "Thứ", "Ca/Tiết", "Giờ học", "Phòng", "Giảng viên"]
            final_cols = [c for c in column_order if c in df.columns]
            
            st.dataframe(df[final_cols], use_container_width=True, hide_index=True)
        else:
            st.warning("Hiện tại chưa có lịch học hoặc bạn chưa đăng ký môn.")

    # === TRANG 4: TIẾN ĐỘ HỌC TẬP ===
    elif page == "Tiến độ học tập":
        c1, c2 = st.columns([4, 1])
        c1.title("📊 Tiến độ học tập")
        c2.button("⬅️ Trang chủ", key="back_prog", on_click=navigate, args=("Dashboard",))

        prog = ctrl.get_progress_data()
        
        # 1. Lấy số tín chỉ tích lũy (nếu None thì coi là 0)
        acc = prog.get('accumulated') or 0
        
        # 2. Lấy tổng tín chỉ yêu cầu
        req = prog.get('required')

        # 3. Kiểm tra trước khi chia
        if req and req > 0:
            # Nếu có tổng tín chỉ đàng hoàng -> Tính % bình thường
            percent = min(acc / req, 1.0)
            label = f"{acc} / {req}"
        else:
            # Nếu chưa có khung chương trình (req bị None) -> Set 0% để không sập App
            percent = 0.0
            label = f"{acc} / (Chưa cập nhật khung CT)"

        # 4. Hiển thị ra màn hình
        st.metric("Tín chỉ tích lũy", label)
        st.progress(percent)
        
        # ------------------------------------------------

        st.divider()
        st.subheader("Danh sách các môn đã hoàn thành")
        if prog.get('details'):
            st.dataframe(pd.DataFrame(prog['details']), use_container_width=True, hide_index=True)
        else:
            st.info("Chưa có môn học nào hoàn thành.")

   # === TRANG 5: KẾT QUẢ HỌC TẬP & PHÚC KHẢO ===
    elif page == "Kết quả học tập":
        st.title("📑 Bảng điểm & Phúc khảo")

        # --- PHẦN 1: XEM ĐIỂM (THEO ĐẶC TẢ) ---
        
        # 1. Gọi hàm lấy danh sách Học kỳ
        semesters = ctrl.get_student_semesters()
        
        if not semesters:
            st.info("⚠️ Bạn chưa có dữ liệu học tập nào.")
        else:
            # 2. Tạo Dropdown chọn Học kỳ
            sem_dict = {s.semesterID: s.name for s in semesters}
            # Mặc định chọn học kỳ mới nhất (cuối danh sách)
            sel_sem = st.selectbox("Chọn học kỳ:", list(sem_dict.keys()), format_func=lambda x: sem_dict[x])

            # 3. Gọi hàm lấy GPA, CPA và Bảng điểm chi tiết
            df_grades, gpa, cpa = ctrl.get_academic_results(sel_sem)

            # 4. Hiển thị GPA và CPA (KPIs)
            c1, c2 = st.columns(2)
            c1.metric(f"GPA ({sem_dict[sel_sem]})", f"{gpa} / 10")
            c2.metric("CPA Tích lũy", f"{cpa} / 10", delta="Toàn khóa")

            st.divider()

            # 5. Hiển thị bảng điểm
            st.subheader(f"Chi tiết bảng điểm: {sem_dict[sel_sem]}")
            st.dataframe(df_grades, use_container_width=True, hide_index=True)
            st.caption("(*) Điểm chữ A, B, C, D, F quy đổi từ thang điểm 10.")

        st.divider()

        # --- PHẦN 2: PHÚC KHẢO (CODE CỦA BẠN GIỮ NGUYÊN LOGIC) ---
        st.subheader("📝 Quản lý Phúc khảo")
        
        history = ctrl.get_review_history(current_student.studentID)
        if not history:
            st.info("Chưa có lịch sử phúc khảo.")
        else:
            for item in history:
                status_color = "orange" if item['status'] == "Chưa xử lý" else "green" if item['status'] == "Đã duyệt" else "red"
                with st.expander(f"{item['courseName']} ({item['sectionID']}) - :{status_color}[{item['status']}]"):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.write(f"**Ngày gửi:** {item['date']}")
                        st.write(f"**Lý do:** {item['reason']}")
                        if item['reply']:
                            st.info(f"👨‍🏫 **GV Phản hồi:** {item['reply']}")
                    with c2:
                        if item['status'] == "Chưa xử lý":
                            if st.button("🗑️ Hủy đơn", key=f"del_{item['requestID']}"):
                                ok, msg = ctrl.cancel_review_request(item['requestID'])
                                if ok:
                                    st.success(msg)
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error(msg)

        st.divider()
        st.subheader("Gửi yêu cầu mới")
        
        # Logic chọn môn để phúc khảo
        all_courses = ctrl.get_reviewable_courses()
        pending_sections = [h['sectionID'] for h in history if h['status'] == "Chưa xử lý"]
        # Chỉ hiện môn chưa có đơn đang chờ
        available_courses = [c for c in all_courses if c.sectionID not in pending_sections]

        if not available_courses:
            st.success("✅ Bạn không có môn nào cần phúc khảo.")
        else:
            with st.form("create_review"):
                options_map = {c.sectionID: f"{c.courseName} ({c.sectionID})" for c in available_courses}
                selected_sec_id = st.selectbox("Chọn môn:", list(options_map.keys()), format_func=lambda x: options_map[x])
                reason = st.text_area("Lý do phúc khảo (>10 ký tự):")
                
                if st.form_submit_button("🚀 Gửi yêu cầu"):
                    if len(reason.strip()) < 10:
                        st.error("Vui lòng nhập lý do cụ thể hơn.")
                    else:
                        ok, msg = ctrl.create_review_request(selected_sec_id, reason)
                        if ok:
                            st.success(msg)
                            time.sleep(1.5)
                            st.rerun()
                        else:
                            st.error(msg)

    # === TRANG 6: ĐỔI MẬT KHẨU ===
    elif page == "Đổi mật khẩu":
        c1, c2 = st.columns([4, 1])
        c1.title("🔐 Đổi mật khẩu")
        c2.button("⬅️ Trang chủ", key="back_pass", on_click=navigate, args=("Dashboard",))

        with st.form("change_pass_form"):
            o = st.text_input("Mật khẩu cũ", type="password")
            n = st.text_input("Mật khẩu mới", type="password")
            c = st.text_input("Xác nhận mật khẩu mới", type="password")
            if st.form_submit_button("Lưu thay đổi"):
                ok, msg = auth.change_password(user.userID, o, n, c)
                if ok: 
                    st.success(msg)
                    time.sleep(1.5)
                    st.rerun()
                else: 
                    st.error(msg)