from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import Email, DataRequired, Length,EqualTo


class LoginForm(FlaskForm):
    email=StringField("Email: ", validators=[Email("Некорректный email")])
    psw=PasswordField("Пароль: ", validators=[DataRequired(), Length(min=7, max=30, message="Пароль должен содержать не менее 7 символов")])
    remember=BooleanField("Запомнить", default=False)
    submit=SubmitField("Войти")


class RegisterForm(FlaskForm):
    name = StringField("Имя: ", validators=[Length(min=4, max=100, message="Имя должно быть от 4 до 100 символов")])
    email = StringField("Email: ", validators=[Email("Некорректный email")])
    psw = PasswordField("Пароль: ", validators=[DataRequired(),
                                                Length(min=7, max=30,
                                                       message="Пароль должен быть от 7 до 30 символов")])

    psw2 = PasswordField("Повтор пароля: ", validators=[DataRequired(), EqualTo('psw', message="Пароли не совпадают")])
    submit = SubmitField("Регистрация")

