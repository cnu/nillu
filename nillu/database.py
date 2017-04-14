from nillu import app
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import nillu.models
    db.create_all()
