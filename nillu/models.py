import datetime
from sqlalchemy import Column, Integer, String
from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from nillu.database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(120), unique=True)
    role = Column(Enum('developer', 'non-developer'))

    def __init__(self, name=None, email=None):
        self.name = name
        self.email = email

    def __repr__(self):
        return '<User {}>'.format(self.name)


class Entry(Base):
    __tablename__ = 'entries'
    id = Column(Integer, primary_key=True)
    text = Column(String)
    type = Column(Enum('todo', 'done', 'blocking'))
    date = Column(Date, server_default=func.current_date())
    time_created = Column(DateTime, server_default=func.current_timestamp())
    time_updated = Column(DateTime, onupdate=func.current_timestamp())
    user = relationship('User', back_populates='entries')

    def __init__(self, text, entry_type, user):
        self.text = text
        self.type = entry_type
        self.user = user

    def __repr__(self):
        return '<Entry {}:{}:{}'.format(self.user.name, self.type, self.text[:50])
