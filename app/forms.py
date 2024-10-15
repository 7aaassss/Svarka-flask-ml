from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, FileField
from wtforms.validators import DataRequired, ValidationError
from app import db
from app.models import Client
from sqlalchemy import select

class LoginForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    recaptcha = RecaptchaField()
    submit = SubmitField('Sign In')


class RegForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    submit = SubmitField('Create account')

    def validate_username(self, login):
        client = db.session.execute(select(Client).where(Client.login == login.data)).scalar_one_or_none()
        if client is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        client = db.session.execute(select(Client).where(Client.email == email.data)).scalar_one_or_none()
        if client is not None:
            raise ValidationError('Please use a different email address.')

class ImageForm(FlaskForm):
    file = FileField('File', validators=[DataRequired()])
    methodSelect = SelectField('Method', choices=[('DETR', 'DETR'), ('YOLO', 'YOLO')], validators=[DataRequired()])
    submit = SubmitField('Upload')
