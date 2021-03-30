# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'finish_step_dialogodeduf.ui'
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
        Dialog.resize(678, 501)
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
        self.leftArea = QFrame(self.mainArea)
        self.leftArea.setObjectName(u"leftArea")
        self.leftArea.setFrameShape(QFrame.NoFrame)
        self.leftArea.setFrameShadow(QFrame.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.leftArea)
        self.verticalLayout_3.setSpacing(10)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(10, 10, 10, 10)
        self.plateSizes = QGroupBox(self.leftArea)
        self.plateSizes.setObjectName(u"plateSizes")
        self.formLayout = QFormLayout(self.plateSizes)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setHorizontalSpacing(0)
        self.formLayout.setVerticalSpacing(10)
        self.formLayout.setContentsMargins(10, 5, 10, 10)
        self.label_4 = QLabel(self.plateSizes)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setMinimumSize(QSize(100, 0))
        font = QFont()
        font.setPointSize(9)
        self.label_4.setFont(font)

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label_4)

        self.plateHeight = QDoubleSpinBox(self.plateSizes)
        self.plateHeight.setObjectName(u"plateHeight")
        self.plateHeight.setFont(font)
        self.plateHeight.setMaximum(999.990000000000009)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.plateHeight)

        self.label_5 = QLabel(self.plateSizes)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setMinimumSize(QSize(100, 0))
        self.label_5.setFont(font)

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_5)

        self.plateWidth = QDoubleSpinBox(self.plateSizes)
        self.plateWidth.setObjectName(u"plateWidth")
        self.plateWidth.setFont(font)
        self.plateWidth.setMaximum(999.990000000000009)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.plateWidth)


        self.verticalLayout_3.addWidget(self.plateSizes)

        self.defects = QGroupBox(self.leftArea)
        self.defects.setObjectName(u"defects")
        self.defects.setCheckable(True)
        self.defects.setChecked(True)
        self.verticalLayout_2 = QVBoxLayout(self.defects)
        self.verticalLayout_2.setSpacing(10)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(10, 10, 10, 10)
        self.label_1 = QLabel(self.defects)
        self.label_1.setObjectName(u"label_1")

        self.verticalLayout_2.addWidget(self.label_1)

        self.frame_1 = QFrame(self.defects)
        self.frame_1.setObjectName(u"frame_1")
        self.frame_1.setMinimumSize(QSize(0, 50))
        self.frame_1.setFrameShape(QFrame.StyledPanel)
        self.frame_1.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_5 = QHBoxLayout(self.frame_1)
        self.horizontalLayout_5.setSpacing(5)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.defectsList_1 = QListWidget(self.frame_1)
        self.defectsList_1.setObjectName(u"defectsList_1")
        self.defectsList_1.setMinimumSize(QSize(0, 100))

        self.horizontalLayout_5.addWidget(self.defectsList_1)

        self.controls_1 = QFrame(self.frame_1)
        self.controls_1.setObjectName(u"controls_1")
        self.controls_1.setFrameShape(QFrame.StyledPanel)
        self.controls_1.setFrameShadow(QFrame.Raised)
        self.verticalLayout_5 = QVBoxLayout(self.controls_1)
        self.verticalLayout_5.setSpacing(5)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.toolButton_2 = QToolButton(self.controls_1)
        self.toolButton_2.setObjectName(u"toolButton_2")
        self.toolButton_2.setMinimumSize(QSize(22, 22))

        self.verticalLayout_5.addWidget(self.toolButton_2)

        self.toolButton_3 = QToolButton(self.controls_1)
        self.toolButton_3.setObjectName(u"toolButton_3")
        self.toolButton_3.setMinimumSize(QSize(22, 22))

        self.verticalLayout_5.addWidget(self.toolButton_3)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_5.addItem(self.verticalSpacer_2)


        self.horizontalLayout_5.addWidget(self.controls_1)


        self.verticalLayout_2.addWidget(self.frame_1)

        self.label_2 = QLabel(self.defects)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout_2.addWidget(self.label_2)

        self.frame_2 = QFrame(self.defects)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setMinimumSize(QSize(0, 50))
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.frame_2)
        self.horizontalLayout_4.setSpacing(5)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.defectsList_2 = QListWidget(self.frame_2)
        self.defectsList_2.setObjectName(u"defectsList_2")
        self.defectsList_2.setMinimumSize(QSize(0, 100))

        self.horizontalLayout_4.addWidget(self.defectsList_2)

        self.controls_2 = QFrame(self.frame_2)
        self.controls_2.setObjectName(u"controls_2")
        self.controls_2.setFrameShape(QFrame.StyledPanel)
        self.controls_2.setFrameShadow(QFrame.Raised)
        self.verticalLayout_6 = QVBoxLayout(self.controls_2)
        self.verticalLayout_6.setSpacing(5)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.add_2 = QToolButton(self.controls_2)
        self.add_2.setObjectName(u"add_2")
        self.add_2.setMinimumSize(QSize(22, 22))

        self.verticalLayout_6.addWidget(self.add_2)

        self.remove_2 = QToolButton(self.controls_2)
        self.remove_2.setObjectName(u"remove_2")
        self.remove_2.setMinimumSize(QSize(22, 22))

        self.verticalLayout_6.addWidget(self.remove_2)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_6.addItem(self.verticalSpacer_3)


        self.horizontalLayout_4.addWidget(self.controls_2)


        self.verticalLayout_2.addWidget(self.frame_2)


        self.verticalLayout_3.addWidget(self.defects)


        self.horizontalLayout.addWidget(self.leftArea)

        self.rightArea = QFrame(self.mainArea)
        self.rightArea.setObjectName(u"rightArea")
        self.rightArea.setFrameShape(QFrame.NoFrame)
        self.rightArea.setFrameShadow(QFrame.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.rightArea)
        self.verticalLayout_4.setSpacing(10)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(10, 10, 10, 10)
        self.leftoverSizes = QGroupBox(self.rightArea)
        self.leftoverSizes.setObjectName(u"leftoverSizes")
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.leftoverSizes.sizePolicy().hasHeightForWidth())
        self.leftoverSizes.setSizePolicy(sizePolicy)
        self.leftoverSizes.setMaximumSize(QSize(16777215, 16777215))
        self.formLayout_2 = QFormLayout(self.leftoverSizes)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.formLayout_2.setHorizontalSpacing(0)
        self.formLayout_2.setVerticalSpacing(10)
        self.formLayout_2.setContentsMargins(10, 5, 10, 10)
        self.label_7 = QLabel(self.leftoverSizes)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setMinimumSize(QSize(100, 0))

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.label_7)

        self.leftoverHeight = QDoubleSpinBox(self.leftoverSizes)
        self.leftoverHeight.setObjectName(u"leftoverHeight")
        self.leftoverHeight.setMaximum(999.990000000000009)

        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.leftoverHeight)

        self.label_8 = QLabel(self.leftoverSizes)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setMinimumSize(QSize(100, 0))

        self.formLayout_2.setWidget(1, QFormLayout.LabelRole, self.label_8)

        self.leftoverWidth = QDoubleSpinBox(self.leftoverSizes)
        self.leftoverWidth.setObjectName(u"leftoverWidth")
        self.leftoverWidth.setMaximum(999.990000000000009)

        self.formLayout_2.setWidget(1, QFormLayout.FieldRole, self.leftoverWidth)

        self.addLeftover = QPushButton(self.leftoverSizes)
        self.addLeftover.setObjectName(u"addLeftover")

        self.formLayout_2.setWidget(2, QFormLayout.FieldRole, self.addLeftover)


        self.verticalLayout_4.addWidget(self.leftoverSizes)

        self.leftoversTable = QTableWidget(self.rightArea)
        if (self.leftoversTable.columnCount() < 4):
            self.leftoversTable.setColumnCount(4)
        __qtablewidgetitem = QTableWidgetItem()
        self.leftoversTable.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.leftoversTable.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.leftoversTable.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.leftoversTable.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        self.leftoversTable.setObjectName(u"leftoversTable")
        self.leftoversTable.setMinimumSize(QSize(0, 300))
        self.leftoversTable.setStyleSheet(u"QTableWidget {\n"
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
        self.leftoversTable.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.leftoversTable.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.leftoversTable.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.leftoversTable.horizontalHeader().setStretchLastSection(True)
        self.leftoversTable.verticalHeader().setVisible(False)

        self.verticalLayout_4.addWidget(self.leftoversTable)


        self.horizontalLayout.addWidget(self.rightArea)


        self.verticalLayout.addWidget(self.mainArea)

        self.verticalSpacer_1 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_1)

        self.buttonArea = QFrame(Dialog)
        self.buttonArea.setObjectName(u"buttonArea")
        self.buttonArea.setMinimumSize(QSize(0, 40))
        self.buttonArea.setMaximumSize(QSize(16777215, 40))
        self.buttonArea.setFrameShape(QFrame.NoFrame)
        self.buttonArea.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.buttonArea)
        self.horizontalLayout_2.setSpacing(10)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 10, 0)
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.finish = QPushButton(self.buttonArea)
        self.finish.setObjectName(u"finish")
        self.finish.setMinimumSize(QSize(80, 0))

        self.horizontalLayout_2.addWidget(self.finish)

        self.cancel = QPushButton(self.buttonArea)
        self.cancel.setObjectName(u"cancel")
        self.cancel.setMinimumSize(QSize(80, 0))

        self.horizontalLayout_2.addWidget(self.cancel)


        self.verticalLayout.addWidget(self.buttonArea)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"\u0417\u0430\u0432\u0435\u0440\u0448\u0435\u043d\u0438\u0435 \u0437\u0430\u043a\u0430\u0437\u0430", None))
        self.plateSizes.setTitle(QCoreApplication.translate("Dialog", u"\u0420\u0430\u0437\u043c\u0435\u0440\u044b \u043f\u043b\u0430\u0441\u0442\u0438\u043d\u044b", None))
        self.label_4.setText(QCoreApplication.translate("Dialog", u"\u0414\u043b\u0438\u043d\u0430", None))
        self.plateHeight.setSuffix(QCoreApplication.translate("Dialog", u" \u043c\u043c", None))
        self.label_5.setText(QCoreApplication.translate("Dialog", u"\u0428\u0438\u0440\u0438\u043d\u0430", None))
        self.plateWidth.setSuffix(QCoreApplication.translate("Dialog", u" \u043c\u043c", None))
        self.defects.setTitle(QCoreApplication.translate("Dialog", u"\u0414\u0435\u0444\u0435\u043a\u0442\u044b \u0440\u0430\u0441\u043a\u0430\u0442\u0430", None))
        self.label_1.setText(QCoreApplication.translate("Dialog", u"\u0414\u0435\u0444\u0435\u043a\u0442\u044b \u0440\u0430\u0441\u043a\u0430\u0442\u0430", None))
        self.toolButton_2.setText(QCoreApplication.translate("Dialog", u"+", None))
        self.toolButton_3.setText(QCoreApplication.translate("Dialog", u"-", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"\u0411\u0440\u0430\u043a \u0432 \u0434\u0435\u0442\u0430\u043b\u044f\u0445", None))
        self.add_2.setText(QCoreApplication.translate("Dialog", u"+", None))
        self.remove_2.setText(QCoreApplication.translate("Dialog", u"-", None))
        self.leftoverSizes.setTitle(QCoreApplication.translate("Dialog", u"\u041f\u0430\u0440\u0430\u043c\u0435\u0442\u0440\u044b \u043e\u0441\u0442\u0430\u0442\u043a\u0430", None))
        self.label_7.setText(QCoreApplication.translate("Dialog", u"\u0414\u043b\u0438\u043d\u0430:    ", None))
        self.leftoverHeight.setSuffix(QCoreApplication.translate("Dialog", u" \u043c\u043c", None))
        self.label_8.setText(QCoreApplication.translate("Dialog", u"\u0428\u0438\u0440\u0438\u043d\u0430:    ", None))
        self.leftoverWidth.setSuffix(QCoreApplication.translate("Dialog", u" \u043c\u043c", None))
        self.addLeftover.setText(QCoreApplication.translate("Dialog", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u043e\u0441\u0442\u0430\u0442\u043e\u043a", None))
        ___qtablewidgetitem = self.leftoversTable.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("Dialog", u"\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435", None));
        ___qtablewidgetitem1 = self.leftoversTable.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("Dialog", u"\u0414\u043b\u0438\u043d\u0430", None));
        ___qtablewidgetitem2 = self.leftoversTable.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("Dialog", u"\u0428\u0438\u0440\u0438\u043d\u0430", None));
        ___qtablewidgetitem3 = self.leftoversTable.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("Dialog", u"\u0422\u043e\u043b\u0449\u0438\u043d\u0430", None));
        self.finish.setText(QCoreApplication.translate("Dialog", u"\u0417\u0430\u0432\u0435\u0440\u0448\u0438\u0442\u044c", None))
        self.cancel.setText(QCoreApplication.translate("Dialog", u"\u041e\u0442\u043c\u0435\u043d\u0430", None))
    # retranslateUi

