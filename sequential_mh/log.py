"""Модуль функций логирования параметров"""

import time
from functools import wraps


def timeit(func):
    """Таймер времени выполнения функции

    :param func: функция, время выполнения которой измеряется
    :type func: Collable
    """
    @wraps(func)
    def inner(*args, **kwargs):
        start = time.time()
        try:
            return func(*args, **kwargs)
        finally:
            end = time.time()
            print(f'Time {func.__name__}: {end - start} sec')
    return inner
