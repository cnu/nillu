from flask import Flask
from flask_login import LoginManager

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('settings.py')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message_category = "warning"


import nillu.views
import nillu.commands