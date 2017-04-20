import re

import bleach
from flask_heroku import Heroku
from jinja2 import evalcontextfilter, Markup, escape
from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flaskext.markdown import Markdown

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('settings.py')
mail = Mail(app)
heroku = Heroku(app)
markdown = Markdown(app, extensions=['nl2br'])

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message_category = "warning"

_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')


@app.template_filter()
def restrict_markdown(value):
    allowed_tags = ['a', 'b','em', 'i', 'li', 'ol', 'strong', 'ul', 'br']
    output = Markup(bleach.linkify(bleach.clean(value, tags=allowed_tags, strip=True)))
    return output


import nillu.views
import nillu.commands
