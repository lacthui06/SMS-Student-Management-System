DROP DATABASE IF EXISTS gr2;
CREATE DATABASE gr2 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE gr2;

create table Account (
    userID char(12) primary key,
    passWord varchar(100),
    role varchar(50),
    status boolean
);

create table Semester( -- Đã thêm bảng này theo datamodel
    semesterId char(10) primary key,
    name varchar(100),
    startDate date,
    endDate date,
    registrationOpenDate date,
    registrationCloseDate date
);

create table Lecturer(
    lecturerID char(12) primary key,
    userID char(12),
    fullName varchar(100),
    dob date, -- Đã sửa từ dod thành dob
    address varchar(200),
    phone varchar(20),
    email varchar(100),
    citizenID char(12),
    degree varchar(200),
    gender boolean,
    pob varchar(200),
    position varchar(200),
    foreign key (userID) references Account(userID)
);

create table Faculty(
    facultyID char(10) primary key,
    facultyName varchar(100),
    phone varchar(20)
);

create table Admin(
    adminID char(12) primary key,
    userID char(12),
    fullName varchar(100),
    position varchar(100),
    workEmail varchar(100),
    foreign key (userID) references Account(userID)
);

create table Major(
    majorID char(11) primary key,
    facultyID char(10),
    majorName varchar(100),
    requiredCredits integer,
    tuitionFeePerCredit decimal(15,0), -- Đã sửa dấu chấm thành phẩy
    foreign key (facultyID) references Faculty(facultyID)
);

create table Student(
    studentID char(12) primary key,
    userID char(12),
    majorID char(11),
    fullName varchar(100),
    dob date,
    address varchar(200),
    phone varchar(20),
    email varchar(100),
    gender boolean,
    pob varchar(200),
    citizenID char(12),
    foreign key (userID) references Account(userID),
    foreign key (majorID) references Major(majorID)
);

create table Course(
    courseID char(11) primary key,
    majorID char(11),
    courseName varchar(100),
    credits integer,
    description varchar(200),
    foreign key (majorID) references Major(majorID)
);

create table CourseSection(
    sectionID char(11) primary key,
    lecturerID char(12),
    courseID char(11),
    semesterID char(10),
    sectionName varchar(100),
    room varchar(50),
    dayOfWeek varchar(20), -- Thêm: Thứ (2, 3, 4...)
    startPeriod integer,   -- Thêm: Tiết bắt đầu
    endPeriod integer,     -- Thêm: Tiết kết thúc
    maxSlot integer,
    currentSlot integer,
    status integer,
    foreign key (lecturerID) references Lecturer(lecturerID),
    foreign key (courseID) references Course(courseID),
    foreign key (semesterID) references Semester(semesterID)
);

create table GradeReport(
    studentID char(12),
    sectionID char(11),
    componentGrade decimal(4,2), -- Đã sửa dấu chấm thành phẩy
    finalScore decimal(4,2),     -- Đã sửa dấu chấm thành phẩy
    totalScore decimal(4,2),     -- Đã sửa dấu chấm thành phẩy
    letterGrade varchar(100),
    primary key (studentID, sectionID),
    foreign key (studentID) references Student(studentID),
    foreign key (sectionID) references CourseSection(sectionID)
);

create table GradeReviewRequest(
    requestID char(10) primary key, -- Đã sửa từ 12 thành 10
    studentID char(12),
    sectionID char(11),
    studentComment varchar(100),
    lecturerReply varchar(100),
    status integer,
    createDate date,
    foreign key (studentID) references Student(studentID),
    foreign key (sectionID) references CourseSection(sectionID)
);

INSERT INTO Account VALUES
('AD01','admin123','ADMIN',1);

INSERT INTO Account VALUES
('GV01','123','LECTURER',1),
('GV02','123','LECTURER',1),
('GV03','123','LECTURER',1),
('GV04','123','LECTURER',1),
('GV05','123','LECTURER',1),
('GV06','123','LECTURER',1);

INSERT INTO Account VALUES
('SV001','123','STUDENT',1),('SV002','123','STUDENT',1),
('SV003','123','STUDENT',1),('SV004','123','STUDENT',1),
('SV005','123','STUDENT',1),('SV006','123','STUDENT',1),
('SV007','123','STUDENT',1),('SV008','123','STUDENT',1),
('SV009','123','STUDENT',1),('SV010','123','STUDENT',1),
('SV011','123','STUDENT',1),('SV012','123','STUDENT',1),
('SV013','123','STUDENT',1),('SV014','123','STUDENT',1),
('SV015','123','STUDENT',1),('SV016','123','STUDENT',1),
('SV017','123','STUDENT',1),('SV018','123','STUDENT',1),
('SV019','123','STUDENT',1),('SV020','123','STUDENT',1),
('SV021','123','STUDENT',1),('SV022','123','STUDENT',1),
('SV023','123','STUDENT',1),('SV024','123','STUDENT',1),
('SV025','123','STUDENT',1),
('SV026','123','STUDENT',1),('SV027','123','STUDENT',1),
('SV028','123','STUDENT',1),('SV029','123','STUDENT',1),
('SV030','123','STUDENT',1),('SV031','123','STUDENT',1),
('SV032','123','STUDENT',1),('SV033','123','STUDENT',1),
('SV034','123','STUDENT',1),('SV035','123','STUDENT',1),
('SV036','123','STUDENT',1),('SV037','123','STUDENT',1),
('SV038','123','STUDENT',1),('SV039','123','STUDENT',1),
('SV040','123','STUDENT',1),('SV041','123','STUDENT',1),
('SV042','123','STUDENT',1),('SV043','123','STUDENT',1),
('SV044','123','STUDENT',1),('SV045','123','STUDENT',1),
('SV046','123','STUDENT',1),('SV047','123','STUDENT',1),
('SV048','123','STUDENT',1),('SV049','123','STUDENT',1),
('SV050','123','STUDENT',1),
('SV051','123','STUDENT',1),('SV052','123','STUDENT',1),
('SV053','123','STUDENT',1),('SV054','123','STUDENT',1),
('SV055','123','STUDENT',1),('SV056','123','STUDENT',1),
('SV057','123','STUDENT',1),('SV058','123','STUDENT',1),
('SV059','123','STUDENT',1),('SV060','123','STUDENT',1),
('SV061','123','STUDENT',1),('SV062','123','STUDENT',1),
('SV063','123','STUDENT',1),('SV064','123','STUDENT',1),
('SV065','123','STUDENT',1),('SV066','123','STUDENT',1),
('SV067','123','STUDENT',1),('SV068','123','STUDENT',1),
('SV069','123','STUDENT',1),('SV070','123','STUDENT',1),
('SV071','123','STUDENT',1),('SV072','123','STUDENT',1),
('SV073','123','STUDENT',1),('SV074','123','STUDENT',1),
('SV075','123','STUDENT',1),
('SV076','123','STUDENT',1),('SV077','123','STUDENT',1),
('SV078','123','STUDENT',1),('SV079','123','STUDENT',1),
('SV080','123','STUDENT',1),('SV081','123','STUDENT',1),
('SV082','123','STUDENT',1),('SV083','123','STUDENT',1),
('SV084','123','STUDENT',1),('SV085','123','STUDENT',1),
('SV086','123','STUDENT',1),('SV087','123','STUDENT',1),
('SV088','123','STUDENT',1),('SV089','123','STUDENT',1),
('SV090','123','STUDENT',1),('SV091','123','STUDENT',1),
('SV092','123','STUDENT',1),('SV093','123','STUDENT',1),
('SV094','123','STUDENT',1),('SV095','123','STUDENT',1),
('SV096','123','STUDENT',1),('SV097','123','STUDENT',1),
('SV098','123','STUDENT',1),('SV099','123','STUDENT',1),
('SV100','123','STUDENT',1),
('SV101','123','STUDENT',1),('SV102','123','STUDENT',1),
('SV103','123','STUDENT',1),('SV104','123','STUDENT',1),
('SV105','123','STUDENT',1),('SV106','123','STUDENT',1),
('SV107','123','STUDENT',1),('SV108','123','STUDENT',1),
('SV109','123','STUDENT',1),('SV110','123','STUDENT',1),
('SV111','123','STUDENT',1),('SV112','123','STUDENT',1),
('SV113','123','STUDENT',1),('SV114','123','STUDENT',1),
('SV115','123','STUDENT',1),('SV116','123','STUDENT',1),
('SV117','123','STUDENT',1),('SV118','123','STUDENT',1),
('SV119','123','STUDENT',1),('SV120','123','STUDENT',1),
('SV121','123','STUDENT',1),('SV122','123','STUDENT',1),
('SV123','123','STUDENT',1),('SV124','123','STUDENT',1),
('SV125','123','STUDENT',1);

INSERT INTO Faculty VALUES
('F01','Công nghệ thông tin','0281234567');

INSERT INTO Major VALUES
('M01','F01','Công nghệ thông tin',150,450000);

INSERT INTO Admin VALUES
('AD01','AD01','Nguyễn Thị Thu Trang','Quản trị hệ thống','superstudentmanagementsystem@gmail.com');

INSERT INTO Lecturer VALUES
('GV01','GV01','Nguyễn Văn Hùng','1980-05-12','TP.HCM','0901111111','hung@gr2.edu.vn','123456789001','Tiến sĩ',1,'TP.HCM','Giảng viên chính'),
('GV02','GV02','Trần Thị Lan','1982-08-20','TP.HCM','0902222222','lan@gr2.edu.vn','123456789002','Thạc sĩ',0,'TP.HCM','Giảng viên'),
('GV03','GV03','Lê Minh Tuấn','1979-03-15','TP.HCM','0903333333','tuan@gr2.edu.vn','123456789003','Tiến sĩ',1,'TP.HCM','Trưởng khoa'),
('GV04','GV04','Phạm Quốc Anh','1985-07-10','TP.HCM','0904444444','anh@gr2.edu.vn','123456789004','Thạc sĩ',1,'TP.HCM','Giảng viên'),
('GV05','GV05','Võ Thanh Bình','1983-11-05','TP.HCM','0905555555','binh@gr2.edu.vn','123456789005','Thạc sĩ',1,'TP.HCM','Giảng viên'),
('GV06','GV06','Đặng Thị Hòa','1987-01-25','TP.HCM','0906666666','hoa@gr2.edu.vn','123456789006','Thạc sĩ',0,'TP.HCM','Giảng viên');

INSERT INTO Semester VALUES
('HK1','Học kỳ 1','2024-09-01','2025-01-15','2024-08-01','2024-08-31'),
('HK2','Học kỳ 2','2025-02-01','2025-06-15','2025-01-01','2025-01-31'),
('HK3','Học kỳ hè','2025-07-01','2025-08-31','2025-06-01','2025-06-15');

INSERT INTO Course VALUES
('C01','M01','Cơ sở dữ liệu',3,'Môn học cơ bản về CSDL');

INSERT INTO CourseSection VALUES
('S01','GV01','C01','HK1','Lớp 01','A101', 'Thứ 2', 1, 3, 25, 0, 1),
('S02','GV02','C01','HK1','Lớp 02','A102', 'Thứ 4', 4, 6, 25, 0, 1),
('S03','GV03','C01','HK2','Lớp 03','B201', 'Thứ 6', 7, 9, 25, 0, 1),
('S04','GV04','C01','HK2','Lớp 04','B202', 'Thứ 3', 1, 3, 25, 0, 1),
('S05','GV05','C01','HK3','Lớp 05','C301', 'Thứ 5', 10, 12, 25, 0, 1);

INSERT INTO Student VALUES
('SV001','SV001','M01','Nguyễn Văn An','2004-01-10','TP.HCM','0910000001','sv01@sv.edu.vn',1,'TP.HCM','111111111001'),
('SV002','SV002','M01','Trần Thị Bình','2004-02-12','TP.HCM','0910000002','sv02@sv.edu.vn',0,'TP.HCM','111111111002'),
('SV003','SV003','M01','Lê Minh Châu','2004-03-15','TP.HCM','0910000003','sv03@sv.edu.vn',1,'TP.HCM','111111111003'),
('SV004','SV004','M01','Phạm Quốc Dũng','2004-04-18','TP.HCM','0910000004','sv04@sv.edu.vn',1,'TP.HCM','111111111004'),
('SV005','SV005','M01','Võ Thị Hạnh','2004-05-20','TP.HCM','0910000005','sv05@sv.edu.vn',0,'TP.HCM','111111111005'),
('SV006','SV006','M01','Nguyễn Hoàng Long','2004-06-22','TP.HCM','0910000006','sv06@sv.edu.vn',1,'TP.HCM','111111111006'),
('SV007','SV007','M01','Trần Đức Minh','2004-07-10','TP.HCM','0910000007','sv07@sv.edu.vn',1,'TP.HCM','111111111007'),
('SV008','SV008','M01','Lê Thị Ngọc','2004-08-05','TP.HCM','0910000008','sv08@sv.edu.vn',0,'TP.HCM','111111111008'),
('SV009','SV009','M01','Phan Văn Phúc','2004-09-12','TP.HCM','0910000009','sv09@sv.edu.vn',1,'TP.HCM','111111111009'),
('SV010','SV010','M01','Đặng Thị Quỳnh','2004-10-15','TP.HCM','0910000010','sv10@sv.edu.vn',0,'TP.HCM','111111111010'),
('SV011','SV011','M01','Bùi Anh Tuấn','2004-11-18','TP.HCM','0910000011','sv11@sv.edu.vn',1,'TP.HCM','111111111011'),
('SV012','SV012','M01','Nguyễn Thị Mai','2004-12-20','TP.HCM','0910000012','sv12@sv.edu.vn',0,'TP.HCM','111111111012'),
('SV013','SV013','M01','Trịnh Văn Nam','2004-01-08','TP.HCM','0910000013','sv13@sv.edu.vn',1,'TP.HCM','111111111013'),
('SV014','SV014','M01','Huỳnh Thị Oanh','2004-02-14','TP.HCM','0910000014','sv14@sv.edu.vn',0,'TP.HCM','111111111014'),
('SV015','SV015','M01','Cao Minh Quân','2004-03-19','TP.HCM','0910000015','sv15@sv.edu.vn',1,'TP.HCM','111111111015'),
('SV016','SV016','M01','Phạm Thị Thảo','2004-04-23','TP.HCM','0910000016','sv16@sv.edu.vn',0,'TP.HCM','111111111016'),
('SV017','SV017','M01','Nguyễn Quốc Trung','2004-05-27','TP.HCM','0910000017','sv17@sv.edu.vn',1,'TP.HCM','111111111017'),
('SV018','SV018','M01','Trần Thị Uyên','2004-06-30','TP.HCM','0910000018','sv18@sv.edu.vn',0,'TP.HCM','111111111018'),
('SV019','SV019','M01','Lý Văn Vinh','2004-07-11','TP.HCM','0910000019','sv19@sv.edu.vn',1,'TP.HCM','111111111019'),
('SV020','SV020','M01','Võ Minh Tâm','2004-08-16','TP.HCM','0910000020','sv20@sv.edu.vn',1,'TP.HCM','111111111020'),
('SV021','SV021','M01','Đinh Thị Yến','2004-09-21','TP.HCM','0910000021','sv21@sv.edu.vn',0,'TP.HCM','111111111021'),
('SV022','SV022','M01','Lê Quốc Bảo','2004-10-25','TP.HCM','0910000022','sv22@sv.edu.vn',1,'TP.HCM','111111111022'),
('SV023','SV023','M01','Nguyễn Thanh Hà','2004-11-28','TP.HCM','0910000023','sv23@sv.edu.vn',0,'TP.HCM','111111111023'),
('SV024','SV024','M01','Trần Minh Khoa','2004-12-05','TP.HCM','0910000024','sv24@sv.edu.vn',1,'TP.HCM','111111111024'),
('SV025','SV025','M01','Phạm Thị Lan','2004-01-30','TP.HCM','0910000025','sv25@sv.edu.vn',0,'TP.HCM','111111111025'),
('SV026','SV026','M01','Ngô Văn Cường','2004-02-01','TP.HCM','0910000026','sv26@sv.edu.vn',1,'TP.HCM','111111111026'),
('SV027','SV027','M01','Đỗ Thị Diễm','2004-02-05','TP.HCM','0910000027','sv27@sv.edu.vn',0,'TP.HCM','111111111027'),
('SV028','SV028','M01','Mai Quốc Đạt','2004-02-09','TP.HCM','0910000028','sv28@sv.edu.vn',1,'TP.HCM','111111111028'),
('SV029','SV029','M01','Tạ Thị Hồng','2004-02-13','TP.HCM','0910000029','sv29@sv.edu.vn',0,'TP.HCM','111111111029'),
('SV030','SV030','M01','Phùng Minh Khôi','2004-02-17','TP.HCM','0910000030','sv30@sv.edu.vn',1,'TP.HCM','111111111030'),
('SV031','SV031','M01','Đào Thị Liên','2004-02-21','TP.HCM','0910000031','sv31@sv.edu.vn',0,'TP.HCM','111111111031'),
('SV032','SV032','M01','Vũ Hoàng Nam','2004-02-25','TP.HCM','0910000032','sv32@sv.edu.vn',1,'TP.HCM','111111111032'),
('SV033','SV033','M01','Phan Thị Nga','2004-03-01','TP.HCM','0910000033','sv33@sv.edu.vn',0,'TP.HCM','111111111033'),
('SV034','SV034','M01','Hoàng Quốc Phong','2004-03-05','TP.HCM','0910000034','sv34@sv.edu.vn',1,'TP.HCM','111111111034'),
('SV035','SV035','M01','Lâm Thị Phương','2004-03-09','TP.HCM','0910000035','sv35@sv.edu.vn',0,'TP.HCM','111111111035'),
('SV036','SV036','M01','Đinh Minh Quý','2004-03-13','TP.HCM','0910000036','sv36@sv.edu.vn',1,'TP.HCM','111111111036'),
('SV037','SV037','M01','Nguyễn Thị Sơn','2004-03-17','TP.HCM','0910000037','sv37@sv.edu.vn',0,'TP.HCM','111111111037'),
('SV038','SV038','M01','Trần Quốc Thái','2004-03-21','TP.HCM','0910000038','sv38@sv.edu.vn',1,'TP.HCM','111111111038'),
('SV039','SV039','M01','Lê Thị Trúc','2004-03-25','TP.HCM','0910000039','sv39@sv.edu.vn',0,'TP.HCM','111111111039'),
('SV040','SV040','M01','Phạm Minh Tín','2004-03-29','TP.HCM','0910000040','sv40@sv.edu.vn',1,'TP.HCM','111111111040'),
('SV041','SV041','M01','Huỳnh Thị Tuyết','2004-04-02','TP.HCM','0910000041','sv41@sv.edu.vn',0,'TP.HCM','111111111041'),
('SV042','SV042','M01','Nguyễn Quốc Toàn','2004-04-06','TP.HCM','0910000042','sv42@sv.edu.vn',1,'TP.HCM','111111111042'),
('SV043','SV043','M01','Trần Thị Vân','2004-04-10','TP.HCM','0910000043','sv43@sv.edu.vn',0,'TP.HCM','111111111043'),
('SV044','SV044','M01','Võ Minh Đức','2004-04-14','TP.HCM','0910000044','sv44@sv.edu.vn',1,'TP.HCM','111111111044'),
('SV045','SV045','M01','Đặng Thị Xuân','2004-04-18','TP.HCM','0910000045','sv45@sv.edu.vn',0,'TP.HCM','111111111045'),
('SV046','SV046','M01','Nguyễn Thanh Tùng','2004-04-22','TP.HCM','0910000046','sv46@sv.edu.vn',1,'TP.HCM','111111111046'),
('SV047','SV047','M01','Lê Thị Yến','2004-04-26','TP.HCM','0910000047','sv47@sv.edu.vn',0,'TP.HCM','111111111047'),
('SV048','SV048','M01','Phan Quốc Việt','2004-04-30','TP.HCM','0910000048','sv48@sv.edu.vn',1,'TP.HCM','111111111048'),
('SV049','SV049','M01','Bùi Thị Hương','2004-05-04','TP.HCM','0910000049','sv49@sv.edu.vn',0,'TP.HCM','111111111049'),
('SV050','SV050','M01','Trần Minh Nhật','2004-05-08','TP.HCM','0910000050','sv50@sv.edu.vn',1,'TP.HCM','111111111050'),
('SV051','SV051','M01','Nguyễn Văn Cảnh','2004-05-12','TP.HCM','0910000051','sv51@sv.edu.vn',1,'TP.HCM','111111111051'),
('SV052','SV052','M01','Trần Thị Duyên','2004-05-16','TP.HCM','0910000052','sv52@sv.edu.vn',0,'TP.HCM','111111111052'),
('SV053','SV053','M01','Lê Minh Đạt','2004-05-20','TP.HCM','0910000053','sv53@sv.edu.vn',1,'TP.HCM','111111111053'),
('SV054','SV054','M01','Phạm Thị Giang','2004-05-24','TP.HCM','0910000054','sv54@sv.edu.vn',0,'TP.HCM','111111111054'),
('SV055','SV055','M01','Võ Quốc Hưng','2004-05-28','TP.HCM','0910000055','sv55@sv.edu.vn',1,'TP.HCM','111111111055'),
('SV056','SV056','M01','Nguyễn Thị Khánh','2004-06-01','TP.HCM','0910000056','sv56@sv.edu.vn',0,'TP.HCM','111111111056'),
('SV057','SV057','M01','Trần Minh Lộc','2004-06-05','TP.HCM','0910000057','sv57@sv.edu.vn',1,'TP.HCM','111111111057'),
('SV058','SV058','M01','Lê Thị My','2004-06-09','TP.HCM','0910000058','sv58@sv.edu.vn',0,'TP.HCM','111111111058'),
('SV059','SV059','M01','Phan Quốc Nam','2004-06-13','TP.HCM','0910000059','sv59@sv.edu.vn',1,'TP.HCM','111111111059'),
('SV060','SV060','M01','Đặng Thị Oanh','2004-06-17','TP.HCM','0910000060','sv60@sv.edu.vn',0,'TP.HCM','111111111060'),
('SV061','SV061','M01','Bùi Minh Phát','2004-06-21','TP.HCM','0910000061','sv61@sv.edu.vn',1,'TP.HCM','111111111061'),
('SV062','SV062','M01','Nguyễn Thị Quyên','2004-06-25','TP.HCM','0910000062','sv62@sv.edu.vn',0,'TP.HCM','111111111062'),
('SV063','SV063','M01','Trần Quốc Sang','2004-06-29','TP.HCM','0910000063','sv63@sv.edu.vn',1,'TP.HCM','111111111063'),
('SV064','SV064','M01','Lê Thị Thanh','2004-07-03','TP.HCM','0910000064','sv64@sv.edu.vn',0,'TP.HCM','111111111064'),
('SV065','SV065','M01','Phạm Minh Thắng','2004-07-07','TP.HCM','0910000065','sv65@sv.edu.vn',1,'TP.HCM','111111111065'),
('SV066','SV066','M01','Võ Thị Trang','2004-07-11','TP.HCM','0910000066','sv66@sv.edu.vn',0,'TP.HCM','111111111066'),
('SV067','SV067','M01','Nguyễn Quốc Trí','2004-07-15','TP.HCM','0910000067','sv67@sv.edu.vn',1,'TP.HCM','111111111067'),
('SV068','SV068','M01','Trần Thị Uyển','2004-07-19','TP.HCM','0910000068','sv68@sv.edu.vn',0,'TP.HCM','111111111068'),
('SV069','SV069','M01','Lê Minh Vũ','2004-07-23','TP.HCM','0910000069','sv69@sv.edu.vn',1,'TP.HCM','111111111069'),
('SV070','SV070','M01','Phan Thị Xuân','2004-07-27','TP.HCM','0910000070','sv70@sv.edu.vn',0,'TP.HCM','111111111070'),
('SV071','SV071','M01','Bùi Quốc Việt','2004-07-31','TP.HCM','0910000071','sv71@sv.edu.vn',1,'TP.HCM','111111111071'),
('SV072','SV072','M01','Nguyễn Thị Yến','2004-08-04','TP.HCM','0910000072','sv72@sv.edu.vn',0,'TP.HCM','111111111072'),
('SV073','SV073','M01','Trần Minh Đức','2004-08-08','TP.HCM','0910000073','sv73@sv.edu.vn',1,'TP.HCM','111111111073'),
('SV074','SV074','M01','Lê Thị Hương','2004-08-12','TP.HCM','0910000074','sv74@sv.edu.vn',0,'TP.HCM','111111111074'),
('SV075','SV075','M01','Phạm Quốc Khánh','2004-08-16','TP.HCM','0910000075','sv75@sv.edu.vn',1,'TP.HCM','111111111075'),
('SV076','SV076','M01','Nguyễn Minh An','2004-08-20','TP.HCM','0910000076','sv76@sv.edu.vn',1,'TP.HCM','111111111076'),
('SV077','SV077','M01','Trần Thị Bích','2004-08-24','TP.HCM','0910000077','sv77@sv.edu.vn',0,'TP.HCM','111111111077'),
('SV078','SV078','M01','Lê Quốc Cường','2004-08-28','TP.HCM','0910000078','sv78@sv.edu.vn',1,'TP.HCM','111111111078'),
('SV079','SV079','M01','Phạm Thị Diễm','2004-09-01','TP.HCM','0910000079','sv79@sv.edu.vn',0,'TP.HCM','111111111079'),
('SV080','SV080','M01','Võ Minh Hải','2004-09-05','TP.HCM','0910000080','sv80@sv.edu.vn',1,'TP.HCM','111111111080'),
('SV081','SV081','M01','Nguyễn Thị Hòa','2004-09-09','TP.HCM','0910000081','sv81@sv.edu.vn',0,'TP.HCM','111111111081'),
('SV082','SV082','M01','Trần Quốc Huy','2004-09-13','TP.HCM','0910000082','sv82@sv.edu.vn',1,'TP.HCM','111111111082'),
('SV083','SV083','M01','Lê Thị Lan','2004-09-17','TP.HCM','0910000083','sv83@sv.edu.vn',0,'TP.HCM','111111111083'),
('SV084','SV084','M01','Phan Minh Khoa','2004-09-21','TP.HCM','0910000084','sv84@sv.edu.vn',1,'TP.HCM','111111111084'),
('SV085','SV085','M01','Đặng Thị Ly','2004-09-25','TP.HCM','0910000085','sv85@sv.edu.vn',0,'TP.HCM','111111111085'),
('SV086','SV086','M01','Bùi Quốc Minh','2004-09-29','TP.HCM','0910000086','sv86@sv.edu.vn',1,'TP.HCM','111111111086'),
('SV087','SV087','M01','Nguyễn Thị Nga','2004-10-03','TP.HCM','0910000087','sv87@sv.edu.vn',0,'TP.HCM','111111111087'),
('SV088','SV088','M01','Trần Minh Phúc','2004-10-07','TP.HCM','0910000088','sv88@sv.edu.vn',1,'TP.HCM','111111111088'),
('SV089','SV089','M01','Lê Thị Oanh','2004-10-11','TP.HCM','0910000089','sv89@sv.edu.vn',0,'TP.HCM','111111111089'),
('SV090','SV090','M01','Phạm Quốc Toàn','2004-10-15','TP.HCM','0910000090','sv90@sv.edu.vn',1,'TP.HCM','111111111090'),
('SV091','SV091','M01','Võ Thị Phượng','2004-10-19','TP.HCM','0910000091','sv91@sv.edu.vn',0,'TP.HCM','111111111091'),
('SV092','SV092','M01','Nguyễn Minh Quân','2004-10-23','TP.HCM','0910000092','sv92@sv.edu.vn',1,'TP.HCM','111111111092'),
('SV093','SV093','M01','Trần Thị Thu','2004-10-27','TP.HCM','0910000093','sv93@sv.edu.vn',0,'TP.HCM','111111111093'),
('SV094','SV094','M01','Lê Quốc Trung','2004-10-31','TP.HCM','0910000094','sv94@sv.edu.vn',1,'TP.HCM','111111111094'),
('SV095','SV095','M01','Phan Thị Tuyết','2004-11-04','TP.HCM','0910000095','sv95@sv.edu.vn',0,'TP.HCM','111111111095'),
('SV096','SV096','M01','Bùi Minh Tân','2004-11-08','TP.HCM','0910000096','sv96@sv.edu.vn',1,'TP.HCM','111111111096'),
('SV097','SV097','M01','Nguyễn Thị Vân','2004-11-12','TP.HCM','0910000097','sv97@sv.edu.vn',0,'TP.HCM','111111111097'),
('SV098','SV098','M01','Trần Quốc Long','2004-11-16','TP.HCM','0910000098','sv98@sv.edu.vn',1,'TP.HCM','111111111098'),
('SV099','SV099','M01','Lê Thị Phương','2004-11-20','TP.HCM','0910000099','sv99@sv.edu.vn',0,'TP.HCM','111111111099'),
('SV100','SV100','M01','Phạm Minh Đức','2004-11-24','TP.HCM','0910000100','sv100@sv.edu.vn',1,'TP.HCM','111111111100'),
('SV101','SV101','M01','Nguyễn Quốc An','2004-11-28','TP.HCM','0910000101','sv101@sv.edu.vn',1,'TP.HCM','111111111101'),
('SV102','SV102','M01','Trần Thị Ánh','2004-12-02','TP.HCM','0910000102','sv102@sv.edu.vn',0,'TP.HCM','111111111102'),
('SV103','SV103','M01','Lê Minh Bảo','2004-12-06','TP.HCM','0910000103','sv103@sv.edu.vn',1,'TP.HCM','111111111103'),
('SV104','SV104','M01','Phạm Thị Cẩm','2004-12-10','TP.HCM','0910000104','sv104@sv.edu.vn',0,'TP.HCM','111111111104'),
('SV105','SV105','M01','Võ Quốc Duy','2004-12-14','TP.HCM','0910000105','sv105@sv.edu.vn',1,'TP.HCM','111111111105'),
('SV106','SV106','M01','Nguyễn Thị Diệu','2004-12-18','TP.HCM','0910000106','sv106@sv.edu.vn',0,'TP.HCM','111111111106'),
('SV107','SV107','M01','Trần Minh Hiếu','2004-12-22','TP.HCM','0910000107','sv107@sv.edu.vn',1,'TP.HCM','111111111107'),
('SV108','SV108','M01','Lê Thị Hân','2004-12-26','TP.HCM','0910000108','sv108@sv.edu.vn',0,'TP.HCM','111111111108'),
('SV109','SV109','M01','Phan Quốc Hậu','2004-12-30','TP.HCM','0910000109','sv109@sv.edu.vn',1,'TP.HCM','111111111109'),
('SV110','SV110','M01','Đặng Thị Hoa','2005-01-03','TP.HCM','0910000110','sv110@sv.edu.vn',0,'TP.HCM','111111111110'),
('SV111','SV111','M01','Bùi Minh Khang','2005-01-07','TP.HCM','0910000111','sv111@sv.edu.vn',1,'TP.HCM','111111111111'),
('SV112','SV112','M01','Nguyễn Thị Linh','2005-01-11','TP.HCM','0910000112','sv112@sv.edu.vn',0,'TP.HCM','111111111112'),
('SV113','SV113','M01','Trần Quốc Lâm','2005-01-15','TP.HCM','0910000113','sv113@sv.edu.vn',1,'TP.HCM','111111111113'),
('SV114','SV114','M01','Lê Thị Loan','2005-01-19','TP.HCM','0910000114','sv114@sv.edu.vn',0,'TP.HCM','111111111114'),
('SV115','SV115','M01','Phạm Minh Lợi','2005-01-23','TP.HCM','0910000115','sv115@sv.edu.vn',1,'TP.HCM','111111111115'),
('SV116','SV116','M01','Võ Thị Mai','2005-01-27','TP.HCM','0910000116','sv116@sv.edu.vn',0,'TP.HCM','111111111116'),
('SV117','SV117','M01','Nguyễn Quốc Minh','2005-01-31','TP.HCM','0910000117','sv117@sv.edu.vn',1,'TP.HCM','111111111117'),
('SV118','SV118','M01','Trần Thị Ngân','2005-02-04','TP.HCM','0910000118','sv118@sv.edu.vn',0,'TP.HCM','111111111118'),
('SV119','SV119','M01','Lê Minh Phong','2005-02-08','TP.HCM','0910000119','sv119@sv.edu.vn',1,'TP.HCM','111111111119'),
('SV120','SV120','M01','Phạm Thị Quyên','2005-02-12','TP.HCM','0910000120','sv120@sv.edu.vn',0,'TP.HCM','111111111120'),
('SV121','SV121','M01','Võ Quốc Thịnh','2005-02-16','TP.HCM','0910000121','sv121@sv.edu.vn',1,'TP.HCM','111111111121'),
('SV122','SV122','M01','Nguyễn Thị Thúy','2005-02-20','TP.HCM','0910000122','sv122@sv.edu.vn',0,'TP.HCM','111111111122'),
('SV123','SV123','M01','Trần Minh Tài','2005-02-24','TP.HCM','0910000123','sv123@sv.edu.vn',1,'TP.HCM','111111111123'),
('SV124','SV124','M01','Lê Thị Vinh','2005-02-28','TP.HCM','0910000124','sv124@sv.edu.vn',0,'TP.HCM','111111111124'),
('SV125','SV125','M01','Phạm Quốc Vinh','2005-03-04','TP.HCM','0910000125','sv125@sv.edu.vn',1,'TP.HCM','111111111125');

INSERT INTO GradeReport (studentID, sectionID) VALUES
('SV001','S01'),('SV002','S01'),('SV003','S01'),('SV004','S01'),('SV005','S01'),
('SV006','S01'),('SV007','S01'),('SV008','S01'),('SV009','S01'),('SV010','S01'),
('SV011','S01'),('SV012','S01'),('SV013','S01'),('SV014','S01'),('SV015','S01'),
('SV016','S01'),('SV017','S01'),('SV018','S01'),('SV019','S01'),('SV020','S01'),
('SV021','S01'),('SV022','S01'),('SV023','S01'),('SV024','S01'),('SV025','S01');

UPDATE GradeReport
SET componentGrade=8, finalScore=7, totalScore=7.5, letterGrade='B+'
WHERE sectionID='S01' AND studentID IN
('SV001','SV002','SV003','SV007','SV008','SV009','SV010');
 
 UPDATE GradeReport
SET componentGrade=7
WHERE sectionID='S01' AND studentID IN
('SV004','SV005','SV006',
 'SV011','SV012','SV013','SV014','SV015',
 'SV016','SV017','SV018','SV019','SV020');

INSERT INTO GradeReport (studentID, sectionID) VALUES
('SV026','S02'),('SV027','S02'),('SV028','S02'),('SV029','S02'),('SV030','S02'),
('SV031','S02'),('SV032','S02'),('SV033','S02'),('SV034','S02'),('SV035','S02'),
('SV036','S02'),('SV037','S02'),('SV038','S02'),('SV039','S02'),('SV040','S02'),
('SV041','S02'),('SV042','S02'),('SV043','S02'),('SV044','S02'),('SV045','S02'),
('SV046','S02'),('SV047','S02'),('SV048','S02'),('SV049','S02'),('SV050','S02');

UPDATE GradeReport
SET componentGrade=9, finalScore=8, totalScore=8.5, letterGrade='A'
WHERE sectionID='S02' AND studentID IN
('SV026','SV027','SV028','SV029','SV030',
 'SV031','SV032','SV033','SV034','SV035','SV037','SV038');

UPDATE GradeReport
SET componentGrade=6.5
WHERE sectionID='S02' AND studentID IN
('SV036','SV039','SV040',
 'SV041','SV042','SV043','SV044','SV045');

INSERT INTO GradeReport (studentID, sectionID) VALUES
('SV051','S03'),('SV052','S03'),('SV053','S03'),('SV054','S03'),('SV055','S03'),
('SV056','S03'),('SV057','S03'),('SV058','S03'),('SV059','S03'),('SV060','S03'),
('SV061','S03'),('SV062','S03'),('SV063','S03'),('SV064','S03'),('SV065','S03'),
('SV066','S03'),('SV067','S03'),('SV068','S03'),('SV069','S03'),('SV070','S03'),
('SV071','S03'),('SV072','S03'),('SV073','S03'),('SV074','S03'),('SV075','S03');

UPDATE GradeReport
SET componentGrade=7.5, finalScore=7, totalScore=7.25, letterGrade='B'
WHERE sectionID='S03' AND studentID IN
('SV051','SV052','SV053','SV054','SV055',
 'SV056','SV057','SV058','SV059','SV060','SV062','SV067','SV069');

UPDATE GradeReport
SET componentGrade=8
WHERE sectionID='S03' AND studentID IN
('SV061','SV063','SV064','SV065',
 'SV066','SV068','SV070',"SV075");

INSERT INTO GradeReport (studentID, sectionID) VALUES
('SV076','S04'),('SV077','S04'),('SV078','S04'),('SV079','S04'),('SV080','S04'),
('SV081','S04'),('SV082','S04'),('SV083','S04'),('SV084','S04'),('SV085','S04'),
('SV086','S04'),('SV087','S04'),('SV088','S04'),('SV089','S04'),('SV090','S04'),
('SV091','S04'),('SV092','S04'),('SV093','S04'),('SV094','S04'),('SV095','S04'),
('SV096','S04'),('SV097','S04'),('SV098','S04'),('SV099','S04'),('SV100','S04');

UPDATE GradeReport
SET componentGrade=5, finalScore=6, totalScore=5.5, letterGrade='C'
WHERE sectionID='S04' AND studentID IN
('SV076','SV077','SV078','SV079','SV080',
 'SV081','SV082','SV083','SV084','SV085','SV090','SV094');

UPDATE GradeReport
SET componentGrade=6
WHERE sectionID='S04' AND studentID IN
('SV086','SV087','SV088','SV089',
 'SV091','SV092','SV093','SV095',"SV098");

INSERT INTO GradeReport (studentID, sectionID) VALUES
('SV101','S05'),('SV102','S05'),('SV103','S05'),('SV104','S05'),('SV105','S05'),
('SV106','S05'),('SV107','S05'),('SV108','S05'),('SV109','S05'),('SV110','S05'),
('SV111','S05'),('SV112','S05'),('SV113','S05'),('SV114','S05'),('SV115','S05'),
('SV116','S05'),('SV117','S05'),('SV118','S05'),('SV119','S05'),('SV120','S05'),
('SV121','S05'),('SV122','S05'),('SV123','S05'),('SV124','S05'),('SV125','S05');

UPDATE GradeReport
SET componentGrade=9, finalScore=9, totalScore=9, letterGrade='A+'
WHERE sectionID='S05' AND studentID IN
('SV101','SV103','SV104','SV105',
 'SV106','SV107','SV108','SV110',"SV123");

UPDATE GradeReport
SET componentGrade=7
WHERE sectionID='S05' AND studentID IN
('SV102','SV109','SV111','SV112','SV113','SV114','SV115',
 'SV116','SV117','SV118','SV119','SV120');

USE gr2;

-- BƯỚC 1: Tắt kiểm tra khóa ngoại để dọn dẹp dữ liệu cũ (nếu cần)
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE Course;
TRUNCATE TABLE Major; -- Xóa cả ngành cũ làm lại cho sạch
SET FOREIGN_KEY_CHECKS = 1;

-- BƯỚC 2: Tạo danh sách Ngành trước (BẮT BUỘC)
INSERT INTO Major (majorID, majorName) VALUES 
('SE', 'Kỹ thuật phần mềm'),
('AI', 'Trí tuệ nhân tạo'),
('IS', 'An toàn thông tin'),
('IT', 'Công nghệ thông tin'),
('CS', 'Khoa học máy tính');

-- Ngành SE (Software Engineering) - Tổng ~120 tín chỉ
INSERT INTO Course (courseID, majorID, courseName, credits) VALUES 
('SE01', 'SE', 'Nhập môn kỹ thuật phần mềm', 3), ('SE02', 'SE', 'Cấu trúc dữ liệu và giải thuật', 4),
('SE03', 'SE', 'Cơ sở dữ liệu', 3), ('SE04', 'SE', 'Lập trình hướng đối tượng', 4),
('SE05', 'SE', 'Phân tích thiết kế hệ thống', 3), ('SE06', 'SE', 'Kiểm thử phần mềm', 3),
('SE07', 'SE', 'Quản lý dự án phần mềm', 3), ('SE08', 'SE', 'Lập trình Web', 4),
('SE09', 'SE', 'Lập trình di động', 4), ('SE10', 'SE', 'Đồ án chuyên ngành', 10);
-- (Bạn lặp lại tương tự cho đến khi đủ ~35 môn mỗi ngành để đạt 120 tín)

-- Ngành AI (Artificial Intelligence)
INSERT INTO Course (courseID, majorID, courseName, credits) VALUES 
('AI01', 'AI', 'Toán rời rạc', 3), ('AI02', 'AI', 'Xác suất thống kê', 3),
('AI03', 'AI', 'Học máy cơ bản', 4), ('AI04', 'AI', 'Xử lý ngôn ngữ tự nhiên', 4),
('AI05', 'AI', 'Thị giác máy tính', 4), ('AI06', 'AI', 'Mạng nơ-ron sâu', 4);

USE gr2;

-- =================================================================
-- 1. THÊM NGÀNH (Dùng IGNORE để nếu có 'SE' rồi thì tự bỏ qua)
-- =================================================================
INSERT IGNORE INTO Major (majorID, facultyID, majorName, requiredCredits, tuitionFeePerCredit) VALUES 
('SE', 'F01', 'Kỹ thuật phần mềm', 120, 450000),
('AI', 'F01', 'Trí tuệ nhân tạo', 120, 450000),
('IS', 'F01', 'An toàn thông tin', 120, 450000),
('IT', 'F01', 'Công nghệ thông tin', 120, 450000),
('CS', 'F01', 'Khoa học máy tính', 120, 450000);

-- =================================================================
-- 2. THÊM LỚP HỌC PHẦN (Kết nối Lịch dạy cho GV)
-- =================================================================
-- Lớp SE01 - Nhập môn KTPM (Thứ 2)
INSERT IGNORE INTO CourseSection (sectionID, lecturerID, courseID, semesterID, sectionName, room, dayOfWeek, startPeriod, endPeriod, maxSlot, currentSlot, status) VALUES 
('Lop_Test_01', 'GV01', 'SE01', 'HK1', 'KTPM_01', 'P301', 'Thứ 2', 1, 3, 30, 2, 1);

-- Lớp SE02 - Cấu trúc dữ liệu (Thứ 4)
INSERT IGNORE INTO CourseSection (sectionID, lecturerID, courseID, semesterID, sectionName, room, dayOfWeek, startPeriod, endPeriod, maxSlot, currentSlot, status) VALUES 
('Lop_Test_02', 'GV01', 'SE02', 'HK1', 'CTDL_01', 'P302', 'Thứ 4', 7, 9, 30, 5, 1);

-- =================================================================
-- 3. XẾP SINH VIÊN VÀO LỚP (Kết nối Lịch học & Bảng điểm cho SV)
-- =================================================================
-- Đảm bảo SV001 có trong DB (Nếu chưa có thì thêm, có rồi thì thôi)
INSERT IGNORE INTO Student (studentID, userID, majorID, fullName) VALUES ('SV001', 'SV001', 'SE', 'Nguyễn Văn Test');

-- Xếp SV001 vào học 2 lớp trên
INSERT IGNORE INTO GradeReport (studentID, sectionID, componentGrade, finalScore, totalScore, letterGrade) VALUES 
('SV001', 'Lop_Test_01', NULL, NULL, NULL, NULL), -- Mới học
('SV001', 'Lop_Test_02', 7.5, 8.0, 7.9, 'B');     -- Đã có điểm


USE gr2;

-- 1. Đảm bảo có Ngành CS (Khoa học máy tính) để hiện Khung chương trình
INSERT IGNORE INTO Major (majorID, facultyID, majorName, requiredCredits, tuitionFeePerCredit) VALUES 
('CS', 'F01', 'Khoa học máy tính', 120, 450000);

-- 2. Thêm vài môn cho ngành CS
INSERT IGNORE INTO Course (courseID, majorID, courseName, credits) VALUES 
('CS01', 'CS', 'Nhập môn CS', 3),
('CS02', 'CS', 'Trí tuệ nhân tạo cơ bản', 3);

-- 3. TẠO LỚP HỌC (Để GV thấy chỗ nhập điểm)
-- Giả sử GV01 dạy môn SE01
INSERT IGNORE INTO CourseSection (sectionID, lecturerID, courseID, semesterID, sectionName, room, dayOfWeek, startPeriod, endPeriod, maxSlot, currentSlot, status) VALUES 
('Lop_SE01', 'GV01', 'SE01', 'HK1', 'Lớp KTPM 01', 'A101', 'Thứ 2', 1, 3, 30, 0, 1);

-- 4. XẾP SINH VIÊN VÀO LỚP (Để SV thấy Lịch học & Bảng điểm)
-- Giả sử SV001 học lớp SE01 ở trên
INSERT IGNORE INTO GradeReport (studentID, sectionID, componentGrade, finalScore, totalScore, letterGrade) VALUES 
('SV001', 'Lop_SE01', 0, 0, 0, 'F');


USE gr2;

-- Thêm 10 sinh viên mẫu thuộc ngành AI (Trí tuệ nhân tạo)
INSERT IGNORE INTO Student (studentID, userID, majorID, fullName, email) VALUES 
('SV_AI_01', 'SV_AI_01', 'AI', 'An Trí Tuệ', 'ai01@fpt.edu.vn'),
('SV_AI_02', 'SV_AI_02', 'AI', 'Bình Machine', 'ai02@fpt.edu.vn'),
('SV_AI_03', 'SV_AI_03', 'AI', 'Cường Neural', 'ai03@fpt.edu.vn'),
('SV_AI_04', 'SV_AI_04', 'AI', 'Dũng Deep', 'ai04@fpt.edu.vn'),
('SV_AI_05', 'SV_AI_05', 'AI', 'Em Python', 'ai05@fpt.edu.vn'),
('SV_AI_06', 'SV_AI_06', 'AI', 'Giang Data', 'ai06@fpt.edu.vn'),
('SV_AI_07', 'SV_AI_07', 'AI', 'Hương Vision', 'ai07@fpt.edu.vn'),
('SV_AI_08', 'SV_AI_08', 'AI', 'Khánh Robot', 'ai08@fpt.edu.vn'),
('SV_AI_09', 'SV_AI_09', 'AI', 'Lan Logic', 'ai09@fpt.edu.vn'),
('SV_AI_10', 'SV_AI_10', 'AI', 'Minh Model', 'ai10@fpt.edu.vn');

-- Tạo tài khoản đăng nhập cho họ luôn (Pass: 123)
INSERT IGNORE INTO Account (userID, passWord, role, status) VALUES 
('SV_AI_01', '123', 'STUDENT', 1), ('SV_AI_02', '123', 'STUDENT', 1),
('SV_AI_03', '123', 'STUDENT', 1), ('SV_AI_04', '123', 'STUDENT', 1),
('SV_AI_05', '123', 'STUDENT', 1), ('SV_AI_06', '123', 'STUDENT', 1),
('SV_AI_07', '123', 'STUDENT', 1), ('SV_AI_08', '123', 'STUDENT', 1),
('SV_AI_09', '123', 'STUDENT', 1), ('SV_AI_10', '123', 'STUDENT', 1);

INSERT IGNORE INTO Major (majorID, facultyID, majorName, requiredCredits, tuitionFeePerCredit) 
VALUES ('AI', 'F01', 'Trí tuệ nhân tạo', 120, 450000);

-- 2. XÓA các sinh viên AI cũ (để tránh bị lỗi trùng ID mà không cập nhật được)
DELETE FROM GradeReport WHERE studentID LIKE 'SV_AI_%'; -- Xóa điểm/lớp cũ của họ trước
DELETE FROM Student WHERE studentID LIKE 'SV_AI_%';     -- Xóa sinh viên
DELETE FROM Account WHERE userID LIKE 'SV_AI_%';        -- Xóa tài khoản

-- 3. CHÈN LẠI MỚI (Lần này chắc chắn sẽ vào đúng ngành AI)
INSERT INTO Account (userID, passWord, role, status) VALUES 
('SV_AI_01', '123', 'STUDENT', 1), ('SV_AI_02', '123', 'STUDENT', 1),
('SV_AI_03', '123', 'STUDENT', 1), ('SV_AI_04', '123', 'STUDENT', 1),
('SV_AI_05', '123', 'STUDENT', 1), ('SV_AI_06', '123', 'STUDENT', 1),
('SV_AI_07', '123', 'STUDENT', 1), ('SV_AI_08', '123', 'STUDENT', 1),
('SV_AI_09', '123', 'STUDENT', 1), ('SV_AI_10', '123', 'STUDENT', 1);

INSERT INTO Student (studentID, userID, majorID, fullName, email) VALUES 
('SV_AI_01', 'SV_AI_01', 'AI', 'An Trí Tuệ', 'ai01@fpt.edu.vn'),
('SV_AI_02', 'SV_AI_02', 'AI', 'Bình Machine', 'ai02@fpt.edu.vn'),
('SV_AI_03', 'SV_AI_03', 'AI', 'Cường Neural', 'ai03@fpt.edu.vn'),
('SV_AI_04', 'SV_AI_04', 'AI', 'Dũng Deep', 'ai04@fpt.edu.vn'),
('SV_AI_05', 'SV_AI_05', 'AI', 'Em Python', 'ai05@fpt.edu.vn'),
('SV_AI_06', 'SV_AI_06', 'AI', 'Giang Data', 'ai06@fpt.edu.vn'),
('SV_AI_07', 'SV_AI_07', 'AI', 'Hương Vision', 'ai07@fpt.edu.vn'),
('SV_AI_08', 'SV_AI_08', 'AI', 'Khánh Robot', 'ai08@fpt.edu.vn'),
('SV_AI_09', 'SV_AI_09', 'AI', 'Lan Logic', 'ai09@fpt.edu.vn'),
('SV_AI_10', 'SV_AI_10', 'AI', 'Minh Model', 'ai10@fpt.edu.vn');
SELECT * FROM Student WHERE majorID = 'AI';


-- Tắt kiểm tra khóa ngoại để xóa cho mượt
SET FOREIGN_KEY_CHECKS = 0;

-- 1. Xóa sạch lịch sử yêu cầu phúc khảo
TRUNCATE TABLE GradeReviewRequest;

-- 2. (Tùy chọn) Reset lại điểm của sinh viên về trạng thái ban đầu để test lại từ đầu
-- Ví dụ: Reset điểm của SV_AI_01 trong lớp Lop_Test_AI về 5.0
UPDATE GradeReport 
SET componentGrade = 5.0, finalScore = 5.0, totalScore = 5.0, letterGrade = 'D'
WHERE studentID = 'SV_AI_01' AND sectionID = 'Lop_Test_AI';

SET FOREIGN_KEY_CHECKS = 1;

DELETE FROM GradeReviewRequest 
WHERE studentID = 'SV001';


UPDATE Major 
SET requiredCredits = 120 
WHERE majorID = 'M01';