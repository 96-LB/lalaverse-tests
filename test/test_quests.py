import random
from unittest import TestCase

import api


class QuestTestCase(TestCase):
    
    # TODO: this is terrible lol
    def test_quest(self):
        name = str(random.randint(1000000, 9999999))
        description = str(random.randint(1000000, 9999999))
        deadline = random.random() + random.randint(1000000, 9999999)
        difficulty = random.randint(1, 99)
        
        response = api.post('quests', {
            'name': name,
            'description': description,
            'deadline': deadline,
            'difficulty': difficulty,
        })
        
        self.assertIsInstance(response, dict)
        assert isinstance(response, dict)
        
        self.assertIn('uuid', response)
        uuid = response['uuid']
        
        self.assertIn('quest', response)
        quest = response['quest']
        
        self.assertEqual(response.get('prereqs'), [])
        
        self.assertIsInstance(quest, dict)
        
        self.assertEqual(quest.get('name'), name)
        self.assertEqual(quest.get('description'), description)
        self.assertEqual(quest.get('deadline'), deadline)
        self.assertEqual(quest.get('difficulty'), difficulty)
        
        ###
        
        response = api.delete(f'quests/{uuid}')
        
        self.assertEqual(None, response)
        
        ###
        
        with self.assertRaises(api.ApiException) as cm:
            api.get(f'quests/{uuid}')
        
        self.assertEqual(cm.exception.status_code, 404)
