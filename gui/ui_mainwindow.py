# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\Projects\PyQtProjects\oci\gui\mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1491, 854)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/kras-logo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setStyleSheet("")
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tab_area = QtWidgets.QFrame(self.centralWidget)
        self.tab_area.setStyleSheet("QFrame {\n"
"    background-color: rgb(225, 225, 225);\n"
"}")
        self.tab_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.tab_area.setFrameShadow(QtWidgets.QFrame.Raised)
        self.tab_area.setObjectName("tab_area")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.tab_area)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.information = QtWidgets.QPushButton(self.tab_area)
        self.information.setEnabled(True)
        self.information.setMinimumSize(QtCore.QSize(100, 30))
        self.information.setMaximumSize(QtCore.QSize(16777215, 30))
        self.information.setStyleSheet("QPushButton {\n"
"    border: none;\n"
"    background-color: rgb(225, 225, 225);\n"
"    padding: 0px;\n"
"    color: black;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: rgb(235, 235, 235);\n"
"    border-bottom: 3px solid gray;\n"
"    font-weight: 800;\n"
"    padding-top: 3px;\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: rgb(245, 245, 245);\n"
"    border-bottom: 3px solid gray;\n"
"    font-weight: 800;\n"
"    padding-top: 3px;\n"
"}\n"
"\n"
"QPushButton:checked {\n"
"    background-color: rgb(225, 225, 225);\n"
"    border-bottom: 3px solid black;\n"
"    padding-top: 3px;\n"
"    font-weight: 800;\n"
"}")
        self.information.setCheckable(True)
        self.information.setChecked(True)
        self.information.setAutoExclusive(True)
        self.information.setObjectName("information")
        self.horizontalLayout_3.addWidget(self.information)
        self.chart = QtWidgets.QPushButton(self.tab_area)
        self.chart.setEnabled(False)
        self.chart.setMinimumSize(QtCore.QSize(100, 30))
        self.chart.setMaximumSize(QtCore.QSize(16777215, 30))
        self.chart.setStyleSheet("QPushButton:disabled {\n"
"    border: none;\n"
"    background-color: rgb(225, 225, 225);\n"
"    padding: 0px;\n"
"    color: black;\n"
"}\n"
"\n"
"QPushButton:disabled:checked {\n"
"    border-bottom: 3px solid black;\n"
"    background-color: rgb(225, 225, 225);\n"
"    padding-top: 3px;\n"
"    font-weight: 800;\n"
"    color: black;\n"
"}")
        self.chart.setCheckable(True)
        self.chart.setAutoExclusive(True)
        self.chart.setObjectName("chart")
        self.horizontalLayout_3.addWidget(self.chart)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.verticalLayout.addWidget(self.tab_area)
        self.top_area = QtWidgets.QFrame(self.centralWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.top_area.sizePolicy().hasHeightForWidth())
        self.top_area.setSizePolicy(sizePolicy)
        self.top_area.setMinimumSize(QtCore.QSize(0, 80))
        self.top_area.setStyleSheet("QFrame {\n"
"    background-color: rgb(225, 225, 225);\n"
"}")
        self.top_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.top_area.setFrameShadow(QtWidgets.QFrame.Raised)
        self.top_area.setObjectName("top_area")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.top_area)
        self.horizontalLayout_2.setContentsMargins(10, 10, 10, 5)
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.storage = QtWidgets.QToolButton(self.top_area)
        self.storage.setMinimumSize(QtCore.QSize(50, 60))
        self.storage.setMaximumSize(QtCore.QSize(16777215, 80))
        self.storage.setStyleSheet("QToolButton {\n"
"    background-color: rgb(225, 225, 225);\n"
"    border-radius: 3px;\n"
"    padding-top: 2px;\n"
"    color: black;\n"
"    border: none;\n"
"}\n"
"\n"
"QToolButton:hover {\n"
"    background-color: rgb(210, 210, 210);\n"
"}\n"
"\n"
"QToolButton:pressed {\n"
"    background-color: rgb(189, 189, 189);\n"
"    padding-left: 0px;\n"
"    padding-top: 2px;\n"
"}")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/gold-ingot.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.storage.setIcon(icon1)
        self.storage.setIconSize(QtCore.QSize(40, 40))
        self.storage.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.storage.setObjectName("storage")
        self.horizontalLayout_2.addWidget(self.storage)
        self.catalog = QtWidgets.QToolButton(self.top_area)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.catalog.sizePolicy().hasHeightForWidth())
        self.catalog.setSizePolicy(sizePolicy)
        self.catalog.setMinimumSize(QtCore.QSize(50, 60))
        self.catalog.setMaximumSize(QtCore.QSize(16777215, 80))
        self.catalog.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.catalog.setStyleSheet("QToolButton {\n"
"    background-color: rgb(225, 225, 225);\n"
"    border-radius: 3px;\n"
"    padding-top: 2px;\n"
"    color: black;\n"
"    border: none;\n"
"}\n"
"\n"
"QToolButton:hover {\n"
"    background-color: rgb(210, 210, 210);\n"
"}\n"
"\n"
"QToolButton:pressed {\n"
"    background-color: rgb(189, 189, 189);\n"
"    padding-left: 0px;\n"
"    padding-top: 2px;\n"
"}")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icons/book.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.catalog.setIcon(icon2)
        self.catalog.setIconSize(QtCore.QSize(40, 30))
        self.catalog.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.catalog.setObjectName("catalog")
        self.horizontalLayout_2.addWidget(self.catalog)
        self.settings = QtWidgets.QToolButton(self.top_area)
        self.settings.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.settings.setStyleSheet("QToolButton {\n"
"    background-color: rgb(225, 225, 225);\n"
"    border-radius: 3px;\n"
"    padding-top: 2px;\n"
"    color: black;\n"
"    border: none;\n"
"}\n"
"\n"
"QToolButton:hover {\n"
"    background-color: rgb(210, 210, 210);\n"
"}\n"
"\n"
"QToolButton:pressed {\n"
"    background-color: rgb(189, 189, 189);\n"
"    padding-left: 0px;\n"
"    padding-top: 2px;\n"
"}")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/icons/settings.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.settings.setIcon(icon3)
        self.settings.setIconSize(QtCore.QSize(40, 30))
        self.settings.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.settings.setObjectName("settings")
        self.horizontalLayout_2.addWidget(self.settings)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.verticalLayout.addWidget(self.top_area)
        self.main_area = QtWidgets.QStackedWidget(self.centralWidget)
        self.main_area.setStyleSheet("")
        self.main_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.main_area.setFrameShadow(QtWidgets.QFrame.Raised)
        self.main_area.setObjectName("main_area")
        self.order_page = QtWidgets.QWidget()
        self.order_page.setObjectName("order_page")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.order_page)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.orders_area = QtWidgets.QFrame(self.order_page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.orders_area.sizePolicy().hasHeightForWidth())
        self.orders_area.setSizePolicy(sizePolicy)
        self.orders_area.setMinimumSize(QtCore.QSize(400, 0))
        self.orders_area.setMaximumSize(QtCore.QSize(400, 16777215))
        self.orders_area.setStyleSheet("QFrame {\n"
"    background-color: rgb(232, 232, 232);\n"
"}")
        self.orders_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.orders_area.setFrameShadow(QtWidgets.QFrame.Raised)
        self.orders_area.setObjectName("orders_area")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.orders_area)
        self.verticalLayout_2.setContentsMargins(20, 20, 20, 20)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.new_order = QtWidgets.QPushButton(self.orders_area)
        self.new_order.setMinimumSize(QtCore.QSize(0, 50))
        self.new_order.setStyleSheet("QPushButton {\n"
"    background-color: rgb(215, 215, 215);\n"
"    border: 1px solid gray;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: rgb(220, 220, 220);\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: rgb(205, 205, 205);\n"
"}")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/icons/add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.new_order.setIcon(icon4)
        self.new_order.setFlat(True)
        self.new_order.setObjectName("new_order")
        self.verticalLayout_2.addWidget(self.new_order)
        self.frame = QtWidgets.QFrame(self.orders_area)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_5.setContentsMargins(0, 10, 0, 0)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.orders_view = QtWidgets.QTreeView(self.frame)
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(8)
        self.orders_view.setFont(font)
        self.orders_view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.orders_view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.orders_view.setProperty("showDropIndicator", False)
        self.orders_view.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.orders_view.setIndentation(0)
        self.orders_view.setAnimated(True)
        self.orders_view.setHeaderHidden(True)
        self.orders_view.setExpandsOnDoubleClick(False)
        self.orders_view.setObjectName("orders_view")
        self.verticalLayout_5.addWidget(self.orders_view)
        self.verticalLayout_2.addWidget(self.frame)
        self.horizontalLayout.addWidget(self.orders_area)
        self.orders_information_area = QtWidgets.QStackedWidget(self.order_page)
        self.orders_information_area.setObjectName("orders_information_area")
        self.default_page = QtWidgets.QWidget()
        self.default_page.setStyleSheet("QWidget#defaultPage {\n"
"    background-color: rgb(255, 255, 255);\n"
"}")
        self.default_page.setObjectName("default_page")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.default_page)
        self.verticalLayout_3.setContentsMargins(20, 20, 20, 20)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.default_label = QtWidgets.QLabel(self.default_page)
        self.default_label.setStyleSheet("border: 2px dashed rgb(231, 231, 231);\n"
"border-radius: 10px;")
        self.default_label.setAlignment(QtCore.Qt.AlignCenter)
        self.default_label.setObjectName("default_label")
        self.verticalLayout_3.addWidget(self.default_label)
        self.orders_information_area.addWidget(self.default_page)
        self.information_page = QtWidgets.QWidget()
        self.information_page.setStyleSheet("QWidget#informationPage {\n"
"    background-color: rgb(255, 255, 255);\n"
"}")
        self.information_page.setObjectName("information_page")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.information_page)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 20)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.order_name = QtWidgets.QLabel(self.information_page)
        self.order_name.setMinimumSize(QtCore.QSize(0, 40))
        self.order_name.setMaximumSize(QtCore.QSize(16777215, 40))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.order_name.setFont(font)
        self.order_name.setStyleSheet("QLabel {\n"
"    padding-left: 10px;\n"
"    background-color: rgb(225, 225, 225);\n"
"}")
        self.order_name.setObjectName("order_name")
        self.verticalLayout_4.addWidget(self.order_name)
        self.splitter = QtWidgets.QSplitter(self.information_page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setMinimumSize(QtCore.QSize(497, 0))
        self.splitter.setStyleSheet("QSplitter {\n"
"    padding: 0px 20px;\n"
"}")
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setOpaqueResize(False)
        self.splitter.setChildrenCollapsible(True)
        self.splitter.setObjectName("splitter")
        self.complects_area = QtWidgets.QFrame(self.splitter)
        self.complects_area.setMinimumSize(QtCore.QSize(497, 251))
        self.complects_area.setMaximumSize(QtCore.QSize(16777215, 840))
        self.complects_area.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.complects_area.setFrameShadow(QtWidgets.QFrame.Raised)
        self.complects_area.setObjectName("complects_area")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.complects_area)
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_9.setSpacing(0)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.complects_label = QtWidgets.QLabel(self.complects_area)
        self.complects_label.setMinimumSize(QtCore.QSize(0, 40))
        self.complects_label.setMaximumSize(QtCore.QSize(16777215, 40))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.complects_label.setFont(font)
        self.complects_label.setStyleSheet("QLabel {\n"
"    margin-top: 10px;\n"
"    background-color: rgb(234, 234, 234);\n"
"    border: 1px solid gray;\n"
"    border-bottom: none;\n"
"}")
        self.complects_label.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.complects_label.setObjectName("complects_label")
        self.verticalLayout_9.addWidget(self.complects_label)
        self.complects_view = QtWidgets.QTreeView(self.complects_area)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.complects_view.sizePolicy().hasHeightForWidth())
        self.complects_view.setSizePolicy(sizePolicy)
        self.complects_view.setMinimumSize(QtCore.QSize(0, 210))
        self.complects_view.setMaximumSize(QtCore.QSize(16777215, 800))
        self.complects_view.viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.complects_view.setStyleSheet("QTreeView {\n"
"    border: 1px solid gray;\n"
"}\n"
"\n"
"\n"
"QHeaderView::section {\n"
"    background-color: rgb(231, 231, 231);\n"
"    padding-left: 10px;\n"
"    border: 1px solid gray;\n"
"    border-left: none;\n"
"    border-top: none;\n"
"}\n"
"\n"
"QHeaderView::section:last {\n"
"    background-color: rgb(231, 231, 231);\n"
"    padding-left: 10px;\n"
"    border: 1px solid gray;\n"
"    border-left: none;\n"
"    border-right: none;\n"
"    border-top: none;\n"
"}\n"
"\n"
"QTreeView::branch:has-siblings:!adjoins-item {\n"
"    border-image: url(:icons/vline.png) 0;\n"
"}\n"
"\n"
"QTreeView::branch:has-siblings:adjoins-item {\n"
"    border-image: url(:icons/branch-more.png) 0;\n"
"}\n"
"\n"
"QTreeView::branch:!has-children:!has-siblings:adjoins-item {\n"
"    border-image: url(:icons/branch-end.png) 0;\n"
"}\n"
"\n"
"QTreeView::branch:has-children:!has-siblings:closed,\n"
"QTreeView::branch:closed:has-children:has-siblings {\n"
"        border-image: none;\n"
"        image: url(:icons/branch-closed.png);\n"
"}\n"
"\n"
"QTreeView::branch:open:has-children:!has-siblings,\n"
"QTreeView::branch:open:has-children:has-siblings  {\n"
"        border-image: none;\n"
"        image: url(:icons/branch-open.png);\n"
"}")
        self.complects_view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.complects_view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.complects_view.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked|QtWidgets.QAbstractItemView.SelectedClicked)
        self.complects_view.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.complects_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.complects_view.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.complects_view.setAnimated(True)
        self.complects_view.setObjectName("complects_view")
        self.verticalLayout_9.addWidget(self.complects_view)
        self.ingots_area = QtWidgets.QFrame(self.splitter)
        self.ingots_area.setMinimumSize(QtCore.QSize(497, 271))
        self.ingots_area.setMaximumSize(QtCore.QSize(16777215, 271))
        self.ingots_area.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.ingots_area.setFrameShadow(QtWidgets.QFrame.Raised)
        self.ingots_area.setObjectName("ingots_area")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.ingots_area)
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_8.setSpacing(0)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.buttons = QtWidgets.QFrame(self.ingots_area)
        self.buttons.setMinimumSize(QtCore.QSize(0, 35))
        self.buttons.setMaximumSize(QtCore.QSize(16777215, 35))
        self.buttons.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.buttons.setFrameShadow(QtWidgets.QFrame.Raised)
        self.buttons.setObjectName("buttons")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout(self.buttons)
        self.horizontalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_9.setSpacing(5)
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.assign_ingot = QtWidgets.QPushButton(self.buttons)
        self.assign_ingot.setMinimumSize(QtCore.QSize(120, 35))
        self.assign_ingot.setMaximumSize(QtCore.QSize(120, 16777215))
        self.assign_ingot.setObjectName("assign_ingot")
        self.horizontalLayout_9.addWidget(self.assign_ingot)
        self.complete_order = QtWidgets.QPushButton(self.buttons)
        self.complete_order.setMinimumSize(QtCore.QSize(120, 35))
        self.complete_order.setMaximumSize(QtCore.QSize(120, 16777215))
        self.complete_order.setObjectName("complete_order")
        self.horizontalLayout_9.addWidget(self.complete_order)
        self.recalculate = QtWidgets.QPushButton(self.buttons)
        self.recalculate.setMinimumSize(QtCore.QSize(120, 35))
        self.recalculate.setMaximumSize(QtCore.QSize(120, 16777215))
        self.recalculate.setObjectName("recalculate")
        self.horizontalLayout_9.addWidget(self.recalculate)
        self.plan = QtWidgets.QPushButton(self.buttons)
        self.plan.setMinimumSize(QtCore.QSize(120, 35))
        self.plan.setMaximumSize(QtCore.QSize(120, 16777215))
        self.plan.setObjectName("plan")
        self.horizontalLayout_9.addWidget(self.plan)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_9.addItem(spacerItem2)
        self.verticalLayout_8.addWidget(self.buttons)
        self.ingots_label = QtWidgets.QLabel(self.ingots_area)
        self.ingots_label.setMinimumSize(QtCore.QSize(0, 40))
        self.ingots_label.setMaximumSize(QtCore.QSize(16777215, 40))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.ingots_label.setFont(font)
        self.ingots_label.setStyleSheet("QLabel {\n"
"    margin-top: 10px;\n"
"    background-color: rgb(234, 234, 234);\n"
"    border: 1px solid gray;\n"
"    border-bottom: none;\n"
"}")
        self.ingots_label.setObjectName("ingots_label")
        self.verticalLayout_8.addWidget(self.ingots_label)
        self.ingots_view = QtWidgets.QListView(self.ingots_area)
        self.ingots_view.setMinimumSize(QtCore.QSize(0, 195))
        self.ingots_view.setMaximumSize(QtCore.QSize(16777215, 195))
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(8)
        self.ingots_view.setFont(font)
        self.ingots_view.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.ingots_view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.ingots_view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.ingots_view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.ingots_view.setProperty("showDropIndicator", False)
        self.ingots_view.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.ingots_view.setFlow(QtWidgets.QListView.LeftToRight)
        self.ingots_view.setObjectName("ingots_view")
        self.verticalLayout_8.addWidget(self.ingots_view)
        self.verticalLayout_4.addWidget(self.splitter)
        self.orders_information_area.addWidget(self.information_page)
        self.horizontalLayout.addWidget(self.orders_information_area)
        self.main_area.addWidget(self.order_page)
        self.chart_page = QtWidgets.QWidget()
        self.chart_page.setObjectName("chart_page")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.chart_page)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.chart_information_area = QtWidgets.QFrame(self.chart_page)
        self.chart_information_area.setMinimumSize(QtCore.QSize(700, 0))
        self.chart_information_area.setMaximumSize(QtCore.QSize(700, 16777215))
        self.chart_information_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.chart_information_area.setFrameShadow(QtWidgets.QFrame.Raised)
        self.chart_information_area.setObjectName("chart_information_area")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.chart_information_area)
        self.verticalLayout_7.setContentsMargins(20, 20, 20, 20)
        self.verticalLayout_7.setSpacing(10)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.ingots_residuals_view = QtWidgets.QTreeView(self.chart_information_area)
        self.ingots_residuals_view.setMinimumSize(QtCore.QSize(0, 200))
        self.ingots_residuals_view.setMaximumSize(QtCore.QSize(16777215, 200))
        self.ingots_residuals_view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.ingots_residuals_view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.ingots_residuals_view.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.ingots_residuals_view.setIndentation(20)
        self.ingots_residuals_view.setAnimated(True)
        self.ingots_residuals_view.setExpandsOnDoubleClick(False)
        self.ingots_residuals_view.setObjectName("ingots_residuals_view")
        self.verticalLayout_7.addWidget(self.ingots_residuals_view)
        self.turn_based_map_view = QtWidgets.QTableView(self.chart_information_area)
        self.turn_based_map_view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.turn_based_map_view.setObjectName("turn_based_map_view")
        self.verticalLayout_7.addWidget(self.turn_based_map_view)
        self.horizontalLayout_4.addWidget(self.chart_information_area)
        self.chart_area = QtWidgets.QFrame(self.chart_page)
        self.chart_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.chart_area.setFrameShadow(QtWidgets.QFrame.Raised)
        self.chart_area.setObjectName("chart_area")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.chart_area)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.heigths_scroll_area = QtWidgets.QScrollArea(self.chart_area)
        self.heigths_scroll_area.setMaximumSize(QtCore.QSize(16777215, 47))
        self.heigths_scroll_area.setStyleSheet("QScrollArea {\n"
"    background-color: rgb(255, 255, 255);\n"
"}\n"
"\n"
"QScrollBar:horizontal {\n"
"    border: none;\n"
"    background: rgb(255, 255, 255);\n"
"    height: 7px;\n"
"}\n"
"\n"
"QScrollBar::handle:horizontal {\n"
"    background-color: rgb(180, 180, 180);\n"
"    min-width: 30px;\n"
"}\n"
"\n"
"QScrollBar::handle:horizontal:hover {\n"
"    background-color: rgb(255, 145, 67);\n"
"}\n"
"\n"
"QScrollBar::handle:horizontal:pressed {\n"
"    background-color: rgb(223, 124, 59);\n"
"}\n"
"\n"
"QScrollBar::sub-line:horizontal {\n"
"    border: none;\n"
"    background-color: rgb(255, 255, 255);\n"
"    width: 7px;\n"
"    subcontrol-position: left;\n"
"    subcontrol-origin: margin;\n"
"}\n"
"\n"
"QScrollBar::add-line:horizontal {\n"
"    border: none;\n"
"    background-color: rgb(255, 255, 255);\n"
"    width: 7px;\n"
"    subcontrol-position: right;\n"
"    subcontrol-origin: margin;\n"
"}\n"
"\n"
"QScrollBar::up-arrow:horizontal, QScrollBar::down-arrow:horizontal {\n"
"    background: none;\n"
"}\n"
"\n"
"QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {\n"
"    background: none;\n"
"}")
        self.heigths_scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.heigths_scroll_area.setFrameShadow(QtWidgets.QFrame.Plain)
        self.heigths_scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.heigths_scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.heigths_scroll_area.setWidgetResizable(True)
        self.heigths_scroll_area.setObjectName("heigths_scroll_area")
        self.heigths_content = QtWidgets.QWidget()
        self.heigths_content.setGeometry(QtCore.QRect(0, 0, 791, 40))
        self.heigths_content.setObjectName("heigths_content")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.heigths_content)
        self.horizontalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_7.setSpacing(0)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.heigths_layout = QtWidgets.QHBoxLayout()
        self.heigths_layout.setContentsMargins(0, 0, 0, 0)
        self.heigths_layout.setSpacing(0)
        self.heigths_layout.setObjectName("heigths_layout")
        self.horizontalLayout_7.addLayout(self.heigths_layout)
        self.heigths_scroll_area.setWidget(self.heigths_content)
        self.verticalLayout_6.addWidget(self.heigths_scroll_area)
        self.horizontalLayout_4.addWidget(self.chart_area)
        self.main_area.addWidget(self.chart_page)
        self.verticalLayout.addWidget(self.main_area)
        self.main_area.raise_()
        self.top_area.raise_()
        self.tab_area.raise_()
        MainWindow.setCentralWidget(self.centralWidget)

        self.retranslateUi(MainWindow)
        self.main_area.setCurrentIndex(0)
        self.orders_information_area.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Раскрой слитка"))
        self.information.setText(_translate("MainWindow", "Заказы"))
        self.chart.setText(_translate("MainWindow", "Карта раскроя"))
        self.storage.setText(_translate("MainWindow", "Склад\n"
"слитков"))
        self.catalog.setText(_translate("MainWindow", "Cправочник\n"
"заготовок"))
        self.settings.setText(_translate("MainWindow", "Настройки"))
        self.new_order.setText(_translate("MainWindow", "Добавить заказ"))
        self.default_label.setText(_translate("MainWindow", "Заказ не выбран"))
        self.order_name.setText(_translate("MainWindow", "Номер заказа"))
        self.complects_label.setText(_translate("MainWindow", "Заготовки"))
        self.assign_ingot.setText(_translate("MainWindow", "Добавить\n"
"слиток"))
        self.complete_order.setText(_translate("MainWindow", "Завершить\n"
"заказ"))
        self.recalculate.setText(_translate("MainWindow", "Пересчитать"))
        self.plan.setText(_translate("MainWindow", "Карта раскроя"))
        self.ingots_label.setText(_translate("MainWindow", "Выбранный металл"))
import application_rc
