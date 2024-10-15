import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login
from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Client(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    login: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    name: so.Mapped[str] = so.mapped_column(sa.String(256), index=True)
    surname: so.Mapped[str] = so.mapped_column(sa.String(256), index=True)
    work_age: so.Mapped[int] = so.mapped_column(sa.Integer(), index=True)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Client {self.login}>'

class Photo(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    employee_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('client.id'), nullable=False)
    path: so.Mapped[str] = so.mapped_column(sa.String(255), nullable=False)

    def __repr__(self):
        return f'<Photo {self.id}, Path: {self.path}>'

class ProcessedPhoto(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    employee_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('client.id'), nullable=False)
    path: so.Mapped[str] = so.mapped_column(sa.String(255), nullable=False)
    base_photo_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('photo.id'), nullable=False)
    num_of_defects: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=True)

    def __repr__(self):
        return f'<ProcessedPhoto {self.id}, Base Photo: {self.base_photo_id}, Defects: {self.num_of_defects}>'

@login.user_loader
def load_user(id):
    return db.session.get(Client, int(id))