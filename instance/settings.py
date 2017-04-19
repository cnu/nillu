import os

from nillu import app

is_heroku = os.environ.get('IS_HEROKU', None)

if is_heroku:
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS')
    if MAIL_USE_TLS.lower() == 'true':
        MAIL_USE_TLS = True
    else:
        MAIL_USE_TLS = False
    MAIL_PORT = int(os.environ.get('MAIL_PORT'))
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    SECRET_KEY = os.environ.get('SECRET_KEY')
else:
    DEBUG = True
    SECRET_KEY = '\xbb\xda`\x19\xefP"\xf5\xca\xcc\xe6\xee\r\xdd\x8e\x91\x8d\xf4\xa4\xc0\xdc\xad\x90\x7f'
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.instance_path, 'nillu.db')
    SQLALCHEMY_DATABASE_URI = 'postgresql://nilluuser:foobar@localhost/nilludb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
