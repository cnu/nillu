import unittest

from tests import BaseTestCase


class LoginTestCase(BaseTestCase):
    def test_non_login_redirect(self):
        rv = self.client.get('/')
        self.assertRedirects(rv, '/login?next=%2F')


if __name__ == '__main__':
    unittest.main()
