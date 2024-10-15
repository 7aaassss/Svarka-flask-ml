from flask_sqlalchemy import SQLAlchemy
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin



class Client(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(256))
    name = db.Column(db.String(256), index=True)
    surname = db.Column(db.String(256), index=True)
    work_age = db.Column(db.Integer, index=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Client {self.login}>'

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    path = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<Photo {self.id}, Path: {self.path}>'

class ProcessedPhoto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    path = db.Column(db.String(255), nullable=False)
    base_photo_id = db.Column(db.Integer, db.ForeignKey('photo.id'), nullable=False)
    num_of_defects = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f'<ProcessedPhoto {self.id}, Base Photo: {self.base_photo_id}, Defects: {self.num_of_defects}>'

@login.user_loader
def load_user(id):
    return db.session.get(Client, int(id))
