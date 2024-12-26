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
    si_so = Column(Integer)
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

        u = User(ho='Lê Anh', ten='Hào', username="admin", password=str(hashlib.md5("123".encode('utf-8')).hexdigest()), user_role=UserRole.ADMIN)
        db.session.add(u)
        db.session.commit()