import streamlit as st
from core.database import MockDatabase

class AuthController:
    def __init__(self):
        self.db = MockDatabase()

    def login(self, username, password):
        user = self.db.get_user(username)
        if user and user.password == password:
            if hasattr(user, 'status') and user.status is False:
                return None # Tài khoản bị khóa
            return user
        return None

    def change_password(self, user_id, old_pass, new_pass, confirm_pass):
        # 1. Kiểm tra nhập thiếu
        if not old_pass or not new_pass or not confirm_pass:
            return False, "Vui lòng nhập đầy đủ thông tin."
        
        # 2. Kiểm tra xác nhận mật khẩu
        if new_pass != confirm_pass:
            return False, "Mật khẩu xác nhận không khớp."

        # 3. --- BỔ SUNG CHECK: MẬT KHẨU MỚI KHÔNG ĐƯỢC TRÙNG CŨ ---
        if new_pass == old_pass:
            return False, "❌ Mật khẩu mới không được trùng với mật khẩu hiện tại."

        # 4. Kiểm tra độ dài (Tùy chọn thêm nếu muốn chặt chẽ hơn)
        if len(new_pass) < 3:
            return False, "Mật khẩu mới phải có ít nhất 3 ký tự."

        # 5. Kiểm tra mật khẩu cũ có đúng không
        user = self.db.get_user(user_id)
        if user and user.password == old_pass:
            user.password = new_pass
            return True, "✅ Đổi mật khẩu thành công!"
        else:
            return False, "❌ Mật khẩu cũ không chính xác."
    
    # ... (Các hàm send_otp, verify_otp, reset_password giữ nguyên) ...