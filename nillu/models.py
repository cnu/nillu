from sqlalchemy.sql import func
from nillu.database import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True)
    role = db.Column(db.Enum('developer', 'non-developer'))

    def __init__(self, name=None, email=None):
        self.name = name
        self.email = email

    def __repr__(self):
        return '<User {}>'.format(self.name)


class Entry(db.Model):
    __tablename__ = 'entries'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String)
    type = db.Column(db.Enum('todo', 'done', 'blocking'))
    date = db.Column(db.Date, server_default=func.current_date())
    time_created = db.Column(db.DateTime, server_default=func.current_timestamp())
    time_updated = db.Column(db.DateTime, onupdate=func.current_timestamp())
    user = db.relationship('User', backref=db.backref('entries', lazy='dynamic'))

    def __init__(self, text, entry_type, user):
        self.text = text
        self.type = entry_type
        self.user = user

    def __repr__(self):
        return '<Entry {}:{}:{}'.format(self.user.name, self.type, self.text[:50])
