from sqlalchemy import Column, Integer, Float, String, Boolean, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship, backref
from testapp import app, db
from datetime import datetime
from flask_login import UserMixin
from enum import Enum as MyEnum
import hashlib

# DemoUser --------------------------------------------------------------------------------------------------------------------------------------
class UserRole(MyEnum):
    ADMIN = 1
    STAFF = 2
    TEACHER = 3


class DiemType(MyEnum):
    DIEM_15PHUT = "Điểm 15 phút"
    DIEM_45PHUT = "Điểm 1 tiết"
    DIEM_CUOIKY = "Điểm cuối kỳ"

class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ho = Column(String(50), nullable=False)
    ten = Column(String(50), nullable=False)
    username = Column(String(50), nullable=False)
    password = Column(String(255), nullable=False)
    active = Column(Boolean, default=True)
    user_role = Column(Enum(UserRole))

    def __str__(self):
        return f'{self.ho} {self.ten}'


class Teacher(User):
    id = Column(Integer, ForeignKey(User.id, ondelete='CASCADE'), primary_key=True)
    subject_id = Column(Integer, ForeignKey('subject.id'), nullable=False)

    def __str__(self):
        return f'{self.ho} {self.ten}'

class Subject(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    teachers = relationship('Teacher', backref='subject', lazy=True)
    marks = relationship('Mark', backref='subject', lazy=True)

    def __str__(self):
        return self.name


class Mark(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.Enum(DiemType), nullable=False)
    value = Column(Float, nullable=False)
    subject_id = Column(Integer, ForeignKey('subject.id'), nullable=False)
    semester_id = Column(Integer, ForeignKey('semester.id'), nullable=False)
    student_id = Column(Integer, ForeignKey('student.id'), nullable=False)


class SchoolYear(db.Model):
    __tablename__ = 'schoolyear'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), nullable=False)  # Tên năm học, ví dụ: "2023-2024"
    semesters = relationship('Semester', backref='schoolyear', lazy=True)

    def __str__(self):
        return self.name

class Semester(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    semester_type = Column(Enum('Học kỳ 1', 'Học kỳ 2'), nullable=False)  # Loại học kỳ
    school_year_id = Column(Integer, ForeignKey('schoolyear.id'), nullable=False)  # Liên kết với Năm học
    marks = relationship('Mark', backref='semester', lazy=True)
    #
    # def __str__(self):
    #     return f'{self.name} - {self.school_year.name}'



class Student(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ho = Column(String(50), nullable=False)
    ten = Column(String(50), nullable=False)
    sex = Column(Enum('Nam', 'Nữ'), nullable=False)
    DoB = Column(DateTime, nullable=False)
    address = Column(String(100), nullable=False)
    sdt = Column(String(20), nullable=False)
    email = Column(String(50), nullable=False)
    marks = relationship('Mark', backref='student', lazy=True)

    def __str__(self):
        return f'{self.ho} {self.ten}'

class Khoi(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    lops = relationship('Lop', backref='khoi', lazy=True)

    def __str__(self):
        return self.name

class Lop(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    si_so = Column(Integer, default=0)
    khoi_id = Column(Integer, ForeignKey(Khoi.id), nullable=False)
    students = relationship('Student', secondary='lop_student', lazy='subquery',
                            backref=backref('lop', lazy=True))

    def __str__(self):
        return self.name


lop_student = db.Table('lop_student',
                       Column('lop_id', Integer,ForeignKey('lop.id'), primary_key=True),
                       Column('student_id', Integer,ForeignKey('student.id'), primary_key=True))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        u1 = User(ho='Lê Anh', ten='Hào', username="admin", password=str(hashlib.md5("123".encode('utf-8')).hexdigest()), user_role=UserRole.ADMIN)


        db.session.add_all([u1])
        db.session.commit()

        grade1 = Khoi(name='Khối 10')
        grade2 = Khoi(name='Khối 11')
        grade3 = Khoi(name='Khối 12')
        db.session.add_all([grade1, grade2, grade3])
        db.session.commit()

        c1 = Lop(name='10A1', khoi_id=1)
        c2 = Lop(name='10A2', khoi_id=1)
        c3 = Lop(name='10A3', khoi_id=1)
        c4 = Lop(name='10A4', khoi_id=1)
        c5 = Lop(name='10A5', khoi_id=1)
        c6 = Lop(name='11A1', khoi_id=2)
        c7 = Lop(name='11A2', khoi_id=2)
        c8 = Lop(name='11A3', khoi_id=2)
        c9 = Lop(name='11A4', khoi_id=2)
        c10 = Lop(name='11A5', khoi_id=2)
        c11 = Lop(name='12A1', khoi_id=3)
        c12 = Lop(name='12A2', khoi_id=3)
        c13 = Lop(name='12A3', khoi_id=3)
        c14 = Lop(name='12A4', khoi_id=3)
        c15 = Lop(name='12A5', khoi_id=3)
        db.session.add_all([c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15])
        db.session.commit()

        s1 = Subject(name="Ngữ văn")
        s2 = Subject(name="Toán")
        s3 = Subject(name="Ngoại ngữ")
        s4 = Subject(name="Vật lý")
        s5 = Subject(name="Hóa học")
        s6 = Subject(name="Sinh học")
        s7 = Subject(name="Lịch sử")
        s8 = Subject(name="Địa lý")
        s9 = Subject(name="Giáo dục công dân")
        s10 = Subject(name="Tin học")
        s11 = Subject(name="Giáo dục quốc phòng và an ninh")
        s12 = Subject(name="Công nghệ")
        db.session.add_all([s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12])
        db.session.commit()

        hs1 = Student(ho='Nguyễn Văn', ten='B', sex='Nữ', DoB=datetime(2007, 5, 15), address='Hà Nội', sdt='0123456789',
                      email='nguyenvanb@gmail.com')
        hs2 = Student(ho='Nguyễn Văn', ten='C', sex='Nam', DoB=datetime(2006, 3, 10), address='Hà Nội',
                      sdt='0123456790', email='nguyenvanc@gmail.com')
        hs3 = Student(ho='Trần Thị', ten='A', sex='Nữ', DoB=datetime(2008, 7, 25), address='TP HCM', sdt='0123456791',
                      email='tranthia@gmail.com')
        hs4 = Student(ho='Trần Thị', ten='B', sex='Nam', DoB=datetime(2005, 9, 5), address='Đà Nẵng', sdt='0123456792',
                      email='tranthib@gmail.com')
        hs5 = Student(ho='Lê Minh', ten='A', sex='Nữ', DoB=datetime(2007, 11, 18), address='Cần Thơ', sdt='0123456793',
                      email='leminha@gmail.com')
        hs6 = Student(ho='Lê Minh', ten='B', sex='Nam', DoB=datetime(2006, 1, 25), address='Hà Nội', sdt='0123456794',
                      email='leminhb@gmail.com')
        hs7 = Student(ho='Phạm Hoàng', ten='A', sex='Nữ', DoB=datetime(2008, 4, 30), address='Hải Phòng',
                      sdt='0123456795', email='phamhoanga@gmail.com')
        hs8 = Student(ho='Phạm Hoàng', ten='B', sex='Nam', DoB=datetime(2005, 12, 12), address='Đà Nẵng',
                      sdt='0123456796', email='phamhoangb@gmail.com')
        hs9 = Student(ho='Hoàng Văn', ten='A', sex='Nữ', DoB=datetime(2007, 6, 6), address='Cần Thơ', sdt='0123456797',
                      email='hoangvanda@gmail.com')
        hs10 = Student(ho='Hoàng Văn', ten='B', sex='Nam', DoB=datetime(2006, 8, 15), address='TP HCM',
                       sdt='0123456798', email='hoangvanb@gmail.com')
        hs11 = Student(ho='Nguyễn Thanh', ten='A', sex='Nữ', DoB=datetime(2008, 2, 18), address='Hà Nội',
                       sdt='0123456799', email='nguyenhana@gmail.com')
        hs12 = Student(ho='Nguyễn Thanh', ten='B', sex='Nam', DoB=datetime(2005, 10, 22), address='Cần Thơ',
                       sdt='0123456800', email='nguyenthanhb@gmail.com')
        hs13 = Student(ho='Trần Minh', ten='A', sex='Nữ', DoB=datetime(2007, 12, 10), address='Hải Phòng',
                       sdt='0123456801', email='tranminha@gmail.com')
        hs14 = Student(ho='Trần Minh', ten='B', sex='Nam', DoB=datetime(2006, 5, 5), address='Đà Nẵng',
                       sdt='0123456802', email='tranminhb@gmail.com')
        hs15 = Student(ho='Lê Anh', ten='A', sex='Nữ', DoB=datetime(2008, 9, 20), address='TP HCM', sdt='0123456803',
                       email='leanha@gmail.com')
        hs16 = Student(ho='Lê Anh', ten='B', sex='Nam', DoB=datetime(2005, 3, 12), address='Hà Nội', sdt='0123456804',
                       email='leanhb@gmail.com')
        hs17 = Student(ho='Phạm Quang', ten='A', sex='Nữ', DoB=datetime(2007, 8, 8), address='Cần Thơ',
                       sdt='0123456805', email='phamquanga@gmail.com')
        hs18 = Student(ho='Phạm Quang', ten='B', sex='Nam', DoB=datetime(2006, 4, 10), address='Hải Phòng',
                       sdt='0123456806', email='phamquangb@gmail.com')
        hs19 = Student(ho='Hoàng Mai', ten='A', sex='Nữ', DoB=datetime(2008, 1, 15), address='Đà Nẵng',
                       sdt='0123456807', email='hoangmaia@gmail.com')
        hs20 = Student(ho='Hoàng Mai', ten='B', sex='Nam', DoB=datetime(2005, 11, 25), address='TP HCM',
                       sdt='0123456808', email='hoangmaib@gmail.com')

        db.session.add_all([hs1, hs2, hs3, hs4, hs5, hs6, hs7, hs8, hs9, hs10,  hs11, hs12, hs13, hs14, hs15, hs16, hs17, hs18, hs19, hs20])
        db.session.commit()