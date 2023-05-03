import api
from . import LalaTestCase
from .util import random_str

from typing import Any


class DailiesTestCase(LalaTestCase):
    
    def test_multiple_deletion(self):
        with self.temp_daily() as (uuid, _):
            pass
        
        with self.assertApiError(404, 'Daily still exists after deletion.'):
            self.delete_quest(uuid)
    
    
    def test_invalid_daily(self):
        print('made it here!')
        with self.assertApiError(400, 'Expected bad request error for missing argument.'):
            api.post('dailies', {
                'description': random_str(),
            })
        
        with self.assertApiError(400, 'Expected bad request error for wrong type.'):
            api.post('dailies', {
                'name': 0,
                'description': random_str(),
            })
    
    
    def test_patch_daily(self):
        with self.temp_daily() as (uuid, daily):
            daily['name'] = random_str()
            
            response = api.patch('dailies/' + uuid, {
                'name': daily['name']
            })
            response = self.cast(response, dict[str, Any],
                                'Daily patch response is not a dictionary.')
            
            self.assertEqual(response, daily, 'Patched daily has incorrect data.')
