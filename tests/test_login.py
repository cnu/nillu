import unittest

from tests import BaseTestCase


class LoginTestCase(BaseTestCase):
    def test_non_login_redirect(self):
        rv = self.client.get('/')
        self.assertRedirects(rv, '/login?next=%2F')

    def test_correct_login(self):
        rv = self.login('foo@example.com', 'foo')
        assert b'Logged in Successfully.' in rv.data

    def test_incorrect_login(self):
        rv = self.login('foo@example.com', 'foo1')
        assert b'Wrong email/password.' in rv.data

if __name__ == '__main__':
    unittest.main()
