from flask_login import login_user, current_user, login_required, logout_user
from app import app, db, login
from app.forms import LoginForm, RegForm, ImageForm
from app.models import Client, Photo, ProcessedPhoto
import sqlalchemy as sa
from urllib.parse import urlsplit
import os
from flask import request, flash, render_template, jsonify, url_for, redirect
from werkzeug.utils import secure_filename
from app import app, ml
from app.captcha import verify_recaptcha
import uuid
import time
from math import ceil
from sqlalchemy import asc, desc
from config import Config

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()

    if request.method == 'POST':
        captcha_response = request.form.get('g-recaptcha-response')
        if verify_recaptcha(captcha_response)['success']:

            client = db.session.scalar(
                sa.select(Client).where(Client.login == form.login.data))

            if client is None or not client.check_password(form.password.data):
                flash('Неверное имя пользователя или пароль', 'error')
                return redirect(url_for('login'))

            login_user(client, remember=form.remember_me.data)

            next_page = request.args.get('next')
            if not next_page or urlsplit(next_page).netloc != '':
                next_page = url_for('home')
            return redirect(next_page)
        else:
            flash('Ошибка капчи!', 'error')
            return redirect(url_for('login'))

    return render_template('login.html', form=form)


@app.route('/reg', methods=['POST', 'GET'])
def reg():
    form = RegForm()
    if form.validate_on_submit():
        client = Client(login=form.login.data, email=form.email.data, name=form.name.data, surname=form.surname.data, work_age=0)
        client.set_password(form.password.data)
        db.session.add(client)
        db.session.commit()
        flash('Registration successful!')
        return redirect(url_for('login'))
    return render_template('reg.html', title='Register', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route('/all_users', methods=['GET'])
def all_users():
    all_users = db.session.query(Client)
    response = [user.login for user in all_users]
    return jsonify(response)


@app.route('/detection', methods=['POST', 'GET'])
@login_required
def detection():
    form = ImageForm()
    return render_template('try.html', form=form)



ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def uid():
        return str(uuid.uuid4())

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploads', methods=['POST', 'GET'])
def upload_pic():
    form = ImageForm()
    if form.validate_on_submit():
        if 'file' not in request.files:
            flash('Файл не был выбран!', 'error')
            return jsonify({'status': 'error', 'message': 'Файл не был выбран!'})

        file = request.files['file']

        if file.filename == '':
            flash('Имя файла не указано!', 'error')
            return jsonify({'status': 'error', 'message': 'Имя файла не указано!'})

        if file and allowed_file(file.filename):

            user_directory = os.path.join(os.getcwd(), 'app', 'static', str(current_user.id))
            os.makedirs(user_directory, exist_ok=True)

            filename = uid() + file.filename[-4:]
            filepath = os.path.join(user_directory, filename)
            file.save(filepath)

            new_photo = Photo(employee_id=current_user.id, path=os.path.join(str(current_user.id), filename).replace('\\', '/')) # добавляем в бд фото отправленное первым
            db.session.add(new_photo)
            db.session.commit()

            selected_method = request.form['methodSelect']
            if selected_method == 'DETR':
                    obr, num_boxes = ml.show_detected_image(filepath, 'd', current_user.id)
            elif selected_method == 'YOLO':
                    obr, num_boxes = ml.show_detected_image(filepath, 'y', current_user.id)

            new_processed_photo = ProcessedPhoto(
                employee_id=current_user.id,
                path=obr.replace('\\', '/'),
                base_photo_id=new_photo.id,
                num_of_defects=num_boxes
            )
            db.session.add(new_processed_photo)
            db.session.commit()

            return render_template('image.html', filename=obr.replace('\\', '/'))


        flash('Недопустимый тип файла!', 'error')
        return jsonify({'status': 'error', 'message': 'Bad type!'})

    flash('Ошибка валидации формы!', 'error')
    return jsonify({'status': 'error', 'message': 'Smth wrong with form!'})


@app.route('/leaderboard', methods=['GET'])
def leaderboard():
    employees = Client.query.all()
    employees_data = []

    for employee in employees:
        # количество загруженных фотографий сотрудником
        total_photos_uploaded = Photo.query.filter_by(employee_id=employee.id).count()

        # количество обработанных фотографий
        processed_photos_count = ProcessedPhoto.query.filter_by(employee_id=employee.id).count()

        # проценты обработанных фотографий
        percentage = (processed_photos_count / total_photos_uploaded) * 100 if total_photos_uploaded > 0 else 0

        employee_dict = {
            'id': employee.id,
            'name': employee.name,
            'surname': employee.surname,
            'post': employee.work_age,
            'total_photos_uploaded': total_photos_uploaded,
            'percentage': percentage
        }

        employees_data.append(employee_dict)

    return render_template('leaderboard.html', employees=employees_data)


@app.route("/showmyphotos")
@login_required
def showmyphotos():
    my_photos = Photo.query.filter_by(employee_id=current_user.id).all()
    my_proc_photos = ProcessedPhoto.query.filter_by(employee_id=current_user.id).all()


    photos_list = [{'id': photo.id, 'path': photo.path} for photo in my_photos]
    processed_photos_list = [{'id': proc_photo.id, 'path': proc_photo.path} for proc_photo in my_proc_photos]

    pairs = []
    for photo in photos_list:
        processed_photo = next((proc for proc in processed_photos_list if proc['id'] == photo['id']), None)
        pairs.append((photo, processed_photo))

    return render_template('myimages.html', pairs=pairs)


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        if request.form.get('login'):
            login = request.form.get("login")
            current_user.login = login
        if request.form.get('email'):
            email = request.form.get("email")
            current_user.email = email

        db.session.commit()

        flash("Настройки обновлены", "success")
        return redirect(url_for("settings"))

    return render_template("settings.html")

@app.route("/change_password", methods=["POST"])
@login_required
def change_password():
    old_password = request.form.get("old_password")
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")


    if not current_user.check_password(old_password):
        flash("Неверный старый пароль", "danger")
        return redirect(url_for("settings"))


    if new_password != confirm_password:
        flash("Пароли не совпадают", "danger")
        return redirect(url_for("settings"))


    current_user.set_password(new_password)
    db.session.commit()
    flash("Пароль успешно изменен", "success")
    return redirect(url_for("settings"))


@app.route('/users/<int:id>', methods=['GET']) # получение объекта по ID
def get_user(id):
    user = db.session.query(Client).get(id)

    if user is None:
        return jsonify({'error': 'User not found'}), 404

    user_info = {
        'id': user.id,
        'login': user.login,
        'email': user.email,
        'name': user.name,
        'surname': user.surname,
        'work_age': user.work_age
    }

    return jsonify(user_info), 200


@app.route('/photo/<int:id>', methods=['GET']) # получение объекта по ID
def get_photo(id):
    photo = db.session.query(Photo).get(id)

    if photo is None:
        return jsonify({'error': 'Photo not found'}), 404

    photo_info = {
        'id': photo.id,
        'employee_id': photo.employee_id,
        'path': photo.path
    }

    return jsonify(photo_info), 200


@app.route('/photo/<int:id>', methods=['DELETE']) # удаление элемента по ID
@login_required
def delete_photo(id):
    photo = db.session.query(Photo).get(id)

    if photo is None:
        return jsonify({'error': 'Photo not found'}), 404


    db.session.delete(photo)
    db.session.commit()

    return jsonify({'message': 'Photo deleted successfully'}), 200


@app.route('/all_photos', methods=['GET'])
def all_photos():
    # параметры запроса
    sort_by = request.args.get('sort_by', 'id')  #по умолчанию сортируем по 'id'
    order = request.args.get('order', 'asc')  #asc (по возрастанию) или desc (по убыванию)
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))  #по умолчанию 10
    filter_by_employee = request.args.get('employee_id')  # фильтрация по сотруднику

    try:
        # базовый запрос
        query = db.session.query(Photo)

        # фильтрация по employee_id
        if filter_by_employee:
            query = query.filter(Photo.employee_id == filter_by_employee)

        # сортировка
        if order == 'asc':
            query = query.order_by(asc(getattr(Photo, sort_by)))
        else:
            query = query.order_by(desc(getattr(Photo, sort_by)))

        total_photos = query.count()  # количество записей
        query = query.limit(per_page).offset((page - 1) * per_page)  # пагинация по номеру страницы и размеру

        photos = query.all()  # выполнение запроса

        # формирование ответа
        response = {
            'photos': [{'path': photo.path, 'employee_id': photo.employee_id} for photo in photos],
            'pagination': {
                'total_photos': total_photos,
                'current_page': page,
                'per_page': per_page,
                'total_pages': ceil(total_photos / per_page)
            }
        }
        return jsonify(response), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

