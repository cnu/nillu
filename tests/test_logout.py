import unittest

from tests import BaseTestCase


class LogoutTestCase(BaseTestCase):
    def test_correct_logout(self):
        """Test whether a logged in user is able to logout."""
        rv = self.login('foo@example.com', 'foo')
        rv = self.logout()
        assert b'You have been logged out.' in rv.data

    def test_incorrect_logout(self):
        """Test if a non-logged in user is shows a login page."""
        rv = self.logout()
        assert b'Please sign in' in rv.data


if __name__ == '__main__':
    unittest.main()
