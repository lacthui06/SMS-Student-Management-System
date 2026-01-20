import streamlit as st
from controllers.auth_controller import AuthController

def render_login():
    st.markdown("## 🏫 Đăng nhập Hệ thống (EduSoft)")
    
    auth = AuthController()
    
    # Session state cho việc chuyển đổi giữa Login và Recover Password
    if 'auth_mode' not in st.session_state:
        st.session_state['auth_mode'] = 'login'

    if st.session_state['auth_mode'] == 'login':
        with st.form("login_form"):
            username = st.text_input("Tên đăng nhập")
            password = st.text_input("Mật khẩu", type="password")
            submit = st.form_submit_button("Đăng nhập", use_container_width=True)
            
            if submit:
                user = auth.login(username, password)
                if user == "Locked":
                    st.error("Tài khoản đã bị khóa. Liên hệ Admin.")
                elif user:
                    st.session_state['user'] = user
                    st.session_state['page'] = 'Dashboard'
                    st.rerun()
                else:
                    st.error("Sai thông tin đăng nhập.")
        
        if st.button("Quên mật khẩu?"):
            st.session_state['auth_mode'] = 'recover'
            st.rerun()

    elif st.session_state['auth_mode'] == 'recover':
        st.subheader("🔑 Khôi phục mật khẩu (UC3)")
        with st.form("recover_form"):
            email = st.text_input("Nhập Email đã đăng ký")
            otp = st.text_input("Nhập OTP (Demo: 123456)")
            new_pass = st.text_input("Mật khẩu mới", type="password")
            
            c1, c2 = st.columns(2)
            send_otp = c1.form_submit_button("Gửi OTP")
            reset_pass = c2.form_submit_button("Đặt lại mật khẩu")
            
            if send_otp:
                ok, msg = auth.recover_password(email)
                if ok: st.success(msg)
                else: st.error(msg)
            
            if reset_pass:
                ok, msg = auth.verify_otp_and_reset(email, otp, new_pass)
                if ok:
                    st.success(msg)
                    st.session_state['auth_mode'] = 'login'
                    st.rerun()
                else:
                    st.error(msg)
        
        if st.button("Quay lại Đăng nhập"):
            st.session_state['auth_mode'] = 'login'
            st.rerun()