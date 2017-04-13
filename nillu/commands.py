from flask import url_for

from nillu.database import init_db
from nillu import app


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')