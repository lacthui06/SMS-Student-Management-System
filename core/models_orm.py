from sqlalchemy import Column, String, Integer, Float, Date, Boolean, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from core.database import Base

# ==========================================
# 1. Bảng Account (ĐÃ SỬA TÊN CLASS TỪ User -> Account)
# ==========================================
class Account(Base):
    __tablename__ = 'Account'
    userID = Column(String(12), primary_key=True)
    password = Column(String(100), name='passWord') 
    role = Column(String(50))
    status = Column(Boolean)

# ==========================================
# 2. Bảng Semester
# ==========================================
class Semester(Base):
    __tablename__ = 'Semester'
    semesterID = Column(String(10), primary_key=True, name='semesterId')
    name = Column(String(100))
    startDate = Column(Date)
    endDate = Column(Date)
    registrationOpenDate = Column(Date)
    registrationCloseDate = Column(Date)

# ==========================================
# 3. Bảng Faculty
# ==========================================
class Faculty(Base):
    __tablename__ = 'Faculty'
    facultyID = Column(String(10), primary_key=True)
    facultyName = Column(String(100))
    phone = Column(String(20))

# ==========================================
# 4. Bảng Major
# ==========================================
class Major(Base):
    __tablename__ = 'Major'
    majorID = Column(String(11), primary_key=True)
    facultyID = Column(String(10), ForeignKey('Faculty.facultyID'))
    majorName = Column(String(100))
    requiredCredits = Column(Integer)
    tuitionFeePerCredit = Column(DECIMAL(15,0))
    faculty = relationship("Faculty")

# ==========================================
# 5. Bảng Admin
# ==========================================
class Admin(Base):
    __tablename__ = 'Admin'
    adminID = Column(String(12), primary_key=True)
    # ForeignKey trỏ vào Account.userID
    userID = Column(String(12), ForeignKey('Account.userID')) 
    fullName = Column(String(100))
    position = Column(String(100))
    workEmail = Column(String(100))

# ==========================================
# 6. Bảng Lecturer
# ==========================================
class Lecturer(Base):
    __tablename__ = 'Lecturer'
    lecturerID = Column(String(12), primary_key=True)
    userID = Column(String(12), ForeignKey('Account.userID'))
    fullName = Column(String(100))
    dob = Column(Date)
    address = Column(String(200))
    phone = Column(String(20))
    email = Column(String(100))
    citizenID = Column(String(12))
    degree = Column(String(200))
    gender = Column(Boolean)
    pob = Column(String(200))
    position = Column(String(200))

# ==========================================
# 7. Bảng Student
# ==========================================
class Student(Base):
    __tablename__ = 'Student'
    studentID = Column(String(12), primary_key=True)
    userID = Column(String(12), ForeignKey('Account.userID'))
    majorID = Column(String(11), ForeignKey('Major.majorID'))
    fullName = Column(String(100))
    dob = Column(Date)
    address = Column(String(200))
    phone = Column(String(20))
    email = Column(String(100))
    gender = Column(Boolean)
    pob = Column(String(200))
    citizenID = Column(String(12))
    major = relationship("Major")

# ==========================================
# 8. Bảng Course
# ==========================================
class Course(Base):
    __tablename__ = 'Course'
    courseID = Column(String(11), primary_key=True)
    majorID = Column(String(11), ForeignKey('Major.majorID'))
    courseName = Column(String(100))
    credits = Column(Integer)
    description = Column(String(200))

# ==========================================
# 9. Bảng CourseSection
# ==========================================
class CourseSection(Base):
    __tablename__ = 'CourseSection'
    sectionID = Column(String(11), primary_key=True)
    lecturerID = Column(String(12), ForeignKey('Lecturer.lecturerID'))
    courseID = Column(String(11), ForeignKey('Course.courseID'))
    semesterID = Column(String(10), ForeignKey('Semester.semesterId'))
    sectionName = Column(String(100))
    room = Column(String(50))
    dayOfWeek = Column(String(20))
    startPeriod = Column(Integer)
    endPeriod = Column(Integer)
    maxSlot = Column(Integer)
    currentSlot = Column(Integer)
    status = Column(Integer)

    course = relationship("Course")
    lecturer = relationship("Lecturer")
    semester = relationship("Semester")

# ==========================================
# 10. Bảng GradeReport
# ==========================================
class GradeReport(Base):
    __tablename__ = 'GradeReport'
    studentID = Column(String(12), ForeignKey('Student.studentID'), primary_key=True)
    sectionID = Column(String(11), ForeignKey('CourseSection.sectionID'), primary_key=True)
    midterm = Column(Float, name='componentGrade') 
    final = Column(Float, name='finalScore')
    total = Column(Float, name='totalScore')
    letterGrade = Column(String(100))

    section = relationship("CourseSection")
    student = relationship("Student")

# ==========================================
# 11. Bảng GradeReviewRequest
# ==========================================
class GradeReviewRequest(Base):
    __tablename__ = 'GradeReviewRequest'
    requestID = Column(String(10), primary_key=True)
    studentID = Column(String(12), ForeignKey('Student.studentID'))
    sectionID = Column(String(11), ForeignKey('CourseSection.sectionID'))
    studentComment = Column(String(100))
    lecturerReply = Column(String(100))
    status = Column(Integer)
    createDate = Column(Date)

    student = relationship("Student")
    section = relationship("CourseSection")