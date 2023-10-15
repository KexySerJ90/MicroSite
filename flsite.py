from flask import Flask, render_template, url_for, request, flash, session, redirect, abort, g, make_response
import os
import sqlite3
from FDataBase import FDataBase
from UserLogin import UserLogin
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, login_required, logout_user,current_user
from forms import LoginForm,RegisterForm
from admin.admin import admin



DATABASE = '/tmp/fslite.db'
UPLOAD_FOLDER = 'static/images/'
SECRET_KEY = 'asgasgasgasgasgasgkjabjk8y8'
MAX_CONTENT_LENGTH=1024*1024
dbase = None

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'fslite.db')))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.register_blueprint(admin, url_prefix="/admin")
login_manager=LoginManager(app)
login_manager.login_view="login"
login_manager.login_message="Авторизируйтесь для доступа к закрытым страницам"
login_manager.login_message_category="success"

@login_manager.user_loader
def load_user(user_id):
    print("load user")
    return UserLogin().fromDB(user_id,dbase)


def connect_db():
    """функция для установления соединения с базой данных SQLite."""
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    """Вспомогательная функция для создания таблиц БД"""
    db = connect_db()
    with app.open_resource('sq_db.sql') as f:
        db.cursor().executescript(f.read().decode('utf-8'))
    db.commit()
    db.close()


def get_db():
    '''Соединение с БД'''
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db



@app.before_request
def before_request():
    """Установите соединение с БД перед выполнением запроса"""
    global dbase
    db = get_db()
    dbase = FDataBase(db)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.route('/')
def index():
    return render_template('index.html', menu=dbase.getMenu(), posts=dbase.getPostsAnounce())


@app.route('/add_post', methods=["POST", "GET"])
@login_required
def addPost():
    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['post']) > 10:
            res = dbase.addPost(request.form['name'], request.form['post'], request.form['url'])
            if not res:
                flash('Ошибка добавления статьи', category='error')
            else:
                flash('Статья добавлена успешно', category='success')
        else:
            flash('Ошибка добавления статьи', category='error')
    return render_template('add_post.html', menu=dbase.getMenu(), title="Добавление статьи")


@app.route("/post/<alias>")
def showPost(alias):
    title, post = dbase.getPost(alias)
    if not title:
        abort(404)
    return render_template('post.html', menu=dbase.getMenu(), title=title, post=post)


# Маршрут для страницы авторизации
@app.route("/login", methods=["POST", "GET"])
def login():
    # Если пользователь уже авторизован, перенаправляем его на профиль
    if current_user.is_authenticated:
        return redirect(url_for("profile"))
    form=LoginForm()
    if form.validate_on_submit():
        user = dbase.getUserByEmail(form.email.data)
        if user and check_password_hash(user["psw"], form.psw.data):
            userlogin = UserLogin().create(user)
            rm = form.remember.data
            login_user(userlogin, remember=rm)
            return redirect(request.args.get("next") or url_for("profile"))
        flash("Неверная пара логин/пароль", "error")

    return render_template("login.html", menu=dbase.getMenu(), title="Авторизация", form=form)


# Маршрут для страницы регистрации
@app.route("/register", methods=["POST", "GET"])
def register():
    form=RegisterForm()
    if form.validate_on_submit():
        hash = generate_password_hash(form.psw.data)
        res = dbase.addUser(form.name.data, form.email.data, hash)
        if res:
            flash("Вы успешно зарегистрированы", "success")
            return redirect(url_for("login"))
    # Если метод запроса GET, отображаем страницу регистрации
    return render_template("register.html", menu=dbase.getMenu(), title="Регистрация", form=form)

# Маршрут для выхода пользователя из аккаунта
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('login'))

# Маршрут для страницы профиля пользователя
@app.route('/profile')
@login_required
def profile():
    return render_template("profile.html", menu=dbase.getMenu(), title="Профиль")

# Маршрут для получения аватара пользователя
@app.route('/userava')
@login_required
def userava():
    img=current_user.getAvatar(app)
    if not img:
        return ""
    h=make_response(img)
    h.headers["Content-Type"]="image/*"
    return h


@app.route('/upload', methods=["POST", "GET"])
@login_required
def upload():
    if request.method=="POST":
        file=request.files['file']
        if file and current_user.verifyExt(file.filename):
            try:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                img=url_for('static', filename='images/' + filename)
                res=dbase.updateUserAvatar(img, current_user.get_id())
                if not res:
                    flash("Ошибка обновления аватара", "error")
                flash("Аватар обновлен", "success")
            except FileNotFoundError as e:
                flash("Ошибка чтения файлов", "error")
        # else:
            # flash("Неподдерживаемый формат файла или аватар уже загружен", "error")

    return redirect(url_for("profile"))


if __name__ == '__main__':
    app.run(debug=True)
