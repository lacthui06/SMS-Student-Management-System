# --- 1. BASE CLASS ---
class Account:
    def __init__(self, userID, password, role, email=None, status=True):
        self.userID = userID
        self.password = password
        self.role = role
        self.email = email
        self.status = status  # Trạng thái hoạt động

# --- 2. USER ROLE CLASSES ---
class Admin(Account):
    def __init__(self, userID, password, role, fullName, email, status=True):
        super().__init__(userID, password, role, email, status)
        self.fullName = fullName

class Student(Account):
    def __init__(self, userID, password, role, fullName, dob, pob, citizenID, gender, address, phone, email, majorID, facultyID, status=True):
        super().__init__(userID, password, role, email, status)
        self.fullName = fullName
        self.dob = dob
        self.pob = pob
        self.citizenID = citizenID
        self.gender = gender
        self.address = address
        self.phone = phone
        self.majorID = majorID
        self.facultyID = facultyID

class Lecturer(Account):
    def __init__(self, userID, password, role, fullName, dob, pob, citizenID, gender, address, phone, email, degree, position, status=True):
        super().__init__(userID, password, role, email, status)
        self.fullName = fullName
        self.dob = dob
        self.pob = pob
        self.citizenID = citizenID
        self.gender = gender
        self.address = address
        self.phone = phone
        self.degree = degree
        self.position = position

# --- 3. ACADEMIC CLASSES ---
class Faculty:  # <--- CLASS MỚI (9)
    def __init__(self, facultyID, facultyName):
        self.facultyID = facultyID
        self.facultyName = facultyName

class Major:
    def __init__(self, majorID, majorName, requiredCredits, facultyID):
        self.majorID = majorID
        self.majorName = majorName
        self.requiredCredits = requiredCredits
        self.facultyID = facultyID

class Semester: # <--- CLASS MỚI (10)
    def __init__(self, semesterID, semesterName, startDate, endDate):
        self.semesterID = semesterID
        self.semesterName = semesterName
        self.startDate = startDate
        self.endDate = endDate

class Course:
    def __init__(self, courseID, courseName, credits):
        self.courseID = courseID
        self.courseName = courseName
        self.credits = credits

class Section:
    def __init__(self, sectionID, courseID, lecturerID, semesterID, room, dayOfWeek, startPeriod, endPeriod):
        self.sectionID = sectionID
        self.courseID = courseID
        self.lecturerID = lecturerID
        self.semesterID = semesterID
        self.room = room
        self.dayOfWeek = dayOfWeek
        self.startPeriod = startPeriod
        self.endPeriod = endPeriod

# --- 4. GRADE & REQUEST CLASSES ---
class GradeReport:
    def __init__(self, studentID, sectionID, componentGrade, finalScore):
        self.studentID = studentID
        self.sectionID = sectionID
        self.componentGrade = componentGrade
        self.finalScore = finalScore

class GradeReviewRequest: # <--- CLASS (11)
    def __init__(self, requestID, studentID, sectionID, reason, status, reply, createDate):
        self.requestID = requestID
        self.studentID = studentID
        self.sectionID = sectionID
        self.reason = reason
        self.status = status
        self.reply = reply
        self.createDate = createDate