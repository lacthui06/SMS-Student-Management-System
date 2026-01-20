import streamlit as st
import smtplib
import random
import string
from email.mime.text import MIMEText
from core.database import MockDatabase

# --- CẤU HÌNH GMAIL ---
# ⚠️ CẢNH BÁO: Không được lộ mật khẩu này nếu public lên GitHub
SENDER_EMAIL = "superstudentmanagementsystem@gmail.com"  # <--- Thay email của bạn vào đây
SENDER_PASSWORD = "qhld fiuz zdrb dghx"    # <--- Dán mã 16 ký tự App Password vào đây

class AuthController:
    def __init__(self):
        self.db = MockDatabase()

    def login(self, username, password):
        user = self.db.get_user(username)
        if user and user.password == password:
            if hasattr(user, 'status') and user.status is False:
                return None
            return user
        return None

    def change_password(self, user_id, old_pass, new_pass, confirm_pass):
        if not old_pass or not new_pass or not confirm_pass:
            return False, "Vui lòng nhập đầy đủ thông tin."
        if new_pass != confirm_pass:
            return False, "Mật khẩu xác nhận không khớp."
        if new_pass == old_pass:
            return False, "❌ Mật khẩu mới không được trùng với mật khẩu hiện tại."
        if len(new_pass) < 3:
            return False, "Mật khẩu mới phải có ít nhất 3 ký tự."

        user = self.db.get_user(user_id)
        if user and user.password == old_pass:
            user.password = new_pass
            return True, "✅ Đổi mật khẩu thành công!"
        else:
            return False, "❌ Mật khẩu cũ không chính xác."

    # --- HÀM TẠO MÃ OTP NGẪU NHIÊN ---
    def _generate_otp(self, length=6):
        return ''.join(random.choices(string.digits, k=length))

    # --- HÀM GỬI EMAIL THỰC TẾ (SMTP) ---
    def _send_email_via_gmail(self, receiver_email, otp_code):
        msg = MIMEText(f"Mã xác thực (OTP) của bạn là: {otp_code}\nMã này có hiệu lực trong 5 phút.\nVui lòng không chia sẻ cho ai khác.", 'plain', 'utf-8')
        msg['Subject'] = "MÃ XÁC THỰC KHÔI PHỤC MẬT KHẨU - SMS PROJECT"
        msg['From'] = SENDER_EMAIL
        msg['To'] = receiver_email

        try:
            # Kết nối đến server Gmail
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.send_message(msg)
            return True, None
        except Exception as e:
            return False, str(e)

    # --- CHỨC NĂNG QUÊN MẬT KHẨU ---
    def recover_password(self, email):
        """
        Gửi mã OTP thật vào email qua Gmail SMTP
        """
        # 1. Tìm user trong DB
        users = st.session_state.get('users', {})
        found_user = None
        for u in users.values():
            if hasattr(u, 'email') and u.email == email:
                found_user = u
                break
        
        if not found_user:
            return False, "❌ Email không tồn tại trong hệ thống."

        # 2. Tạo OTP ngẫu nhiên (6 số)
        otp = self._generate_otp()
        
        # 3. Gửi Email thật
        success, error_msg = self._send_email_via_gmail(email, otp)
        
        if success:
            # Lưu OTP vào Session
            st.session_state['reset_otp'] = {
                'email': email,
                'code': otp
            }
            return True, f"✅ Đã gửi mã OTP đến {email}. Vui lòng kiểm tra hộp thư (kể cả Spam)."
        else:
            return False, f"❌ Lỗi gửi mail: {error_msg}"

    def verify_otp_and_reset(self, email, otp, new_pass):
        """
        Xác thực OTP và đặt lại mật khẩu
        """
        stored_data = st.session_state.get('reset_otp')
        
        if not stored_data:
            return False, "❌ Yêu cầu hết hạn. Vui lòng gửi lại OTP."

        if stored_data['email'] != email:
            return False, "❌ Email không khớp."
        
        if stored_data['code'] != otp:
            return False, "❌ Mã OTP không chính xác."

        if not new_pass:
            return False, "❌ Vui lòng nhập mật khẩu mới."

        # Cập nhật DB
        users = st.session_state.get('users', {})
        for u in users.values():
            if hasattr(u, 'email') and u.email == email:
                u.password = new_pass
                del st.session_state['reset_otp']
                return True, "✅ Đặt lại mật khẩu thành công! Hãy đăng nhập ngay."
        
        return False, "❌ Lỗi hệ thống: Không tìm thấy user."