import api
from . import LalaTestCase
from .util import random_bool, random_str

from typing import Any


class CheckboxesTestCase(LalaTestCase):
    
    def test_checkboxes_on_creation(self):
        checkboxes = [random_str() for _ in range(3)]
        with self.temp_quest(checkboxes=checkboxes) as (uuid, _, _):
            response = api.get(f'quests/{uuid}/checkboxes')
            response = self.cast(response, list[dict[str, Any]],
                                 'Checkbox list is not a list.')
            
            self.assertEqual(response, [{'name': i, 'checked': False} for i in checkboxes],
                             'Checkbox list has incorrect data.')
            
            for i in range(len(checkboxes)):
                response = api.get(f'quests/{uuid}/checkboxes/{i}')
                self.assertEqual(response, {'name': checkboxes[i], 'checked': False},
                                 'Checkbox has incorrect data.')
    
    
    def test_checkbox_put(self):
        # rewrite above with N for length
        N = 10
        names = [random_str() for _ in range(N)]
        checked = [random_bool() for _ in range(N)]
        data = {'names': names, 'checked': checked}
        
        with self.temp_quest() as (uuid, _, _):
            
            api.put(f'quests/{uuid}/checkboxes', data)
            
            response = api.get(f'quests/{uuid}/checkboxes')
            response = self.cast(response, list[dict[str, Any]],
                                 'Checkbox list is not a list.')
            
            self.assertEqual(response, [{'name': names[i], 'checked': checked[i]} for i in range(N)])
