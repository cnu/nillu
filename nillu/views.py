import calendar
from collections import defaultdict

import datetime
from flask import flash, request, abort, redirect, render_template, url_for
from flask_mail import Message
from flask_login import login_user, login_required, logout_user
from sqlalchemy import and_

from nillu import app, mail
from nillu.database import db
from nillu.forms import LoginForm
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


def construct_email_text(result):
    subj_tmpl = '''Backend Standup - {}'''
    final_tmpl = '''
Backend Standup - {}
{}
    '''
    user_entry_tmpl = '''
{}
Done:
{}
Todo:
{}
Blocking:
{}
    '''
    final_html_tmpl = '''
Backend Standup - <b>{}</b><br/><br/>
{}
        '''
    user_entry_html_tmpl = '''
<h3>{}</h3>
<p>
<b>Done:</b><br/>
{}
</p>
<p>
<b>Todo:</b><br/>
{}
</p>
<p>
<b>Blocking:</b><br/>
{}
</p>
        '''
    user_entries = []
    user_html_entries = []
    for d, user_data in result.items():
        for u, entries in user_data.items():
            entries_text = [e.text for e in entries]
            entries_html = [e.text.replace('\r\n', '<br/>') for e in entries]
            user_entries.append(user_entry_tmpl.format(u, *entries_text))
            user_html_entries.append(user_entry_html_tmpl.format(u, *entries_html))
    final_str = final_tmpl.format(d, '\n'.join(user_entries))
    final_html_str = final_html_tmpl.format(d, '\n'.join(user_html_entries))
    subject = subj_tmpl.format(d)
    return subject, final_str, final_html_str


def email_entries(entries, users):
    result, date_order, user_order = process_entries_query(entries=entries)
    subject, final_str, final_html_str = construct_email_text(result)

    developers = [u.email for u in users if u.role=='developer']
    non_developers = [u.email for u in users if u.role == 'non-developer']
    msg = Message(subject=subject, sender='notifications@madstreetden.com',
                  recipients=developers, cc=non_developers,
                  body=final_str, html=final_html_str)
    mail.send(msg)


@app.route('/entry/<path:date>/', methods=['GET', 'POST'])
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
        if request.method == 'POST':
            for k, v in request.form.items():
                user_id, entry_type = k.split('_')
                user = User.get(user_id=user_id)
                e = Entry(text=v, entry_type=entry_type, user=user, date=date_obj)
                db.session.add(e)
            db.session.commit()
            entries = Entry.query.filter_by(date=date_obj).order_by(Entry.date, Entry.user_id, Entry.type)
            users = User.query.all()
            email_entries(entries, users)
            return redirect(url_for('entry', date=date))

        if date in ('today', 'yesterday'):
            return redirect(url_for('entry', date=date_obj.strftime('%Y/%m/%d')))

        if resolution == 'day':
            # Use only 1 day
            entries = Entry.query.filter_by(date=date_obj).order_by(Entry.date, Entry.user_id, Entry.type)
            if entries.count() == 0:
                users = User.query.filter_by(role='developer').order_by(User.name)
                entry_types = ('done', 'todo', 'blocking')
                return render_template('entry_edit.html', date=date, date_obj=date_obj, users=users,
                                       entry_types=entry_types)
        else:
            if resolution == 'month':
                _, num_days_in_month = calendar.monthrange(date_obj.year, date_obj.month)
                end_date = datetime.date(date_obj.year, date_obj.month, num_days_in_month)
            elif resolution == 'year':
                end_date = datetime.date(date_obj.year, 12, 31)
            entries = Entry.query.filter(and_(Entry.date>=date_obj, Entry.date <=end_date))
        result, date_order, user_order = process_entries_query(entries)
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