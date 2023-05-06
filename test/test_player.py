from time import time

import api
from . import LalaTestCase

from typing import Any


class PlayerTestCase(LalaTestCase):
    
    def test_last_seen_is_past(self):
        response = api.get('player')
        
        response = self.cast(response, dict[str, Any], 'Player is not a dictionary.')
        
        last_seen = self.getItem(response, 'last_seen', 'Player response does not contain last seen.')
        last_seen = self.cast(last_seen, float, 'Last seen is not a number.')
        
        now = time()
        self.assertTrue(last_seen < now, f'Last seen ({last_seen}) is later than current time ({now}).')
