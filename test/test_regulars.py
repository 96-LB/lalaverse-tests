import api
from . import LalaTestCase
from .util import random_float, random_int, random_str

from typing import Any


class RegularTestCase(LalaTestCase):
    
    def test_multiple_deletion(self):
        with self.temp_regular() as (uuid, _):
            pass
        
        with self.assertApiError(404, 'Regular still exists after deletion.'):
            self.delete_quest(uuid)
    
    
    def test_invalid_regular(self):
        name = random_str()
        description = random_str()
        difficulty = random_int()
        min_cooldown = random_float()
        max_cooldown = min_cooldown + random_float()
                
        with self.assertApiError(400, 'Expected bad request error for missing argument.'):
            api.post('regulars', {
                'description': description,
                'difficulty': difficulty,
                'min_cooldown': min_cooldown,
                'max_cooldown': max_cooldown
            })
        
        with self.assertApiError(400, 'Expected bad request error for wrong type.'):
            api.post('regulars', {
                'name': name,
                'description': description,
                'min_cooldown': min_cooldown,
                'max_cooldown': max_cooldown,
                'difficulty': str(difficulty)
            })
        
        with self.assertApiError(400, 'Expected bad request error for negative minimum cooldown.'):
            api.post('regulars', {
                'name': name,
                'description': description,
                'min_cooldown': -1,
                'max_cooldown': max_cooldown,
                'difficulty': difficulty
            })
        
        with self.assertApiError(400, 'Expected bad request error for maximum not greater than minimum cooldown.'):
            api.post('regulars', {
                'name': name,
                'description': description,
                'min_cooldown': max_cooldown,
                'max_cooldown': min_cooldown,
                'difficulty': difficulty
            })
    
    
    def test_patch_regular(self):
        with self.temp_regular() as (uuid, regular):
            regular['max_cooldown'] += 1
            regular['quest']['name'] = random_str()
            
            response = api.patch('regulars/' + uuid, {
                'max_cooldown': regular['max_cooldown'],
                'name': regular['quest']['name']
            })
            response = self.cast(response, dict[str, Any],
                                'Regular patch response is not a dictionary.')
            
            self.assertEqual(response, regular, 'Patched regular has incorrect data.')
