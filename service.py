import sqlite3
from collections import namedtuple
from abc import ABC, abstractmethod
from typing import List, Dict, Union, Sequence, NewType, Any


TableField = NewType('TableField', Dict[str, Union[str, int, float]])


def db_connector(func):
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
    def save_record(connection, table: str,
                    **saved_fields: Sequence[TableField]) -> bool:

        fields_number = len(saved_fields)
        sql = str(f'INSERT INTO {table} '
                  f'({", ".join(saved_fields.keys())}) VALUES '
                  f'(?{", ?" * (fields_number - 1)})')

        cursor = connection.cursor()
        cursor.execute(sql, tuple(saved_fields.values()))
        return True

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
        cursor.execute(sql, upd_fields)
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
    def fusions_list(connection) -> List:

        cursor = connection.cursor()
        cursor.execute('SELECT fusion_id, name FROM fusions')
        return list(map(list, cursor.fetchall()))


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


class OrderDataService (StandardDataService):

    @staticmethod
    @db_connector
    def get_table(connection, table: str) -> List:

        sql = str('SELECT orders.order_id, orders.name, '
                  'COUNT(DISTINCT complects.article_id) AS structure, '
                  'statuses.name, orders.current_depth, orders.efficiency '
                  'FROM orders '
                  'LEFT JOIN complects '
                  'ON orders.order_id = complects.order_id '
                  'LEFT JOIN statuses '
                  'ON statuses.status_id = orders.status_id '
                  'GROUP BY complects.order_id '
                  'ORDER BY statuses.sort_order')

        cursor = connection.cursor()
        cursor.execute(sql)
        return list(map(list, cursor.fetchall()))

    @staticmethod
    @db_connector
    def ingots(connection, order_id: TableField) -> List:

        field, value = parse_field(order_id)

        sql = str('SELECT ingots.ingot_id, fusions.name, ingots.batch, '
                  'ingots.height, ingots.width, ingots.depth '
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
                  'complects.detail_id, details.name, complects.amount, '
                  'complects.priority '
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
    def cut_blanks(connection, order_id: TableField, d: float = 0) -> Dict:

        field, value = parse_field(order_id)

        sql = str('SELECT complects.detail_id, details.name, '
                  'fusions.name, complects.amount, details.height, '
                  'details.width, details.depth '
                  'FROM complects '
                  'INNER JOIN details '
                  'ON details.detail_id=complects.detail_id '
                  f'{f"AND details.depth={d}" if d > 0 else ""} '
                  'LEFT JOIN fusions ON fusions.fusion_id=details.fusion_id '
                  f'WHERE complects.{field}={value}')

        cursor = connection.cursor()
        cursor.execute(sql)
        return list(map(list, cursor.fetchall()))


class IngotsDataService (StandardDataService):

    @staticmethod
    @db_connector
    def vacancy_ingots(connection) -> List:

        sql = str('SELECT ingots.ingot_id, fusions.name, ingots.batch, '
                  'ingots.height, ingots.width, ingots.depth '
                  'FROM ingots '
                  'LEFT JOIN fusions '
                  'ON fusions.fusion_id = ingots.fusion_id '
                  'WHERE ingots.order_id IS NULL')

        cursor = connection.cursor()
        cursor.execute(sql)
        return list(map(list, cursor.fetchall()))
