import sqlite3
from collections import namedtuple
from abc import ABC, abstractmethod
from sqlite3.dbapi2 import Cursor
from typing import List, Dict, Union, Sequence, NewType, Any


"""
Пользовательский тип TableField предназначается для описания словаря
с названием и значением конкретного атрибута таблицы базы данных, например:
- {'id': 1}
- {'name': 'Питатель'}
- {'status_id': 3}
"""
TableField = NewType('TableField', Dict[str, Union[str, int, float]])


def db_connector(func):
    """Декоратор для работы с базой данных

    Устанавливается подключение к базе данных, включается ограничение на
    внешние ключи для поддержания целостности базы, а затем вызывается метод.
    В зависимости от успешности вызова изменения в базе будут зафиксированы или
    откатаны назад, после чего соединение закроется.

    :param func: Метод-обёртка запроса в базу данных
    :type func: function
    """
    def with_connection(*args, **kwargs):
        database_name = 'data/application_database.db'
        connection = sqlite3.connect(database_name)
        connection.execute('PRAGMA foreign_keys = ON;')
        result = False
        try:
            result = func(connection, *args, **kwargs)
        except sqlite3.Error:
            connection.rollback()
        else:
            connection.commit()
        finally:
            connection.close()
        return result
    return with_connection


def parse_field(record_field: TableField):
    """Парсер атрибута базы данных

    :param record_field: Атрибут таблицы базы данных
    :type record_field: TableField
    :return: Пары в виде ключа и значения атрибута
    :rtype: list
    """
    if len(record_field) != 1:
        return None, None
    return list(record_field.items())[0]


class AbstractDataService (ABC):

    @abstractmethod
    def get_table(table: str) -> List:
        pass

    @abstractmethod
    def get_by_id(table: str, record_id: TableField) -> List:
        pass

    @abstractmethod
    def save_record(table: str, **saved_fields: Sequence[TableField]) -> bool:
        pass

    @abstractmethod
    def update_record(table: str, record_id: TableField,
                      **upd_fields: Sequence[TableField]) -> bool:
        pass

    @abstractmethod
    def delete_by_id(table: str, record_id: TableField) -> bool:
        pass

    @abstractmethod
    def get_by_field(table: str, srch_field: TableField) -> List:
        pass

    @abstractmethod
    def get_by_fields(table: str, **srch_fields: Sequence[TableField]) -> List:
        pass

    @abstractmethod
    def delete_by_fields(table: str,
                         **srch_fields: Sequence[TableField]) -> bool:
        pass


class StandardDataService (AbstractDataService):

    @staticmethod
    @db_connector
    def get_table(connection, table: str) -> List:

        cursor = connection.cursor()
        cursor.execute(f'SELECT * FROM {table}')
        return list(map(list, cursor.fetchall()))

    @staticmethod
    @db_connector
    def get_by_id(connection, table: str, record_id: TableField) -> List:

        field, value = parse_field(record_id)
        sql = str(f'SELECT * FROM {table} WHERE {field}={value}')

        cursor = connection.cursor()
        cursor.execute(sql)
        return cursor.fetchone()

    @staticmethod
    @db_connector
    def get_by_field(connection, table: str, **srch_field: TableField) -> List:

        field, value = parse_field(srch_field)
        sql = str(f'SELECT * FROM {table} WHERE {field}={value}')

        cursor = connection.cursor()
        cursor.execute(sql)
        return list(map(list, cursor.fetchall()))

    @staticmethod
    @db_connector
    def get_by_fields(connection, table: str,
                      **srch_fields: Sequence[TableField]) -> List:

        sql = str(f'SELECT * FROM {table} '
                  f'WHERE {" AND ".join([f"{i}=:{i}" for i in srch_fields])}')

        cursor = connection.cursor()
        cursor.execute(sql, srch_fields)
        return list(map(list, cursor.fetchall()))

    @staticmethod
    @db_connector
    def save_record(connection: sqlite3.Connection, table: str,
                    **saved_fields: Sequence[TableField]) -> int:

        fields_number = len(saved_fields)
        sql = str(f'INSERT INTO {table} '
                  f'({", ".join(saved_fields.keys())}) VALUES '
                  f'(?{", ?" * (fields_number - 1)})')

        cursor = connection.cursor()
        cursor.execute(sql, tuple(saved_fields.values()))
        return cursor.lastrowid

    @staticmethod
    @db_connector
    def update_record(connection, table: str, record_id: TableField,
                      **upd_fields: Sequence[TableField]) -> bool:

        field, value = parse_field(record_id)
        sql = str(f'UPDATE {table} '
                  f'SET {", ".join([f"{i}=:{i}" for i in upd_fields])} '
                  f'WHERE {field}={value}')

        cursor = connection.cursor()
        cursor.execute(sql, upd_fields)
        return True

    @staticmethod
    @db_connector
    def delete_by_id(connection, table: str, record_id: TableField) -> bool:

        field, value = parse_field(record_id)

        cursor = connection.cursor()
        cursor.execute(f'DELETE FROM {table} WHERE {field}={value}')
        return True

    @staticmethod
    @db_connector
    def delete_by_fields(connection, table: str,
                         **srch_fields: Sequence[TableField]) -> bool:

        fields_number = len(srch_fields)
        sql = str(f'DELETE FROM {table} '
                  f'WHERE {" AND ".join([f"{i}=:{i}" for i in srch_fields])}')

        cursor = connection.cursor()
        cursor.execute(sql, srch_fields)
        return True


class ProductDataService (StandardDataService):

    @staticmethod
    @db_connector
    def type_list(connection) -> List:

        sql = str('SELECT DISTINCT product_type '
                  'FROM products ORDER BY product_type')

        cursor = connection.cursor()
        cursor.execute(sql)
        return list(map(lambda x: x[0], cursor.fetchall()))


class ArticleDataService (StandardDataService):

    @staticmethod
    @db_connector
    def last_id(connection) -> int:
        '''
        TODO: вполне возможно, что нужно будет удалить за ненадобностью,
              а в коде можно заменить на get_by_fields с нужными параметрами.
        '''
        cursor = connection.cursor()
        cursor.execute('SELECT MAX(article_id) FROM articles')
        return cursor.fetchone()[0]


class FusionDataService (StandardDataService):

    @staticmethod
    @db_connector
    def fusions_list(connection):

        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute('SELECT fusion_id, name FROM fusions')
        return cursor.fetchall()


class DirectionDataService (StandardDataService):

    @staticmethod
    @db_connector
    def directions_list(connection):

        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute('SELECT direction_id, name FROM directions')
        return cursor.fetchall()


class DetailDataService (StandardDataService):

    @staticmethod
    @db_connector
    def details_list(connection, record_id: TableField) -> List:

        field, value = parse_field(record_id)

        sql = str('SELECT details.name, fusions.name, details.height, '
                  'details.width, details.depth, details.amount, '
                  'details.priority, directions.name, details.detail_id '
                  'FROM details '
                  'LEFT JOIN fusions '
                  'ON fusions.fusion_id = details.fusion_id '
                  'LEFT JOIN directions '
                  'ON directions.direction_id = details.direction_id '
                  f'WHERE details.{field} = {value}')

        cursor = connection.cursor()
        cursor.execute(sql)
        return cursor.fetchall()

    @staticmethod
    @db_connector
    def detail_depth(connection, record_id: TableField) -> float:

        field, value = parse_field(record_id)

        sql = str('SELECT details.depth '
                  'FROM details '
                  f'WHERE details.{field} = {value}')

        cursor = connection.cursor()
        cursor.execute(sql)
        return cursor.fetchone()[0]


class OrderDataService (StandardDataService):

    @staticmethod
    @db_connector
    def max_id(connection) -> int:

        cursor = connection.cursor()
        cursor.execute('SELECT MAX(order_id) FROM orders')
        return cursor.fetchone()[0]

    @staticmethod
    @db_connector
    def get_table(connection, table: str) -> List:

        sql = str('SELECT orders.order_id, orders.name, '
                  'COUNT(DISTINCT complects.article_id) AS structure, '
                  'orders_statuses.name, orders.current_depth, orders.efficiency '
                  'FROM orders '
                  'LEFT JOIN complects '
                  'ON orders.order_id = complects.order_id '
                  'LEFT JOIN orders_statuses '
                  'ON orders_statuses.status_id = orders.status_id '
                  'GROUP BY complects.order_id '
                  'ORDER BY orders_statuses.sort_order')

        cursor = connection.cursor()
        cursor.execute(sql)
        return list(map(list, cursor.fetchall()))

    @staticmethod
    @db_connector
    def get_table_2(connection) -> List:

        sql = str('SELECT order_id, orders_statuses.name, orders_statuses.status_id, '
                  'orders.name, current_depth, efficiency, is_on_storage, date '
                  'FROM orders '
                  'LEFT JOIN orders_statuses '
                  'ON orders_statuses.status_id = orders.status_id')

        cursor = connection.cursor()
        cursor.execute(sql)
        return list(map(list, cursor.fetchall()))

    @staticmethod
    @db_connector
    def ingots(connection, order_id: TableField) -> List:

        field, value = parse_field(order_id)

        sql = str('SELECT ingots.ingot_id, ingots.fusion_id, fusions.name, ingots.batch, '
                  'ingots.height, ingots.width, ingots.depth, ingots.status_id, ingots.efficiency '
                  'FROM ingots '
                  'LEFT JOIN fusions ON fusions.fusion_id = ingots.fusion_id '
                  f'WHERE  ingots.{field}={value}')

        cursor = connection.cursor()
        cursor.execute(sql)
        return list(map(list, cursor.fetchall()))

    @staticmethod
    @db_connector
    def complects(connection, order_id: TableField) -> Dict:

        field, value = parse_field(order_id)

        sql = str('SELECT complects.article_id, articles.nomenclature, '
                  'complects.detail_id, details.fusion_id, details.name,  '
                  'details.height, details.width, details.depth, '
                  'complects.amount, complects.priority, details.direction_id, '
                  'complects.status_id '
                  'FROM complects '
                  'LEFT JOIN details '
                  'ON details.detail_id = complects.detail_id '
                  'LEFT JOIN articles '
                  'ON articles.article_id = complects.article_id '
                  f'WHERE complects.{field}={value}')

        result = dict()
        cursor = connection.cursor()
        cursor.execute(sql)
        for line in cursor.fetchall():
            try:
                result[tuple(line[0:2])].append(line[2:])
            except KeyError:
                result[tuple(line[0:2])] = [line[2:]]
        return result

    @staticmethod
    @db_connector
    def update_status(connection, order_id: TableField, detail_id: TableField,
                      status: str, status_value: int) -> Dict:

        field, value = parse_field(order_id)
        field_2, value_2 = parse_field(detail_id)

        sql = str(f'UPDATE complects SET {status}={status_value} '
                  f'WHERE {field}={value} AND {field_2}={value_2}')

        cursor = connection.cursor()
        cursor.execute(sql)
        return True

    @staticmethod
    @db_connector
    def cut_blanks(connection, order_id: TableField, d: float = 0) -> Dict:

        field, value = parse_field(order_id)

        sql = str('SELECT complects.detail_id, details.name, '
                  'fusions.name, complects.amount, details.height, '
                  'details.width, details.depth '
                  'FROM complects '
                  'INNER JOIN details '
                  'ON details.detail_id=complects.detail_id AND complects.status_id<>4 '
                  f'{f"AND details.depth={d}" if d > 0 else ""} '
                  'LEFT JOIN fusions ON fusions.fusion_id=details.fusion_id '
                  f'WHERE complects.{field}={value}')

        cursor = connection.cursor()
        cursor.execute(sql)
        return list(map(list, cursor.fetchall()))

    @staticmethod
    @db_connector
    def get_detail(connection, order_id: TableField,
                   detail_id: TableField) -> List:

        field_1, value_1 = parse_field(order_id)
        field_2, value_2 = parse_field(detail_id)

        sql = str('SELECT complects.amount, details.height, details.width, '
                  'details.depth, complects.priority, details.direction_id, '
                  'details.name '
                  'FROM complects '
                  'LEFT JOIN details ON '
                  'details.detail_id = complects.detail_id '
                  f'WHERE complects.{field_1}={value_1} '
                  f'AND complects.{field_2}={value_2}')

        cursor = connection.cursor()
        cursor.execute(sql)
        return cursor.fetchone()

    @staticmethod
    @db_connector
    def update_complect(connection, order_id: TableField, article_id: TableField,
                        detail_id: TableField, **upd_fields: Sequence[TableField]) -> bool:

        field1, value1 = parse_field(order_id)
        field2, value2 = parse_field(article_id)
        field3, value3 = parse_field(detail_id)
        sql = str(f'UPDATE complects '
                  f'SET {", ".join([f"{i}=:{i}" for i in upd_fields])} '
                  f'WHERE {field1}={value1} AND {field2}={value2} AND {field3}={value3}')

        cursor = connection.cursor()
        cursor.execute(sql, upd_fields)
        return True

    @staticmethod
    @db_connector
    def vacancy_ingots(connection) -> List:

        sql = str('SELECT ingots.ingot_id, ingots.fusion_id, fusions.name, ingots.batch, '
                  'ingots.height, ingots.width, ingots.depth, ingots.status_id, ingots.efficiency '
                  'FROM ingots '
                  'LEFT JOIN fusions '
                  'ON fusions.fusion_id = ingots.fusion_id '
                  'WHERE ingots.order_id IS NULL')

        cursor = connection.cursor()
        cursor.execute(sql)
        return list(map(list, cursor.fetchall()))
    
    @staticmethod
    @db_connector
    def details_count(connection, order_id: TableField) -> List:

        field, value = parse_field(order_id)

        sql = str('SELECT COUNT(DISTINCT detail_id) FROM complects '
                  f'WHERE {field}={value}')

        cursor = connection.cursor()
        cursor.execute(sql)
        return cursor.fetchone()[0]
    
    @staticmethod
    @db_connector
    def articles_count(connection, order_id: TableField) -> List:

        field, value = parse_field(order_id)

        sql = str('SELECT COUNT(DISTINCT article_id) FROM complects '
                  f'WHERE {field}={value}')

        cursor = connection.cursor()
        cursor.execute(sql)
        return cursor.fetchone()[0]

    @staticmethod
    @db_connector
    def efficiency(connection, order_id: TableField) -> float:
        field, value = parse_field(order_id)

        sql = str('SELECT efficiency FROM ingots '
                  f'WHERE {field}={value}')

        cursor = connection.cursor()
        cursor.execute(sql)
        ingots_efficiencies = [ingot[0] for ingot in cursor.fetchall()]
        if 0.0 in ingots_efficiencies:
            return 0.0
        else:
            return round(sum(ingots_efficiencies) / len(ingots_efficiencies), 2)
