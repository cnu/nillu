from collections import defaultdict
from flask import flash, request, abort, redirect, render_template, url_for
from flask_login import login_user, login_required, logout_user

from nillu import app
from nillu.database import db
from nillu.forms import LoginForm
from nillu.models import User, Entry
from nillu.utils import is_safe_url, DateParseException, FutureDateException, parse_date


@app.route('/')
@login_required
def index():
    """Index view function"""
    return redirect(url_for('entry', date='today'))


@app.route('/entry/<path:date>/edit/', methods=['GET', 'POST'])
@login_required
def entry_edit(date):
    date_obj, resolution = parse_date(date)
    if request.method == 'POST':
        for k, v in request.form.items():
            user_id, entry_type = k.split('_')
            user = User.get(user_id=user_id)
            e = Entry(text=v, entry_type=entry_type, user=user, date=date_obj)
            db.session.add(e)
        db.session.commit()
        return redirect(url_for('entry', date=date))
    else:
        users = User.query.filter_by(role='developer').order_by(User.name)
        entry_types = ('done', 'todo', 'blocking')
        return render_template('entry_edit.html', date=date, date_obj=date_obj, users=users, entry_types=entry_types)


@app.route('/entry/<path:date>/')
@login_required
def entry(date):
    """Display the entries for a particular date

    :param date: the date for which to get the entries

    TODO:
    date could be just an year, year/month or year/month/date
    Eg: "2017" or "2017/04" or "2017/04/14"
    Based on which format is used, the corresponding entries for the
    time period is fetched and displayed.
    """
    try:
        date_obj, resolution = parse_date(date)
        if date in ('today', 'yesterday'):
            return redirect(url_for('entry', date=date_obj.strftime('%Y/%m/%d')))

        if resolution == 'day':
            # Use only 1 day
            entries = Entry.query.filter_by(date=date_obj).order_by(Entry.date, Entry.user_id, Entry.type)
            if entries.count() == 0:
                return redirect(url_for('entry_edit', date=date_obj.strftime('%Y/%m/%d')))
            user_order = set()
            date_order = set()
            result = defaultdict(lambda: defaultdict(list))
            for e in entries:
                date = e.date
                user = e.user.name
                date_order.add(date)
                user_order.add(user)
                result[date][user].append(e)
            date_order = sorted(list(date_order))
            user_order = sorted(list(user_order))
            return render_template('entry.html', result=result, date_order=date_order, user_order=user_order)
    except FutureDateException:
        flash("Great Scott! Your flux capacitor is broken.", 'warning')
        return redirect(url_for('entry', date='today'))
    except DateParseException:
        flash("Couldn't get entries for specified date.", 'danger')
        return redirect(url_for('entry', date='today'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login view function

    accepts both GET and POST to display the login page and accept the login info
    """
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = User.get_by_email(form.email.data)
        # Login and validate the user.
        # user should be an instance of your `User` class
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
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


@app.route("/logout")
@login_required
def logout():
    """Logout the user and redirect back to the login page."""
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect('login')