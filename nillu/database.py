from nillu import app
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import nillu.models
    db.create_all()
    if app.debug:
        u1 = nillu.models.User(name='foo', password='foo', email='foo@example.com', role='developer')
        u2 = nillu.models.User(name='bar', password='bar', email='bar@example.com', role='developer')
        u3 = nillu.models.User(name='baz', password='baz', email='baz@example.com', role='non-developer')
        db.session.add(u1)
        db.session.add(u2)
        db.session.add(u3)
        db.session.commit()

        u1e1 = nillu.models.Entry(text='user 1 entry - done', entry_type='done', user=u1)
        u1e2 = nillu.models.Entry(text='user 1 entry - todo', entry_type='todo', user=u1)
        u1e3 = nillu.models.Entry(text='user 1 entry - blocking', entry_type='blocking', user=u1)

        u2e1 = nillu.models.Entry(text='user 2 entry - done', entry_type='done', user=u2)
        u2e2 = nillu.models.Entry(text='user 2 entry - todo', entry_type='todo', user=u2)
        u2e3 = nillu.models.Entry(text='user 2 entry - blocking', entry_type='blocking', user=u2)

        db.session.add(u1e1)
        db.session.add(u1e2)
        db.session.add(u1e3)
        db.session.add(u2e1)
        db.session.add(u2e2)
        db.session.add(u2e3)
        db.session.commit()