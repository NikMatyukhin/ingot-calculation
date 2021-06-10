# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'catalogqLcxdx.ui'
##
## Created by: Qt User Interface Compiler version 6.0.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

import application_rc

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(1156, 692)
        Form.setMouseTracking(True)
        Form.setContextMenuPolicy(Qt.CustomContextMenu)
        self.verticalLayout_4 = QVBoxLayout(Form)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.topBar = QFrame(Form)
        self.topBar.setObjectName(u"topBar")
        self.topBar.setMinimumSize(QSize(0, 80))
        self.topBar.setMaximumSize(QSize(16777215, 80))
        self.topBar.setStyleSheet(u"background-color: rgb(225, 225, 225);")
        self.topBar.setFrameShape(QFrame.NoFrame)
        self.topBar.setFrameShadow(QFrame.Sunken)
        self.horizontalLayout = QHBoxLayout(self.topBar)
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(10, 5, 0, 5)
        self.newProduct = QToolButton(self.topBar)
        self.newProduct.setObjectName(u"newProduct")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.newProduct.sizePolicy().hasHeightForWidth())
        self.newProduct.setSizePolicy(sizePolicy)
        self.newProduct.setStyleSheet(u"QToolButton {\n"
"	background-color: rgb(225, 225, 225);\n"
"	border-radius: 3px;\n"
"	padding-top: 2px;\n"
"	color: black;\n"
"	border: none;\n"
"	font-size: 11px;\n"
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
        icon = QIcon()
        icon.addFile(u":/icons/manufacture.png", QSize(), QIcon.Normal, QIcon.Off)
        self.newProduct.setIcon(icon)
        self.newProduct.setIconSize(QSize(40, 40))
        self.newProduct.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        self.horizontalLayout.addWidget(self.newProduct)

        self.newArticle = QToolButton(self.topBar)
        self.newArticle.setObjectName(u"newArticle")
        sizePolicy.setHeightForWidth(self.newArticle.sizePolicy().hasHeightForWidth())
        self.newArticle.setSizePolicy(sizePolicy)
        self.newArticle.setStyleSheet(u"QToolButton {\n"
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
        icon1.addFile(u":/icons/conveyor.png", QSize(), QIcon.Normal, QIcon.Off)
        self.newArticle.setIcon(icon1)
        self.newArticle.setIconSize(QSize(40, 40))
        self.newArticle.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        self.horizontalLayout.addWidget(self.newArticle)

        self.newDetail = QToolButton(self.topBar)
        self.newDetail.setObjectName(u"newDetail")
        sizePolicy.setHeightForWidth(self.newDetail.sizePolicy().hasHeightForWidth())
        self.newDetail.setSizePolicy(sizePolicy)
        self.newDetail.setStyleSheet(u"QToolButton {\n"
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
        icon2.addFile(u":/icons/beam.png", QSize(), QIcon.Normal, QIcon.Off)
        self.newDetail.setIcon(icon2)
        self.newDetail.setIconSize(QSize(40, 40))
        self.newDetail.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        self.horizontalLayout.addWidget(self.newDetail)

        self.line = QFrame(self.topBar)
        self.line.setObjectName(u"line")
        self.line.setFrameShadow(QFrame.Plain)
        self.line.setFrameShape(QFrame.VLine)

        self.horizontalLayout.addWidget(self.line)

        self.newImage = QToolButton(self.topBar)
        self.newImage.setObjectName(u"newImage")
        sizePolicy.setHeightForWidth(self.newImage.sizePolicy().hasHeightForWidth())
        self.newImage.setSizePolicy(sizePolicy)
        self.newImage.setStyleSheet(u"QToolButton {\n"
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
        icon3.addFile(u":/icons/patch.png", QSize(), QIcon.Normal, QIcon.Off)
        self.newImage.setIcon(icon3)
        self.newImage.setIconSize(QSize(40, 40))

        self.horizontalLayout.addWidget(self.newImage)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout_4.addWidget(self.topBar)

        self.frame_5 = QFrame(Form)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setFrameShape(QFrame.NoFrame)
        self.frame_5.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_5)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.splitter = QSplitter(self.frame_5)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Horizontal)
        self.frame = QFrame(self.splitter)
        self.frame.setObjectName(u"frame")
        self.frame.setMinimumSize(QSize(0, 580))
        self.frame.setMaximumSize(QSize(620, 16777215))
        self.frame.setFrameShape(QFrame.NoFrame)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout = QVBoxLayout(self.frame)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.searchParameters = QGroupBox(self.frame)
        self.searchParameters.setObjectName(u"searchParameters")
        self.searchParameters.setMinimumSize(QSize(0, 100))
        self.gridLayout = QGridLayout(self.searchParameters)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setHorizontalSpacing(10)
        self.gridLayout.setVerticalSpacing(0)
        self.gridLayout.setContentsMargins(10, 0, 10, 0)
        self.register_number = QLineEdit(self.searchParameters)
        self.register_number.setObjectName(u"register_number")

        self.gridLayout.addWidget(self.register_number, 2, 0, 1, 1)

        self.designation = QLineEdit(self.searchParameters)
        self.designation.setObjectName(u"designation")
        self.designation.setMinimumSize(QSize(200, 0))
        self.designation.setMaximumSize(QSize(16777215, 16777215))

        self.gridLayout.addWidget(self.designation, 0, 0, 1, 2)

        self.nomenclature = QLineEdit(self.searchParameters)
        self.nomenclature.setObjectName(u"nomenclature")
        self.nomenclature.setMinimumSize(QSize(200, 0))

        self.gridLayout.addWidget(self.nomenclature, 3, 0, 1, 1)

        self.type = QComboBox(self.searchParameters)
        self.type.setObjectName(u"type")
        self.type.setMinimumSize(QSize(100, 0))

        self.gridLayout.addWidget(self.type, 2, 1, 1, 1)

        self.rent = QCheckBox(self.searchParameters)
        self.rent.setObjectName(u"rent")

        self.gridLayout.addWidget(self.rent, 3, 1, 1, 1)


        self.verticalLayout.addWidget(self.searchParameters)

        self.productsView = QTreeView(self.frame)
        self.productsView.setObjectName(u"productsView")
        self.productsView.setMinimumSize(QSize(600, 400))
        self.productsView.setMaximumSize(QSize(600, 16777215))
        self.productsView.setFocusPolicy(Qt.StrongFocus)
        self.productsView.setStyleSheet(u"QTreeWidget {\n"
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
        self.productsView.setFrameShape(QFrame.StyledPanel)
        self.productsView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.productsView.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContentsOnFirstShow)
        self.productsView.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.productsView.setAnimated(True)
        self.productsView.setWordWrap(True)
        self.productsView.header().setMinimumSectionSize(100)
        self.productsView.header().setHighlightSections(True)
        self.productsView.header().setStretchLastSection(True)

        self.verticalLayout.addWidget(self.productsView)

        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")
        self.label.setFrameShape(QFrame.StyledPanel)
        self.label.setScaledContents(False)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setMargin(3)

        self.verticalLayout.addWidget(self.label)

        self.splitter.addWidget(self.frame)
        self.frame_2 = QFrame(self.splitter)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setMinimumSize(QSize(0, 580))
        self.frame_2.setFrameShape(QFrame.NoFrame)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame_2)
        self.verticalLayout_2.setSpacing(10)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(10, 10, 10, 10)
        self.detailsView = QTableWidget(self.frame_2)
        if (self.detailsView.columnCount() < 9):
            self.detailsView.setColumnCount(9)
        __qtablewidgetitem = QTableWidgetItem()
        __qtablewidgetitem.setTextAlignment(Qt.AlignLeading|Qt.AlignVCenter);
        self.detailsView.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        __qtablewidgetitem1.setTextAlignment(Qt.AlignLeading|Qt.AlignVCenter);
        self.detailsView.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        __qtablewidgetitem2.setTextAlignment(Qt.AlignLeading|Qt.AlignVCenter);
        self.detailsView.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        __qtablewidgetitem3.setTextAlignment(Qt.AlignLeading|Qt.AlignVCenter);
        self.detailsView.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        __qtablewidgetitem4.setTextAlignment(Qt.AlignLeading|Qt.AlignVCenter);
        self.detailsView.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        __qtablewidgetitem5.setTextAlignment(Qt.AlignLeading|Qt.AlignVCenter);
        self.detailsView.setHorizontalHeaderItem(5, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        __qtablewidgetitem6.setTextAlignment(Qt.AlignLeading|Qt.AlignVCenter);
        self.detailsView.setHorizontalHeaderItem(6, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        __qtablewidgetitem7.setTextAlignment(Qt.AlignLeading|Qt.AlignVCenter);
        self.detailsView.setHorizontalHeaderItem(7, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        self.detailsView.setHorizontalHeaderItem(8, __qtablewidgetitem8)
        self.detailsView.setObjectName(u"detailsView")
        self.detailsView.setMinimumSize(QSize(400, 300))
        self.detailsView.setStyleSheet(u"QTableWidget {\n"
"	border: none;\n"
"	border: 1px solid gray;\n"
"}\n"
"\n"
"QHeaderView::section {\n"
"	background-color: rgb(231, 231, 231);\n"
"	padding-left: 10px;\n"
"	border: 1px solid gray;\n"
"	border-left: none;\n"
"	border-top: none;\n"
"}")
        self.detailsView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.detailsView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.detailsView.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.detailsView.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.detailsView.horizontalHeader().setStretchLastSection(True)
        self.detailsView.verticalHeader().setVisible(False)

        self.verticalLayout_2.addWidget(self.detailsView)

        self.frame_3 = QFrame(self.frame_2)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setMinimumSize(QSize(0, 0))
        self.frame_3.setFrameShape(QFrame.NoFrame)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.frame_3)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.detailTitle = QLabel(self.frame_3)
        self.detailTitle.setObjectName(u"detailTitle")
        self.detailTitle.setMinimumSize(QSize(0, 40))
        self.detailTitle.setMaximumSize(QSize(16777215, 40))
        self.detailTitle.setStyleSheet(u"background-color: rgb(231, 231, 231);\n"
"padding-left: 10px;")

        self.verticalLayout_3.addWidget(self.detailTitle)

        self.detailBody = QFrame(self.frame_3)
        self.detailBody.setObjectName(u"detailBody")
        self.detailBody.setFrameShape(QFrame.NoFrame)
        self.detailBody.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.detailBody)
        self.horizontalLayout_2.setSpacing(10)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 10, 0, 0)
        self.imageView = QGraphicsView(self.detailBody)
        self.imageView.setObjectName(u"imageView")
        self.imageView.setMinimumSize(QSize(200, 200))
        self.imageView.setMaximumSize(QSize(200, 200))

        self.horizontalLayout_2.addWidget(self.imageView)

        self.detailInfo = QLabel(self.detailBody)
        self.detailInfo.setObjectName(u"detailInfo")
        self.detailInfo.setMaximumSize(QSize(16777215, 250))
        self.detailInfo.setStyleSheet(u"padding-left: 10px;")
        self.detailInfo.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)

        self.horizontalLayout_2.addWidget(self.detailInfo)


        self.verticalLayout_3.addWidget(self.detailBody)

        self.verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)


        self.verticalLayout_2.addWidget(self.frame_3)

        self.splitter.addWidget(self.frame_2)

        self.horizontalLayout_3.addWidget(self.splitter)


        self.verticalLayout_4.addWidget(self.frame_5)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"\u0421\u043f\u0440\u0430\u0432\u043e\u0447\u043d\u0438\u043a \u0437\u0430\u0433\u043e\u0442\u043e\u0432\u043e\u043a", None))
#if QT_CONFIG(tooltip)
        self.newProduct.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.newProduct.setText(QCoreApplication.translate("Form", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c\n"
"\u043f\u0440\u043e\u0434\u0443\u043a\u0446\u0438\u044e", None))
#if QT_CONFIG(tooltip)
        self.newArticle.setToolTip(QCoreApplication.translate("Form", u"\u0414\u043e\u0431\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u0438\u0437\u0434\u0435\u043b\u0438\u044f \u043a \u0432\u044b\u0434\u0435\u043b\u0435\u043d\u043d\u043e\u0439 \u043f\u0440\u043e\u0434\u0443\u043a\u0446\u0438\u0438", None))
#endif // QT_CONFIG(tooltip)
        self.newArticle.setText(QCoreApplication.translate("Form", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c\n"
"\u0438\u0437\u0434\u0435\u043b\u0438\u0435", None))
#if QT_CONFIG(tooltip)
        self.newDetail.setToolTip(QCoreApplication.translate("Form", u"\u0414\u043e\u0431\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u0437\u0430\u0433\u043e\u0442\u043e\u0432\u043a\u0438 \u043a \u0432\u044b\u0434\u0435\u043b\u0435\u043d\u043d\u043e\u0439 \u043f\u0440\u043e\u0434\u0443\u043a\u0446\u0438\u0438", None))
#endif // QT_CONFIG(tooltip)
        self.newDetail.setText(QCoreApplication.translate("Form", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c\n"
"\u0437\u0430\u0433\u043e\u0442\u043e\u0432\u043a\u0443", None))
        self.newImage.setText(QCoreApplication.translate("Form", u"+ 4", None))
        self.searchParameters.setTitle(QCoreApplication.translate("Form", u"\u041f\u0430\u0440\u0430\u043c\u0435\u0442\u0440\u044b \u043f\u043e\u0438\u0441\u043a\u0430", None))
        self.register_number.setPlaceholderText(QCoreApplication.translate("Form", u"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u043d\u043e\u043c\u0435\u0440 \u0432\u0435\u0434\u043e\u043c\u043e\u0441\u0442\u0438...", None))
        self.designation.setPlaceholderText(QCoreApplication.translate("Form", u"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u043f\u0440\u043e\u0434\u0443\u043a\u0446\u0438\u0438...", None))
        self.nomenclature.setPlaceholderText(QCoreApplication.translate("Form", u"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u043d\u043e\u043c\u0435\u043d\u043a\u043b\u0430\u0442\u0443\u0440\u0443...", None))
        self.rent.setText(QCoreApplication.translate("Form", u"\u0412 \u0430\u0440\u0435\u043d\u0434\u0443", None))
#if QT_CONFIG(tooltip)
        self.productsView.setToolTip(QCoreApplication.translate("Form", u"\u0414\u043e\u0431\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u0441\u0432\u044f\u0437\u0435\u0439 \u043f\u0440\u0438\u043c\u0435\u043d\u044f\u0435\u0442\u0441\u044f \u0442\u043e\u043b\u044c\u043a\u043e \u043a \u0432\u044b\u0434\u0435\u043b\u0435\u043d\u043d\u044b\u043c \u043e\u0431\u044a\u0435\u043a\u0442\u0430\u043c", None))
#endif // QT_CONFIG(tooltip)
        self.label.setText(QCoreApplication.translate("Form", u"\u0414\u043e\u0431\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u0441\u0432\u044f\u0437\u0435\u0439 \u043f\u0440\u0438\u043c\u0435\u043d\u044f\u0435\u0442\u0441\u044f \u0442\u043e\u043b\u044c\u043a\u043e \u043a \u0432\u044b\u0434\u0435\u043b\u0435\u043d\u043d\u044b\u043c \u043e\u0431\u044a\u0435\u043a\u0442\u0430\u043c", None))
        ___qtablewidgetitem = self.detailsView.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("Form", u"\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435", None));
        ___qtablewidgetitem1 = self.detailsView.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("Form", u"\u0421\u043f\u043b\u0430\u0432", None));
        ___qtablewidgetitem2 = self.detailsView.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("Form", u"\u0414\u043b\u0438\u043d\u0430", None));
        ___qtablewidgetitem3 = self.detailsView.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("Form", u"\u0428\u0438\u0440\u0438\u043d\u0430", None));
        ___qtablewidgetitem4 = self.detailsView.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("Form", u"\u0422\u043e\u043b\u0449\u0438\u043d\u0430", None));
        ___qtablewidgetitem5 = self.detailsView.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("Form", u"\u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e", None));
        ___qtablewidgetitem6 = self.detailsView.horizontalHeaderItem(6)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("Form", u"\u041f\u0440\u0438\u043e\u0440\u0438\u0442\u0435\u0442", None));
        ___qtablewidgetitem7 = self.detailsView.horizontalHeaderItem(7)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("Form", u"\u041f\u043e\u0432\u043e\u0440\u043e\u0442", None));
        ___qtablewidgetitem8 = self.detailsView.horizontalHeaderItem(8)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("Form", u"ID", None));
        self.detailTitle.setText(QCoreApplication.translate("Form", u"\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u0434\u0435\u0442\u0430\u043b\u0438: ...", None))
        self.detailInfo.setText(QCoreApplication.translate("Form", u"\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435 \u0434\u0435\u0442\u0430\u043b\u0438: ...", None))
    # retranslateUi

