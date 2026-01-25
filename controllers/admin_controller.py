import pandas as pd
from sqlalchemy import or_, and_
from core.database import Session
from core.models_orm import (
    Account, Student, Lecturer, Admin, 
    Semester, Major, Course, CourseSection, GradeReport
)
from core.utils import get_time_string
from datetime import datetime, date

class AdminController:
    def __init__(self):
        self.session = Session()

    def __del__(self):
        self.session.close()

    # --- HÀM PHỤ TRỢ: XỬ LÝ NGÀY THÁNG THÔNG MINH ---
    def _parse_date_smart(self, val):
        """Chuyển đổi mọi định dạng (Excel serial, Chuỗi, Datetime) về date chuẩn"""
        if val is None or pd.isna(val) or str(val).strip() == '' or str(val).lower() == 'nan':
            return None
        
        # 1. Nếu đã là dạng ngày tháng (datetime/timestamp)
        if hasattr(val, 'date'):
            return val.date()
        
        # 2. Nếu là số (Excel Serial Date: 31118 -> 1985-03-12)
        try:
            # Ép kiểu sang float để xử lý cả trường hợp chuỗi số "31118"
            val_float = float(val)
            # Excel Serial Date thường lớn hơn 10000 (năm 1927 trở đi)
            if val_float > 10000:
                return pd.to_datetime(val_float, unit='D', origin='1899-12-30').date()
        except:
            pass # Không phải số, bỏ qua để thử cách khác

        # 3. Nếu là chuỗi ngày tháng thông thường (dd/mm/yyyy, yyyy-mm-dd...)
        try:
            return pd.to_datetime(val, dayfirst=True, errors='coerce').date()
        except:
            return None

    # =================================================================
    # 1. THỐNG KÊ DASHBOARD
    # =================================================================
    def get_stats(self):
        try:
            return {
                "users": self.session.query(Account).count(),
                "courses": self.session.query(Course).count(),
                "sections": self.session.query(CourseSection).count(),
                "semesters": self.session.query(Semester).count()
            }
        except: return {"users": 0, "courses": 0, "sections": 0, "semesters": 0}

    # =================================================================
    # 2. QUẢN LÝ TÀI KHOẢN (IMPORT)
    # =================================================================
    def preview_import_users(self, f):
        if not f: return None
        try:
            # Đọc file
            df = pd.read_csv(f) if f.name.endswith('.csv') else pd.read_excel(f)
            
            # Chuẩn hóa tên cột để tìm cột ngày sinh
            df.columns = [str(c).strip().lower() for c in df.columns]
            
            # Convert hiển thị ngày tháng ngay tại đây để bạn thấy đúng trên UI
            if 'dob' in df.columns:
                df['dob'] = df['dob'].apply(self._parse_date_smart)
            elif 'ngaysinh' in df.columns:
                df['ngaysinh'] = df['ngaysinh'].apply(self._parse_date_smart)
                
            return df
        except: return None

    def save_import_users(self, df):
        success = 0
        errors = []
        
        try:
            df.columns = [str(c).strip().lower() for c in df.columns]
            
            for idx, row in df.iterrows():
                # --- A. TÌM ID ---
                uid = None
                for col in ['userid','lecturerid','studentid','magv','masv','id']:
                    if col in df.columns and str(row[col]).strip().lower() != 'nan':
                        uid = str(row[col]).strip()
                        break
                
                if not uid:
                    errors.append(f"Dòng {idx+1}: Thiếu ID -> Bỏ qua")
                    continue

                if self.session.query(Account).get(uid):
                    errors.append(f"Dòng {idx+1}: ID '{uid}' đã tồn tại -> Bỏ qua")
                    continue

                try:
                    # --- B. LẤY DỮ LIỆU CƠ BẢN ---
                    full_name = str(row.get('fullname') or row.get('hoten') or "No Name").strip()
                    if full_name == 'nan': full_name = "No Name"
                    
                    email = str(row.get('email') or "").strip()
                    if email == 'nan': email = ""

                    # --- C. XỬ LÝ NGÀY SINH (GỌI HÀM SMART) ---
                    dob_raw = row.get('dob') or row.get('ngaysinh')
                    dob_val = self._parse_date_smart(dob_raw)

                    # --- D. LẤY CÁC CỘT PHỤ (TRÁNH NULL) ---
                    phone = str(row.get('phone') or row.get('sdt') or "").strip()
                    if phone == 'nan': phone = ""
                    if phone.endswith('.0'): phone = phone[:-2]

                    addr = str(row.get('address') or row.get('diachi') or "").strip()
                    if addr == 'nan': addr = ""

                    cid_card = str(row.get('citizenid') or row.get('cccd') or "").strip()
                    if cid_card == 'nan': cid_card = ""
                    if cid_card.endswith('.0'): cid_card = cid_card[:-2]

                    # Giới tính
                    g_raw = str(row.get('gender') or row.get('gioitinh') or "").lower()
                    gender = True if g_raw in ['1', 'true', 'nam', 'male'] else False

                    # Xác định Role
                    role = str(row.get('role') or "").strip()
                    if role == 'nan' or not role:
                        role = 'Lecturer' if uid.upper().startswith(('GV','L')) else 'Student'

                    # --- E. LƯU VÀO DB ---
                    acc = Account(userID=uid, password=uid, role=role, status=True)
                    self.session.add(acc)
                    self.session.flush() 

                    if role == 'Student':
                        mid = str(row.get('majorid') or row.get('nganh') or "").strip()
                        if mid == 'nan': mid = None
                        
                        stu = Student(
                            studentID=uid, userID=uid, fullName=full_name, email=email,
                            dob=dob_val, phone=phone, address=addr, gender=gender,
                            citizenID=cid_card, majorID=mid
                        )
                        self.session.add(stu)

                    elif role == 'Lecturer':
                        deg = str(row.get('degree') or row.get('hocvi') or "").strip()
                        pos = str(row.get('position') or row.get('chucvu') or "").strip()
                        if deg == 'nan': deg = ""
                        if pos == 'nan': pos = ""

                        lec = Lecturer(
                            lecturerID=uid, userID=uid, fullName=full_name, email=email,
                            dob=dob_val, phone=phone, address=addr, gender=gender,
                            citizenID=cid_card, degree=deg, position=pos
                        )
                        self.session.add(lec)
                    
                    success += 1

                except Exception as ex:
                    errors.append(f"Dòng {idx+1} ({uid}): Lỗi Data - {str(ex)}")

            self.session.commit()
            return success, errors

        except Exception as e:
            self.session.rollback()
            return 0, [f"Lỗi File: {str(e)}"]

    # --- USER ACTIONS ---
    def get_users_filtered(self, t):
        q = self.session.query(Account)
        if t: q = q.filter(Account.userID.like(f"%{t}%"))
        return q.all()

    def lock_user(self, u, r):
        try:
            acc = self.session.query(Account).get(u)
            if acc: acc.status = False; self.session.commit(); return True, "Đã khóa"
            return False, "K thấy User"
        except Exception as e: return False, str(e)

    def unlock_user(self, u):
        try:
            acc = self.session.query(Account).get(u)
            if acc: acc.status = True; self.session.commit(); return True, "Đã mở"
            return False, "K thấy User"
        except Exception as e: return False, str(e)

    # =================================================================
    # 3. QUẢN LÝ HỌC KỲ (THÊM & XÓA)
    # =================================================================
    def get_all_semesters(self):
        return self.session.query(Semester).order_by(Semester.startDate.desc()).all()

    def add_semester(self, sid, name, s, e):
        if not sid or len(sid.strip()) < 2: return False, "❌ Mã HK quá ngắn"
        if not name: return False, "❌ Thiếu tên HK"
        if s >= e: return False, "❌ Ngày bắt đầu >= kết thúc"
        try:
            if self.session.query(Semester).get(sid): return False, "❌ Trùng mã HK"
            self.session.add(Semester(semesterID=sid, name=name, startDate=s, endDate=e))
            self.session.commit()
            return True, "✅ Thêm HK thành công"
        except Exception as e: self.session.rollback(); return False, str(e)

    def delete_semester(self, sid):
        try:
            sem = self.session.query(Semester).get(sid)
            if not sem: return False, "❌ Không tìm thấy HK"
            # Chặn xóa nếu có lớp học
            if self.session.query(CourseSection).filter_by(semesterID=sid).first():
                return False, f"❌ HK {sid} đang có lớp học, không thể xóa!"
            self.session.delete(sem); self.session.commit(); return True, "🗑️ Đã xóa HK"
        except: self.session.rollback(); return False, "Lỗi hệ thống"

    # =================================================================
    # 4. MÔN HỌC
    # =================================================================
    def get_all_courses(self): 
        return {c.courseID: c for c in self.session.query(Course).all()}
    def get_all_majors(self): return self.session.query(Major).all()
    def get_all_lecturers(self): return self.session.query(Lecturer).all()

    def add_course(self, cid, mid, name, cre):
        if not cid or not name: return False, "❌ Thiếu thông tin"
        try:
            cid = str(cid).strip().upper()
            if self.session.query(Course).get(cid): return False, f"❌ Mã {cid} đã tồn tại"
            self.session.add(Course(courseID=cid, courseName=name, credits=cre, majorID=mid))
            self.session.commit()
            return True, "✅ Thêm môn thành công"
        except Exception as e: self.session.rollback(); return False, str(e)

    def delete_course(self, cid):
        try:
            c = self.session.query(Course).get(cid)
            if c: self.session.delete(c); self.session.commit(); return True, "🗑️ Đã xóa môn"
            return False, "K thấy môn"
        except: self.session.rollback(); return False, "❌ Môn này đang có dữ liệu, k xóa đc"

    # =================================================================
    # 5. LỚP HỌC PHẦN (CONFLICT CHECK + SMART DELETE)
    # =================================================================
    def get_all_sections(self):
        return [{"Mã lớp": s.sectionID, "Môn": s.courseID, "GV": s.lecturerID, "Phòng": s.room, "Lịch": f"{s.dayOfWeek} ({s.startPeriod}-{s.endPeriod})"} for s in self.session.query(CourseSection).all()]

    def cancel_section(self, sid):
        try:
            s = self.session.query(CourseSection).get(sid)
            if not s: return False, "❌ K thấy lớp"
            
            # Check xem có điểm chưa
            has_score = self.session.query(GradeReport).filter(
                GradeReport.sectionID == sid, 
                or_(GradeReport.midterm != None, GradeReport.final != None)
            ).first()
            
            if has_score: return False, "⚠️ Lớp đã có điểm, KHÔNG thể xóa!"
            
            # Xóa sinh viên trong danh sách đăng ký trước
            self.session.query(GradeReport).filter_by(sectionID=sid).delete()
            # Xóa lớp
            self.session.delete(s)
            self.session.commit()
            return True, "✅ Đã hủy lớp & Xóa DS đăng ký"
        except Exception as e: self.session.rollback(); return False, str(e)

    def create_section_auto_enroll(self, sid, cid, lid, sem, room, day, p1, p2, mx, tm):
        # 1. Chuẩn hóa dữ liệu đầu vào
        sid = str(sid).strip()
        room = str(room).strip()
        day = str(day).strip() # Quan trọng: Xóa khoảng trắng thừa ở "Thứ"
        
        # Validate cơ bản
        if len(sid) < 3: return False, "❌ Mã lớp quá ngắn!"
        if not room: return False, "❌ Thiếu thông tin Phòng!"
        try:
            p1 = int(p1); p2 = int(p2)
        except: return False, "❌ Tiết học phải là số nguyên"
        
        if p1 >= p2: return False, "❌ Tiết Bắt đầu phải nhỏ hơn Tiết Kết thúc!"

        try:
            # 2. Check Mã lớp trùng
            if self.session.query(CourseSection).get(sid): 
                return False, f"❌ Mã lớp '{sid}' đã tồn tại!"

            # 3. CHECK TRÙNG LỊCH (DÙNG LOGIC SQL GIAO NHAU CHUẨN)
            # Công thức giao nhau: (StartA < EndB) AND (EndA > StartB)
            # Tìm các lớp có cùng Học kỳ + cùng Thứ + có giờ giao nhau
            overlapping_sections = self.session.query(CourseSection).filter(
                CourseSection.semesterID == sem,
                CourseSection.dayOfWeek == day,
                CourseSection.startPeriod < p2,  # Bắt đầu lớp cũ < Kết thúc lớp mới
                CourseSection.endPeriod > p1     # Kết thúc lớp cũ > Bắt đầu lớp mới
            ).all()

            # Duyệt qua các lớp bị giao nhau thời gian để check cụ thể
            for sec in overlapping_sections:
                # A. Check Trùng GIẢNG VIÊN (Quan trọng nhất)
                if sec.lecturerID == lid:
                    return False, f"❌ TRÙNG LỊCH GV: {lid} đang dạy lớp {sec.sectionID} ({sec.dayOfWeek} Tiết {sec.startPeriod}-{sec.endPeriod})!"
                
                # B. Check Trùng PHÒNG
                if sec.room == room:
                    return False, f"❌ KẸT PHÒNG: Phòng {room} đang có lớp {sec.sectionID} ({sec.dayOfWeek} Tiết {sec.startPeriod}-{sec.endPeriod})!"

            # 4. Tìm Sinh viên để Auto Enroll
            stus = self.session.query(Student).filter_by(majorID=tm).limit(mx).all()
            if not stus: return False, f"⚠️ Không tìm thấy sinh viên ngành {tm}!"

            # 5. Tạo lớp mới
            new_sec = CourseSection(
                sectionID=sid, courseID=cid, lecturerID=lid, semesterID=sem, 
                room=room, dayOfWeek=day, startPeriod=p1, endPeriod=p2, 
                maxSlot=mx, currentSlot=len(stus), status=1
            )
            self.session.add(new_sec)
            self.session.flush()
            
            # 6. Thêm SV vào lớp (Enroll)
            for s in stus: 
                self.session.add(GradeReport(studentID=s.studentID, sectionID=sid))
            
            self.session.commit()
            return True, f"✅ Mở lớp {sid} thành công! ({len(stus)} SV)"

        except Exception as e:
            self.session.rollback()
            return False, f"Lỗi hệ thống: {str(e)}"

    # =================================================================
    # 6. KHUNG CHƯƠNG TRÌNH
    # =================================================================
    def get_curriculum(self, mid): return self.session.query(Course).filter_by(majorID=mid).all()
    def add_course_to_curriculum(self, c, m, n, cr): return self.add_course(c, m, n, cr)
    
    def update_course(self, cid, n, cr):
        try:
            c = self.session.query(Course).get(cid)
            if c: c.courseName=n; c.credits=cr; self.session.commit(); return True, "✅ Cập nhật OK"
            return False, "K thấy môn"
        except: return False, "Lỗi"
        
    def remove_course_from_curriculum(self, cid): return self.delete_course(cid)