from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, AnyOf, EqualTo


class LoginForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=True)


class UserAddForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])
    role = StringField('role', validators=[DataRequired(),
                                           AnyOf(values=['developer', 'non-developer'])
                                           ])


class ChangePasswordForm(FlaskForm):
    password = PasswordField('password', validators=[DataRequired(),
                                                     EqualTo('confirm_password', message='Passwords do not match')])
    confirm_password = PasswordField('confirm_password')