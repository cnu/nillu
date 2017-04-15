import unittest
from flask_testing import TestCase

import nillu
from nillu import database


class BaseTestCase(TestCase):
    def create_app(self):
        app = nillu.app
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        return app

    def setUp(self):
        database.init_db()

    def tearDown(self):
        database.db.session.remove()
        database.db.drop_all()


if __name__ == '__main__':
    unittest.main()
