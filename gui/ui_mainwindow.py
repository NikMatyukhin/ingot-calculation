# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindowITUiXe.ui'
##
## Created by: Qt User Interface Compiler version 6.0.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import application_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1115, 704)
        icon = QIcon()
        icon.addFile(u":/icons/kras-logo.png", QSize(), QIcon.Normal, QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setStyleSheet(u"")
        self.centralWidget = QWidget(MainWindow)
        self.centralWidget.setObjectName(u"centralWidget")
        self.verticalLayout = QVBoxLayout(self.centralWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.pageBar = QFrame(self.centralWidget)
        self.pageBar.setObjectName(u"pageBar")
        self.pageBar.setStyleSheet(u"QFrame {\n"
"	background-color: rgb(225, 225, 225);\n"
"}")
        self.pageBar.setFrameShape(QFrame.NoFrame)
        self.pageBar.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.pageBar)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.information = QPushButton(self.pageBar)
        self.information.setObjectName(u"information")
        self.information.setEnabled(True)
        self.information.setMinimumSize(QSize(100, 30))
        self.information.setMaximumSize(QSize(16777215, 30))
        self.information.setStyleSheet(u"QPushButton {\n"
"	border: none;\n"
"	background-color: rgb(225, 225, 225);\n"
"	padding: 0px;\n"
"	color: black;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	background-color: rgb(235, 235, 235);\n"
"	border-bottom: 3px solid gray;\n"
"	font-weight: 800;\n"
"	padding-top: 3px;\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"	background-color: rgb(245, 245, 245);\n"
"	border-bottom: 3px solid gray;\n"
"	font-weight: 800;\n"
"	padding-top: 3px;\n"
"}\n"
"\n"
"QPushButton:checked {\n"
"	background-color: rgb(225, 225, 225);\n"
"	border-bottom: 3px solid black;\n"
"	padding-top: 3px;\n"
"	font-weight: 800;\n"
"}")
        self.information.setCheckable(True)
        self.information.setChecked(True)
        self.information.setAutoExclusive(True)

        self.horizontalLayout_3.addWidget(self.information)

        self.chart = QPushButton(self.pageBar)
        self.chart.setObjectName(u"chart")
        self.chart.setEnabled(False)
        self.chart.setMinimumSize(QSize(100, 30))
        self.chart.setMaximumSize(QSize(16777215, 30))
        self.chart.setStyleSheet(u"QPushButton:disabled {\n"
"	border: none;\n"
"	background-color: rgb(225, 225, 225);\n"
"	padding: 0px;\n"
"	color: black;\n"
"}\n"
"\n"
"QPushButton:disabled:checked {\n"
"	border-bottom: 3px solid black;\n"
"	background-color: rgb(225, 225, 225);\n"
"	padding-top: 3px;\n"
"	font-weight: 800;\n"
"	color: black;\n"
"}")
        self.chart.setCheckable(True)
        self.chart.setAutoExclusive(True)

        self.horizontalLayout_3.addWidget(self.chart)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)


        self.verticalLayout.addWidget(self.pageBar)

        self.topBar = QFrame(self.centralWidget)
        self.topBar.setObjectName(u"topBar")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.topBar.sizePolicy().hasHeightForWidth())
        self.topBar.setSizePolicy(sizePolicy)
        self.topBar.setMinimumSize(QSize(0, 80))
        self.topBar.setStyleSheet(u"QFrame {\n"
"	background-color: rgb(225, 225, 225);\n"
"}")
        self.topBar.setFrameShape(QFrame.NoFrame)
        self.topBar.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.topBar)
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(10, 10, 10, 5)
        self.newOrder = QToolButton(self.topBar)
        self.newOrder.setObjectName(u"newOrder")
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Maximum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.newOrder.sizePolicy().hasHeightForWidth())
        self.newOrder.setSizePolicy(sizePolicy1)
        self.newOrder.setMinimumSize(QSize(50, 60))
        self.newOrder.setMaximumSize(QSize(16777215, 80))
        self.newOrder.setCursor(QCursor(Qt.PointingHandCursor))
        self.newOrder.setStyleSheet(u"QToolButton {\n"
"	background-color: rgb(225, 225, 225);\n"
"	border-radius: 3px;\n"
"	padding-top: 2px;\n"
"	color: black;\n"
"	border: none;\n"
"}\n"
"\n"
"QToolButton:hover {\n"
"	background-color: rgb(210, 210, 210);\n"
"}\n"
"\n"
"QToolButton:pressed {\n"
"	background-color: rgb(189, 189, 189);\n"
"	padding-left: 0px;\n"
"	padding-top: 2px;\n"
"}")
        icon1 = QIcon()
        icon1.addFile(u":/icons/clipboard.png", QSize(), QIcon.Normal, QIcon.Off)
        self.newOrder.setIcon(icon1)
        self.newOrder.setIconSize(QSize(30, 30))
        self.newOrder.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        self.horizontalLayout_2.addWidget(self.newOrder)

        self.newIngot = QToolButton(self.topBar)
        self.newIngot.setObjectName(u"newIngot")
        sizePolicy1.setHeightForWidth(self.newIngot.sizePolicy().hasHeightForWidth())
        self.newIngot.setSizePolicy(sizePolicy1)
        self.newIngot.setMinimumSize(QSize(50, 0))
        self.newIngot.setMaximumSize(QSize(16777215, 80))
        self.newIngot.setCursor(QCursor(Qt.PointingHandCursor))
        self.newIngot.setStyleSheet(u"QToolButton {\n"
"	background-color: rgb(225, 225, 225);\n"
"	border-radius: 3px;\n"
"	padding-top: 2px;\n"
"	color: black;\n"
"	border: none;\n"
"}\n"
"\n"
"QToolButton:hover {\n"
"	background-color: rgb(210, 210, 210);\n"
"}\n"
"\n"
"QToolButton:pressed {\n"
"	background-color: rgb(189, 189, 189);\n"
"	padding-left: 0px;\n"
"	padding-top: 2px;\n"
"}")
        icon2 = QIcon()
        icon2.addFile(u":/icons/ingot.png", QSize(), QIcon.Normal, QIcon.Off)
        self.newIngot.setIcon(icon2)
        self.newIngot.setIconSize(QSize(30, 30))
        self.newIngot.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        self.horizontalLayout_2.addWidget(self.newIngot)

        self.line_1 = QFrame(self.topBar)
        self.line_1.setObjectName(u"line_1")
        self.line_1.setMinimumSize(QSize(0, 0))
        self.line_1.setFrameShape(QFrame.VLine)
        self.line_1.setFrameShadow(QFrame.Plain)
        self.line_1.setLineWidth(1)

        self.horizontalLayout_2.addWidget(self.line_1)

        self.catalog = QToolButton(self.topBar)
        self.catalog.setObjectName(u"catalog")
        sizePolicy1.setHeightForWidth(self.catalog.sizePolicy().hasHeightForWidth())
        self.catalog.setSizePolicy(sizePolicy1)
        self.catalog.setMinimumSize(QSize(50, 60))
        self.catalog.setMaximumSize(QSize(16777215, 80))
        self.catalog.setCursor(QCursor(Qt.PointingHandCursor))
        self.catalog.setStyleSheet(u"QToolButton {\n"
"	background-color: rgb(225, 225, 225);\n"
"	border-radius: 3px;\n"
"	padding-top: 2px;\n"
"	color: black;\n"
"	border: none;\n"
"}\n"
"\n"
"QToolButton:hover {\n"
"	background-color: rgb(210, 210, 210);\n"
"}\n"
"\n"
"QToolButton:pressed {\n"
"	background-color: rgb(189, 189, 189);\n"
"	padding-left: 0px;\n"
"	padding-top: 2px;\n"
"}")
        icon3 = QIcon()
        icon3.addFile(u":/icons/book.png", QSize(), QIcon.Normal, QIcon.Off)
        self.catalog.setIcon(icon3)
        self.catalog.setIconSize(QSize(40, 30))
        self.catalog.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        self.horizontalLayout_2.addWidget(self.catalog)

        self.horizontal_spacer_1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontal_spacer_1)

        self.settings = QToolButton(self.topBar)
        self.settings.setObjectName(u"settings")
        self.settings.setCursor(QCursor(Qt.PointingHandCursor))
        self.settings.setStyleSheet(u"QToolButton {\n"
"	background-color: rgb(225, 225, 225);\n"
"	border-radius: 3px;\n"
"	padding-top: 2px;\n"
"	color: black;\n"
"	border: none;\n"
"}\n"
"\n"
"QToolButton:hover {\n"
"	background-color: rgb(210, 210, 210);\n"
"}\n"
"\n"
"QToolButton:pressed {\n"
"	background-color: rgb(189, 189, 189);\n"
"	padding-left: 0px;\n"
"	padding-top: 2px;\n"
"}")
        icon4 = QIcon()
        icon4.addFile(u":/icons/settings.png", QSize(), QIcon.Normal, QIcon.Off)
        self.settings.setIcon(icon4)
        self.settings.setIconSize(QSize(40, 30))
        self.settings.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        self.horizontalLayout_2.addWidget(self.settings)


        self.verticalLayout.addWidget(self.topBar)

        self.mainArea = QStackedWidget(self.centralWidget)
        self.mainArea.setObjectName(u"mainArea")
        self.mainArea.setStyleSheet(u"")
        self.mainArea.setFrameShape(QFrame.NoFrame)
        self.mainArea.setFrameShadow(QFrame.Raised)
        self.observerPage = QWidget()
        self.observerPage.setObjectName(u"observerPage")
        self.horizontalLayout = QHBoxLayout(self.observerPage)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.leftMenu_1 = QFrame(self.observerPage)
        self.leftMenu_1.setObjectName(u"leftMenu_1")
        self.leftMenu_1.setMaximumSize(QSize(400, 16777215))
        self.leftMenu_1.setFrameShape(QFrame.NoFrame)
        self.leftMenu_1.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.leftMenu_1)
        self.verticalLayout_2.setSpacing(10)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(20, 20, 20, 20)
        self.searchNumber = QLineEdit(self.leftMenu_1)
        self.searchNumber.setObjectName(u"searchNumber")
        self.searchNumber.setEnabled(False)
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.searchNumber.sizePolicy().hasHeightForWidth())
        self.searchNumber.setSizePolicy(sizePolicy2)
        self.searchNumber.setMinimumSize(QSize(0, 30))
        self.searchNumber.setMaximumSize(QSize(16777215, 30))
        self.searchNumber.setClearButtonEnabled(True)

        self.verticalLayout_2.addWidget(self.searchNumber)

        self.searchType = QComboBox(self.leftMenu_1)
        self.searchType.addItem("")
        self.searchType.addItem("")
        self.searchType.addItem("")
        self.searchType.addItem("")
        self.searchType.addItem("")
        self.searchType.setObjectName(u"searchType")
        self.searchType.setEnabled(False)
        sizePolicy2.setHeightForWidth(self.searchType.sizePolicy().hasHeightForWidth())
        self.searchType.setSizePolicy(sizePolicy2)
        self.searchType.setMinimumSize(QSize(0, 30))
        self.searchType.setMaximumSize(QSize(16777215, 30))
        self.searchType.setCursor(QCursor(Qt.PointingHandCursor))

        self.verticalLayout_2.addWidget(self.searchType)

        self.searchResult_1 = QListView(self.leftMenu_1)
        self.searchResult_1.setObjectName(u"searchResult_1")

        self.verticalLayout_2.addWidget(self.searchResult_1)


        self.horizontalLayout.addWidget(self.leftMenu_1)

        self.orderInformationArea = QStackedWidget(self.observerPage)
        self.orderInformationArea.setObjectName(u"orderInformationArea")
        self.defaultPage = QWidget()
        self.defaultPage.setObjectName(u"defaultPage")
        self.defaultPage.setStyleSheet(u"QWidget#defaultPage {\n"
"	background-color: rgb(255, 255, 255);\n"
"}")
        self.verticalLayout_3 = QVBoxLayout(self.defaultPage)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(20, 20, 20, 20)
        self.defaultLabel = QLabel(self.defaultPage)
        self.defaultLabel.setObjectName(u"defaultLabel")
        self.defaultLabel.setStyleSheet(u"border: 2px dashed rgb(231, 231, 231);\n"
"border-radius: 10px;")
        self.defaultLabel.setAlignment(Qt.AlignCenter)

        self.verticalLayout_3.addWidget(self.defaultLabel)

        self.orderInformationArea.addWidget(self.defaultPage)
        self.informationPage = QWidget()
        self.informationPage.setObjectName(u"informationPage")
        self.informationPage.setStyleSheet(u"QWidget#informationPage {\n"
"	background-color: rgb(255, 255, 255);\n"
"}")
        self.verticalLayout_5 = QVBoxLayout(self.informationPage)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.informationPage)
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

        self.verticalLayout_5.addWidget(self.label)

        self.scrollArea = QScrollArea(self.informationPage)
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
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 681, 1299))
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
        self.verticalLayout_4 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 20)
        self.complectsFrame = QFrame(self.scrollAreaWidgetContents)
        self.complectsFrame.setObjectName(u"complectsFrame")
        self.complectsFrame.setStyleSheet(u"* {\n"
"	margin-right: 0px;\n"
"}")
        self.complectsFrame.setFrameShape(QFrame.StyledPanel)
        self.complectsFrame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_8 = QHBoxLayout(self.complectsFrame)
        self.horizontalLayout_8.setSpacing(0)
        self.horizontalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.label_2 = QLabel(self.complectsFrame)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMinimumSize(QSize(0, 40))
        self.label_2.setMaximumSize(QSize(16777215, 40))
        self.label_2.setFont(font)
        self.label_2.setStyleSheet(u"QLabel {\n"
"	background-color: rgb(234, 234, 234);\n"
"}")

        self.horizontalLayout_8.addWidget(self.label_2)

        self.saveComplect = QPushButton(self.complectsFrame)
        self.saveComplect.setObjectName(u"saveComplect")
        self.saveComplect.setMinimumSize(QSize(120, 40))
        self.saveComplect.setMaximumSize(QSize(120, 40))
        self.saveComplect.setStyleSheet(u"QPushButton {\n"
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

        self.horizontalLayout_8.addWidget(self.saveComplect)

        self.saveComplectAndRecreate = QPushButton(self.complectsFrame)
        self.saveComplectAndRecreate.setObjectName(u"saveComplectAndRecreate")
        self.saveComplectAndRecreate.setMinimumSize(QSize(120, 40))
        self.saveComplectAndRecreate.setMaximumSize(QSize(120, 40))
        self.saveComplectAndRecreate.setStyleSheet(u"QPushButton {\n"
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

        self.horizontalLayout_8.addWidget(self.saveComplectAndRecreate)


        self.verticalLayout_4.addWidget(self.complectsFrame)

        self.complectsView = QTreeView(self.scrollAreaWidgetContents)
        self.complectsView.setObjectName(u"complectsView")
        self.complectsView.setMinimumSize(QSize(0, 300))
        self.complectsView.viewport().setProperty("cursor", QCursor(Qt.ArrowCursor))
        self.complectsView.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.complectsView.setEditTriggers(QAbstractItemView.DoubleClicked|QAbstractItemView.SelectedClicked)
        self.complectsView.setAlternatingRowColors(False)
        self.complectsView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.complectsView.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.complectsView.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.complectsView.setAnimated(True)

        self.verticalLayout_4.addWidget(self.complectsView)

        self.label_3 = QLabel(self.scrollAreaWidgetContents)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setMinimumSize(QSize(0, 40))
        self.label_3.setMaximumSize(QSize(16777215, 40))
        self.label_3.setFont(font)
        self.label_3.setStyleSheet(u"QLabel {\n"
"	background-color: rgb(234, 234, 234);\n"
"}")

        self.verticalLayout_4.addWidget(self.label_3)

        self.ingotsView = QListView(self.scrollAreaWidgetContents)
        self.ingotsView.setObjectName(u"ingotsView")
        self.ingotsView.setMinimumSize(QSize(0, 195))
        self.ingotsView.setMaximumSize(QSize(16777215, 195))
        self.ingotsView.setFrameShape(QFrame.Box)
        self.ingotsView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ingotsView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ingotsView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ingotsView.setProperty("showDropIndicator", False)
        self.ingotsView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ingotsView.setFlow(QListView.LeftToRight)

        self.verticalLayout_4.addWidget(self.ingotsView)

        self.detailedPlanFrame = QFrame(self.scrollAreaWidgetContents)
        self.detailedPlanFrame.setObjectName(u"detailedPlanFrame")
        self.detailedPlanFrame.setStyleSheet(u"* {\n"
"	margin-right: 0px;\n"
"}")
        self.detailedPlanFrame.setFrameShape(QFrame.NoFrame)
        self.detailedPlanFrame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_5 = QHBoxLayout(self.detailedPlanFrame)
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.label_7 = QLabel(self.detailedPlanFrame)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setMinimumSize(QSize(0, 40))
        self.label_7.setMaximumSize(QSize(16777215, 40))
        self.label_7.setFont(font)
        self.label_7.setStyleSheet(u"QLabel {\n"
"	background-color: rgb(234, 234, 234);\n"
"}")

        self.horizontalLayout_5.addWidget(self.label_7)

        self.recalculate = QPushButton(self.detailedPlanFrame)
        self.recalculate.setObjectName(u"recalculate")
        self.recalculate.setMinimumSize(QSize(120, 40))
        self.recalculate.setMaximumSize(QSize(120, 40))
        self.recalculate.setStyleSheet(u"QPushButton {\n"
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

        self.horizontalLayout_5.addWidget(self.recalculate)

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

        self.horizontalLayout_5.addWidget(self.fullScreen)

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

        self.horizontalLayout_5.addWidget(self.detailedPlan)


        self.verticalLayout_4.addWidget(self.detailedPlanFrame)

        self.graphicsView = QGraphicsView(self.scrollAreaWidgetContents)
        self.graphicsView.setObjectName(u"graphicsView")
        self.graphicsView.setMinimumSize(QSize(0, 500))
        self.graphicsView.setDragMode(QGraphicsView.ScrollHandDrag)

        self.verticalLayout_4.addWidget(self.graphicsView)

        self.label_5 = QLabel(self.scrollAreaWidgetContents)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setMinimumSize(QSize(0, 40))
        self.label_5.setMaximumSize(QSize(16777215, 40))
        self.label_5.setFont(font)
        self.label_5.setStyleSheet(u"QLabel {\n"
"	background-color: rgb(234, 234, 234);\n"
"}")

        self.verticalLayout_4.addWidget(self.label_5)

        self.label_6 = QLabel(self.scrollAreaWidgetContents)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setTextFormat(Qt.AutoText)

        self.verticalLayout_4.addWidget(self.label_6)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_5.addWidget(self.scrollArea)

        self.orderInformationArea.addWidget(self.informationPage)

        self.horizontalLayout.addWidget(self.orderInformationArea)

        self.mainArea.addWidget(self.observerPage)
        self.chartPage = QWidget()
        self.chartPage.setObjectName(u"chartPage")
        self.horizontalLayout_4 = QHBoxLayout(self.chartPage)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.leftMenu_2 = QFrame(self.chartPage)
        self.leftMenu_2.setObjectName(u"leftMenu_2")
        self.leftMenu_2.setMinimumSize(QSize(400, 0))
        self.leftMenu_2.setMaximumSize(QSize(400, 16777215))
        self.leftMenu_2.setFrameShape(QFrame.NoFrame)
        self.leftMenu_2.setFrameShadow(QFrame.Raised)
        self.verticalLayout_7 = QVBoxLayout(self.leftMenu_2)
        self.verticalLayout_7.setSpacing(10)
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(20, 20, 20, 20)
        self.searchName = QLineEdit(self.leftMenu_2)
        self.searchName.setObjectName(u"searchName")
        self.searchName.setEnabled(False)
        self.searchName.setMinimumSize(QSize(0, 30))
        self.searchName.setMaximumSize(QSize(16777215, 30))
        self.searchName.setClearButtonEnabled(True)

        self.verticalLayout_7.addWidget(self.searchName)

        self.searchResult_2 = QScrollArea(self.leftMenu_2)
        self.searchResult_2.setObjectName(u"searchResult_2")
        self.searchResult_2.setFrameShape(QFrame.NoFrame)
        self.searchResult_2.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.searchResult_2.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.searchResult_2.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = QWidget()
        self.scrollAreaWidgetContents_2.setObjectName(u"scrollAreaWidgetContents_2")
        self.scrollAreaWidgetContents_2.setGeometry(QRect(0, 0, 83, 30))
        self.verticalLayout_9 = QVBoxLayout(self.scrollAreaWidgetContents_2)
        self.verticalLayout_9.setSpacing(0)
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_8 = QVBoxLayout()
        self.verticalLayout_8.setSpacing(10)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(-1, -1, 7, -1)
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_8.addItem(self.verticalSpacer)


        self.verticalLayout_9.addLayout(self.verticalLayout_8)

        self.searchResult_2.setWidget(self.scrollAreaWidgetContents_2)

        self.verticalLayout_7.addWidget(self.searchResult_2)

        self.closeOrder = QPushButton(self.leftMenu_2)
        self.closeOrder.setObjectName(u"closeOrder")
        self.closeOrder.setMinimumSize(QSize(0, 40))

        self.verticalLayout_7.addWidget(self.closeOrder)


        self.horizontalLayout_4.addWidget(self.leftMenu_2)

        self.chartArea = QFrame(self.chartPage)
        self.chartArea.setObjectName(u"chartArea")
        self.chartArea.setFrameShape(QFrame.NoFrame)
        self.chartArea.setFrameShadow(QFrame.Raised)
        self.verticalLayout_6 = QVBoxLayout(self.chartArea)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.depthLine = QScrollArea(self.chartArea)
        self.depthLine.setObjectName(u"depthLine")
        self.depthLine.setMaximumSize(QSize(16777215, 47))
        self.depthLine.setStyleSheet(u"QScrollArea {\n"
"	background-color: rgb(255, 255, 255);\n"
"}\n"
"\n"
"QScrollBar:horizontal {\n"
"	border: none;\n"
"	background: rgb(255, 255, 255);\n"
"	height: 7px;\n"
"}\n"
"\n"
"QScrollBar::handle:horizontal {\n"
"	background-color: rgb(180, 180, 180);\n"
"	min-width: 30px;\n"
"}\n"
"\n"
"QScrollBar::handle:horizontal:hover {\n"
"	background-color: rgb(255, 145, 67);\n"
"}\n"
"\n"
"QScrollBar::handle:horizontal:pressed {\n"
"	background-color: rgb(223, 124, 59);\n"
"}\n"
"\n"
"QScrollBar::sub-line:horizontal {\n"
"	border: none;\n"
"	background-color: rgb(255, 255, 255);\n"
"	width: 7px;\n"
"	subcontrol-position: left;\n"
"	subcontrol-origin: margin;\n"
"}\n"
"\n"
"QScrollBar::add-line:horizontal {\n"
"	border: none;\n"
"	background-color: rgb(255, 255, 255);\n"
"	width: 7px;\n"
"	subcontrol-position: right;\n"
"	subcontrol-origin: margin;\n"
"}\n"
"\n"
"QScrollBar::up-arrow:horizontal, QScrollBar::down-arrow:horizontal {\n"
"	background: none;\n"
"}\n"
"\n"
"QScrollBar::add-page:horizontal, QScrollBar:"
                        ":sub-page:horizontal {\n"
"	background: none;\n"
"}")
        self.depthLine.setFrameShape(QFrame.NoFrame)
        self.depthLine.setFrameShadow(QFrame.Plain)
        self.depthLine.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.depthLine.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.depthLine.setWidgetResizable(True)
        self.scrollAreaWidgetContents_3 = QWidget()
        self.scrollAreaWidgetContents_3.setObjectName(u"scrollAreaWidgetContents_3")
        self.scrollAreaWidgetContents_3.setGeometry(QRect(0, 0, 98, 42))
        self.horizontalLayout_7 = QHBoxLayout(self.scrollAreaWidgetContents_3)
        self.horizontalLayout_7.setSpacing(0)
        self.horizontalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setSpacing(0)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.sourcePlate = QPushButton(self.scrollAreaWidgetContents_3)
        self.sourcePlate.setObjectName(u"sourcePlate")
        sizePolicy3 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.sourcePlate.sizePolicy().hasHeightForWidth())
        self.sourcePlate.setSizePolicy(sizePolicy3)
        self.sourcePlate.setMinimumSize(QSize(80, 40))
        self.sourcePlate.setMaximumSize(QSize(80, 40))
        font1 = QFont()
        font1.setPointSize(8)
        self.sourcePlate.setFont(font1)
        self.sourcePlate.setStyleSheet(u"QPushButton {\n"
"	border: none;\n"
"	background-color: rgb(225, 225, 225);\n"
"	width: 80px;\n"
"	height: 40px;\n"
"	padding: 0px;\n"
"	color: black;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	background-color: rgb(235, 235, 235);\n"
"	border-bottom: 3px solid gray;\n"
"	font-weight: 800;\n"
"	padding-top: 3px;\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"	background-color: rgb(245, 245, 245);\n"
"	border-bottom: 3px solid gray;\n"
"	font-weight: 800;\n"
"	padding-top: 3px;\n"
"}\n"
"\n"
"QPushButton:checked {\n"
"	background-color: rgb(225, 225, 225);\n"
"	border-bottom: 3px solid black;\n"
"	padding-top: 3px;\n"
"	font-weight: 800;\n"
"}")
        self.sourcePlate.setCheckable(True)
        self.sourcePlate.setChecked(True)
        self.sourcePlate.setAutoExclusive(True)

        self.horizontalLayout_6.addWidget(self.sourcePlate)


        self.horizontalLayout_7.addLayout(self.horizontalLayout_6)

        self.depthLine.setWidget(self.scrollAreaWidgetContents_3)

        self.verticalLayout_6.addWidget(self.depthLine)


        self.horizontalLayout_4.addWidget(self.chartArea)

        self.mainArea.addWidget(self.chartPage)

        self.verticalLayout.addWidget(self.mainArea)

        MainWindow.setCentralWidget(self.centralWidget)
        self.mainArea.raise_()
        self.topBar.raise_()
        self.pageBar.raise_()
        self.statusBar = QStatusBar(MainWindow)
        self.statusBar.setObjectName(u"statusBar")
        MainWindow.setStatusBar(self.statusBar)

        self.retranslateUi(MainWindow)

        self.mainArea.setCurrentIndex(0)
        self.orderInformationArea.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"\u0420\u0430\u0441\u043a\u0440\u043e\u0439 \u0441\u043b\u0438\u0442\u043a\u0430", None))
        self.information.setText(QCoreApplication.translate("MainWindow", u"\u0417\u0430\u043a\u0430\u0437\u044b", None))
        self.chart.setText(QCoreApplication.translate("MainWindow", u"\u041a\u0430\u0440\u0442\u0430 \u0440\u0430\u0441\u043a\u0440\u043e\u044f", None))
        self.newOrder.setText(QCoreApplication.translate("MainWindow", u"\u041d\u043e\u0432\u044b\u0439\n"
"\u0437\u0430\u043a\u0430\u0437", None))
        self.newIngot.setText(QCoreApplication.translate("MainWindow", u"\u041d\u043e\u0432\u044b\u0439\n"
"\u0441\u043b\u0438\u0442\u043e\u043a", None))
        self.catalog.setText(QCoreApplication.translate("MainWindow", u"C\u043f\u0440\u0430\u0432\u043e\u0447\u043d\u0438\u043a\n"
"\u0437\u0430\u0433\u043e\u0442\u043e\u0432\u043e\u043a", None))
        self.settings.setText(QCoreApplication.translate("MainWindow", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438\n"
"\u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u044f", None))
        self.searchNumber.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u041d\u043e\u043c\u0435\u0440 \u0437\u0430\u043a\u0430\u0437\u0430...", None))
        self.searchType.setItemText(0, QCoreApplication.translate("MainWindow", u"\u0412\u0441\u0435 \u0437\u0430\u043a\u0430\u0437\u044b", None))
        self.searchType.setItemText(1, QCoreApplication.translate("MainWindow", u"\u0412 \u043f\u0440\u043e\u0446\u0435\u0441\u0441\u0435", None))
        self.searchType.setItemText(2, QCoreApplication.translate("MainWindow", u"\u0412 \u043e\u0436\u0438\u0434\u0430\u043d\u0438\u0438 \u0440\u0430\u0441\u043a\u0440\u043e\u044f", None))
        self.searchType.setItemText(3, QCoreApplication.translate("MainWindow", u"\u041d\u0435 \u043d\u0430\u0447\u0430\u0442\u044b\u0435", None))
        self.searchType.setItemText(4, QCoreApplication.translate("MainWindow", u"\u0417\u0430\u0432\u0435\u0440\u0448\u0451\u043d\u043d\u044b\u0435", None))

        self.defaultLabel.setText(QCoreApplication.translate("MainWindow", u"\u0417\u0430\u043a\u0430\u0437 \u043d\u0435 \u0432\u044b\u0431\u0440\u0430\u043d", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"\u041d\u043e\u043c\u0435\u0440 \u0437\u0430\u043a\u0430\u0437\u0430", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"\u0412\u044b\u0431\u0440\u0430\u043d\u043d\u044b\u0435 \u0437\u0430\u0433\u043e\u0442\u043e\u0432\u043a\u0438", None))
        self.saveComplect.setText(QCoreApplication.translate("MainWindow", u"\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c", None))
        self.saveComplectAndRecreate.setText(QCoreApplication.translate("MainWindow", u"\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c\n"
"\u0438 \u043f\u0435\u0440\u0435\u0441\u0447\u0438\u0442\u0430\u0442\u044c", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"\u0412\u044b\u0431\u0440\u0430\u043d\u043d\u044b\u0435 \u0441\u043b\u0438\u0442\u043a\u0438", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"\u041a\u0430\u0440\u0442\u0430 \u0440\u0430\u0441\u043a\u0440\u043e\u044f", None))
        self.recalculate.setText(QCoreApplication.translate("MainWindow", u"\u041f\u0435\u0440\u0435\u0441\u0447\u0438\u0442\u0430\u0442\u044c", None))
        self.fullScreen.setText(QCoreApplication.translate("MainWindow", u"\u041d\u0430 \u0432\u0435\u0441\u044c \u044d\u043a\u0440\u0430\u043d", None))
        self.detailedPlan.setText(QCoreApplication.translate("MainWindow", u"\u041f\u0435\u0440\u0435\u0439\u0442\u0438 \u043a \u043f\u043b\u0430\u043d\u0443", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"\u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430 \u043f\u043e \u0437\u0430\u043a\u0430\u0437\u0443", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"\u0412\u044b\u0445\u043e\u0434 \u0433\u043e\u0434\u043d\u043e\u0433\u043e:\n"
"\n"
"\u0413\u043e\u0442\u043e\u0432\u044b\u0445 \u0434\u0435\u0442\u0430\u043b\u0435\u0439:\n"
"\u041d\u0435\u0443\u043a\u043e\u043c\u043f\u043b\u0435\u043a\u0442\u043e\u0432\u0430\u043d\u043d\u044b\u0445 \u0434\u0435\u0442\u0430\u043b\u0435\u0439:\n"
"\n"
"\u0414\u0435\u0444\u0435\u043a\u0442\u043e\u0432 \u0440\u0430\u0441\u043a\u0440\u043e\u044f:\n"
"\u0417\u0430\u0431\u0440\u0430\u043a\u043e\u0432\u0430\u043d\u043d\u044b\u0445 \u0434\u0435\u0442\u0430\u043b\u0435\u0439:", None))
        self.searchName.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u0434\u0435\u0442\u0430\u043b\u0438...", None))
        self.closeOrder.setText(QCoreApplication.translate("MainWindow", u"\u0417\u0430\u0432\u0435\u0440\u0448\u0438\u0442\u044c \u0437\u0430\u043a\u0430\u0437", None))
        self.sourcePlate.setText(QCoreApplication.translate("MainWindow", u"\u041a\u0430\u0440\u0442\u0430\n"
"\u0440\u0430\u0441\u043a\u0440\u043e\u044f", None))
    # retranslateUi

