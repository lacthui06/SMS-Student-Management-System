import smtplib, random, string, hashlib
from email.mime.text import MIMEText
from core.database import Session as DBSession
from core.models_orm import Account, Student, Lecturer 

SENDER_EMAIL = "superstudentmanagementsystem@gmail.com" 
SENDER_PASSWORD = "fuop lxpg sxmj lsmv" 

class AuthController:
    def __init__(self):
        self.session = DBSession()

    def _hash_password(self, password):
        return hashlib.sha256(str(password).encode('utf-8')).hexdigest()

    def login(self, user_id, password_input):
        try:
            user = self.session.query(Account).filter_by(userID=user_id).first()
            
            if not user: return None, "❌ Tên đăng nhập không tồn tại!"
            if user.status == 0: return None, "🚫 Tài khoản đã bị khóa."

            hashed_input = self._hash_password(password_input)
            
            # Biến cờ để xác định đăng nhập thành công hay không
            login_success = False
            msg = ""

            # Kiểm tra mật khẩu cũ (chưa hash)
            if len(user.password) < 60:
                if user.password == password_input:
                    user.password = hashed_input
                    self.session.commit()
                    login_success = True
                    msg = "✅ Đăng nhập thành công (Đã nâng cấp bảo mật)!"
                else:
                    msg = "❌ Mật khẩu không đúng!"
            
            # Kiểm tra mật khẩu chuẩn (đã hash)
            elif user.password == hashed_input:
                login_success = True
                msg = "✅ Đăng nhập thành công!"
            else:
                msg = "❌ Mật khẩu không đúng!"

            if login_success:
                # 👇 QUAN TRỌNG: Tách user ra khỏi session để dùng được sau khi close()
                self.session.expunge(user)
                return user, msg
            else:
                return None, msg

        except Exception as e:
            return None, f"Lỗi: {str(e)}"
        finally:
            self.session.close()

    def change_password(self, user_id, old_pass, new_pass, confirm_pass):
        try:
            if new_pass != confirm_pass: return False, "❌ Mật khẩu xác nhận không khớp!"
            if len(new_pass) < 6: return False, "⚠️ Mật khẩu quá ngắn."

            user = self.session.query(Account).filter_by(userID=user_id).first()
            if not user: return False, "Tài khoản không tồn tại."

            hashed_old = self._hash_password(old_pass)
            is_valid_old = False
            
            if len(user.password) < 60:
                if user.password == old_pass: is_valid_old = True
            else:
                if user.password == hashed_old: is_valid_old = True
            
            if is_valid_old:
                user.password = self._hash_password(new_pass)
                self.session.commit()
                return True, "✅ Đổi mật khẩu thành công!"
            return False, "❌ Mật khẩu cũ không đúng!"
        finally: self.session.close()

    def send_email_otp(self, receiver_email, otp_code):
        msg = MIMEText(f"Mã OTP của bạn là: {otp_code}\nCó hiệu lực trong 5 phút.")
        msg['Subject'] = "🔐 Mã xác thực OTP - EduSoft"
        msg['From'] = SENDER_EMAIL
        msg['To'] = receiver_email
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
            return True
        except Exception as e:
            print(f"Lỗi gửi mail: {e}")
            return False

    def recover_password(self, email):
        try:
            target = self.session.query(Student).filter_by(email=email).first() or \
                     self.session.query(Lecturer).filter_by(email=email).first()
            if not target: return False, "❌ Email chưa đăng ký.", None

            otp = ''.join(random.choices(string.digits, k=6))
            if self.send_email_otp(email, otp): return True, f"✅ Đã gửi OTP đến {email}", otp
            return False, "⚠️ Lỗi gửi mail.", None
        finally: self.session.close()

    def reset_password_with_otp(self, email, new_pass):
        try:
            target = self.session.query(Student).filter_by(email=email).first() or \
                     self.session.query(Lecturer).filter_by(email=email).first()
            if target:
                user = self.session.query(Account).filter_by(userID=target.userID).first()
                if user:
                    user.password = self._hash_password(new_pass)
                    self.session.commit()
                    return True, "✅ Đặt lại mật khẩu thành công!"
            return False, "❌ Lỗi tài khoản."
        finally: self.session.close()