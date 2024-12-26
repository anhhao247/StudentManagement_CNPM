from sqlalchemy import func, case
from sqlalchemy.exc import NoResultFound

from testapp.models import *

def get_semester_by_schoolyear_id(schoolyear_id):
    return Semester.query.filter_by(school_year_id=schoolyear_id).all()

def calculate_subject_avg(subject_marks):
    """
    Tính điểm trung bình cho một môn học dựa trên các loại điểm
    """
    weighted_avg = (
        sum(subject_marks['15_phut']) * 1 +
        sum(subject_marks['45_phut']) * 2 +
        sum(subject_marks['cuoi_ky']) * 3
    )
    total_weight = (
        len(subject_marks['15_phut']) * 1 +
        len(subject_marks['45_phut']) * 2 +
        len(subject_marks['cuoi_ky']) * 3
    )
    return weighted_avg / total_weight if total_weight > 0 else 0

def get_marks_by_subject(student_id, semester_id):
    """
    Lấy điểm cho từng môn học của học sinh trong một học kỳ
    """
    marks = Mark.query.filter_by(student_id=student_id, semester_id=semester_id).all()
    subjects = {}

    for m in marks:
        subject = m.subject_id
        if subject not in subjects:
            subjects[subject] = {'15_phut': [], '45_phut': [], 'cuoi_ky': []}
        if m.type == DiemType.DIEM_15PHUT:
            subjects[subject]['15_phut'].append(m.value)
        elif m.type == DiemType.DIEM_45PHUT:
            subjects[subject]['45_phut'].append(m.value)
        elif m.type == DiemType.DIEM_CUOIKY:
            subjects[subject]['cuoi_ky'].append(m.value)

    return subjects

def calculate_avg_for_semester(student_id, semester_id):
    """
    Tính điểm trung bình cho từng học kỳ của học sinh
    """
    subjects = get_marks_by_subject(student_id, semester_id)
    avg_list = [calculate_subject_avg(marks) for subject, marks in subjects.items()]
    return sum(avg_list) / len(avg_list) if avg_list else 0

def calculate_avg_for_year(student_id, semesters):
    """
    Tính điểm trung bình năm học dựa trên các học kỳ
    """
    hk1_avg = 0
    hk2_avg = 0

    for semester in semesters:
        if semester.semester_type == 'Học kỳ 1':
            hk1_avg = calculate_avg_for_semester(student_id, semester.id)
        elif semester.semester_type == 'Học kỳ 2':
            hk2_avg = calculate_avg_for_semester(student_id, semester.id)

    hk1_avg_rounded = round(hk1_avg, 1)
    hk2_avg_rounded = round(hk2_avg, 1)
    total_avg = (hk2_avg * 2 + hk1_avg) / 3 if hk1_avg or hk2_avg else 0
    total_avg_rounded = round(total_avg, 1)

    return {
        'hk1_avg': hk1_avg_rounded,
        'hk2_avg': hk2_avg_rounded,
        'total_avg': total_avg_rounded
    }
# load khoi
def load_grade():
    return Khoi.query.all()


# load lop
def load_class(grade_id=None):
    if grade_id:
        classes = Lop.query.filter_by(khoi_id=grade_id).all()
    else:
        classes = Lop.query.all()
    return classes


# load monhoc
def load_monhoc(grade_id=None):
    return Subject.query.all()


def them_monhoc(name):
    if Subject.query.filter_by(name=name).first():
        raise ValueError("Môn học đã tồn tại!")
    new_monhoc = Subject(name=name)
    db.session.add(new_monhoc)
    db.session.commit()


def sua_monhoc(id, name):
    # Kiểm tra nếu môn học mới có tên giống với môn học khác
    if Subject.query.filter_by(name=name).first():
        raise ValueError("Môn học đã tồn tại!")

    monhoc = Subject.query.get(id)
    if monhoc:
        monhoc.name = name
        db.session.commit()
        return True
    return False


def xoa_monhoc(id):
    monhoc = Subject.query.get(id)
    if not monhoc:
        return False
    # Kiểm tra nếu môn học liên kết với dữ liệu khác
    if Mark.query.filter_by(monhoc_id=id).first():
        raise ValueError("Không thể xóa môn học vì có dữ liệu liên quan.")
    db.session.delete(monhoc)
    db.session.commit()
    return True


# load hoc sinh
def load_student():
    return Student.query.all()


# Delete student
def xoa_hocsinh(id):
    # Tìm học sinh theo ID
    hocsinh = Student.query.get(id)  # Sử dụng model ORM
    if not hocsinh:
        return False

    try:
        # Xóa dữ liệu liên quan trong bảng Diem
        Mark.query.filter_by(student_id=id).delete()

        # Xóa dữ liệu liên quan trong bảng Lop_Student
        # Lop_Student.query.filter_by(student_id=id).delete()

        # Xóa học sinh
        db.session.delete(hocsinh)
        db.session.commit()
        return True

    except Exception as e:
        db.session.rollback()  # Hoàn tác nếu có lỗi
        raise ValueError(f"Lỗi khi xóa học sinh: {e}")


# add student
def them_hoc_sinh(ho, ten, gioi_tinh, ngay_sinh, dia_chi, sdt, email):
    # Kiểm tra email hợp lệ
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

    # Kiểm tra số điện thoại chỉ chứa số
    # Kiểm tra độ tuổi
    dob = datetime.strptime(ngay_sinh, '%Y-%m-%d')  # Chuyển ngày sinh từ chuỗi sang đối tượng datetime
    today = datetime.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))  # Tính tuổi chính xác
    if age < 15 or age > 20:
        raise ValueError("Chỉ chấp nhận học sinh từ 15 đến 20 tuổi!")

    # Kiểm tra nếu email đã tồn tại
    if Student.query.filter_by(email=email).first():
        raise ValueError("Email đã tồn tại!")

    # Kiểm tra nếu sđt học sinh đã tồn tại
    if Student.query.filter_by(sdt=sdt).first():
        raise ValueError("SĐT học sinh đã tồn tại!")

    # Thêm học sinh mới
    new_student = Student(
        ho=ho,
        ten=ten,
        sex=gioi_tinh,
        DoB=ngay_sinh,
        address=dia_chi,
        sdt=sdt,
        email=email
    )
    db.session.add(new_student)
    db.session.commit()


# load diem theo mon
def load_diem_theo_mon_hoc(monhoc_id=None):
    return Mark.query.all()


# load user
def load_user():
    return User.query.all()


# load giaovien
def load_teacher():
    return Teacher.query.all()


def get_student_by_id(student_id):
    return Student.query.get(student_id)

def load_semester():
    return Semester.query.all()

def load_namhoc():
    return SchoolYear.query.all()


# DinhLuan
# Load học kỳ
# def load_hoc_ky():
#     return HocKy.query.all()

# def check_password(Stored_password, entered_password):
#     return check_password_hash(Stored_password, entered_password)


# def get_user_by_username(username):
#     # Truy vấn cơ sở dữ liệu để lấy thông tin người dùng
#     # Ví dụ, trả về một đối tượng người dùng có chứa mật khẩu đã băm
#     user = db.session.query(User).filter_by(username=username).first()
#     if user:
#         return {"id": user.id, "username": user.username, "password": user.password}
#     return None
#
def get_user_by_id(user_id):
    # Lấy thông tin người dùng từ cơ sở dữ liệu dựa trên user_id
    user = User.query.get(user_id)  # Truy vấn cơ sở dữ liệu với user_id
    if user:
        return {
            "id": user.id,
            "name": user.name,
            "job": user.user_role
        }
    return None  # Nếu không tìm thấy người dùng, trả về None


def auth_user(username, password, role=None):
    if username and password:
        password = str(hashlib.md5(password.encode('utf-8')).hexdigest())
        user = User.query.filter(User.username.__eq__(username.strip()),
                                 User.password.__eq__(password))
        if role:
            user = user.filter(User.user_role.__eq__(role))
        return user.first()


def get_user_by_id2(user_id):
    return User.query.get(user_id)


# OuterJoin
def count_class_by_grade():
    return db.session.query(Khoi.id, Khoi.name, func.count(Lop.id)).join(Lop, Lop.khoi_id == Khoi.id,
                                                                         isouter=True).group_by(Khoi.id).all()


def count_student_by_class():
    return db.session.query(Lop.id,Lop.name,func.count(lop_student.c.student_id)).join(lop_student, Lop.id == lop_student.c.lop_id, isouter=True).group_by(Lop.id).all()

def count_student_by_class_id(lop_id):
    siso = db.session.query(func.count(lop_student.c.student_id)).filter(lop_student.c.lop_id == lop_id).scalar()
    return siso

def get_semester_by_id(semester_id):
    return Semester.query.get(semester_id)

# def tinh_diem_tb_mon_theo_hk(student_id, mh_id, hk_id, namhoc_id):
#     student = get_student_by_id(student_id)
#     if namhoc_id == get_semester_by_id(hk_id).school_year_id:
#         diem_student = Mark.query.filter_by(subject_id=mh_id, semester_id=hk_id, student_id=student_id).all()
#         diem_tb = 0
#         if not diem_student:
#             return None
#         else
#             if diem_student.type == DiemType.DIEM_15PHUT.name:
#                 diem_tb =
#
#     return diem_tb

# Corrected function
def calculate_average_score(school_year_id, semester_id, subject_id):
    # Adjusted `case()` to pass positional arguments
    weight_case = case(
        (Mark.type.name == "DIEM_15PHUT", 1),
        (Mark.type.name == "DIEM_45PHUT", 2),
        (Mark.type.name == "DIEM_CUOIKY", 3),
        else_=0
    )

    # Tính tổng điểm có áp dụng hệ số và tổng hệ số
    results = db.session.query(
        Student.id.label('student_id'),
        Student.ho.label('last_name'),
        Student.ten.label('first_name'),
        func.sum(Mark.value * weight_case).label('total_score'),
        func.sum(weight_case).label('total_weight')
    ).join(Mark, Mark.student_id == Student.id
    ).join(Semester, Mark.semester_id == Semester.id
    ).join(SchoolYear, Semester.school_year_id == SchoolYear.id
    ).filter(
        SchoolYear.id == school_year_id,
        Semester.id == semester_id,
        Mark.subject_id == subject_id
    ).group_by(Student.id, Student.ho, Student.ten).all()

    # Tính điểm trung bình
    average_scores = [
        {
            'student_id': row.student_id,
            'name': f"{row.last_name} {row.first_name}",
            'average_score': round(row.total_score / row.total_weight, 2) if row.total_weight > 0 else None
        }
        for row in results
    ]
    return average_scores

def test():
    s = Student.query.get(1)
    if s.lop:  # Nếu học sinh có lớp
        # Lấy lớp của học sinh (nếu có nhiều lớp, chúng ta cần xử lý)
        for lop in s.lop:  # Sử dụng mối quan hệ nhiều-nhiều
            return lop.si_so
    else:
        return "Học sinh chưa có lớp"

if __name__ == "__main__":
    from testapp import app

    with app.app_context():
        print(test())
        # test()
# def get_user_by_id(user_id):
#     # Lấy thông tin người dùng từ cơ sở dữ liệu dựa trên user_id
#     user = User.query.get(user_id)  # Truy vấn cơ sở dữ liệu với user_id
#     if user:
#         return {
#             "id": user.id,
#             "name": user.name,
#             "job": user.user_role
#         }
#     return None  # Nếu không tìm thấy người dùng, trả về None
#
#
# # Hàm xóa người dùng theo ID
# def delete_user_by_id(user_id):
#     try:
#         # Tìm người dùng theo ID
#         user = User.query.filter_by(id=user_id).one()
#
#         # Xóa người dùng khỏi cơ sở dữ liệu
#         db.session.delete(user)
#         db.session.commit()
#         print(f"Đã xóa người dùng có ID {user_id}")
#     except NoResultFound:
#         print(f"Không tìm thấy người dùng với ID {user_id}")
#         return False
#     return True
#
# def save_user(user):
#     if user.id:  # Kiểm tra nếu user đã có id, nghĩa là đây là người dùng đã tồn tại
#         # Cập nhật thông tin người dùng
#         existing_user = User.query.filter_by(id=user.id).first()
#         if existing_user:
#             existing_user.name = user.name
#             existing_user.username = user.username
#             existing_user.email = user.email
#             existing_user.active = user.active
#             existing_user.user_role = user.user_role
#             db.session.commit()  # Lưu thay đổi
#             print(f"Đã cập nhật thông tin người dùng có ID {user.id}")
#         else:
#             print(f"Không tìm thấy người dùng có ID {user.id}")
#     else:
#         # Nếu user chưa có id (người dùng mới), thêm người dùng mới vào cơ sở dữ liệu
#         db.session.add(user)
#         db.session.commit()  # Lưu bản ghi mới
#         print(f"Đã thêm người dùng mới: {user.name}")
# =======
#    return User.query.get(user_id)

# >>>>>>> main
