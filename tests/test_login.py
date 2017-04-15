import unittest

from tests import BaseTestCase


class LoginTestCase(BaseTestCase):
    def test_non_login_redirect(self):
        r = self.client.get('/')
        self.assertRedirects(r, '/login?next=%2F')


if __name__ == '__main__':
    unittest.main()
