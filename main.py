from flask import Flask, render_template, url_for, redirect, request, flash
from flask_restful import abort, Api, Resource, reqparse
from data import db_session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from data.users import User
from data.reviews import Review
from data.albums import Album
from data.booking import Booking
from data.forms import *
import datetime
from reviews_resourses import ReviewsResource, ReviewsListResource
from transliterate import translit
import os
import shutil

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'randomstring'

login_manager = LoginManager()
login_manager.init_app(app)


def ru_to_en(text):
    trans = translit(text, 'ru', reversed=True)
    trans = trans.replace(' ', '-')
    trans = trans.replace('\'', '').lower()
    return trans


def get_albums():
    session = db_session.create_session()
    list_albums = session.query(Album).all()
    return list_albums


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/')
def main_page():
    return render_template('main_page.html', title='Главная', albums=get_albums())


@app.route('/feedback')
def feedback():
    session = db_session.create_session()
    reviews = session.query(Review).all()[::-1]
    return render_template('feedback.html', title='Отзывы', reviews=reviews, albums=get_albums())


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form,
                                   message='Пароли не совпадают', albums=get_albums())
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message='Пользователь с таким email уже существует', albums=get_albums())
        user = User()
        user.email = form.email.data
        user.set_password(form.password.data)
        user.name = form.name.data
        user.surname = form.surname.data
        user.age = form.age.data
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form, albums=get_albums())


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect('/')
        return render_template('login.html', title='Вход', form=form,
                               message='Неверный логин или пароль', albums=get_albums())
    return render_template('login.html', title='Вход', form=form, albums=get_albums())


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@app.route('/review_form', methods=['GET', 'POST'])
def review_form():
    form = ReviewForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        review = Review()
        review.user_id = current_user.id
        review.user_name = current_user.name
        review.user_surname = current_user.surname
        review.rating = form.rating.data
        review.content = form.content.data
        review.date = datetime.date.today()
        session.add(review)
        session.commit()
        flash('Успех')
        return redirect('/feedback')
    else:
        return render_template('review_form.html', form=form, albums=get_albums())


@app.route('/review/edit/<int:id>', methods=['GET', 'POST'])
def edit_review(id):
    form = ReviewForm()
    session = db_session.create_session()
    review = session.query(Review).filter(Review.id == id, Review.user_id == current_user.id).first()
    if not review:
        abort(404)
    if form.validate_on_submit():
        review.rating = form.rating.data
        review.content = form.content.data
        session.commit()
        flash('Успех')
        return redirect('/feedback')
    else:
        form.rating.data = review.rating
        form.content.data = review.content
        return render_template('review_form.html', title='Изменить отзыв', form=form, albums=get_albums())


@app.route('/review/delete/<int:id>', methods=['GET', 'POST'])
def delete_review(id):
    session = db_session.create_session()
    review = session.query(Review).filter(Review.id == id,
                                         (Review.user_id == current_user.id) | (current_user.id == 1)).first()
    if review:
        session.delete(review)
        session.commit()
        flash('Успех')
        return redirect('/feedback')
    else:
        return render_template('404.html', title='Ошибка 404', albums=get_albums())


@app.route('/albums/<album_name>')
def albums(album_name):
    session = db_session.create_session()
    album = session.query(Album).filter(Album.translit_name == album_name).first()
    if album:
        return render_template('album_view.html', title=album.name, album=album, albums=get_albums())
    else:
        abort(404)


@app.route('/albums/upload', methods=['GET', 'POST'])
def upload():
    if current_user.is_authenticated and  current_user.id == 1:
        form = AlbumForm()
        session = db_session.create_session()
        if form.validate_on_submit():
            album = session.query(Album).filter(Album.name == form.name.data).first()
            if album:
                return render_template('album_form.html', title='Загрузить альбом',
                                       form=form, message='Такой альбом уже существует', albums=get_albums())
            album = Album()
            album.name = form.name.data
            album.translit_name = ru_to_en(album.name)
            album.lenght = len(form.photos.data)
            try:
                os.mkdir(f'static/albums/{album.translit_name}')
            except FileExistsError:
                return render_template('album_form.html', title='Загрузить альбом',
                                       form=form, message='Альбом с таким названием уже существует', albums=get_albums())
            for i, file in enumerate(form.photos.data):
                file.save(os.path.join(f'static/albums/{album.translit_name}',  f'{i}.jpg'))
            session.add(album)
            session.commit()
            flash('Успех')
            return redirect(f'/albums/{album.translit_name}')
        return render_template('album_form.html', title='Загрузить альбом', form=form, albums=get_albums())
    abort(404)


@app.route('/albums/edit/<name>', methods=['GET', 'POST'])
def edit_album(name):
    if current_user.is_authenticated and current_user.id == 1:
        form = AlbumForm()
        session = db_session.create_session()
        album = session.query(Album).filter(Album.translit_name == name).first()
        if not album:
            abort(404)
        if form.validate_on_submit():
            album.name = form.name.data
            for i, file in enumerate(form.photos.data, start=album.lenght):
                file.save(os.path.join(f'static/albums/{album.translit_name}', f'{i}.jpg'))
            album.lenght += len(form.photos.data)
            session.commit()
            flash('Успех')
            return redirect(f'/albums/{name}')
        form.name.data = album.name
        return render_template('album_form.html', title='Редактировать альбом', form=form, albums=get_albums())
    abort(404)


@app.route('/albums/delete/<name>')
def delete_album(name):
    if current_user.is_authenticated and current_user.id == 1:
        session = db_session.create_session()
        album = session.query(Album).filter(Album.translit_name == name).first()
        if album:
            shutil.rmtree(os.path.join('static/albums', name))
            session.delete(album)
            session.commit()
            flash('Успех')
            return redirect('/')
    abort(404)


@app.route('/pricelist', methods=['GET', 'POST'])
def booking():
    session = db_session.create_session()
    form = BookingForm()
    if form.validate_on_submit():
        book = Booking()
        book.name = form.name.data
        book.surname = form.surname.data
        book.tel = form.tel.data
        book.type = form.type.data
        book.date = form.date.data
        book.content = form.content.data
        session.add(book)
        session.commit()
        flash('Успешно отправлено')
        return redirect('/pricelist')
    if current_user.is_authenticated and current_user.id == 1:
        books = session.query(Booking).all()[::-1]
        return render_template('booking.html', title='Услуги и цены', books=books, albums=get_albums())
    return render_template('booking.html', title='Услуги и цены', form=form, albums=get_albums())


@app.route('/booking/delete/<int:id>')
def book_delete(id):
    if current_user.is_authenticated and current_user.id == 1:
        session = db_session.create_session()
        book = session.query(Booking).filter(Booking.id == id).first()
        session.delete(book)
        session.commit()
        flash('Успех')
        return redirect('/pricelist')
    abort(404)


@app.route('/about')
def about():
    return render_template('about.html', title='Обо мне', albums=get_albums())


@app.route('/contacts')
def contacts():
    return render_template('contacts.html', title='Контакты', albums=get_albums())


def feel_db():
    session = db_session.create_session()
    for i in range(1, 6):
        review = Review()
        review.user_id = 1
        review.user_name = session.query(User).filter(User.id == 1).first().name
        review.user_surname = session.query(User).filter(User.id == 1).first().surname
        review.rating = i
        review.content = 'Lorem ipsum dolor sit amet consectetur, adipisicing elit. Quisquam ipsam fugiat natus ' \
                         'tempora molestias illo quis provident quod, maiores doloremque?'
        review.date = datetime.date.today()
        session.add(review)
    session.commit()


if __name__ == '__main__':
    app.template_folder = 'template'
    db_session.global_init('db/main_db.sqlite')
    api.add_resource(ReviewsResource, '/api/review/<int:id>')
    api.add_resource(ReviewsListResource, '/api/reviews/<int:rating>')
    app.run(port=5000, host='127.0.0.1')