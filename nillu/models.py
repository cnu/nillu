from flask_bcrypt import Bcrypt
from flask_login import UserMixin
from sqlalchemy.sql import func

from nillu import app, login_manager
from nillu.database import db

bcrypt = Bcrypt(app)


class User(db.Model, UserMixin):
    """User model class

    Uses flask_login's UserMixin to implement default properties and methods
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    role = db.Column(db.Enum('developer', 'non-developer', name='user_roles'))

    def __init__(self, name, password, email, role):
        self.name = name
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        self.email = email
        self.role = role

    def __repr__(self):
        return '<User {}>'.format(self.name)

    @classmethod
    def get(cls, user_id):
        """Get a user object from a user_id"""
        u = cls.query.get(user_id)
        return u

    @classmethod
    def get_by_email(cls, email):
        """Get a user object from an email address"""
        q = cls.query.filter_by(email=email)
        return q.one_or_none()

    def update_password(self, new_password):
        """Update the password of a user with a new_password"""
        self.password = bcrypt.generate_password_hash(new_password).decode('utf-8')

    def check_password(self, password):
        """Check if the user's password matches with the given password"""
        return bcrypt.check_password_hash(self.password, password)


@login_manager.user_loader
def load_user(user_id):
    """Flask Login's user_loader function"""
    return User.get(user_id)


class Entry(db.Model):
    """Entry model class

    Each user has three rows on entries for a date - done, todo, blocking.
    """
    __tablename__ = 'entries'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String)
    type = db.Column(db.Enum('done', 'todo', 'blocking', name='entry_types'))
    date = db.Column(db.Date, server_default=func.current_date())
    time_created = db.Column(db.DateTime, server_default=func.current_timestamp())
    time_updated = db.Column(db.DateTime, onupdate=func.current_timestamp())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref=db.backref('entries', lazy='dynamic'))

    __table_args__ = (db.UniqueConstraint('type', 'user_id', 'date', name='_type_user_date_uc'), )

    def __init__(self, text, entry_type, user, date=None):
        self.text = text
        self.type = entry_type
        self.user = user
        if date:
            self.date = date

    def __repr__(self):
        return '<Entry {}:{}:{}'.format(self.user.name, self.type, self.text[:50])
