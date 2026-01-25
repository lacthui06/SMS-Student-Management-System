import streamlit as st
from controllers.auth_controller import AuthController

def render_login():
    st.markdown("## 🏫 Đăng nhập Hệ thống SMS")
    
    auth = AuthController()
    
    # --- KHỞI TẠO STATE ---
    # Biến điều khiển chuyển màn hình Login <-> Recover
    if 'auth_mode' not in st.session_state:
        st.session_state['auth_mode'] = 'login'
    
    # Biến lưu mã OTP thật để kiểm tra
    if 'real_otp_code' not in st.session_state:
        st.session_state['real_otp_code'] = None
    if 'reset_email' not in st.session_state:
        st.session_state['reset_email'] = None

    # ==========================================
    # 1. MÀN HÌNH ĐĂNG NHẬP
    # ==========================================
    if st.session_state['auth_mode'] == 'login':
        with st.form("login_form"):
            username = st.text_input("Tên đăng nhập")
            password = st.text_input("Mật khẩu", type="password")
            submit = st.form_submit_button("Đăng nhập", use_container_width=True)
            
            if submit:
                user, msg = auth.login(username, password)
                if user:
                    st.success(msg)
                    st.session_state['user'] = user
                    st.session_state['logged_in'] = True
                    st.rerun()
                else:
                    st.error(msg)
        
        # Nút chuyển qua màn hình quên mật khẩu
        if st.button("Quên mật khẩu?"):
            st.session_state['auth_mode'] = 'recover'
            st.rerun()

    # ==========================================
    # 2. MÀN HÌNH KHÔI PHỤC MẬT KHẨU
    # ==========================================
    elif st.session_state['auth_mode'] == 'recover':
        st.subheader("🔑 Khôi phục mật khẩu")
        
        with st.form("recover_form"):
            email = st.text_input("Nhập Email đã đăng ký")
            # Hiển thị luôn các ô nhập liệu như code mẫu của bạn
            otp = st.text_input("Nhập OTP (Kiểm tra email)")
            new_pass = st.text_input("Mật khẩu mới", type="password")
            
            c1, c2 = st.columns(2)
            send_otp = c1.form_submit_button("Gửi OTP")
            reset_pass = c2.form_submit_button("Đặt lại mật khẩu")
            
            # --- XỬ LÝ NÚT GỬI OTP ---
            if send_otp:
                if not email:
                    st.warning("Vui lòng nhập Email!")
                else:
                    # Gọi controller gửi mail thật (trả về 3 giá trị)
                    ok, msg, otp_code = auth.recover_password(email)
                    if ok:
                        st.success(msg)
                        # Lưu OTP thật và Email vào session để lát nữa kiểm tra
                        st.session_state['real_otp_code'] = otp_code
                        st.session_state['reset_email'] = email
                    else:
                        st.error(msg)
            
            # --- XỬ LÝ NÚT ĐẶT LẠI MẬT KHẨU ---
            if reset_pass:
                # 1. Kiểm tra xem người dùng đã nhập đúng OTP thật chưa
                if st.session_state['real_otp_code'] and otp == st.session_state['real_otp_code']:
                    
                    # 2. Kiểm tra email có khớp với email lúc gửi OTP không
                    if email == st.session_state['reset_email']:
                        # Gọi hàm đổi pass trong DB
                        ok, msg = auth.reset_password_with_otp(email, new_pass)
                        if ok:
                            st.success(msg)
                            # Reset xong thì quay về đăng nhập
                            st.session_state['auth_mode'] = 'login'
                            st.session_state['real_otp_code'] = None # Xóa OTP cũ cho an toàn
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.error("Email không khớp với mã OTP đã gửi!")
                else:
                    st.error("❌ Mã OTP không đúng hoặc bạn chưa bấm Gửi OTP!")
        
        # Nút quay lại
        if st.button("Quay lại Đăng nhập"):
            st.session_state['auth_mode'] = 'login'
            st.rerun()