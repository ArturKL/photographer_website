from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired, Length, Email
from wtforms.fields.html5 import EmailField, IntegerField, TelField


class RegisterForm(FlaskForm):
    email = EmailField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторить пароль', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    age = IntegerField('Возраст')
    submit = SubmitField('Регистрация')


class LoginForm(FlaskForm):
    email = EmailField('E-mail', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить')
    submit = SubmitField('Войти')


class ReviewForm(FlaskForm):
    rating = SelectField('Оценка', choices=[('1', 1), ('2', 2), ('3', 3), ('4', 4), ('5', 5)][::-1], validators=[
        DataRequired()])
    content = TextAreaField('Отзыв', validators=[Length(max=500, message='Максимальный размер отзыва - 500 символов')])
    submit = SubmitField('Оставить отзыв')


class AlbumForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    photos = MultipleFileField('Загрузить фото')
    submit = SubmitField('Сохранить')


class BookingForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    tel = TelField('Номер телефона', validators=[DataRequired()])
    type = SelectField('Тип фотосессии', choices=[('Минимальная', 'Минимальная'),
                                                  ('Оптимальная', 'Оптимальная'),
                                                  ('Премиальная', 'Премиальная')], validators=[DataRequired()])
    date = DateField('Дата')
    content = TextAreaField('Сообщение')
    submit = SubmitField('Отправить')
