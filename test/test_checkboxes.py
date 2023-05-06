import random

import api
from . import LalaTestCase
from .util import random_bool, random_str


class CheckboxesTestCase(LalaTestCase):
    
    def test_checkbox_creation(self):
        N = 3
        checkboxes = [random_str() for _ in range(N)]
        expected = [{'name': i, 'checked': False} for i in checkboxes]
        
        with self.temp_quest(checkboxes=checkboxes) as (uuid, _, _):
            response = api.get(f'quests/{uuid}/checkboxes')
            self.assertEqual(response, expected,
                             'Checkbox list has incorrect data.')
            
            for i in range(N):
                response = api.get(f'quests/{uuid}/checkboxes/{i}')
                self.assertEqual(response, expected[i],
                                 'Checkbox has incorrect data.')
    
    
    def test_checkbox_put(self):
        N = 10
        names = [random_str() for _ in range(N)]
        checked = [random_bool() for _ in range(N)]
        data = {'names': names, 'checked': checked}
        expected = [{'name': names[i], 'checked': checked[i]} for i in range(N)]
        
        with self.temp_quest() as (uuid, _, _):
            response = api.put(f'quests/{uuid}/checkboxes', data)
            self.assertEqual(response, expected,
                            'Checkbox list put has incorrect data.')
            
            response = api.get(f'quests/{uuid}/checkboxes')
            self.assertEqual(response, expected,
                            'Checkbox list has incorrect data.')
    
    
    def test_checkbox_patch(self):
        N = 10
        checkboxes = [random_str() for _ in range(N)]
        index = random.randrange(0, N)
        data = {'name': random_str(), 'checked': True}
        
        with self.temp_quest(checkboxes=checkboxes) as (uuid, _, _):
            response = api.patch(f'quests/{uuid}/checkboxes/{index}', data)
            self.assertEqual(response, data,
                            'Checkbox patch has incorrect data.')
            
            response = api.get(f'quests/{uuid}/checkboxes/{index}')
            self.assertEqual(response, data,
                            'Checkbox has incorrect data.')
    
    
    def test_checkbox_delete(self):
        N = 10
        M = 4
        checkboxes = [random_str() for _ in range(N)]
        expected = [{'name': checkboxes[i], 'checked': False} for i in range(N)]
        
        with self.temp_quest(checkboxes=checkboxes) as (uuid, _, _):
            for i in range(M):
                index = random.randrange(0, N - i)
                del expected[index]
                response = api.delete(f'quests/{uuid}/checkboxes/{index}')
                self.assertEqual(response, expected,
                                'Checkbox deletion has incorrect data.')
            
            with self.assertApiError(404):
                api.delete(f'quests/{uuid}/checkboxes/{N}')
            
            with self.assertApiError(404):
                api.delete(f'quests/{uuid}/checkboxes/-1')
            
            response = api.get(f'quests/{uuid}/checkboxes')
            self.assertEqual(response, expected,
                            'Checkbox list has incorrect data.')
