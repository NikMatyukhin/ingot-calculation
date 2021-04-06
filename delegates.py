from PySide6.QtWidgets import (
    QItemDelegate, QWidget, QStyleOptionViewItem, QComboBox
)
from PySide6.QtCore import (
    QModelIndex, Qt, QAbstractItemModel
)


class ListValuesDelegate(QItemDelegate):

    def __init__(self, names_list, parent=None):
        super(ListValuesDelegate, self).__init__(parent)
        self.names = names_list

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem,
                     index: QModelIndex) -> QWidget:
        editor = QComboBox(parent)
        editor.addItems(self.names)
        return editor

    def setEditorData(self, editor: QWidget, index: QModelIndex):
        value = index.model().data(index, Qt.EditRole)
        editor.setCurrentIndex(self.names.index(value))

    def setModelData(self, editor: QWidget, model: QAbstractItemModel,
                     index: QModelIndex):
        value = editor.currentText()
        model.setData(index, value, Qt.EditRole)

    def updateEditorGeometry(self, editor: QWidget,
                             option: QStyleOptionViewItem, index: QModelIndex):
        editor.setGeometry(option.rect)
