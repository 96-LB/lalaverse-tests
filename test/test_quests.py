from contextlib import contextmanager
import api
from . import LalaTestCase

from typing import Any, Generator

class QuestTestCase(LalaTestCase):
    
    def make_quest(self, name: str = ..., description: str = ..., deadline: float = ..., difficulty: int = ..., checkboxes: list[str] = ..., prereqs: list[str] = ...) -> tuple[str, dict[str, Any], list[str]]:
        name = self.random_str() if name is ... else name
        description = self.random_str() if description is ... else description
        deadline = self.random_float() if deadline is ... else deadline
        difficulty = self.random_int() if difficulty is ... else difficulty
        checkboxes = [] if checkboxes is ... else checkboxes
        prereqs = [] if prereqs is ... else prereqs
        
        response = api.post('quests', {
            'name': name,
            'description': description,
            'deadline': deadline,
            'difficulty': difficulty,
            'checkboxes': checkboxes,
            'prereqs': prereqs
        })
        
        response = self.cast(response, dict[str, Any],
                             'Quest creation response is not a dictionary.')
        
        uuid, quest, prereqs = self.getItems(response, ('uuid', 'quest', 'prereqs'),
                                                'Quest creation response missing keys.')
                
        uuid = self.cast(uuid, str, 'Created quest UUID is not a string.')
        quest = self.cast(quest, dict[str, Any], 'Created quest data is not a dictionary.')
        prereqs = self.cast(prereqs, list[str], 'Created quest prerequisites are not a list of UUIDs.')
        
        self.assertDictHas(
            quest,
            'Created quest doesn\'t match inputs.',
            name=name,
            description=description,
            deadline=deadline,
            difficulty=difficulty
        )
        
        checkboxes_obj = self.getItem(quest, 'checkboxes', 'Checkboxes missing from quests response.')
        checkboxes_obj = self.cast(checkboxes_obj, list[dict[str, Any]], 'Checkboxes is not a dictionary.')
        self.assertEqual(checkboxes, [checkbox_obj['name'] for checkbox_obj in checkboxes_obj])
        
        return uuid, quest, prereqs
    
    
    def delete_quest(self, uuid: str) -> None:
        api.delete(f'quests/{uuid}')
        
        with self.assertApiError(404, 'Quest still exists after deletion.'):
            api.get(f'quests/{uuid}')
    
    
    @contextmanager
    def temp_quest(self, name: str = ..., description: str = ..., deadline: float = ..., difficulty: int = ..., checkboxes: list[str] = ..., prereqs: list[str] = ...) -> Generator[tuple[str, dict[str, Any], list[str]], None, None]:
        uuid, quest, prereqs = self.make_quest(name, description, deadline, difficulty, checkboxes, prereqs)
        try:
            yield uuid, quest, prereqs
        finally:
            self.delete_quest(uuid)
    
    
    def test_multiple_deletion(self):
        with self.temp_quest() as (uuid, _, _):
            pass
        
        with self.assertApiError(404, 'Quest still exists after deletion.'):
            self.delete_quest(uuid)
    
    
    def test_invalid_quest(self):
        name = self.random_str()
        description = self.random_str()
        deadline = self.random_float()
        difficulty = self.random_int()
        
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
            quest['name'] = self.random_str()
            
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
