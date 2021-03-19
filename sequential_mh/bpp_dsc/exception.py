"""Модуль исключений библиотеки"""


class BPPError(Exception):
    """Общий базовый класс для всех исключений"""


class SizeError(BPPError):
    """Класс для исключений, связанных с некорректными размерами"""


class MaterialError(BPPError):
    """Исключения, связанные с материалом"""


class NodeError(BPPError):
    """Базовый класс для всех исключений, связанных с узлами дерева"""


class ParentNodeError(NodeError):
    """Некорректный предок узла"""


class ChildrenNodeError(NodeError):
    """Некорректный потомок узла"""


class NodeTypeError(NodeError):
    """Некорректны тип узла"""


class OperationNodeError(NodeError):
    """Класс исключений, связанных с узлами операций"""


class OperationTypeError(NodeTypeError):
    """Некорректны тип узла операций"""


class KitError(BPPError):
    """Общий класс исключений, связанных с набором заготовок"""


class DirectionError(BPPError):
    """Ошибки направлений"""
