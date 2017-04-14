import os

from nillu import app

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.instance_path, 'nillu.db')
DEBUG = True
SECRET_KEY = '\xbb\xda`\x19\xefP"\xf5\xca\xcc\xe6\xee\r\xdd\x8e\x91\x8d\xf4\xa4\xc0\xdc\xad\x90\x7f'
