from flask import flash, request, abort, redirect, render_template, url_for
from flask_login import login_user, login_required

from nillu import app
from nillu.forms import LoginForm
from nillu.models import User
from nillu.utils import is_safe_url


@app.route('/')
@login_required
def index():
    return 'Hello World!'


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = User.get_by_email(form.email.data)
        # Login and validate the user.
        # user should be an instance of your `User` class
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Logged in Successfully.', 'success')

            next = request.args.get('next')
            # is_safe_url should check if the url is safe for redirects.
            # See http://flask.pocoo.org/snippets/62/ for an example.
            if not is_safe_url(next):
                return abort(400)
            return redirect(next or url_for('index'))
        else:
            flash('Wrong email/password.', 'danger')
    return render_template('login.html', form=form)
