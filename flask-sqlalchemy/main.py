from datetime import datetime
from flask import Flask, render_template, redirect, request
from data import db_session
from data.users import User
from data.jobs import Jobs
from data.departments import Department
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms import IntegerField
from wtforms.validators import DataRequired
from flask_login import LoginManager, login_user, login_required, logout_user
import flask_login

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


class AddingJobForm(FlaskForm):
    job = StringField('Job Title', validators=[DataRequired()])
    team_leader_id = StringField(
        'Team Leader id', validators=[DataRequired()])
    work_size = IntegerField('Work Size', validators=[DataRequired()])
    collaborators = StringField('Collaborators', validators=[DataRequired()])
    is_job_finished = BooleanField('is job finished')
    submit = SubmitField('Submit')


class AddingDepForm(FlaskForm):
    title = StringField('Department Title', validators=[DataRequired()])
    chief = StringField('Chief id', validators=[DataRequired()])
    members = StringField('Members', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    email = StringField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    login_or_mail = StringField('Login / email',
                                validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    repeat_password = StringField(
        'Repeat password', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    position = StringField('Position', validators=[DataRequired()])
    speciality = StringField('Speciality', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    submit = SubmitField('Submit')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def index():
    db_session.global_init("db/mars.db")
    db_sess = db_session.create_session()
    jobs = [job for job in db_sess.query(Jobs).all()]
    users = [user for user in db_sess.query(User).all()]
    return render_template('works_journal.html', title='Journal works',
                           jobs=jobs, users=users)


@app.route('/departments')
def departments():
    db_session.global_init("db/mars.db")
    db_sess = db_session.create_session()
    deps = [dep for dep in db_sess.query(Department).all()]
    users = [user for user in db_sess.query(User).all()]
    return render_template('list_of_deps.html', title='List of departments',
                           deps=deps, users=users)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        db_session.global_init("db/mars.db")
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(
            User.email == form.login_or_mail.data).first()
        if user:
            return render_template('register_form.html', form=form,
                                   message='Колонист с такой почтой уже есть!')
        if form.repeat_password.data != form.password.data:
            return render_template('register_form.html', form=form,
                                   message='Введенные пароли не совпадают!')
        user = User()
        user.surname = form.surname.data
        user.name = form.name.data
        user.age = form.age.data
        user.position = form.position.data
        user.speciality = form.speciality.data
        user.address = form.address.data
        user.email = form.login_or_mail.data
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/register')
    return render_template('register_form.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    db_session.global_init("db/mars.db")
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(
            User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/add_job', methods=['GET', 'POST'])
@login_required
def adding_job():
    form = AddingJobForm()
    if form.validate_on_submit():
        db_session.global_init("db/mars.db")
        db_sess = db_session.create_session()
        job = Jobs()
        job.job = form.job.data
        job.team_leader = form.team_leader_id.data
        job.work_size = form.work_size.data
        job.collaborators = form.collaborators.data
        job.start_date = datetime.now()
        job.is_finished = form.is_job_finished.data
        db_sess.add(job)
        db_sess.commit()
        return redirect("/")
    return render_template('add_job.html', form=form)


@app.route('/delete_job/<job_id>', methods=['GET', 'POST'])
@login_required
def delete_job(job_id):
    db_session.global_init("db/mars.db")
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).filter(Jobs.id == int(job_id)).first()
    if (job and (flask_login.current_user.id == job.team_leader
                 or flask_login.current_user.id == 1)):
        db_session.global_init("db/mars.db")
        db_sess = db_session.create_session()
        job = db_sess.query(Jobs).filter(Jobs.id == int(job_id)).first()
        db_sess.delete(job)
        db_sess.commit()
    return redirect('/')


@app.route('/edit_job/<job_id>', methods=['GET', 'POST'])
@login_required
def edit_job(job_id):
    db_session.global_init("db/mars.db")
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).filter(Jobs.id == int(job_id)).first()
    if not job:
        return redirect('/')
    elif (flask_login.current_user.id == job.team_leader
          or flask_login.current_user.id == 1):
        print(flask_login.current_user.id, job.team_leader)
        form = AddingJobForm()
        if form.validate_on_submit():
            db_session.global_init("db/mars.db")
            db_sess = db_session.create_session()
            job = db_sess.query(Jobs).filter(Jobs.id == int(job_id)).first()
            job.job = form.job.data
            job.team_leader = form.team_leader_id.data
            job.work_size = form.work_size.data
            job.collaborators = form.collaborators.data
            job.start_date = datetime.now()
            job.is_finished = form.is_job_finished.data
            db_sess.commit()
            return redirect("/")
        return render_template('add_job.html', form=form)
    else:
        return redirect('/')


@app.route('/add_dep', methods=['GET', 'POST'])
@login_required
def adding_dep():
    form = AddingDepForm()
    if form.validate_on_submit():
        db_session.global_init("db/mars.db")
        db_sess = db_session.create_session()
        dep = Department()
        dep.title = form.title.data
        dep.chief = form.chief.data
        dep.members = form.members.data
        dep.email = form.email.data
        db_sess.add(dep)
        db_sess.commit()
        return redirect("/departments")
    return render_template('add_dep.html', form=form)


@app.route('/delete_dep/<dep_id>', methods=['GET', 'POST'])
@login_required
def delete_dep(dep_id):
    db_session.global_init("db/mars.db")
    db_sess = db_session.create_session()
    dep = db_sess.query(Department).filter(
        Department.id == int(dep_id)).first()
    if (dep and (flask_login.current_user.id == dep.chief
                 or flask_login.current_user.id == 1)):
        db_session.global_init("db/mars.db")
        db_sess = db_session.create_session()
        dep = db_sess.query(Department).filter(
            Department.id == int(dep_id)).first()
        db_sess.delete(dep)
        db_sess.commit()
    return redirect('/')


@app.route('/edit_dep/<dep_id>', methods=['GET', 'POST'])
@login_required
def edit_dep(dep_id):
    db_session.global_init("db/mars.db")
    db_sess = db_session.create_session()
    dep = db_sess.query(Department).filter(
        Department.id == int(dep_id)).first()
    if not dep:
        return redirect('/')
    elif (flask_login.current_user.id == dep.chief
          or flask_login.current_user.id == 1):
        form = AddingDepForm()
        if form.validate_on_submit():
            db_session.global_init("db/mars.db")
            db_sess = db_session.create_session()
            dep = db_sess.query(Department).filter(
                Department.id == int(dep_id)).first()
            dep.title = form.title.data
            dep.chief = form.chief.data
            dep.members = form.members.data
            dep.email = form.email.data
            db_sess.commit()
            return redirect("/")
        return render_template('add_dep.html', form=form)
    else:
        return redirect('/')


def main():
    db_session.global_init("db/mars.db")
    db_sess = db_session.create_session()
    user = db_sess.query(User).first()
    db_sess.add(user)
    db_sess.commit()
    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()


'''@app.route('/training/<prof>')


def training(prof):
    return render_template('training.html', prof=prof)'''

