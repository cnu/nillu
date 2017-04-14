from flask import url_for

from nillu import app


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    from nillu.database import init_db
    init_db()
    print('Initialized the database.')


@app.cli.command('list_routes')
def list_routes():
    import urllib.parse
    output = []
    for rule in app.url_map.iter_rules():
        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)
        methods = ','.join(rule.methods)
        line = urllib.parse.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, rule))
        output.append(line)

    for line in sorted(output):
        print(line)