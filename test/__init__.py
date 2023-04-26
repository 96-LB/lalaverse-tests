from contextlib import contextmanager
import random
from unittest import TestCase

import api

from typing import Any, Container, Generator, Iterable, TypeVar
from types import GenericAlias


T = TypeVar('T')

# TODO: major code cleanup
class LalaTestCase(TestCase):
    
    def setUp(self) -> None:
        print(f' Running {self.id()}')
        return super().setUp()
    
    
    def assertIns(self, members: Iterable[T], container: Iterable[T] | Container[T], msg: Any = None) -> None:
        for member in members:
            self.assertIn(member, container, msg)
    
    
    def getFromDict(self, data: dict[str, T], keys: Iterable[str], msg: Any = None) -> Iterable[T]:
        for key in keys:
            self.assertIn(key, data, msg)
            yield data[key]
    
    
    def assertDictHas(self, data: dict[str, T], msg: Any = None, **kwargs: T) -> None:
        self.assertIsInstance(data, dict, msg)
        self.assertEqual(data, data | kwargs, msg)
    
    
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
    
    
    def random_str(self, len: int = 10) -> str:
        return ''.join('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._' for _ in range(len))
    
    
    def random_int(self, len: int = 10) -> int:
        return random.randrange(0, 10 ** len)
    
    
    def random_float(self, len: int = 10) -> float:
        return self.random_int(len) + random.random()
