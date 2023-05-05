import random


def random_str(len: int = 10) -> str:
    return ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._') for _ in range(len))


def random_int(len: int = 8) -> int:
    return random.randrange(0, 10 ** len)


def random_float(len: int = 6) -> float:
    return random_int(len) + random.random()


def random_bool() -> bool:
    return random.choice((True, False))
