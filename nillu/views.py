import calendar
from collections import defaultdict

import datetime
from flask import flash, request, abort, redirect, render_template, url_for
from flask import render_template_string
from flask_mail import Message
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import and_

from nillu import app, mail, restrict_markdown
from nillu.database import db
from nillu.forms import LoginForm, UserAddForm, ChangePasswordForm
from nillu.models import User, Entry
from nillu.utils import is_safe_url, DateParseException, FutureDateException, parse_date


@app.route('/')
@login_required
def index():
    """Index view function"""
    return redirect(url_for('entry', date='today'))


def process_entries_query(entries):
    user_order = set()
    date_order = set()
    # {date: {user: []}}
    result = defaultdict(lambda: defaultdict(list))
    for e in entries:
        date = e.date
        user = e.user.name
        date_order.add(date)
        user_order.add(user)
        result[date][user].append(e)
    date_order = sorted(list(date_order))
    user_order = sorted(list(user_order))
    return result, date_order, user_order


def construct_email_text(result, date_order, user_order, date_str):
    subj_j2_tmpl = '''Backend Standup - {{ date }}'''
    body_j2_html_tmpl = '''
{% for date in date_order %}
<h2><a href="https://backend-nillu.herokuapp.com/entry/{{ date.year }}/{{ date.month }}/{{ date.day }}/">{{ date }}</a></h2>
    {% for user in user_order %}
    <h1>{{ user }}</h1>
        {% for entry in result[date][user] %}
        <h3>{{ entry.type|capitalize }}</h3>
        <p>{{ entry.text|markdown|restrict_markdown }}</p>
        {% endfor %}
    {% endfor %}
{% endfor %}

--
<p>This StandUp log entry was automatically generated by <a href="https://backend-nillu.herokuapp.com/">Nillu</a>.</p>
'''
    body_j2_text_tmpl = '''
Backend Standup
{% for date in date_order %}
## {{ date }}
{% for user in user_order %}
# {{ user }}
{% for entry in result[date][user] %}
### {{ entry.type }}
{{ entry.text }}
{% endfor %}
{% endfor %}
{% endfor %}

--
This StandUp log entry was automatically generated by Nillu.
'''
    final_str = render_template_string(body_j2_text_tmpl, date_order=date_order, user_order=user_order, result=result)
    final_html_str = render_template_string(body_j2_html_tmpl, date_order=date_order, user_order=user_order, result=result)
    subject = render_template_string(subj_j2_tmpl, date=date_str)
    return subject, final_str, final_html_str


def email_entries(entries, users, from_date, to_date):
    """given an entries record set, and list of users, send the email to all users.

    the from_date and to_date is needed to format the subject line correctly.
    """
    if from_date == to_date:
        date_str = from_date
    else:
        date_str = '{} to {}'.format(from_date, to_date)
    result, date_order, user_order = process_entries_query(entries=entries)
    subject, final_str, final_html_str = construct_email_text(result, date_order, user_order, date_str)

    developers = [u.email for u in users if u.role == 'developer']
    non_developers = [u.email for u in users if u.role == 'non-developer']
    msg = Message(subject=subject, sender='notifications@madstreetden.com',
                  recipients=developers, cc=non_developers,
                  body=final_str, html=final_html_str)
    mail.send(msg)


@app.route('/entry/')
@app.route('/entry/<path:date>/', methods=['GET', 'POST'])
@login_required
def entry(date=None):
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
        if request.method == 'POST':
            if request.form.get('edit').lower() == 'true':
                edit = True
            else:
                edit = False

            save_entry(form_items=request.form.items(), date_obj=date_obj, edit=edit)
            entries = Entry.query.filter_by(date=date_obj).order_by(Entry.date, Entry.user_id, Entry.type)
            users = User.query.all()
            if not edit:
                email_entries(entries, users, date_obj, date_obj)
            return redirect(url_for('entry', date=date))

        if date in ('today', 'yesterday'):
            return redirect(url_for('entry', date=date_obj.strftime('%Y/%m/%d')))

        if resolution == 'day':
            # Use only 1 day
            entries = Entry.query.filter_by(date=date_obj).order_by(Entry.date, Entry.user_id, Entry.type)
            users = User.query.filter_by(role='developer').order_by(User.name)
            entry_types = ('done', 'todo', 'blocking')
            end_date = date_obj
            if entries.count() == 0:
                return render_template('entry_edit.html', date=date, date_obj=date_obj, users=users,
                                       entry_types=entry_types, edit=False)
            else:
                if request.args.get('edit', 'false').lower() == 'true':
                    user_entry = defaultdict(dict)
                    for e in entries:
                        user_entry[e.user.name][e.type] = e
                    return render_template('entry_edit.html', date=date, date_obj=date_obj, users=users,
                                           entry_types=entry_types, user_entry=user_entry, edit=True)
        else:
            if resolution == 'month':
                _, num_days_in_month = calendar.monthrange(date_obj.year, date_obj.month)
                end_date = datetime.date(date_obj.year, date_obj.month, num_days_in_month)
            elif resolution == 'year':
                end_date = datetime.date(date_obj.year, 12, 31)
            elif resolution == 'custom':
                start_date = request.args.get('from')
                date_obj = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = request.args.get('to')
                end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
            entries = Entry.query.filter(and_(Entry.date >= date_obj, Entry.date <= end_date))
        result, date_order, user_order = process_entries_query(entries)
        return render_template('entry.html', result=result, date_order=date_order, user_order=user_order,
                               from_date=date_obj, to_date=end_date)
    except FutureDateException:
        flash("Great Scott! Your flux capacitor is broken.", 'warning')
        return redirect(url_for('entry', date='today'))
    except DateParseException:
        flash("Couldn't get entries for specified date.", 'danger')
        return redirect(url_for('entry', date='today'))


@app.route('/entry/last/<int:days>/')
@login_required
def entry_n_days(days):
    """Display the last N day's entries"""
    today = datetime.date.today()
    delta = datetime.timedelta(days=days)
    from_date = today - delta
    params = {'from': from_date, 'to': today}
    return redirect(url_for('entry', **params))


@app.route('/entry/email/', methods=['POST'])
@login_required
def entry_email():
    """given a from and to dates, email all the entries."""
    from_date = request.form['from']
    to_date = request.form['to']
    from_date = datetime.datetime.strptime(from_date, '%Y-%m-%d').date()
    to_date = datetime.datetime.strptime(to_date, '%Y-%m-%d').date()
    entries = Entry.query.filter(and_(Entry.date >= from_date, Entry.date <= to_date))
    users = User.query.all()
    email_entries(entries, users, from_date, to_date)

    next = request.form.get('next')
    # is_safe_url should check if the url is safe for redirects.
    # See http://flask.pocoo.org/snippets/62/ for an example.
    if not is_safe_url(next):
        return abort(400)
    return redirect(next or url_for('index'))


def save_entry(form_items, date_obj, edit):
    """save all entries for a date from a list of form items"""
    for k, v in form_items:
        if '_' not in k:
            # dont want to try splitting the "edit" hidden input tag.
            # TODO: prepend the form text areas with a diff prefix
            continue
        user_id, entry_type = k.split('_')
        user = User.get(user_id=user_id)
        e = Entry.query.filter_by(user=user, date=date_obj, type=entry_type).first()
        if edit and e:
            e.text = v
        else:
            e = Entry(text=v, entry_type=entry_type, user=user, date=date_obj)
        db.session.add(e)
    db.session.commit()


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


@app.route('/user/add/', methods=['GET', 'POST'])
@login_required
def user_add():
    form = UserAddForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = User.get_by_email(form.email.data)
        if user:
            flash('User with email:{} already exists'.format(form.email.data), 'danger')
            return redirect(url_for('user_add'))
        user = User(name=form.name.data, password=form.password.data, email=form.email.data, role=form.role.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('user', user_id=user.id))
    else:
        return render_template('user_add.html', form=form)


@app.route('/user/')
@app.route('/user/<int:user_id>/')
@login_required
def user(user_id=None):
    if user_id is None:
        users = User.query.order_by('name')
        return render_template('users.html', users=users)
    else:
        user_obj = User.query.filter_by(id=user_id).first_or_404()
        return render_template('user.html', user=user_obj)


@app.route('/password/change/', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        changed = current_user.update_password(new_password=form.password.data)
        if changed:
            logout_user()
            flash(u'Your password has been changed successfully.', 'success')
            return redirect(url_for('index'))
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'danger')
    return render_template('change_password.html', form=form)
