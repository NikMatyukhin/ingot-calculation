# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'order_pagebZBRSO.ui'
##
## Created by: Qt User Interface Compiler version 6.0.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(627, 1476)
        Form.setMinimumSize(QSize(627, 0))
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(Form)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(0, 40))
        self.label.setMaximumSize(QSize(16777215, 40))
        font = QFont()
        font.setPointSize(14)
        self.label.setFont(font)
        self.label.setStyleSheet(u"QLabel {\n"
"	padding-left: 10px;\n"
"	background-color: rgb(225, 225, 225);\n"
"}")

        self.verticalLayout.addWidget(self.label)

        self.scrollArea = QScrollArea(Form)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setStyleSheet(u"QScrollArea {\n"
"	padding-left: 20px;\n"
"	padding-right: 7px;\n"
"	background-color: rgb(255, 255, 255);\n"
"}\n"
"\n"
"QScrollBar:vertical {\n"
"	border: none;\n"
"	margin-top: 5px;\n"
"	margin-bottom: 5px;\n"
"	background: rgb(255, 255, 255);\n"
"	width: 7px;\n"
"}\n"
"\n"
"QScrollBar::handle:vertical {\n"
"	background-color: rgb(180, 180, 180);\n"
"	min-height: 30px;\n"
"	border-radius: 3px;\n"
"}\n"
"\n"
"QScrollBar::handle:vertical:hover {\n"
"	background-color: rgb(255, 145, 67);\n"
"}\n"
"\n"
"QScrollBar::handle:vertical:pressed {\n"
"	background-color: rgb(223, 124, 59);\n"
"}\n"
"\n"
"QScrollBar::sub-line:vertical {\n"
"	border: none;\n"
"	background-color: rgb(255, 255, 255);\n"
"	height: 7px;\n"
"	subcontrol-position: top;\n"
"	subcontrol-origin: margin;\n"
"}\n"
"\n"
"QScrollBar::add-line:vertical {\n"
"	border: none;\n"
"	background-color: rgb(255, 255, 255);\n"
"	height: 7px;\n"
"	subcontrol-position: bottom;\n"
"	subcontrol-origin: margin;\n"
"}\n"
"\n"
"QScrollBar::up-arrow:vertical, QScrollB"
                        "ar::down-arrow:vertical {\n"
"	background: none;\n"
"}\n"
"\n"
"QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {\n"
"	background: none;\n"
"}")
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 593, 1462))
        self.scrollAreaWidgetContents.setStyleSheet(u"* {\n"
"	margin-right: 7px;\n"
"}\n"
"\n"
"QScrollArea, QFrame, QLabel, QWidget#scrollAreaWidgetContents, QWidget#scrollAreaWidgetContents_2, QWidget#scrollAreaWidgetContents_3 {\n"
"	background-color: rgb(255, 255, 255);\n"
"}\n"
"\n"
"QLabel {\n"
"	margin-top: 10px;\n"
"}\n"
"\n"
"	")
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 20)
        self.label_2 = QLabel(self.scrollAreaWidgetContents)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMinimumSize(QSize(0, 40))
        self.label_2.setMaximumSize(QSize(16777215, 40))
        self.label_2.setFont(font)
        self.label_2.setStyleSheet(u"QLabel {\n"
"	background-color: rgb(234, 234, 234);\n"
"}")

        self.verticalLayout_2.addWidget(self.label_2)

        self.treeWidget = QTreeWidget(self.scrollAreaWidgetContents)
        self.treeWidget.setObjectName(u"treeWidget")
        self.treeWidget.setMinimumSize(QSize(0, 300))
        self.treeWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.treeWidget.setAlternatingRowColors(True)
        self.treeWidget.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.treeWidget.setAnimated(True)
        self.treeWidget.header().setStretchLastSection(True)

        self.verticalLayout_2.addWidget(self.treeWidget)

        self.label_3 = QLabel(self.scrollAreaWidgetContents)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setMinimumSize(QSize(0, 40))
        self.label_3.setMaximumSize(QSize(16777215, 40))
        self.label_3.setFont(font)
        self.label_3.setStyleSheet(u"QLabel {\n"
"	background-color: rgb(234, 234, 234);\n"
"}")

        self.verticalLayout_2.addWidget(self.label_3)

        self.scrollArea_2 = QScrollArea(self.scrollAreaWidgetContents)
        self.scrollArea_2.setObjectName(u"scrollArea_2")
        self.scrollArea_2.setMinimumSize(QSize(0, 160))
        self.scrollArea_2.setMaximumSize(QSize(16777215, 160))
        self.scrollArea_2.setStyleSheet(u"QScrollArea {\n"
"	padding: 0px;\n"
"}")
        self.scrollArea_2.setFrameShape(QFrame.StyledPanel)
        self.scrollArea_2.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea_2.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollAreaWidgetContents_3 = QWidget()
        self.scrollAreaWidgetContents_3.setObjectName(u"scrollAreaWidgetContents_3")
        self.scrollAreaWidgetContents_3.setGeometry(QRect(0, 0, 577, 144))
        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_3)

        self.verticalLayout_2.addWidget(self.scrollArea_2)

        self.label_4 = QLabel(self.scrollAreaWidgetContents)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setMinimumSize(QSize(0, 40))
        self.label_4.setMaximumSize(QSize(16777215, 40))
        self.label_4.setFont(font)
        self.label_4.setStyleSheet(u"QLabel {\n"
"	background-color: rgb(234, 234, 234);\n"
"}")

        self.verticalLayout_2.addWidget(self.label_4)

        self.scrollArea_3 = QScrollArea(self.scrollAreaWidgetContents)
        self.scrollArea_3.setObjectName(u"scrollArea_3")
        self.scrollArea_3.setMinimumSize(QSize(0, 160))
        self.scrollArea_3.setMaximumSize(QSize(16777215, 160))
        self.scrollArea_3.setStyleSheet(u"QScrollArea {\n"
"	padding: 0px;\n"
"}")
        self.scrollArea_3.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea_3.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea_3.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = QWidget()
        self.scrollAreaWidgetContents_2.setObjectName(u"scrollAreaWidgetContents_2")
        self.scrollAreaWidgetContents_2.setGeometry(QRect(0, 0, 577, 144))
        self.scrollArea_3.setWidget(self.scrollAreaWidgetContents_2)

        self.verticalLayout_2.addWidget(self.scrollArea_3)

        self.detailedPlanFrame = QFrame(self.scrollAreaWidgetContents)
        self.detailedPlanFrame.setObjectName(u"detailedPlanFrame")
        self.detailedPlanFrame.setStyleSheet(u"* {\n"
"	margin-right: 0px;\n"
"}")
        self.detailedPlanFrame.setFrameShape(QFrame.NoFrame)
        self.detailedPlanFrame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.detailedPlanFrame)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.label_7 = QLabel(self.detailedPlanFrame)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setMinimumSize(QSize(0, 40))
        self.label_7.setMaximumSize(QSize(16777215, 40))
        self.label_7.setFont(font)
        self.label_7.setStyleSheet(u"QLabel {\n"
"	background-color: rgb(234, 234, 234);\n"
"}")

        self.horizontalLayout.addWidget(self.label_7)

        self.fullScreen = QPushButton(self.detailedPlanFrame)
        self.fullScreen.setObjectName(u"fullScreen")
        self.fullScreen.setMinimumSize(QSize(120, 40))
        self.fullScreen.setMaximumSize(QSize(120, 40))
        self.fullScreen.setStyleSheet(u"QPushButton {\n"
"	margin-top: 10px;\n"
"	border: none;\n"
"	background-color: rgb(234, 234, 234);\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	background-color: rgb(216, 216, 216);\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"	background-color: rgb(200, 200, 200);\n"
"}")

        self.horizontalLayout.addWidget(self.fullScreen)

        self.detailedPlan = QPushButton(self.detailedPlanFrame)
        self.detailedPlan.setObjectName(u"detailedPlan")
        self.detailedPlan.setMinimumSize(QSize(120, 40))
        self.detailedPlan.setMaximumSize(QSize(120, 40))
        self.detailedPlan.setStyleSheet(u"QPushButton {\n"
"	margin-top: 10px;\n"
"	margin-right: 7px;\n"
"	border: none;\n"
"	background-color: rgb(234, 234, 234);\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	background-color: rgb(216, 216, 216);\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"	background-color: rgb(200, 200, 200);\n"
"}")

        self.horizontalLayout.addWidget(self.detailedPlan)


        self.verticalLayout_2.addWidget(self.detailedPlanFrame)

        self.graphicsView = QGraphicsView(self.scrollAreaWidgetContents)
        self.graphicsView.setObjectName(u"graphicsView")
        self.graphicsView.setMinimumSize(QSize(0, 500))
        self.graphicsView.setDragMode(QGraphicsView.ScrollHandDrag)

        self.verticalLayout_2.addWidget(self.graphicsView)

        self.label_5 = QLabel(self.scrollAreaWidgetContents)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setMinimumSize(QSize(0, 40))
        self.label_5.setMaximumSize(QSize(16777215, 40))
        self.label_5.setFont(font)
        self.label_5.setStyleSheet(u"QLabel {\n"
"	background-color: rgb(234, 234, 234);\n"
"}")

        self.verticalLayout_2.addWidget(self.label_5)

        self.label_6 = QLabel(self.scrollAreaWidgetContents)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setTextFormat(Qt.AutoText)

        self.verticalLayout_2.addWidget(self.label_6)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label.setText(QCoreApplication.translate("Form", u"\u041d\u043e\u043c\u0435\u0440 \u0437\u0430\u043a\u0430\u0437\u0430", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"\u0412\u044b\u0431\u0440\u0430\u043d\u043d\u044b\u0435 \u0434\u0435\u0442\u0430\u043b\u0438", None))
        ___qtreewidgetitem = self.treeWidget.headerItem()
        ___qtreewidgetitem.setText(6, QCoreApplication.translate("Form", u"\u0421\u0442\u0430\u0442\u0443\u0441", None));
        ___qtreewidgetitem.setText(5, QCoreApplication.translate("Form", u"\u041f\u0440\u0438\u043e\u0440\u0438\u0442\u0435\u0442", None));
        ___qtreewidgetitem.setText(4, QCoreApplication.translate("Form", u"\u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e", None));
        ___qtreewidgetitem.setText(3, QCoreApplication.translate("Form", u"\u0422\u043e\u043b\u0449\u0438\u043d\u0430", None));
        ___qtreewidgetitem.setText(2, QCoreApplication.translate("Form", u"\u0428\u0438\u0440\u0438\u043d\u0430", None));
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("Form", u"\u0414\u043b\u0438\u043d\u0430", None));
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("Form", u"\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435", None));
        self.label_3.setText(QCoreApplication.translate("Form", u"\u0412\u044b\u0431\u0440\u0430\u043d\u043d\u044b\u0435 \u0441\u043b\u0438\u0442\u043a\u0438", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"\u041e\u0441\u0442\u0430\u0442\u043a\u0438 \u0441\u043e \u0441\u043b\u0438\u0442\u043a\u043e\u0432", None))
        self.label_7.setText(QCoreApplication.translate("Form", u"\u041a\u0430\u0440\u0442\u0430 \u0440\u0430\u0441\u043a\u0440\u043e\u044f", None))
        self.fullScreen.setText(QCoreApplication.translate("Form", u"\u041d\u0430 \u0432\u0435\u0441\u044c \u044d\u043a\u0440\u0430\u043d", None))
        self.detailedPlan.setText(QCoreApplication.translate("Form", u"\u041f\u0435\u0440\u0435\u0439\u0442\u0438 \u043a \u043f\u043b\u0430\u043d\u0443", None))
        self.label_5.setText(QCoreApplication.translate("Form", u"\u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430 \u043f\u043e \u0437\u0430\u043a\u0430\u0437\u0443", None))
        self.label_6.setText(QCoreApplication.translate("Form", u"\u0412\u044b\u0445\u043e\u0434 \u0433\u043e\u0434\u043d\u043e\u0433\u043e:\n"
"\n"
"\u0413\u043e\u0442\u043e\u0432\u044b\u0445 \u0434\u0435\u0442\u0430\u043b\u0435\u0439:\n"
"\u041d\u0435\u0443\u043a\u043e\u043c\u043f\u043b\u0435\u043a\u0442\u043e\u0432\u0430\u043d\u043d\u044b\u0445 \u0434\u0435\u0442\u0430\u043b\u0435\u0439:\n"
"\n"
"\u0414\u0435\u0444\u0435\u043a\u0442\u043e\u0432 \u0440\u0430\u0441\u043a\u0440\u043e\u044f:\n"
"\u0417\u0430\u0431\u0440\u0430\u043a\u043e\u0432\u0430\u043d\u043d\u044b\u0445 \u0434\u0435\u0442\u0430\u043b\u0435\u0439:", None))
    # retranslateUi

