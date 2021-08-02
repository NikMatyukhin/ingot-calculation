# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\QtProjects\oci\gui\catalog.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1268, 685)
        Form.setMouseTracking(True)
        Form.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.top_area = QtWidgets.QFrame(Form)
        self.top_area.setMinimumSize(QtCore.QSize(0, 50))
        self.top_area.setMaximumSize(QtCore.QSize(16777215, 50))
        self.top_area.setStyleSheet("background-color: rgb(225, 225, 225);")
        self.top_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.top_area.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.top_area.setObjectName("top_area")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.top_area)
        self.horizontalLayout.setContentsMargins(5, 5, 5, 5)
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.add_article = QtWidgets.QPushButton(self.top_area)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.add_article.sizePolicy().hasHeightForWidth())
        self.add_article.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(8)
        font.setBold(False)
        font.setWeight(50)
        self.add_article.setFont(font)
        self.add_article.setAutoFillBackground(False)
        self.add_article.setStyleSheet("QPushButton {\n"
"    background-color: rgb(225, 225, 225);\n"
"    border-radius: 3px;\n"
"    padding: 5px;\n"
"    color: black;\n"
"    border: none;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: rgb(210, 210, 210);\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: rgb(189, 189, 189);\n"
"    padding: 5px;\n"
"}")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/manufacture.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.add_article.setIcon(icon)
        self.add_article.setIconSize(QtCore.QSize(20, 20))
        self.add_article.setObjectName("add_article")
        self.horizontalLayout.addWidget(self.add_article)
        self.line = QtWidgets.QFrame(self.top_area)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout.addWidget(self.line)
        self.add_detail = QtWidgets.QPushButton(self.top_area)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.add_detail.sizePolicy().hasHeightForWidth())
        self.add_detail.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(8)
        font.setBold(False)
        font.setWeight(50)
        self.add_detail.setFont(font)
        self.add_detail.setAutoFillBackground(False)
        self.add_detail.setStyleSheet("QPushButton {\n"
"    background-color: rgb(225, 225, 225);\n"
"    border-radius: 3px;\n"
"    padding: 5px;\n"
"    color: black;\n"
"    border: none;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: rgb(210, 210, 210);\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: rgb(189, 189, 189);\n"
"    padding: 5px;\n"
"}")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/beam.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.add_detail.setIcon(icon1)
        self.add_detail.setIconSize(QtCore.QSize(20, 20))
        self.add_detail.setObjectName("add_detail")
        self.horizontalLayout.addWidget(self.add_detail)
        self.line_2 = QtWidgets.QFrame(self.top_area)
        self.line_2.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.horizontalLayout.addWidget(self.line_2)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout_4.addWidget(self.top_area)
        self.main_area = QtWidgets.QFrame(Form)
        self.main_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.main_area.setFrameShadow(QtWidgets.QFrame.Raised)
        self.main_area.setObjectName("main_area")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.main_area)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.splitter = QtWidgets.QSplitter(self.main_area)
        self.splitter.setStyleSheet("QSplitter::handle {\n"
"    background-image: url(:/icons/top_part.png);\n"
"    background-repeat: no-repeat;\n"
"}")
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setHandleWidth(10)
        self.splitter.setObjectName("splitter")
        self.left_area = QtWidgets.QFrame(self.splitter)
        self.left_area.setMinimumSize(QtCore.QSize(0, 0))
        self.left_area.setMaximumSize(QtCore.QSize(460, 16777215))
        self.left_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.left_area.setFrameShadow(QtWidgets.QFrame.Raised)
        self.left_area.setObjectName("left_area")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.left_area)
        self.verticalLayout.setContentsMargins(10, 10, 0, 10)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName("verticalLayout")
        self.articles = QtWidgets.QGroupBox(self.left_area)
        self.articles.setMinimumSize(QtCore.QSize(0, 50))
        self.articles.setObjectName("articles")
        self.gridLayout = QtWidgets.QGridLayout(self.articles)
        self.gridLayout.setContentsMargins(10, 5, 10, 10)
        self.gridLayout.setSpacing(10)
        self.gridLayout.setObjectName("gridLayout")
        self.name = QtWidgets.QLineEdit(self.articles)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.name.sizePolicy().hasHeightForWidth())
        self.name.setSizePolicy(sizePolicy)
        self.name.setMinimumSize(QtCore.QSize(0, 25))
        self.name.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.name.setStyleSheet("QLineEdit {\n"
"    padding-left: 5px;\n"
"}")
        self.name.setClearButtonEnabled(True)
        self.name.setObjectName("name")
        self.gridLayout.addWidget(self.name, 0, 0, 1, 2)
        self.articles_view = QtWidgets.QTreeView(self.articles)
        self.articles_view.setMinimumSize(QtCore.QSize(400, 0))
        self.articles_view.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.articles_view.setStyleSheet("QHeaderView::section {\n"
"    padding-left: 10px;\n"
"}")
        self.articles_view.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.articles_view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.articles_view.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContentsOnFirstShow)
        self.articles_view.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.articles_view.setIndentation(0)
        self.articles_view.setItemsExpandable(False)
        self.articles_view.setAnimated(True)
        self.articles_view.setWordWrap(True)
        self.articles_view.setObjectName("articles_view")
        self.articles_view.header().setHighlightSections(False)
        self.articles_view.header().setSortIndicatorShown(False)
        self.articles_view.header().setStretchLastSection(True)
        self.gridLayout.addWidget(self.articles_view, 1, 0, 1, 2)
        self.verticalLayout.addWidget(self.articles)
        self.tip = QtWidgets.QLabel(self.left_area)
        self.tip.setMinimumSize(QtCore.QSize(0, 21))
        self.tip.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.tip.setScaledContents(False)
        self.tip.setAlignment(QtCore.Qt.AlignCenter)
        self.tip.setObjectName("tip")
        self.verticalLayout.addWidget(self.tip)
        self.right_area = QtWidgets.QFrame(self.splitter)
        self.right_area.setMinimumSize(QtCore.QSize(0, 580))
        self.right_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.right_area.setFrameShadow(QtWidgets.QFrame.Raised)
        self.right_area.setObjectName("right_area")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.right_area)
        self.verticalLayout_2.setContentsMargins(0, 10, 10, 10)
        self.verticalLayout_2.setSpacing(10)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.details = QtWidgets.QGroupBox(self.right_area)
        self.details.setObjectName("details")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.details)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.details_view = QtWidgets.QTableView(self.details)
        self.details_view.setMinimumSize(QtCore.QSize(776, 300))
        self.details_view.setStyleSheet("QTableWidget {\n"
"    border: none;\n"
"    border: 1px solid gray;\n"
"}\n"
"\n"
"QHeaderView::section {\n"
"    background-color: rgb(231, 231, 231);\n"
"    padding-left: 10px;\n"
"    border: 1px solid gray;\n"
"    border-left: none;\n"
"    border-top: none;\n"
"}")
        self.details_view.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked|QtWidgets.QAbstractItemView.EditKeyPressed)
        self.details_view.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.details_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.details_view.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.details_view.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.details_view.setObjectName("details_view")
        self.details_view.horizontalHeader().setStretchLastSection(True)
        self.details_view.verticalHeader().setVisible(False)
        self.verticalLayout_3.addWidget(self.details_view)
        self.verticalLayout_2.addWidget(self.details)
        self.horizontalLayout_3.addWidget(self.splitter)
        self.verticalLayout_4.addWidget(self.main_area)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Справочник заготовок"))
        self.add_article.setToolTip(_translate("Form", "Добавить новое изделие"))
        self.add_article.setText(_translate("Form", "Добавить\n"
"изделие"))
        self.add_detail.setToolTip(_translate("Form", "Добавление заготовки к выделенному изделию"))
        self.add_detail.setText(_translate("Form", "Добавить\n"
"заготовку"))
        self.articles.setTitle(_translate("Form", "Изделия"))
        self.name.setPlaceholderText(_translate("Form", "Введите название изделия..."))
        self.articles_view.setToolTip(_translate("Form", "Добавление связей применяется только к выделенным объектам"))
        self.tip.setText(_translate("Form", "Добавление заготовок применяется только к выбранным изделиям"))
        self.details.setTitle(_translate("Form", "Заготовки"))
import application_rc
