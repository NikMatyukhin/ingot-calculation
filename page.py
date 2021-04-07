from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QTreeWidgetItem, QGraphicsScene,
    QGraphicsView, QDialog
)
from plate import Plate
from charts.map import CuttingMapPainter
from gui import ui_order_page, ui_full_screen


class OrderPage (QWidget):

    def __init__(self):
        super(OrderPage, self).__init__()
        self.ui = ui_order_page.Ui_Form()
        self.ui.setupUi(self)

        self.scene = QGraphicsScene()
        self.map_painter = CuttingMapPainter(self.scene)
        self.ui.graphicsView.setScene(self.scene)
        self.ui.fullScreen.clicked.connect(self.openFullScreen)

    def hideForStatus(self, status: int):
        """Скрывает ненужные элементы интерфейса

        Если статус <В работе> и <В ожидании>, то скрыть статистику и остатки.
        Если статус <Завершён>, то скрыть кнопку перехода к подробному плану.
        """
        if status == 1 or status == 2:
            self.ui.label_4.hide()
            self.ui.label_5.hide()
            self.ui.label_6.hide()
            self.ui.scrollArea_3.hide()
        elif status == 4 or status == 5:
            self.ui.detailedPlan.hide()

    def setPageTitle(self, name: str, on_storage: bool = False):
        """Назначение названия заказа"""
        storage = ' (на склад)' if int(on_storage) else ''
        self.ui.label.setText('Заказ ' + name + storage)

    def setComplects(self, complects: dict):
        """Назначение списка изделий и деталей заказа"""
        for article, details in complects.items():
            article_item = QTreeWidgetItem(
                self.ui.treeWidget, [article[1], None, None, None, None, None])
            for detail in details:
                detail_item = QTreeWidgetItem(
                    article_item, [detail[1], str(detail[4]), str(detail[5]), str(detail[6]), str(detail[2]), str(detail[3])])
                for column in range(1, 6):
                    detail_item.setTextAlignment(column, Qt.AlignCenter)
            self.ui.treeWidget.addTopLevelItem(article_item)
        self.ui.treeWidget.expandAll()
        for column in range(6):
            self.ui.treeWidget.resizeColumnToContents(column)

    def setIngots(self, ingots: list):
        """Назначение слитков заказа"""
        ingots_layout = QHBoxLayout()
        for ingot in ingots:
            ingot_plate = Plate(ingot[0], ingot[1], ingot[2], ingot[3:])
            ingots_layout.addWidget(ingot_plate)
        ingots_layout.setContentsMargins(0, 0, 0, 0)
        ingots_layout.setSpacing(0)
        ingots_layout.addStretch()
        self.ui.scrollAreaWidgetContents_3.setLayout(ingots_layout)

    def drawCuttingMap(self, tree, efficiency):
        self.map_painter.setTree(tree)
        self.map_painter.setEfficiency(efficiency)
        self.map_painter.drawTree()

    def openFullScreen(self):
        window = FullScreenWindow(self)
        window.ui.graphicsView.setScene(self.scene)
        window.setWindowTitle('Карта: полноэкранный режим')
        window.show()


class FullScreenWindow (QDialog):

    def __init__(self, parent=None):
        super(FullScreenWindow, self).__init__(parent)
        self.ui = ui_full_screen.Ui_Dialog()
        self.ui.setupUi(self)

        self.setWindowFlags(Qt.Window)