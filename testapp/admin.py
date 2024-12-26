from tkinter.font import names

from testapp import app, db, dao
from flask_admin import Admin, BaseView, expose, AdminIndexView

from testapp.dao import load_monhoc
from testapp.models import Khoi, Lop, Student, User, UserRole, Subject, Teacher, lop_student, Semester, SchoolYear
from flask_admin.contrib.sqla import ModelView
import hashlib
from flask_login import logout_user, current_user
from flask import redirect, session
from sqlalchemy import func

class MyAdminIndexView(AdminIndexView):
    @expose("/")
    def index(self):

        return self.render('admin/index.html', khois=dao.count_class_by_grade())

admin = Admin(app=app, name='Student Management', template_mode='bootstrap4', index_view=MyAdminIndexView())

class AuthenticatedView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role.__eq__(UserRole.ADMIN)


class LopView(AuthenticatedView):
    form_columns = ['students' ,'name', 'khoi']
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

    def on_model_change(self, form, model, is_created):
        if not is_created:  # Trường hợp cập nhật học sinh
            # Lưu danh sách lớp cũ trước khi có bất kỳ thay đổi nào
            old_lops = set(model.lop)  # Chuyển sang set để so sánh dễ dàng hơn
            new_lops = set(form.lop.data)

            # Tìm các lớp bị xóa và các lớp được thêm mới
            removed_lops = old_lops - new_lops
            added_lops = new_lops - old_lops

            # Cập nhật sĩ số
            for lop in removed_lops:
                lop.si_so = max(0, lop.si_so - 1)
                db.session.add(lop)

            for lop in added_lops:
                lop.si_so += 1
                db.session.add(lop)

        else:  # Trường hợp thêm mới học sinh
            if model.lop:
                for lop in model.lop:
                    lop.si_so += 1
                    db.session.add(lop)

        # Gọi super để cập nhật model
        super().on_model_change(form, model, is_created)

        # Commit tất cả các thay đổi
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e




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

class StatsView(AuthendicatedBaseView):
    @expose("/")
    def index(self):
        return self.render('admin/stats.html', lops=dao.count_student_by_class(), mh=dao.load_monhoc(), hk=dao.load_semester(), namhoc=dao.load_namhoc())

admin.add_view(KhoiView(Khoi, db.session, name='Khối'))
admin.add_view(LopView(Lop, db.session, name='Lớp học'))
admin.add_view(UserView(User, db.session))
admin.add_view(StudentView(Student, db.session, name='Học sinh'))
admin.add_view(TeacherView(Teacher, db.session, name='Giáo Viên'))
admin.add_view(SubjectView(Subject, db.session, name='Môn học'))
admin.add_view(SemesterView(Semester, db.session, name='Học kỳ'))
admin.add_view(SchoolYearView(SchoolYear, db.session, name='Năm học'))
admin.add_view(StatsView(name='Thống kê'))
admin.add_view(LogoutView(name='Logout'))

