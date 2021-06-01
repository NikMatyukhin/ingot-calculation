"""Модуль функций логирования параметров"""

import time
import logging
import logging.config
from pathlib import Path
from functools import wraps

import yaml


def setup_logging(filename='log_config.yaml', level=logging.INFO):
    """Конфигурирование логгера

    :param filename: Файл конфигурации, defaults to 'log_config.yaml'
    :type filename: str, optional
    :param level: Уровень логирования, defaults to logging.INFO
    :type level: int, optional
    """
    dir_path = Path(__file__).parent.absolute()
    abs_path = dir_path / filename

    if abs_path.exists():
        with abs_path.open('r') as f:
            try:
                config = yaml.safe_load(f.read())
                logging.config.dictConfig(config)
            except Exception as e:
                print(e)
                logging.basicConfig(level=level)
                logging.error(
                    'Ошибка конфигурации логгера. '
                    'Используется стандартная конфигурация'
                )
    else:
        logging.basicConfig(level=level)
        logging.error(
            'Файл конфигурации логгера не найден. '
            'Используется стандартная конфигурация'
        )


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
            logging.info(
                'Время выполнения функции %(name)s: '
                '%(time).4f сек', {'name': func.__name__, 'time': end - start}
            )
    return inner
