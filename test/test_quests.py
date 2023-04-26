import api
from . import LalaTestCase

from typing import Any

class QuestTestCase(LalaTestCase):
    
    def test_quest(self):
        name = self.random_str()
        description = self.random_str()
        deadline = self.random_float()
        difficulty = self.random_int()
        
        response = api.post('quests', {
            'name': name,
            'description': description,
            'deadline': deadline,
            'difficulty': difficulty,
        })
        
        response = self.cast(response, dict[str, Any],
                             'Quest creation response is not a dictionary.')
        
        uuid, quest, prereqs = self.getFromDict(response, ('uuid', 'quest', 'prereqs'),
                                                'Quest creation response missing keys.')
        
        self.assertEqual(prereqs, [])
        
        self.assertDictHas(
            quest,
            'Created quest doesn\'t match inputs.',
            name=name,
            description=description,
            deadline=deadline,
            difficulty=difficulty
        )
        
        ###
        
        api.delete(f'quests/{uuid}')
        
        with self.assertApiError(404, 'Quest still exists after deletion.'):
            api.get(f'quests/{uuid}')
