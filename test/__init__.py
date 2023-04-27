from contextlib import contextmanager
from unittest import TestCase

import api
from .util import random_str, random_float, random_int

from typing import Any, Container, Generator, Iterable, TypeVar
from types import GenericAlias


T = TypeVar('T')

class LalaTestCase(TestCase):
    
    #
    # ASSERTIONS
    #
    
    def assertIns(self, members: Iterable[T], container: Iterable[T] | Container[T], msg: Any = None) -> None:
        for member in members:
            self.assertIn(member, container, msg)
    
    
    def assertDictHas(self, data: dict[str, T], msg: Any = None, **kwargs: T) -> None:
        self.assertIsInstance(data, dict, msg)
        self.assertEqual(data, data | kwargs, msg)
    
    
    def getItem(self, obj: dict[str, T], key: str, msg: Any = None) -> T:
        self.assertIn(key, obj, msg)
        return obj[key]
    
    
    def getItems(self, data: dict[str, T], keys: Iterable[str], msg: Any = None) -> Iterable[T]:
        for key in keys:
            self.assertIn(key, data, msg)
            yield data[key]
    
    
    def cast(self, obj: object, cls: type[T], msg: Any = None) -> T:
        if isinstance(cls, GenericAlias):
            cls = cls.__origin__
        self.assertIsInstance(obj, cls, msg)
        return obj # type: ignore
    
    
    @contextmanager
    def assertApiError(self, status_code: int, msg: Any = None) -> Generator[None, None, None]:
        with self.assertRaises(api.ApiException, msg=msg) as cm:
            yield
        
        self.assertEqual(cm.exception.status_code, status_code, msg)
    
    #
    # API CALLS
    #
    
    def make_quest(self, name: str = ..., description: str = ..., deadline: float = ..., difficulty: int = ..., checkboxes: list[str] = ..., prereqs: list[str] = ...) -> tuple[str, dict[str, Any], list[str]]:
        name = random_str() if name is ... else name
        description = random_str() if description is ... else description
        deadline = random_float() if deadline is ... else deadline
        difficulty = random_int() if difficulty is ... else difficulty
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
