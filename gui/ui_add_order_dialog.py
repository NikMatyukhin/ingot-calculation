# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'add_order_dialogNYHVjt.ui'
##
## Created by: Qt User Interface Compiler version 6.0.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(1062, 654)
        Dialog.setContextMenuPolicy(Qt.CustomContextMenu)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.mainArea = QFrame(Dialog)
        self.mainArea.setObjectName(u"mainArea")
        self.mainArea.setFrameShape(QFrame.NoFrame)
        self.mainArea.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.mainArea)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.splitter = QSplitter(self.mainArea)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setStyleSheet(u"QSplitter::handle {\n"
"	background: rgb(231, 231, 231);\n"
"}")
        self.splitter.setOrientation(Qt.Horizontal)
        self.leftArea = QFrame(self.splitter)
        self.leftArea.setObjectName(u"leftArea")
        self.leftArea.setStyleSheet(u"QFrame {\n"
"	background-color: rgb(231, 231, 231);\n"
"}")
        self.leftArea.setFrameShape(QFrame.NoFrame)
        self.leftArea.setFrameShadow(QFrame.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.leftArea)
        self.verticalLayout_3.setSpacing(10)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(10, 10, 10, 10)
        self.searchName = QLineEdit(self.leftArea)
        self.searchName.setObjectName(u"searchName")
        self.searchName.setMinimumSize(QSize(0, 25))
        self.searchName.setStyleSheet(u"QLineEdit {\n"
"	background-color: rgb(255, 255, 255);\n"
"}")

        self.verticalLayout_3.addWidget(self.searchName)

        self.treeView_1 = QTreeView(self.leftArea)
        self.treeView_1.setObjectName(u"treeView_1")
        self.treeView_1.setStyleSheet(u"QTreeView {\n"
"	border: 1px solid gray;\n"
"	background-color: white;\n"
"}\n"
"\n"
"QTreeView::item {\n"
"    margin-top: 3px;\n"
"}\n"
"\n"
"QHeaderView::section {\n"
"	background-color: rgb(231, 231, 231);\n"
"	padding-left: 10px;\n"
"	border: 1px solid gray;\n"
"	border-left: none;\n"
"	border-top: none;\n"
"}")
        self.treeView_1.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.treeView_1.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.treeView_1.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.treeView_1.setAnimated(True)
        self.treeView_1.setWordWrap(True)

        self.verticalLayout_3.addWidget(self.treeView_1)

        self.splitter.addWidget(self.leftArea)
        self.rightArea = QFrame(self.splitter)
        self.rightArea.setObjectName(u"rightArea")
        self.rightArea.setFrameShape(QFrame.NoFrame)
        self.rightArea.setFrameShadow(QFrame.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.rightArea)
        self.verticalLayout_4.setSpacing(10)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(20, 10, 10, 10)
        self.orderName = QLineEdit(self.rightArea)
        self.orderName.setObjectName(u"orderName")
        self.orderName.setMinimumSize(QSize(0, 25))
        self.orderName.setStyleSheet(u"")

        self.verticalLayout_4.addWidget(self.orderName)

        self.frame = QFrame(self.rightArea)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame)
        self.horizontalLayout_3.setSpacing(5)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.line = QFrame(self.frame)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.VLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.horizontalLayout_3.addWidget(self.line)

        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")
        self.label.setEnabled(False)

        self.horizontalLayout_3.addWidget(self.label)

        self.doubleSpinBox = QDoubleSpinBox(self.frame)
        self.doubleSpinBox.setObjectName(u"doubleSpinBox")
        self.doubleSpinBox.setEnabled(False)

        self.horizontalLayout_3.addWidget(self.doubleSpinBox)

        self.line_2 = QFrame(self.frame)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.VLine)
        self.line_2.setFrameShadow(QFrame.Sunken)

        self.horizontalLayout_3.addWidget(self.line_2)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)


        self.verticalLayout_4.addWidget(self.frame)

        self.treeView_2 = QTreeView(self.rightArea)
        self.treeView_2.setObjectName(u"treeView_2")
        self.treeView_2.setStyleSheet(u"QTreeWidget {\n"
"	border: 1px solid gray;\n"
"}\n"
"\n"
"QTreeWidget::item {\n"
"    margin-top: 3px;\n"
"}\n"
"\n"
"QHeaderView::section {\n"
"	background-color: rgb(231, 231, 231);\n"
"	padding-left: 10px;\n"
"	border: 1px solid gray;\n"
"	border-left: none;\n"
"	border-top: none;\n"
"}")
        self.treeView_2.setAnimated(True)
        self.treeView_2.setWordWrap(True)

        self.verticalLayout_4.addWidget(self.treeView_2)

        self.ingotsView = QListView(self.rightArea)
        self.ingotsView.setObjectName(u"ingotsView")
        self.ingotsView.setMinimumSize(QSize(0, 195))
        self.ingotsView.setMaximumSize(QSize(16777215, 195))
        self.ingotsView.setFrameShadow(QFrame.Plain)
        self.ingotsView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ingotsView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ingotsView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ingotsView.setProperty("showDropIndicator", False)
        self.ingotsView.setSelectionMode(QAbstractItemView.MultiSelection)
        self.ingotsView.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.ingotsView.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.ingotsView.setFlow(QListView.LeftToRight)
        self.ingotsView.setSpacing(5)

        self.verticalLayout_4.addWidget(self.ingotsView)

        self.splitter.addWidget(self.rightArea)

        self.horizontalLayout.addWidget(self.splitter)


        self.verticalLayout.addWidget(self.mainArea)

        self.buttonArea = QFrame(Dialog)
        self.buttonArea.setObjectName(u"buttonArea")
        self.buttonArea.setMinimumSize(QSize(0, 40))
        self.buttonArea.setMaximumSize(QSize(16777215, 40))
        self.buttonArea.setStyleSheet(u"QFrame {\n"
"	background-color: rgb(231, 231, 231);\n"
"}")
        self.buttonArea.setFrameShape(QFrame.NoFrame)
        self.buttonArea.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.buttonArea)
        self.horizontalLayout_2.setSpacing(10)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 10, 0)
        self.horizontalSpacer_1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_1)

        self.add = QPushButton(self.buttonArea)
        self.add.setObjectName(u"add")
        self.add.setMinimumSize(QSize(80, 0))

        self.horizontalLayout_2.addWidget(self.add)

        self.pushButton = QPushButton(self.buttonArea)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setEnabled(False)

        self.horizontalLayout_2.addWidget(self.pushButton)

        self.cancel = QPushButton(self.buttonArea)
        self.cancel.setObjectName(u"cancel")
        self.cancel.setMinimumSize(QSize(80, 0))

        self.horizontalLayout_2.addWidget(self.cancel)


        self.verticalLayout.addWidget(self.buttonArea)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"\u041d\u043e\u0432\u044b\u0439 \u0437\u0430\u043a\u0430\u0437", None))
        self.searchName.setPlaceholderText(QCoreApplication.translate("Dialog", u"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u0438\u0437\u0434\u0435\u043b\u0438\u044f...", None))
        self.orderName.setPlaceholderText(QCoreApplication.translate("Dialog", u"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u0437\u0430\u043a\u0430\u0437\u0430...", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"\u0422\u043e\u043b\u0449\u0438\u043d\u0430 \u0440\u0435\u0437\u0430:", None))
        self.add.setText(QCoreApplication.translate("Dialog", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c", None))
        self.pushButton.setText(QCoreApplication.translate("Dialog", u"\u0420\u0430\u0441\u0441\u0447\u0438\u0442\u0430\u0442\u044c", None))
        self.cancel.setText(QCoreApplication.translate("Dialog", u"\u041e\u0442\u043c\u0435\u043d\u0430", None))
    # retranslateUi

