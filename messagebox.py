"""Модуль всплывающих сообщений"""


from PyQt5.QtWidgets import QMessageBox


def message_box_info(message: str, parent=None):
    """Информационное сообщение"""
    return QMessageBox.information(parent, 'Внимание', message, QMessageBox.Ok)


def message_box_error(message: str, parent=None):
    """Сообщение об ошибке"""
    return QMessageBox.warning(parent, 'Ошибка', message, QMessageBox.Ok)
