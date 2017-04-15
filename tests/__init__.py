import unittest
from flask_testing import TestCase

import nillu
from nillu import database


class BaseTestCase(TestCase):
    def create_app(self):
        app = nillu.app
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        app.config['WTF_CSRF_ENABLED'] = False
        return app

    def setUp(self):
        database.init_db()

    def tearDown(self):
        database.db.session.remove()
        database.db.drop_all()

    def login(self, email, password):
        return self.client.post('/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.client.get('/logout', follow_redirects=True)


if __name__ == '__main__':
    unittest.main()
