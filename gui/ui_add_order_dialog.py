# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'add_order_dialogleWatp.ui'
##
## Created by: Qt User Interface Compiler version 6.0.0
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

        self.storage = QCheckBox(self.rightArea)
        self.storage.setObjectName(u"storage")
        self.storage.setStyleSheet(u"")

        self.verticalLayout_4.addWidget(self.storage)

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

        self.ingots = QScrollArea(self.rightArea)
        self.ingots.setObjectName(u"ingots")
        self.ingots.setMinimumSize(QSize(0, 160))
        self.ingots.setMaximumSize(QSize(16777215, 160))
        self.ingots.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ingots.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.ingots.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 496, 141))
        self.ingots.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_4.addWidget(self.ingots)

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
        self.storage.setText(QCoreApplication.translate("Dialog", u"\u0417\u0430\u043a\u0430\u0437 \u043d\u0430 \u0441\u043a\u043b\u0430\u0434", None))
        self.add.setText(QCoreApplication.translate("Dialog", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c", None))
        self.cancel.setText(QCoreApplication.translate("Dialog", u"\u041e\u0442\u043c\u0435\u043d\u0430", None))
    # retranslateUi

