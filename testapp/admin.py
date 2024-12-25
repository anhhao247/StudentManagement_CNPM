from tkinter.font import names

from testapp import app, db
from flask_admin import Admin, BaseView, expose
from testapp.models import Khoi, Lop, Student, User, UserRole, Subject, Teacher, lop_student, Semester, SchoolYear
from flask_admin.contrib.sqla import ModelView
import hashlib
from flask_login import logout_user, current_user
from flask import redirect


admin = Admin(app=app, name='Student Management', template_mode='bootstrap4')

class AuthenticatedView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role.__eq__(UserRole.ADMIN)


class LopView(AuthenticatedView):
    form_columns = ['students' ,'name', 'si_so', 'khoi']
    # column_list = ['name', 'si_so', 'khoi']
    # pass

class KhoiView(AuthenticatedView):
        column_list = ['name', 'lops']
        # form_columns = ['name', 'lops']
        pass

class UserView(AuthenticatedView):
    def on_model_change(self, form, model, is_created):
        form_columns = ['ho', 'ten', 'username', 'password', 'active', 'user_role']
        # Kiểm tra nếu người dùng nhập mật khẩu
        if form.password.data:
            # Mã hóa mật khẩu trước khi lưu vào database
            model.password = str(hashlib.md5(form.password.data.encode('utf-8')).hexdigest())
        super().on_model_change(form, model, is_created)

class TeacherView(AuthenticatedView):

    def on_model_change(self, form, model, is_created):
        form_columns = ['ho', 'ten', 'username', 'password', 'active', 'user_role', 'subjects']
        # Kiểm tra nếu người dùng nhập mật khẩu
        if form.password.data:
            # Mã hóa mật khẩu trước khi lưu vào database
            model.password = str(hashlib.md5(form.password.data.encode('utf-8')).hexdigest())
        super().on_model_change(form, model, is_created)

class StudentView(AuthenticatedView):
    column_list = ['ho', 'ten', 'sex', 'DoB', 'address', 'sdt', 'email', 'lop']
    column_details_list = ['ho', 'ten', 'sex', 'DoB', 'address', 'sdt', 'email', 'lop']
    form_columns = ['ho', 'ten', 'sex', 'DoB', 'address', 'sdt', 'email', 'lop']
    form_excluded_columns = ['subjects']
    can_view_details = True
    edit_modal = True
    column_filters = ['ten', 'lop']
    column_searchable_list = ['ten']

class SemesterView(AuthenticatedView):
    pass

class SchoolYearView(AuthenticatedView):
    pass

class SubjectView(AuthenticatedView):
    form_columns = ['name']

class AuthendicatedBaseView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated

class LogoutView(AuthendicatedBaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')



admin.add_view(KhoiView(Khoi, db.session, name='Khối'))
admin.add_view(LopView(Lop, db.session, name='Lớp học'))
admin.add_view(UserView(User, db.session))
admin.add_view(StudentView(Student, db.session, name='Học sinh'))
admin.add_view(TeacherView(Teacher, db.session, name='Giáo Viên'))
admin.add_view(SubjectView(Subject, db.session, name='Môn học'))
admin.add_view(SemesterView(Semester, db.session, name='Học kỳ'))
admin.add_view(SchoolYearView(SchoolYear, db.session, name='Năm học'))

admin.add_view(LogoutView(name='Logout'))
