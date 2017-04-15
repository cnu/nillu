import unittest

from tests import BaseTestCase


class LoginTestCase(BaseTestCase):
    def test_non_login_redirect(self):
        rv = self.client.get('/')
        self.assertRedirects(rv, '/login?next=%2F')

    def test_correct_login(self):
        """Test a correct email/password login."""
        rv = self.login('foo@example.com', 'foo')
        assert b'Logged in Successfully.' in rv.data

    def test_incorrect_password_login(self):
        """Test an incorrect password login."""
        rv = self.login('foo@example.com', 'foo1')
        assert b'Wrong email/password.' in rv.data

    def test_incorrect_email_login(self):
        """Test an incorrect email login."""
        rv = self.login('spam@example.com', 'foo')
        assert b'Wrong email/password.' in rv.data

if __name__ == '__main__':
    unittest.main()
