from functools import wraps

from flask_login import login_user

from testapp import app, dao, login
from flask import request, render_template, session, redirect, url_for, flash,  logging, abort
from flask_login import login_user, logout_user, login_required
from testapp.dao import get_user_by_id, xoa_hocsinh
from testapp.models import  User, lop_student, UserRole
import pandas as pd
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from flask import jsonify
from testapp.admin import *
from functools import wraps
from testapp.models import *



# Tạo Decorator kiểm tra đăng nhập
def admin_or_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.is_authenticated and current_user.user_role == UserRole.ADMIN:
                # ADMIN được phép truy cập tất cả
                return f(*args, **kwargs)
            elif current_user.is_authenticated and current_user.user_role == role:
                # Kiểm tra nếu đúng vai trò yêu cầu
                return f(*args, **kwargs)
            else:
                # Từ chối truy cập
                abort(403)
        return decorated_function
    return decorator

@app.context_processor
def inject_user_role():
    return dict(UserRole=UserRole)

@app.route("/")
def index():
    return render_template('index.html')

@login.user_loader
def user_load(user_id):
    return dao.get_user_by_id2(user_id)

@app.route('/login', methods=['GET', 'POST'])
def view_login():
    err_msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = dao.auth_user(username=username, password=password)
        if user:
            login_user(user=user)
            nextr = request.args.get('next')
            return redirect(nextr if nextr else '/')
        else:
            err_msg = 'Invalid username or password'
    return render_template('login.html', err_msg=err_msg)

@app.route('/login-admin', methods=['GET', 'POST'])
def login_admin_process():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = dao.auth_user(username=username, password=password, role=UserRole.ADMIN)
        if user:
            login_user(user=user)
    return redirect('/admin')

@app.route('/user-logout')
def logout():
    logout_user()
    return redirect(url_for('view_login'))


@app.route('/nhap-diem', methods=['GET', 'POST'])
@login_required
@admin_or_required(role=UserRole.TEACHER)
def nhapdiem():
    lops = Lop.query.all()
    selected_lop = None
    students_in_lop = []
    hk = []
    mh = Subject.query.all()
    namhoc = SchoolYear.query.all()
    khois = Khoi.query.all()
    diem_types = [diem for diem in DiemType]
    student_marks = {}
    marks_by_student = {}
    marks = {}
    selected_school_year = None

    if request.method == 'POST':
        selected_lop = Lop.query.filter(Lop.id == request.form['lop_id']).first()
        selected_school_year = SchoolYear.query.filter(SchoolYear.id == request.form['namhoc_id']).first()
        if 'view_lop' in request.form:
            if selected_lop and selected_school_year:
                students_in_lop = selected_lop.students
                hk = selected_school_year.semesters

        if 'nhap_diem' in request.form:
            exam_type = request.form.get('examType')
            subject_id = request.form.get('subject_id')
            semester_id = request.form.get('semester_id')


            if not all([exam_type, subject_id, semester_id]):
                flash('Vui lòng chọn đầy đủ thông tin trước khi lưu điểm!', 'danger')
            else:
                try:
                    # Lấy danh sách học sinh của lớp đã chọn
                    students_in_lop = selected_lop.students

                    for student in students_in_lop:
                        mark_value = request.form.get(f"mark_{student.id}")
                        if mark_value and mark_value.strip():
                                new_mark = Mark(
                                    type=exam_type,
                                    value=float(mark_value),
                                    subject_id=subject_id,
                                    semester_id=semester_id,
                                    student_id=student.id
                                )
                                db.session.add(new_mark)

                    db.session.commit()
                    flash('Điểm đã được lưu thành công!', 'success')
                except Exception as e:
                    db.session.rollback()
                    flash(f'Có lỗi xảy ra khi lưu điểm: {str(e)}', 'danger')



        if 'sua_diem' in request.form:
            exam_type = request.form.get('examType')
            subject_id = request.form.get('subject_id')
            semester_id = request.form.get('semester_id')

            if not all([exam_type, subject_id, semester_id]):
                flash('Vui lòng chọn đầy đủ thông tin trước khi lưu điểm!', 'danger')
            else:
                    # Lấy danh sách học sinh của lớp đã chọn
                    students_in_lop = selected_lop.students

                    for student in students_in_lop:
                        mark_value = request.form.get(f"mark_{student.id}")
                        if mark_value and mark_value.strip():
                            # Kiểm tra xem đã có điểm cho học sinh này chưa
                            existing_mark = Mark.query.filter_by(
                                student_id=student.id,
                                subject_id=subject_id,
                                semester_id=semester_id,
                                type=exam_type
                            ).first()

                            if existing_mark:
                                # Nếu đã có điểm thì cập nhật
                                existing_mark.value = float(mark_value)
                                db.session.commit()

        if 'xoa_diem' in request.form:
            exam_type = request.form.get('examType')
            subject_id = request.form.get('subject_id')
            semester_id = request.form.get('semester_id')

            if not all([exam_type, subject_id, semester_id]):
                flash('Vui lòng chọn đầy đủ thông tin trước khi lưu điểm!', 'danger')
            else:
                    # Lấy danh sách học sinh của lớp đã chọn
                    students_in_lop = selected_lop.students

                    for student in students_in_lop:
                        mark_value = request.form.get(f"mark_{student.id}")
                        if mark_value and mark_value.strip():
                            # Kiểm tra xem đã có điểm cho học sinh này chưa
                            existing_mark = Mark.query.filter_by(
                                student_id=student.id,
                                subject_id=subject_id,
                                semester_id=semester_id,
                                type=exam_type
                            ).first()
                        if existing_mark:
                            # Nếu đã có điểm thì cập nhật
                            db.session.delete(existing_mark)
                            db.session.commit()

        if 'xem_diem' in request.form:
            subject_id = request.form.get('subject_id')
            semester_id = request.form.get('semester_id')

            if not all([subject_id, semester_id]):
                flash('Vui lòng chọn đầy đủ thông tin trước khi lưu điểm!', 'danger')
            else:
                # Lấy danh sách học sinh của lớp đã chọn
                students_in_lop = selected_lop.students
                for student in students_in_lop:
                    marks = Mark.query.filter_by(
                        student_id=student.id,
                        subject_id=subject_id,
                        semester_id=semester_id
                    ).all()

                    student_marks[student.id] = {
                        DiemType.DIEM_15PHUT.name: [m.value for m in marks if m.type == DiemType.DIEM_15PHUT],
                        DiemType.DIEM_45PHUT.name: [m.value for m in marks if m.type == DiemType.DIEM_45PHUT],
                        DiemType.DIEM_CUOIKY.name: [m.value for m in marks if m.type == DiemType.DIEM_CUOIKY]
                    }


                flash('Điểm đã được lấy thành công!', 'success')

    return render_template('nhapdiem.html',
                           lops=lops,
                           students_in_lop=students_in_lop,
                           selected_lop=selected_lop,
                           hk=hk,
                           mh=mh,
                           namhoc=namhoc,
                           khois=khois,
                           diem_types=diem_types,
                           marks=marks,
                           marks_by_student=marks_by_student,
                           student_marks=student_marks,
                           selected_school_year=selected_school_year)

#xuất điểm
@app.route('/xuat-diem', methods=['GET', 'POST'])
@login_required
@admin_or_required(role=UserRole.TEACHER)
def xuatdiem():
    # Lấy thông tin các lớp và năm học
    lops = Lop.query.all()
    namhoc = SchoolYear.query.all()

    selected_year_id = request.form.get('school_year_id')
    selected_class_id = request.form.get('class_id')

    students_in_lop = []
    student_marks = {}

    if selected_year_id and selected_class_id:
        # Lấy học kỳ tương ứng với năm học đã chọn
        semesters = Semester.query.filter_by(school_year_id=selected_year_id).all()
        selected_class = Lop.query.filter_by(id=selected_class_id).first()
        # In thông tin học kỳ và lớp
        print(f"Học kỳ cho năm học {selected_year_id}: {semesters}")
        print(f"Lớp đã chọn: {selected_class}")

        if selected_class and semesters:
            # Lấy học sinh trong lớp đã chọn
            students_in_lop = selected_class.students

            for student in students_in_lop:
                student_marks[student.id] = {
                    'name': student.ho + " " + student.ten,
                    'class': selected_class.name,
                    'hk1_avg': 0,
                    'hk2_avg': 0,
                    'total_avg': 0
                }

                # Tạo danh sách điểm cho từng học kỳ
                hk1_subjects = {}
                hk2_subjects = {}

                for semester in semesters:
                    print(f"Checking semester type for semester {semester.id}: {semester.semester_type}")
                    marks = Mark.query.filter_by(student_id=student.id, semester_id=semester.id).all()
                    print(f"Marks for student {student.ho} {student.ten} in semester {semester.id}: {marks}")

                    # Lọc điểm theo từng loại điểm cho từng học kỳ và môn học
                    for m in marks:
                        subject = m.subject_id
                        if semester.semester_type == 'Học kỳ 1':
                            if subject not in hk1_subjects:
                                hk1_subjects[subject] = {'15_phut': [], '45_phut': [], 'cuoi_ky': []}
                            if m.type == DiemType.DIEM_15PHUT:
                                hk1_subjects[subject]['15_phut'].append(m.value)
                            elif m.type == DiemType.DIEM_45PHUT:
                                hk1_subjects[subject]['45_phut'].append(m.value)
                            elif m.type == DiemType.DIEM_CUOIKY:
                                hk1_subjects[subject]['cuoi_ky'].append(m.value)
                        elif semester.semester_type == 'Học kỳ 2':
                            if subject not in hk2_subjects:
                                hk2_subjects[subject] = {'15_phut': [], '45_phut': [], 'cuoi_ky': []}
                            if m.type == DiemType.DIEM_15PHUT:
                                hk2_subjects[subject]['15_phut'].append(m.value)
                            elif m.type == DiemType.DIEM_45PHUT:
                                hk2_subjects[subject]['45_phut'].append(m.value)
                            elif m.type == DiemType.DIEM_CUOIKY:
                                hk2_subjects[subject]['cuoi_ky'].append(m.value)

                # Tính điểm trung bình theo từng môn học cho từng học kỳ
                def calculate_subject_avg(subject_marks):
                    weighted_avg = sum(subject_marks['15_phut']) * 1 + sum(subject_marks['45_phut']) * 2 + sum(subject_marks['cuoi_ky']) * 3
                    total_weight = len(subject_marks['15_phut']) * 1 + len(subject_marks['45_phut']) * 2 + len(subject_marks['cuoi_ky']) * 3
                    return weighted_avg / total_weight if total_weight > 0 else 0

                hk1_avg_list = [calculate_subject_avg(marks) for subject, marks in hk1_subjects.items()]
                hk2_avg_list = [calculate_subject_avg(marks) for subject, marks in hk2_subjects.items()]

                hk1_avg = sum(hk1_avg_list) / len(hk1_avg_list) if hk1_avg_list else 0
                hk2_avg = sum(hk2_avg_list) / len(hk2_avg_list) if hk2_avg_list else 0
                total_avg = (hk2_avg * 2 + hk1_avg) / 3 if (hk1_avg_list or hk2_avg_list) else 0

                # Cập nhật điểm trung bình cho học sinh
                student_marks[student.id].update({
                    'hk1_avg': hk1_avg,
                    'hk2_avg': hk2_avg,
                    'total_avg': total_avg
                })

    return render_template('xuatdiem.html',
                           lops=lops,
                           namhoc=namhoc,
                           students_in_lop=students_in_lop,
                           student_marks=student_marks,
                           selected_year_id=selected_year_id,
                           selected_class_id=selected_class_id)

@app.route("/class")
@login_required
def view_class():
    # user_id =
    # user = get_user_by_id(user_id)  # Lấy thông tin người dùng từ cơ sở dữ liệu
    # Lấy danh sách các khối

    # grade_id = request.args.get('grade_id')
    grades = dao.load_grade()  # Đây là nơi bạn cần chắc chắn rằng có danh sách khối từ dao
    classes = dao.load_class()

    return render_template('class.html', grades=grades, classes=classes)

@app.route("/lop/<int:lop_id>/students", methods=['GET'])
@login_required
def get_students_by_lop(lop_id):
    lop = Lop.query.get(lop_id)
    if not lop:
        return jsonify({"error": "Lớp không tồn tại"}), 404

    # Lấy danh sách học sinh của lớp thông qua relationship
    students = [{
        "id": s.id,
        "ho": s.ho,
        "ten": s.ten,
        "dob": s.DoB.strftime('%Y-%m-%d') if s.DoB else None,
        "sex": s.sex,
        "address": s.address
    } for s in lop.students]

    return jsonify({"students": students}), 200


@app.route('/students/not-in-class', methods=['GET'])
@login_required
def get_students_not_in_class():
    try:
        # Truy vấn học sinh không thuộc lớp nào (lọc qua bảng trung gian lop_student)
        students = db.session.query(Student).outerjoin(lop_student).filter(lop_student.c.lop_id.is_(None)).all()

        student_list = [{
            "id": s.id,
            "ho": s.ho,
            "ten": s.ten,
            "dob": s.DoB.strftime('%Y-%m-%d') if s.DoB else None,
            "sex": s.sex
        } for s in students]

        return jsonify({"students": student_list}), 200
    except Exception as e:
        logging.error(f"Error fetching students not in class: {e}", exc_info=True)
        return jsonify({"error": "Unable to fetch data"}), 500


@app.route('/lop/add-students', methods=['POST'])
@login_required
def add_students_to_class():
    try:
        # Lấy dữ liệu từ request
        data = request.get_json()
        class_id = data.get("class_id")
        student_ids = data.get("student_ids")

        # Kiểm tra dữ liệu đầu vào
        if not (class_id and student_ids):
            return jsonify({"error": "Thiếu thông tin bắt buộc"}), 400

        # Lấy lớp học từ database
        lop = Lop.query.get(class_id)
        if not lop:
            return jsonify({"error": "Lớp không tồn tại"}), 404

        # Thêm học sinh vào lớp (lop_student)
        for student_id in student_ids:
            student = Student.query.get(student_id)
            if not student:
                continue

            # Kiểm tra nếu học sinh đã tồn tại trong lớp
            connection_exists = db.session.query(lop_student).filter_by(
                lop_id=class_id, student_id=student_id).first()
            if not connection_exists:
                # Thêm vào bảng trung gian lop_student
                db.session.execute(lop_student.insert().values(lop_id=class_id, student_id=student_id))

        db.session.commit()
        return jsonify({"success": True}), 200

    except Exception as e:
        logging.error(f"Lỗi xảy ra: {str(e)}")
        return jsonify({"error": "Có lỗi xảy ra khi thêm học sinh"}), 500


#Đếm số học sinh đang có
@app.route('/class', methods=['GET'])
@login_required
def class_list():
    classes = Lop.query.all()

    class_data = []
    for lop in classes:
        # Sử dụng thuộc tính `siso` để lấy sĩ số thực tế
        class_data.append({
            "id": lop.id,
            "name": lop.name,
            "siso": lop.siso  # Tính sĩ số thực tế
        })

    return render_template('class.html', classes=class_data)
@app.route('/lop/<int:lop_id>/count', methods=['GET'])
@login_required
def get_student_count(lop_id):
    siso = db.session.query(lop_student).filter(lop_student.c.lop_id == lop_id).count()
    return jsonify({"siso": siso})




@app.route('/lop/<int:lop_id>/remove-student/<int:student_id>', methods=['DELETE'])
@login_required
def remove_student_from_class(lop_id, student_id):
    try:
        lop = Lop.query.get(lop_id)
        if not lop:
            return jsonify({"error": "Lớp không tồn tại"}), 404

        student_in_class = db.session.query(lop_student).filter_by(lop_id=lop_id, student_id=student_id).first()
        if not student_in_class:
            return jsonify({"error": "Học sinh không thuộc lớp này"}), 404

        db.session.query(lop_student).filter_by(lop_id=lop_id, student_id=student_id).delete()
        db.session.commit()

        return jsonify({"success": True}), 200

    except Exception as e:
        logging.error(f"Lỗi khi xóa học sinh khỏi lớp: {str(e)}")
        return jsonify({"error": "Không thể xóa học sinh khỏi lớp"}), 500


# @app.route('/lop/<int:lop_id>/students', methods=['GET'])
# @login_required
# def get_students_in_class(lop_id):
#     session = db.session
#     lop = session.get(Lop, lop_id)  # Thay đổi từ Lop.query.get(lop_id)
#
#     if not lop:
#         return jsonify({"error": "Lớp không tồn tại"}), 404
#
#     students = [
#         {
#             "id": student.id,
#             "ho": student.ho,
#             "ten": student.ten,
#             "dob": student.DoB.strftime('%Y-%m-%d') if student.DoB else None,
#             "sex": student.sex,
#             "address": student.address,
#         }
#         for student in lop.students
#     ]
#     return jsonify({"students": students}), 200
#

# @app.route("/user")
# def view_user():
#     return render_template('user')

@app.route("/teacher")
@login_required
def view_teacher():
    user_id = session['user_id']
    user = get_user_by_id(user_id)  # Lấy thông tin người dùng từ cơ sở dữ liệu

    teachers = dao.load_teacher()
    return render_template('teacher.html', teachers=teachers, user=user)

@app.route("/student")
@login_required
def view_student():
    user_id = session['user_id']
    user = get_user_by_id(user_id)  # Lấy thông tin người dùng từ cơ sở dữ liệu
    students = dao.load_student()
    return render_template('student.html', students=students, user=user)
# Phân trang
@app.route('/students', methods=['GET'])
@login_required
def get_students():
    page = request.args.get('page', 1, type=int)  # Trang hiện tại
    per_page = request.args.get('per_page', 10, type=int)  # Số lượng mỗi trang

    students_query = Student.query
    total = students_query.count()
    students = students_query.paginate(page=page, per_page=per_page, error_out=False)

    data = [{
        "id": s.id,
        "ho": s.ho,
        "ten": s.ten,
        "sex": s.sex,
        "dob": s.DoB.strftime('%Y-%m-%d'),
        "address": s.address,
        "sdt": s.sdt,
        "email": s.email
    } for s in students.items]

    return jsonify({
        "students": data,
        "total": total,
        "page": page,
        "pages": students.pages
    })

@app.route("/them_students", methods=['POST'])
@login_required
def them_student():
    try:
        data = request.get_json()
        ho = data.get("ho")
        ten = data.get("ten")
        sex = data.get("gender")  # Đổi gioi_tinh thành sex
        ngay_sinh = data.get("dob")
        dia_chi = data.get("address")
        sdt = data.get("phone")
        email = data.get("email")

        if not (ho and ten and sex and ngay_sinh and dia_chi and sdt and email):
            return jsonify({"error": "Thiếu thông tin bắt buộc"}), 400

        dao.them_hoc_sinh(ho, ten, sex, ngay_sinh, dia_chi, sdt, email)
        return jsonify({"success": True}), 200


    except ValueError as e:

        logging.error(f"Validation error: {e}", exc_info=True)

        return jsonify({"error": str(e)}), 400

    except Exception as e:

        logging.error(f"Unexpected error: {e}", exc_info=True)

        return jsonify({"error": "Có lỗi xảy ra"}), 500

@app.route("/edit_student/<int:student_id>", methods=['PUT'])
@login_required
def edit_student(student_id):
    try:
        data = request.get_json()
        ho = data.get("ho")
        ten = data.get("ten")
        gioi_tinh = data.get("gender")
        ngay_sinh = data.get("dob")
        dia_chi = data.get("address")
        sdt = data.get("phone")
        email = data.get("email")

        if not (ho and ten and gioi_tinh and ngay_sinh and dia_chi and sdt and email):
            return jsonify({"error": "Thiếu thông tin bắt buộc"}), 400

        student = Student.query.get(student_id)
        if not student:
            return jsonify({"error": "Học sinh không tồn tại"}), 404

            # Kiểm tra tuổi
        dob_date = datetime.strptime(ngay_sinh, "%Y-%m-%d")  # Chuyển ngày sinh thành đối tượng datetime
        current_date = datetime.now()
        age = current_date.year - dob_date.year - (
                    (current_date.month, current_date.day) < (dob_date.month, dob_date.day))

        if age < 15 or age > 20:
            return jsonify({"error": "Học sinh phải từ 15 đến 20 tuổi"}), 400

        # Kiểm tra nếu số điện thoại đã tồn tại cho một học sinh khác
        existing_phone = Student.query.filter(Student.sdt == sdt, Student.id != student_id).first()
        if existing_phone:
            return jsonify({"error": "Số điện thoại đã tồn tại!"}), 400

        # Kiểm tra nếu email đã tồn tại cho một học sinh khác
        existing_email = Student.query.filter(Student.email == email, Student.id != student_id).first()
        if existing_email:
            return jsonify({"error": "Email đã tồn tại!"}), 400


        # Cập nhật thông tin học sinh
        student.ho = ho
        student.ten = ten
        student.sex = gioi_tinh
        student.DoB = ngay_sinh
        student.address = dia_chi
        student.sdt = sdt
        student.email = email

        db.session.commit()
        return jsonify({"success": True}), 200

    except Exception as e:
        logging.error(f"Unexpected error: {e}", exc_info=True)
        return jsonify({"error": "Có lỗi xảy ra"}), 500

@app.route("/delete_student/<int:student_id>", methods=['DELETE'])
@login_required
def delete_student(student_id):
    try:
        if xoa_hocsinh(student_id):
            return jsonify({"success": True, "message": "Học sinh đã được xóa thành công"}), 200
        else:
            return jsonify({"error": "Học sinh không tồn tại"}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logging.error(f"Unexpected error: {e}", exc_info=True)
        return jsonify({"error": "Có lỗi xảy ra, không thể xóa học sinh"}), 500


@app.route("/diem", methods=["GET", "POST"])
@login_required
def view_diem():
    user_id = session['user_id']
    user = get_user_by_id(user_id)  # Lấy thông tin người dùng từ cơ sở dữ liệu
    if request.method == "POST":
        lop_id = request.form.get("lop")
        monhoc_id = request.form.get("monhoc")
        hoc_ky_id = request.form.get("hoc_ky")

        # Truy vấn cơ sở dữ liệu để lấy bảng điểm
        diems = dao.load_diem_theo_lop_mon_hoc_hoc_ky(lop_id, monhoc_id, hoc_ky_id)

        return render_template('diem.html', diems=diems, user=user)

    # Lấy danh sách lớp, môn học và học kỳ để hiển thị trong dropdown
    danh_sach_lop = dao.load_class()
    danh_sach_mon_hoc = dao.load_monhoc()
    danh_sach_hoc_ky = dao.load_hoc_ky()

    return render_template('diem.html',
                           danh_sach_lop=danh_sach_lop, danh_sach_mon_hoc=danh_sach_mon_hoc,
                           danh_sach_hoc_ky=danh_sach_hoc_ky, user=user)

# monhoc
@app.route("/monhoc")
@login_required
def view_monhoc():
    # user_id = session['user_id']
    # user = get_user_by_id(user_id)  # Lấy thông tin người dùng từ cơ sở dữ liệu

    monhocs = dao.load_monhoc()
    return render_template('monhoc.html',monhocs=monhocs)


@app.route("/them_monhoc", methods=['POST'])
# @login_required
# def them_monhoc():
#
#
#     data = request.get_json()
#     name = data.get("name")
#
#     try:
#         if name:
#             dao.them_monhoc(name)  # Gọi hàm thêm môn học
#             return jsonify({"success": True}), 200
#         else:
#             return jsonify({"error": "Invalid input"}), 400
#     except ValueError as e:  # Bắt lỗi nếu môn học đã tồn tại
#         return jsonify({"error": str(e)}), 400
#
#
#
# @app.route("/sua_monhoc/<int:id>", methods=['PUT'])
# def sua_monhoc(id):
#     data = request.get_json()
#     name = data.get("name")
#
#     try:
#         if dao.sua_monhoc(id, name):
#             return jsonify({"success": True}), 200
#         else:
#             return jsonify({"error": "Not found"}), 404
#     except ValueError as e:
#         return jsonify({"error": str(e)}), 400  # Trả về lỗi nếu môn học đã tồn tại
#
#
# @app.route("/xoa_monhoc/<int:id>", methods=['DELETE'])
# def xoa_monhoc(id):
#     if dao.xoa_monhoc(id):
#         return jsonify({"success": True}), 200
#     else:
#         return jsonify({"error": "Not found"}), 404
#
# # monhoc




@app.route('/upload', methods=['GET', 'POST'])
def upload_students():
    if request.method == 'POST':
        file = request.files['file']
        if not file:
            flash("Vui lòng chọn file!", "error")
            return redirect(request.url)

        try:
            # Đọc file Excel bằng pandas
            df = pd.read_excel(file)

            # Kiểm tra và ánh xạ cột nếu cần
            required_columns = ['ho', 'ten', 'sex', 'DoB', 'address', 'sdt', 'email']
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                raise ValueError(f"Các cột sau bị thiếu trong file Excel: {', '.join(missing_columns)}")

            # Duyệt từng dòng và thêm vào database
            for _, row in df.iterrows():
                # Tính tuổi từ ngày sinh
                dob = pd.to_datetime(row['DoB'])
                current_date = datetime.now()
                age = (current_date - dob).days // 365  # Tính tuổi bằng số ngày chia cho 365

                # Kiểm tra điều kiện độ tuổi
                if age < 15 or age > 20:
                    flash(f"Học sinh {row['ho']} {row['ten']} không trong độ tuổi từ 15 đến 20.", "warning")
                    continue  # Bỏ qua học sinh này

                # Thêm học sinh vào database nếu hợp lệ
                student = Student(
                    ho=row['ho'],
                    ten=row['ten'],
                    sex=row['sex'],
                    DoB=dob,
                    address=row['address'],
                    sdt=row['sdt'],
                    email=row['email']
                )
                db.session.add(student)

            # Lưu các thay đổi
            db.session.commit()
            flash("Thêm học sinh thành công!", "success")
            return redirect(url_for('upload_students'))

        except ValueError as ve:
            flash(str(ve), "error")
        except IntegrityError:
            db.session.rollback()
            flash("Lỗi: Trùng lặp hoặc dữ liệu không hợp lệ!", "error")
        except Exception as e:
            flash(f"Lỗi không xác định: {str(e)}", "error")

    return render_template('upload.html')

# @app.route("/login", methods=['get', 'post'])
# def login_view():
#     if request.method.__eq__('POST'):
#         username = request.form.get('username')
#         password = request.form.get('password')
#         user = dao.auth_user(username=username, password=password)
#         if user:
#             login_user(user=user)
#
#             next = request.args.get('next')
#             return redirect(next if next else '/')
#
#     return render_template('login.html')
#
# @app.route('/login-admin', methods=['post'])
# def login_admin_process():
#     username = request.form.get('username')
#     password = request.form.get('password')
#     user = dao.auth_user(username=username, password=password, role=UserRole.ADMIN)
#     if user:
#         login_user(user=user)
#
#     return redirect('/admin')



if __name__ == '__main__':
    app.run(debug=True)