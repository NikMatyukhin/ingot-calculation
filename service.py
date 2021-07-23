import logging
from math import prod
from sqlite3 import connect, Connection, Error
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Sequence, Literal, Optional
from itertools import groupby
from operator import itemgetter
from collections import OrderedDict


@dataclass
class IngotStatus:
    """Статус слитка

    Содержит название статуса и его ID из базы данных.
    """
    id_: int
    name: set


@dataclass
class Field:
    """Класс управления полями таблицы SQL.

    Класс Field представляет характеристики конкретного столбца базы
    данных, а именно название столбца и значение столбца для записи.
    """
    name: str
    value: object


class FieldCollection:
    """Класс управления итерируемой коллекцией обновляемых статусов.

    Для оптимизации работы запросов обновления, сначала все обновляемые данные
    записываются в коллекцию, после чего она используется в методе сервиса
    заказов update_statuses.
    """
    def __init__(self, columns: list):
        self.__updatable_data = []
        self.__updatable_columns = columns
        self.__step = 0

    def __iter__(self):
        return self

    def __next__(self) -> tuple:
        if self.__step >= len(self.__updatable_data):
            raise StopIteration
        self.__step += 1
        return self.__updatable_data[self.__step - 1]

    def append(self, *fields: Field):
        values = []
        names = []
        for field in fields:
            names.append(field.name)
            values.append(field.value)
        if set(self.__updatable_columns) != set(names):
            raise ValueError("'FieldCollection' has incompatible column names")
        self.__updatable_data.append(tuple(values))

    @property
    def names(self) -> tuple:
        return tuple(self.__updatable_columns)


def db_connector(func):
    """Декоратор для работы с базой данных.

    Устанавливается подключение к базе данных, включается ограничение на
    внешние ключи для поддержания целостности базы, а затем вызывается метод.
    В зависимости от успешности вызова изменения в базе будут зафиксированы или
    откатаны назад, после чего соединение закроется.

    :param func: Метод-обёртка запроса в базу данных
    :type func: function
    """
    def with_connection(*args, **kwargs):
        database_name = 'data/application_database.db'
        connection = connect(database_name)
        connection.execute('PRAGMA foreign_keys = ON;')
        result = False
        try:
            result = func(*args, connection=connection, **kwargs)
        except Error as error:
            connection.rollback()
            logging.critical(f'SqliteDatabaseError: {error.args[0]}')
        else:
            connection.commit()
        finally:
            connection.close()
        return result
    return with_connection


class AbstractDataService(ABC):

    @abstractmethod
    def get_table(table: str, connection: Connection = connect(':memory:')) -> list:
        pass

    @abstractmethod
    def get_by_id(table: str, record_id: Field, connection: Connection = connect(':memory:')) -> list:
        pass

    @abstractmethod
    def get_by_field(table: str, srch_field: Field, connection: Connection = connect(':memory:')) -> list:
        pass

    @abstractmethod
    def get_by_fields(table: str, connection: Connection = connect(':memory:'), **srch_fields: Sequence[Field]) -> list:
        pass

    @abstractmethod
    def save_record(table: str, connection: Connection = connect(':memory:'), **saved_fields: Sequence[Field]) -> bool:
        pass

    @abstractmethod
    def update_record(table: str, record_id: Field, connection: Connection = connect(':memory:'), **upd_fields: Sequence[Field]) -> bool:
        pass

    @abstractmethod
    def delete_by_id(table: str, record_id: Field, connection: Connection = connect(':memory:')) -> bool:
        pass

    @abstractmethod
    def delete_by_fields(table: str, connection: Connection = connect(':memory:'), **srch_fields: Sequence[Field]) -> bool:
        pass


class StandardDataService(AbstractDataService):

    @staticmethod
    @db_connector
    def get_table(table: str, connection: Connection = connect(':memory:')) -> list:
        cursor = connection.cursor()
        cursor.execute(f'SELECT * FROM {table}')

        return cursor.fetchall()

    @staticmethod
    @db_connector
    def get_by_id(table: str, id: Field, connection: Connection = connect(':memory:')) -> list:
        sql = str(f'SELECT * FROM {table} WHERE {id.name}={id.value}')
        cursor = connection.cursor()
        cursor.execute(sql)

        return cursor.fetchone()

    @staticmethod
    @db_connector
    def get_by_field(table: str, condition: Field, connection: Connection = connect(':memory:')) -> list:
        sql = str(f'SELECT * FROM {table} WHERE {condition.name}={condition.value}')
        cursor = connection.cursor()
        cursor.execute(sql)

        return cursor.fetchall()

    @staticmethod
    @db_connector
    def get_by_fields(table: str, connection: Connection = connect(':memory:'), **conditions: dict) -> list:
        sql = str(f'SELECT * FROM {table} '
                  f'WHERE {" AND ".join([f"{key}=:{key}" for key in conditions])}')
        cursor = connection.cursor()
        cursor.execute(sql, conditions)

        return cursor.fetchall()

    @staticmethod
    @db_connector
    def save_record(table: str, connection: Connection = connect(':memory:'), **saved_fields: dict) -> int:
        sql = str(f'INSERT INTO {table} '
                  f'({", ".join(saved_fields)}) VALUES '
                  f'(?{", ?" * (len(saved_fields) - 1)})')
        cursor = connection.cursor()
        cursor.execute(sql, tuple(saved_fields.values()))

        return cursor.lastrowid

    @staticmethod
    @db_connector
    def update_record(table: str, id: Field, connection: Connection = connect(':memory:'), **fields: dict) -> bool:
        sql = str(f'UPDATE {table} '
                  f'SET {", ".join([f"{key}=:{key}" for key in fields])} '
                  f'WHERE {id.name}={id.value}')
        cursor = connection.cursor()
        cursor.execute(sql, fields)

        return True

    @staticmethod
    @db_connector
    def delete_by_id(table: str, id: Field, connection: Connection = connect(':memory:')) -> bool:
        cursor = connection.cursor()
        cursor.execute(f'DELETE FROM {table} WHERE {id.name}={id.value}')

        return True

    @staticmethod
    @db_connector
    def delete_by_fields(table: str, connection: Connection = connect(':memory:'), **fields: dict) -> bool:
        sql = str(f'DELETE FROM {table} '
                  f'WHERE {" AND ".join([f"{key}=:{key}" for key in fields])}')
        cursor = connection.cursor()
        cursor.execute(sql, fields)

        return True


class CatalogDataService(StandardDataService):
    @staticmethod
    @db_connector
    def statuses_list(connection: Connection = connect(':memory:')) -> OrderedDict:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM complects_statuses ORDER BY id')
        collection = OrderedDict()
        for item in cursor.fetchall():
            collection[item[1]] = item[0]
        return collection

    @staticmethod
    @db_connector
    def directions_list(connection: Connection = connect(':memory:')) -> OrderedDict:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM directions ORDER BY id')
        collection = OrderedDict()
        for item in cursor.fetchall():
            collection[item[1]] = item[0]
        return collection

    @staticmethod
    @db_connector
    def fusions_list(connection: Connection = connect(':memory:')) -> OrderedDict:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM fusions ORDER BY id')
        collection = OrderedDict()
        for item in cursor.fetchall():
            collection[item[1]] = item[0]
        return collection

    @staticmethod
    @db_connector
    def type_list(connection: Connection = connect(':memory:')) -> list:
        cursor = connection.cursor()
        cursor.execute('SELECT DISTINCT type FROM articles')

        return list(map(itemgetter(0), cursor.fetchall()))


class IngotStatusDataService(StandardDataService):
    """Сервис работы со статусам слитка"""
    table = 'ingots_statuses'

    @staticmethod
    @db_connector
    def get_table(connection: Connection = connect(':memory:')) -> list:
        """Получение списка статусов"""
        # super здесь не работает, можно было подключение через self сделать
        cursor = connection.cursor()
        cursor.execute(f'SELECT * FROM {IngotStatusDataService.table}')
        return [IngotStatus(*item) for item in cursor.fetchall()]

    @staticmethod
    @db_connector
    def get_by_field(condition: Field, connection: Connection = connect(':memory:')) -> list:
        sql = str(f'SELECT * FROM {IngotStatusDataService.table} WHERE {condition.name}={repr(condition.value)}')
        cursor = connection.cursor()
        cursor.execute(sql)
        return [IngotStatus(*item) for item in cursor.fetchall()]

    @classmethod
    def get_by_name(cls, name: str):
        """Получение статуса по имени"""
        field = Field(name='name', value=name)
        return cls.get_by_field(condition=field)


class OrderDataService(StandardDataService):

    Category = Literal['unused', 'used', 'planned']

    @staticmethod
    @db_connector
    def get_table(status: Field = None, connection: Connection = connect(':memory:')) -> list:
        condition = f'WHERE o.{status.name}={status.value} ' if status else ''
        sql = str('SELECT o.id, o.status_id, o.name, o.date, o.step, '
                  'o.efficiency, COUNT(DISTINCT c.article_id), SUM(c.amount) '
                  'FROM orders AS o '
                  'LEFT JOIN complects AS c ON o.id = c.order_id ' + \
                  condition + 'GROUP BY o.id ORDER BY o.id')
        cursor = connection.cursor()
        cursor.execute(sql)

        return cursor.fetchall()

    @staticmethod
    @db_connector
    def ingots(order: Field, connection: Connection = connect(':memory:')) -> list:
        sql = str(f'SELECT * FROM ingots WHERE {order.name}={order.value}')
        cursor = connection.cursor()
        cursor.execute(sql)

        return cursor.fetchall()

    @staticmethod
    @db_connector
    def ware_ingots(category: Category, connection: Connection = connect(':memory:')) -> list:
        if category == 'planned':
            sql = str('SELECT * FROM ingots WHERE status_id = 3')
        elif category == 'used':
            sql = str('SELECT * FROM ingots WHERE order_id NOT NULL AND status_id <> 3')
        elif category == 'unused':
            sql = str('SELECT * FROM ingots WHERE order_id IS NULL')
        else:
            raise ValueError(f"'Category' can not have '{category}' value")
        cursor = connection.cursor()
        cursor.execute(sql)

        return cursor.fetchall()

    @staticmethod
    @db_connector
    def complects(order: Field, connection: Connection = connect(':memory:')) -> dict:
        result = dict()
        sql = str('SELECT c.article_id, a.name, c.detail_id, d.fusion_id, '
                  'd.direction_id, c.status_id, d.name, d.length, d.width, '
                  'd.height, c.amount, c.total, c.priority '
                  'FROM complects AS c '
                  'LEFT JOIN details AS d ON d.id = c.detail_id '
                  'LEFT JOIN articles AS a ON a.id = c.article_id '
                  f'WHERE c.{order.name}={order.value} ORDER BY c.article_id')
        cursor = connection.cursor()
        cursor.execute(sql)

        for key, values in groupby(cursor.fetchall(), key=itemgetter(0, 1)):
            result[key] = list(map(itemgetter(slice(2, None)), values))
        return result

    @staticmethod
    @db_connector
    def cut_blanks(order: Field, height: Optional[float] = None, connection: Connection = connect(':memory:')) -> dict:
        sql = str('SELECT c.detail_id, d.fusion_id, d.name, c.amount, '
                  'd.length, d.width, d.height FROM complects AS c '
                  'INNER JOIN details AS d '
                  'ON d.id = c.detail_id AND c.status_id <> 4 '
                  f'{f"AND d.height = {height}" if height else ""} '
                  f'WHERE c.{order.name}={order.value}')
        cursor = connection.cursor()
        cursor.execute(sql)

        return cursor.fetchall()

    @staticmethod
    @db_connector
    def update_statuses(updates: FieldCollection, connection: Connection = connect(':memory:')):
        sql = str('UPDATE complects SET {}=?, {}=? WHERE {}=? AND {}=?'.format(*updates.names))
        cursor = connection.cursor()
        cursor.executemany(sql, updates)

        return True

    @staticmethod
    @db_connector
    def update_complects(updates: FieldCollection, connection: Connection = connect(':memory:')) -> bool:
        sql = str('UPDATE complects SET {}=?, {}=? WHERE {}=? AND {}=?'.format(*updates.names))
        cursor = connection.cursor()
        cursor.executemany(sql, updates)

        return True
    
    @staticmethod
    @db_connector
    def save_complects(updates: FieldCollection, connection: Connection = connect(':memory:')) -> bool:
        sql = str('INSERT INTO complects ({}, {}, {}, {}, {}, {}) VALUES (?, ?, ?, ?, ?, ?)'.format(*updates.names))
        cursor = connection.cursor()
        cursor.executemany(sql, updates)
        
        return True

    @staticmethod
    @db_connector
    def discard_statuses(updates: FieldCollection, connection: Connection = connect(':memory:')) -> bool:
        sql = str('UPDATE complects SET {}=? WHERE {}=? AND {}=?'.format(*updates.names))
        cursor = connection.cursor()
        cursor.executemany(sql, updates)
        
        return True

    @staticmethod
    @db_connector
    def efficiency(order: Field, connection: Connection = connect(':memory:')) -> float:
        ingots_sql = str('SELECT i.length, i.width, i.height, f.density '
                         'FROM ingots AS i '
                         'LEFT JOIN fusions AS f ON f.id = i.fusion_id '
                         f'WHERE i.{order.name}={order.value}')
        blanks_sql = str('SELECT d.length, d.width, d.height, f.density, c.total '
                         'FROM complects AS c '
                         'LEFT JOIN details AS d ON d.id = c.detail_id '
                         'LEFT JOIN fusions AS f ON f.id = d.fusion_id '
                         f'WHERE c.{order.name}={order.value} '
                         'AND (c.status_id = 1 OR c.status_id = 5)')
        cursor = connection.cursor()
        ingots_mass = sum(prod(line) for line in cursor.execute(ingots_sql))
        blanks_mass = sum(prod(line) for line in cursor.execute(blanks_sql))
        return round(blanks_mass / ingots_mass, 2)
