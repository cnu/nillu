from flask import Flask
from flask_login import LoginManager

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('settings.py')

login_manager = LoginManager()
login_manager.init_app(app)

import nillu.views
import nillu.commands