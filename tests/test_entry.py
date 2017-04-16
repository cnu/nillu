import unittest

from tests import BaseTestCase


class EntryTestCase(BaseTestCase):
    def test_entry_today(self):
        rv = self.login('foo@example.com', 'foo')
        rv = self.client.get('/entry/today/', follow_redirects=True)
        self.assertIn(b'user 1 entry - done', rv.data)
        self.assertIn(b'user 1 entry - todo', rv.data)
        self.assertIn(b'user 1 entry - blocking', rv.data)
        self.assertIn(b'user 2 entry - done', rv.data)
        self.assertIn(b'user 2 entry - todo', rv.data)
        self.assertIn(b'user 2 entry - blocking', rv.data)


if __name__ == '__main__':
    unittest.main()
