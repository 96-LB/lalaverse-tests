import api
from . import LalaTestCase
from .util import random_str, random_float, random_int

from typing import Any


class QuestsTestCase(LalaTestCase):
    
    def test_multiple_deletion(self):
        with self.temp_quest() as (uuid, _, _):
            pass
        
        with self.assertApiError(404, 'Quest still exists after deletion.'):
            self.delete_quest(uuid)
    
    
    def test_invalid_quest(self):
        name = random_str()
        description = random_str()
        deadline = random_float()
        difficulty = random_int()
        
        with self.assertApiError(400, 'Expected bad request error for missing argument.'):
            api.post('quests', {
                'description': description,
                'deadline': deadline,
                'difficulty': difficulty
            })
        
        with self.assertApiError(400, 'Expected bad request error for wrong type.'):
            api.post('quests', {
                'name': name,
                'description': description,
                'deadline': deadline,
                'difficulty': str(difficulty)
            })
    
    
    def test_patch_quest(self):
        with self.temp_quest() as (uuid, quest, _):
            quest['name'] = random_str()
            
            response = api.patch('quests/' + uuid, {
                'name': quest['name']
            })
            response = self.cast(response, dict[str, Any],
                                'Quest patch response is not a dictionary.')
            
            self.assertEqual(response, quest, 'Patched quest has incorrect data.')
    
    
    def get_quest_lists(self) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
        all_quests = api.get('quests')
        all_quests = self.cast(all_quests, dict[str, Any],
                               'Quest list is not a dictionary.')
        
        active_quests = api.get('quests/active')
        active_quests = self.cast(active_quests, dict[str, Any],
                                  'Active quest list is not a dictionary.')
        
        daily_quests = api.get('quests/daily')
        daily_quests = self.cast(daily_quests, dict[str, Any],
                                 'Daily quest list is not a dictionary.')
        
        return all_quests, active_quests, daily_quests
    
    
    def test_quest_lists_are_subsets(self):
        all_quests, active_quests, daily_quests = self.get_quest_lists()
        self.assertEqual(all_quests, all_quests | active_quests | daily_quests)
    
    
    def test_quest_complete(self):
        with self.temp_quest(deadline=9999999999.0) as (uuid, quest, _):
            all_quests, active_quests, daily_quests = self.get_quest_lists()
            self.assertIn(uuid, all_quests, 'Quest not in quest list.')
            self.assertIn(uuid, active_quests, 'Quest not in active quest list.')
            self.assertNotIn(uuid, daily_quests, 'Normal quest is in daily quest list.')
            
            response = api.post(f'quests/{uuid}/complete')
            response = self.cast(response, dict[str, Any],
                                 'Quest completion response is not a dictionary.')
            
            quest_response, rewards = self.getItems(response, ('quest', 'rewards'),
                                           'Quest completion response missing keys.')
            
            quest['completed'] = True
            self.assertEqual(quest_response, quest, 'Completed quest has incorrect data.')
            
            self.cast(rewards, dict[str, Any],
                      'Quest reward is not a dictionary.')
            
            all_quests, active_quests, daily_quests = self.get_quest_lists()
            self.assertIn(uuid, all_quests, 'Quest not in quest list.')
            self.assertNotIn(uuid, active_quests, 'Completed quest in active quest list.')
            self.assertNotIn(uuid, daily_quests, 'Normal quest is in daily quest list.')
    
    
    def test_quest_chaining(self):
        with self.temp_quest(deadline=9999999999.0) as (uuid1, _, _):
            with self.temp_quest(prereqs=[uuid1], deadline=9999999999.0) as (uuid2, _, _):
                active_quests = api.get('quests/active')
                active_quests = self.cast(active_quests, dict[str, Any], 'Active quest list is not a dictionary.')
                
                self.assertIn(uuid1, active_quests, 'Quest not in active quest list.')
                self.assertNotIn(uuid2, active_quests, 'Quest with prereq in active quest list.')
                
                response = api.get(f'quests/{uuid1}/prereqs')
                self.assertEqual(response, [], 'Quest prereqs list incorrect.')
                
                response = api.get(f'quests/{uuid1}/sequels')
                self.assertEqual(response, [uuid2], 'Quest sequels list incorrect.')
                
                response = api.get(f'quests/{uuid2}/prereqs')
                self.assertEqual(response, [uuid1], 'Quest prereqs list incorrect.')
                
                response = api.get(f'quests/{uuid2}/sequels')
                self.assertEqual(response, [], 'Quest sequels list incorrect.')
                
                api.post(f'quests/{uuid1}/complete')
                
                active_quests = api.get('quests/active')
                active_quests = self.cast(active_quests, dict[str, Any], 'Active quest list is not a dictionary.')
                
                self.assertNotIn(uuid1, active_quests, 'Completed quest in active quest list.')
                self.assertIn(uuid2, active_quests, 'Quest not in active quest list.')
