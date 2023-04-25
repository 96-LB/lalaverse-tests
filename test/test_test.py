from unittest import TestCase

import api


class TestTestCase(TestCase):
    
    def test_player(self):
        self.assertIsInstance(api.get('player'), dict)
