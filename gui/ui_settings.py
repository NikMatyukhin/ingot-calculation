# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'settingsmHLCik.ui'
##
## Created by: Qt User Interface Compiler version 6.0.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

import application_rc

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(460, 400)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setMinimumSize(QSize(460, 400))
        Dialog.setMaximumSize(QSize(460, 400))
        Dialog.setSizeGripEnabled(False)
        Dialog.setModal(True)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.mainArea = QFrame(Dialog)
        self.mainArea.setObjectName(u"mainArea")
        self.mainArea.setFrameShape(QFrame.NoFrame)
        self.mainArea.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_6 = QHBoxLayout(self.mainArea)
        self.horizontalLayout_6.setSpacing(0)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.leftBar = QFrame(self.mainArea)
        self.leftBar.setObjectName(u"leftBar")
        self.leftBar.setMinimumSize(QSize(0, 0))
        self.leftBar.setMaximumSize(QSize(16777215, 16777215))
        self.leftBar.setStyleSheet(u"background-color: rgb(225, 225, 225);")
        self.leftBar.setFrameShape(QFrame.NoFrame)
        self.leftBar.setFrameShadow(QFrame.Raised)
        self.verticalLayout_5 = QVBoxLayout(self.leftBar)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.cutting = QPushButton(self.leftBar)
        self.cutting.setObjectName(u"cutting")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.cutting.sizePolicy().hasHeightForWidth())
        self.cutting.setSizePolicy(sizePolicy1)
        self.cutting.setMinimumSize(QSize(100, 40))
        self.cutting.setMaximumSize(QSize(16777215, 40))
        self.cutting.setStyleSheet(u"QPushButton {\n"
"	background-color: rgb(225, 225, 225);;\n"
"	padding-left: 0px;\n"
"	border: none;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	background-color: rgb(217, 217, 217);\n"
"	border-right: 3px solid gray;\n"
"    padding-left: 3px;\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"	background-color: rgb(202, 202, 202);\n"
"	border-right: 3px solid black;\n"
"    padding-left: 3px;\n"
"}\n"
"\n"
"QPushButton:checked {\n"
"	background-color: rgb(217, 217, 217);\n"
"	border-right: 3px solid black;\n"
"    padding-left: 3px;\n"
"}")
        icon = QIcon()
        icon.addFile(u":/icons/scissors.png", QSize(), QIcon.Normal, QIcon.Off)
        self.cutting.setIcon(icon)
        self.cutting.setIconSize(QSize(20, 20))
        self.cutting.setCheckable(True)
        self.cutting.setChecked(True)
        self.cutting.setAutoExclusive(True)

        self.verticalLayout_5.addWidget(self.cutting)

        self.rolling = QPushButton(self.leftBar)
        self.rolling.setObjectName(u"rolling")
        sizePolicy1.setHeightForWidth(self.rolling.sizePolicy().hasHeightForWidth())
        self.rolling.setSizePolicy(sizePolicy1)
        self.rolling.setMinimumSize(QSize(100, 40))
        self.rolling.setMaximumSize(QSize(16777215, 40))
        self.rolling.setStyleSheet(u"QPushButton {\n"
"	background-color: rgb(225, 225, 225);;\n"
"	padding-left: 0px;\n"
"	border: none;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	background-color: rgb(217, 217, 217);\n"
"	border-right: 3px solid gray;\n"
"    padding-left: 3px;\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"	background-color: rgb(202, 202, 202);\n"
"	border-right: 3px solid black;\n"
"    padding-left: 3px;\n"
"}\n"
"\n"
"QPushButton:checked {\n"
"	background-color: rgb(217, 217, 217);\n"
"	border-right: 3px solid black;\n"
"    padding-left: 3px;\n"
"}")
        icon1 = QIcon()
        icon1.addFile(u":/icons/h-roll.png", QSize(), QIcon.Normal, QIcon.Off)
        self.rolling.setIcon(icon1)
        self.rolling.setIconSize(QSize(25, 25))
        self.rolling.setCheckable(True)
        self.rolling.setAutoExclusive(True)

        self.verticalLayout_5.addWidget(self.rolling)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_5.addItem(self.verticalSpacer_2)


        self.horizontalLayout_6.addWidget(self.leftBar)

        self.stackedWidget = QStackedWidget(self.mainArea)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.setFrameShape(QFrame.NoFrame)
        self.stackedWidget.setFrameShadow(QFrame.Raised)
        self.cuttingPage = QWidget()
        self.cuttingPage.setObjectName(u"cuttingPage")
        self.cuttingPage.setStyleSheet(u"QWidget#cuttingPage {\n"
"	background-color: rgb(255, 255, 255);\n"
"}")
        self.verticalLayout_6 = QVBoxLayout(self.cuttingPage)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(20, 10, 20, 10)
        self.cuttingLabel_1 = QLabel(self.cuttingPage)
        self.cuttingLabel_1.setObjectName(u"cuttingLabel_1")
        font = QFont()
        font.setPointSize(12)
        self.cuttingLabel_1.setFont(font)
        self.cuttingLabel_1.setStyleSheet(u"QLabel {\n"
"	background-color: rgb(234, 234, 234);\n"
"}")

        self.verticalLayout_6.addWidget(self.cuttingLabel_1)

        self.cuttingSettings_1 = QFrame(self.cuttingPage)
        self.cuttingSettings_1.setObjectName(u"cuttingSettings_1")
        self.formLayout_4 = QFormLayout(self.cuttingSettings_1)
        self.formLayout_4.setObjectName(u"formLayout_4")
        self.formLayout_4.setHorizontalSpacing(0)
        self.formLayout_4.setVerticalSpacing(10)
        self.formLayout_4.setContentsMargins(10, 10, 10, 10)
        self.label_10 = QLabel(self.cuttingSettings_1)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setMinimumSize(QSize(210, 0))
        self.label_10.setMaximumSize(QSize(210, 16777215))

        self.formLayout_4.setWidget(0, QFormLayout.LabelRole, self.label_10)

        self.doubleSpinBox = QDoubleSpinBox(self.cuttingSettings_1)
        self.doubleSpinBox.setObjectName(u"doubleSpinBox")
        self.doubleSpinBox.setMaximumSize(QSize(80, 16777215))
        self.doubleSpinBox.setDecimals(0)

        self.formLayout_4.setWidget(0, QFormLayout.FieldRole, self.doubleSpinBox)

        self.label_11 = QLabel(self.cuttingSettings_1)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setMinimumSize(QSize(210, 0))
        self.label_11.setMaximumSize(QSize(210, 16777215))

        self.formLayout_4.setWidget(1, QFormLayout.LabelRole, self.label_11)

        self.spinBox_11 = QSpinBox(self.cuttingSettings_1)
        self.spinBox_11.setObjectName(u"spinBox_11")
        self.spinBox_11.setMaximumSize(QSize(80, 16777215))
        self.spinBox_11.setMaximum(3000)

        self.formLayout_4.setWidget(1, QFormLayout.FieldRole, self.spinBox_11)

        self.label_12 = QLabel(self.cuttingSettings_1)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setMinimumSize(QSize(210, 0))
        self.label_12.setMaximumSize(QSize(210, 16777215))

        self.formLayout_4.setWidget(2, QFormLayout.LabelRole, self.label_12)

        self.spinBox_12 = QSpinBox(self.cuttingSettings_1)
        self.spinBox_12.setObjectName(u"spinBox_12")
        self.spinBox_12.setMaximumSize(QSize(80, 16777215))
        self.spinBox_12.setMaximum(3000)

        self.formLayout_4.setWidget(2, QFormLayout.FieldRole, self.spinBox_12)


        self.verticalLayout_6.addWidget(self.cuttingSettings_1)

        self.cuttingLabel_2 = QLabel(self.cuttingPage)
        self.cuttingLabel_2.setObjectName(u"cuttingLabel_2")
        self.cuttingLabel_2.setFont(font)
        self.cuttingLabel_2.setStyleSheet(u"QLabel {\n"
"	background-color: rgb(234, 234, 234);\n"
"}")

        self.verticalLayout_6.addWidget(self.cuttingLabel_2)

        self.cuttingSettings_2 = QFrame(self.cuttingPage)
        self.cuttingSettings_2.setObjectName(u"cuttingSettings_2")
        self.cuttingSettings_2.setFrameShape(QFrame.StyledPanel)
        self.cuttingSettings_2.setFrameShadow(QFrame.Raised)
        self.formLayout_5 = QFormLayout(self.cuttingSettings_2)
        self.formLayout_5.setObjectName(u"formLayout_5")
        self.formLayout_5.setHorizontalSpacing(0)
        self.formLayout_5.setVerticalSpacing(10)
        self.formLayout_5.setContentsMargins(10, 10, 10, 10)
        self.label_8 = QLabel(self.cuttingSettings_2)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setMinimumSize(QSize(210, 0))
        self.label_8.setMaximumSize(QSize(210, 16777215))

        self.formLayout_5.setWidget(0, QFormLayout.LabelRole, self.label_8)

        self.spinBox_8 = QSpinBox(self.cuttingSettings_2)
        self.spinBox_8.setObjectName(u"spinBox_8")
        self.spinBox_8.setMaximumSize(QSize(80, 16777215))
        self.spinBox_8.setReadOnly(True)
        self.spinBox_8.setMaximum(3000)

        self.formLayout_5.setWidget(0, QFormLayout.FieldRole, self.spinBox_8)

        self.label_9 = QLabel(self.cuttingSettings_2)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setMinimumSize(QSize(210, 0))
        self.label_9.setMaximumSize(QSize(210, 16777215))

        self.formLayout_5.setWidget(1, QFormLayout.LabelRole, self.label_9)

        self.spinBox_9 = QSpinBox(self.cuttingSettings_2)
        self.spinBox_9.setObjectName(u"spinBox_9")
        self.spinBox_9.setMinimumSize(QSize(0, 0))
        self.spinBox_9.setMaximumSize(QSize(80, 16777215))
        self.spinBox_9.setMaximum(3000)

        self.formLayout_5.setWidget(1, QFormLayout.FieldRole, self.spinBox_9)

        self.label_13 = QLabel(self.cuttingSettings_2)
        self.label_13.setObjectName(u"label_13")

        self.formLayout_5.setWidget(2, QFormLayout.LabelRole, self.label_13)

        self.doubleSpinBox_3 = QDoubleSpinBox(self.cuttingSettings_2)
        self.doubleSpinBox_3.setObjectName(u"doubleSpinBox_3")
        self.doubleSpinBox_3.setMaximumSize(QSize(80, 16777215))
        self.doubleSpinBox_3.setDecimals(1)

        self.formLayout_5.setWidget(2, QFormLayout.FieldRole, self.doubleSpinBox_3)


        self.verticalLayout_6.addWidget(self.cuttingSettings_2)

        self.verticalSpacer_1 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_6.addItem(self.verticalSpacer_1)

        self.stackedWidget.addWidget(self.cuttingPage)
        self.rollingPage = QWidget()
        self.rollingPage.setObjectName(u"rollingPage")
        self.rollingPage.setStyleSheet(u"QWidget#rollingPage {\n"
"	background-color: rgb(255, 255, 255);\n"
"}")
        self.verticalLayout_7 = QVBoxLayout(self.rollingPage)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(20, 10, 20, 10)
        self.rollingLabel_1 = QLabel(self.rollingPage)
        self.rollingLabel_1.setObjectName(u"rollingLabel_1")
        self.rollingLabel_1.setFont(font)
        self.rollingLabel_1.setStyleSheet(u"QLabel {\n"
"	background-color: rgb(234, 234, 234);\n"
"}")

        self.verticalLayout_7.addWidget(self.rollingLabel_1)

        self.rollingSettings_1 = QFrame(self.rollingPage)
        self.rollingSettings_1.setObjectName(u"rollingSettings_1")
        self.formLayout_2 = QFormLayout(self.rollingSettings_1)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.formLayout_2.setHorizontalSpacing(0)
        self.formLayout_2.setVerticalSpacing(10)
        self.formLayout_2.setContentsMargins(10, 10, 10, 10)
        self.label_2 = QLabel(self.rollingSettings_1)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMinimumSize(QSize(210, 0))
        self.label_2.setMaximumSize(QSize(180, 16777215))

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.label_2)

        self.spinBox_2 = QSpinBox(self.rollingSettings_1)
        self.spinBox_2.setObjectName(u"spinBox_2")
        self.spinBox_2.setMaximumSize(QSize(80, 16777215))
        self.spinBox_2.setReadOnly(True)
        self.spinBox_2.setMaximum(3000)

        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.spinBox_2)

        self.label_3 = QLabel(self.rollingSettings_1)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setMinimumSize(QSize(210, 0))
        self.label_3.setMaximumSize(QSize(180, 16777215))

        self.formLayout_2.setWidget(1, QFormLayout.LabelRole, self.label_3)

        self.spinBox_3 = QSpinBox(self.rollingSettings_1)
        self.spinBox_3.setObjectName(u"spinBox_3")
        self.spinBox_3.setMaximumSize(QSize(80, 16777215))
        self.spinBox_3.setReadOnly(True)
        self.spinBox_3.setMaximum(3000)

        self.formLayout_2.setWidget(1, QFormLayout.FieldRole, self.spinBox_3)

        self.label_5 = QLabel(self.rollingSettings_1)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setMinimumSize(QSize(210, 0))
        self.label_5.setMaximumSize(QSize(180, 16777215))

        self.formLayout_2.setWidget(2, QFormLayout.LabelRole, self.label_5)

        self.spinBox_5 = QSpinBox(self.rollingSettings_1)
        self.spinBox_5.setObjectName(u"spinBox_5")
        self.spinBox_5.setMaximumSize(QSize(80, 16777215))
        self.spinBox_5.setReadOnly(True)
        self.spinBox_5.setMaximum(3000)

        self.formLayout_2.setWidget(2, QFormLayout.FieldRole, self.spinBox_5)

        self.changeMachine = QPushButton(self.rollingSettings_1)
        self.changeMachine.setObjectName(u"changeMachine")
        self.changeMachine.setEnabled(False)
        self.changeMachine.setMaximumSize(QSize(80, 16777215))

        self.formLayout_2.setWidget(3, QFormLayout.FieldRole, self.changeMachine)


        self.verticalLayout_7.addWidget(self.rollingSettings_1)

        self.rollingLabel_2 = QLabel(self.rollingPage)
        self.rollingLabel_2.setObjectName(u"rollingLabel_2")
        self.rollingLabel_2.setFont(font)
        self.rollingLabel_2.setStyleSheet(u"QLabel {\n"
"	background-color: rgb(234, 234, 234);\n"
"}")

        self.verticalLayout_7.addWidget(self.rollingLabel_2)

        self.rollingSettings_2 = QFrame(self.rollingPage)
        self.rollingSettings_2.setObjectName(u"rollingSettings_2")
        self.formLayout_3 = QFormLayout(self.rollingSettings_2)
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.formLayout_3.setHorizontalSpacing(0)
        self.formLayout_3.setVerticalSpacing(10)
        self.formLayout_3.setContentsMargins(10, 10, 10, 10)
        self.label_6 = QLabel(self.rollingSettings_2)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setMinimumSize(QSize(210, 0))
        self.label_6.setMaximumSize(QSize(180, 16777215))

        self.formLayout_3.setWidget(0, QFormLayout.LabelRole, self.label_6)

        self.spinBox_6 = QSpinBox(self.rollingSettings_2)
        self.spinBox_6.setObjectName(u"spinBox_6")
        self.spinBox_6.setMaximumSize(QSize(80, 16777215))
        self.spinBox_6.setMaximum(3000)

        self.formLayout_3.setWidget(0, QFormLayout.FieldRole, self.spinBox_6)

        self.label_7 = QLabel(self.rollingSettings_2)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setMinimumSize(QSize(210, 0))
        self.label_7.setMaximumSize(QSize(180, 16777215))

        self.formLayout_3.setWidget(1, QFormLayout.LabelRole, self.label_7)

        self.spinBox_7 = QSpinBox(self.rollingSettings_2)
        self.spinBox_7.setObjectName(u"spinBox_7")
        self.spinBox_7.setMaximumSize(QSize(80, 16777215))
        self.spinBox_7.setMaximum(3000)

        self.formLayout_3.setWidget(1, QFormLayout.FieldRole, self.spinBox_7)


        self.verticalLayout_7.addWidget(self.rollingSettings_2)

        self.rollingLabel_3 = QLabel(self.rollingPage)
        self.rollingLabel_3.setObjectName(u"rollingLabel_3")
        self.rollingLabel_3.setFont(font)
        self.rollingLabel_3.setStyleSheet(u"QLabel {\n"
"	background-color: rgb(234, 234, 234);\n"
"}")

        self.verticalLayout_7.addWidget(self.rollingLabel_3)

        self.rollingSettings_3 = QFrame(self.rollingPage)
        self.rollingSettings_3.setObjectName(u"rollingSettings_3")
        self.rollingSettings_3.setFrameShape(QFrame.NoFrame)
        self.rollingSettings_3.setFrameShadow(QFrame.Raised)
        self.formLayout = QFormLayout(self.rollingSettings_3)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setHorizontalSpacing(0)
        self.formLayout.setVerticalSpacing(10)
        self.formLayout.setContentsMargins(10, 10, 10, 10)
        self.label_4 = QLabel(self.rollingSettings_3)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setMinimumSize(QSize(210, 0))
        self.label_4.setMaximumSize(QSize(180, 16777215))

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label_4)

        self.spinBox_4 = QSpinBox(self.rollingSettings_3)
        self.spinBox_4.setObjectName(u"spinBox_4")
        self.spinBox_4.setMaximumSize(QSize(80, 16777215))
        self.spinBox_4.setReadOnly(True)
        self.spinBox_4.setMaximum(3000)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.spinBox_4)

        self.label = QLabel(self.rollingSettings_3)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(210, 0))
        self.label.setMaximumSize(QSize(180, 16777215))

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label)

        self.doubleSpinBox_2 = QDoubleSpinBox(self.rollingSettings_3)
        self.doubleSpinBox_2.setObjectName(u"doubleSpinBox_2")
        self.doubleSpinBox_2.setMaximumSize(QSize(80, 16777215))
        self.doubleSpinBox_2.setDecimals(0)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.doubleSpinBox_2)


        self.verticalLayout_7.addWidget(self.rollingSettings_3)

        self.stackedWidget.addWidget(self.rollingPage)

        self.horizontalLayout_6.addWidget(self.stackedWidget)


        self.verticalLayout.addWidget(self.mainArea)

        self.buttonArea = QFrame(Dialog)
        self.buttonArea.setObjectName(u"buttonArea")
        self.buttonArea.setMinimumSize(QSize(0, 40))
        self.buttonArea.setMaximumSize(QSize(16777215, 40))
        self.buttonArea.setFrameShape(QFrame.NoFrame)
        self.buttonArea.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.buttonArea)
        self.horizontalLayout.setSpacing(10)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 10, 0)
        self.horizontalSpacer_1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_1)

        self.save = QPushButton(self.buttonArea)
        self.save.setObjectName(u"save")
        self.save.setMinimumSize(QSize(80, 0))

        self.horizontalLayout.addWidget(self.save)

        self.cancel = QPushButton(self.buttonArea)
        self.cancel.setObjectName(u"cancel")

        self.horizontalLayout.addWidget(self.cancel)


        self.verticalLayout.addWidget(self.buttonArea)


        self.retranslateUi(Dialog)

        self.stackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438", None))
        self.cutting.setText(QCoreApplication.translate("Dialog", u"\u0420\u0430\u0441\u043a\u0440\u043e\u0439", None))
        self.rolling.setText(QCoreApplication.translate("Dialog", u"\u041f\u0440\u043e\u043a\u0430\u0442", None))
        self.cuttingLabel_1.setText(QCoreApplication.translate("Dialog", u"\u041f\u043e\u0442\u0435\u0440\u0438 \u043f\u0440\u0438 \u043e\u0431\u0440\u0430\u0431\u043e\u0442\u043a\u0435", None))
        self.label_10.setText(QCoreApplication.translate("Dialog", u"\u041e\u0431\u0440\u0430\u0431\u043e\u0442\u043a\u0430 \u0442\u043e\u0440\u0446\u043e\u0432", None))
        self.doubleSpinBox.setSuffix(QCoreApplication.translate("Dialog", u" %", None))
        self.label_11.setText(QCoreApplication.translate("Dialog", u"\u041e\u0431\u0440\u0430\u0431\u043e\u0442\u043a\u0430 \u043a\u0440\u043e\u043c\u043a\u0438 (\u0434\u043e 3 \u043c\u043c)", None))
        self.spinBox_11.setSuffix(QCoreApplication.translate("Dialog", u" \u043c\u043c", None))
        self.label_12.setText(QCoreApplication.translate("Dialog", u"\u041e\u0431\u0440\u0430\u0431\u043e\u0442\u043a\u0430 \u043a\u0440\u043e\u043c\u043a\u0438 (\u043f\u043e\u0441\u043b\u0435 3 \u043c\u043c)", None))
        self.spinBox_12.setSuffix(QCoreApplication.translate("Dialog", u" \u043c\u043c", None))
        self.cuttingLabel_2.setText(QCoreApplication.translate("Dialog", u"\u041f\u0440\u043e\u0447\u0438\u0435 \u043d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438", None))
        self.label_8.setText(QCoreApplication.translate("Dialog", u"\u0428\u0438\u0440\u0438\u043d\u0430 \u043d\u043e\u0436\u0430 \u0433\u0438\u043b\u044c\u043e\u0442\u0438\u043d\u044b", None))
        self.spinBox_8.setSuffix(QCoreApplication.translate("Dialog", u" \u043c\u043c", None))
        self.label_9.setText(QCoreApplication.translate("Dialog", u"\u041f\u0440\u0438\u043f\u0443\u0441\u043a \u043d\u0430 \u0440\u0430\u0437\u0440\u0435\u0437", None))
        self.spinBox_9.setSuffix(QCoreApplication.translate("Dialog", u" \u043c\u043c", None))
        self.label_13.setText(QCoreApplication.translate("Dialog", u"\u0422\u043e\u043b\u0449\u0438\u043d\u0430 \u043d\u0430\u0447\u0430\u043b\u0430 \u0440\u0430\u0441\u043a\u0440\u043e\u044f", None))
        self.doubleSpinBox_3.setSuffix(QCoreApplication.translate("Dialog", u" \u043c\u043c", None))
        self.rollingLabel_1.setText(QCoreApplication.translate("Dialog", u"\u0420\u0430\u0437\u043c\u0435\u0440\u044b \u043f\u0440\u043e\u043a\u0430\u0442\u0430", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"\u041e\u0431\u044b\u0447\u043d\u044b\u0439 \u043f\u0440\u043e\u043a\u0430\u0442", None))
        self.spinBox_2.setSuffix(QCoreApplication.translate("Dialog", u" \u043c\u043c", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", u"\u0427\u0438\u0441\u0442\u043e\u0432\u043e\u0439 \u043f\u0440\u043e\u043a\u0430\u0442", None))
        self.spinBox_3.setSuffix(QCoreApplication.translate("Dialog", u" \u043c\u043c", None))
        self.label_5.setText(QCoreApplication.translate("Dialog", u"\u041c\u0430\u043a\u0441\u0438\u043c\u0430\u043b\u044c\u043d\u0430\u044f \u0434\u043b\u0438\u043d\u0430 \u043f\u0440\u043e\u043a\u0430\u0442\u0430", None))
        self.spinBox_5.setSuffix(QCoreApplication.translate("Dialog", u" \u043c\u043c", None))
        self.changeMachine.setText(QCoreApplication.translate("Dialog", u"\u0421\u0442\u0430\u043d\u043e\u043a", None))
        self.rollingLabel_2.setText(QCoreApplication.translate("Dialog", u"\u0420\u0430\u0437\u043c\u0435\u0440\u044b \u043f\u043b\u0430\u0441\u0442\u0438\u043d\u044b", None))
        self.label_6.setText(QCoreApplication.translate("Dialog", u"\u0428\u0438\u0440\u0438\u043d\u0430 \u043f\u043b\u0430\u0441\u0442\u0438\u043d\u044b", None))
        self.spinBox_6.setSuffix(QCoreApplication.translate("Dialog", u" \u043c\u043c", None))
        self.label_7.setText(QCoreApplication.translate("Dialog", u"\u0414\u043b\u0438\u043d\u0430 \u043f\u043b\u0430\u0441\u0442\u0438\u043d\u044b", None))
        self.spinBox_7.setSuffix(QCoreApplication.translate("Dialog", u" \u043c\u043c", None))
        self.rollingLabel_3.setText(QCoreApplication.translate("Dialog", u"\u041f\u0440\u043e\u0447\u0438\u0435 \u043d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438", None))
        self.label_4.setText(QCoreApplication.translate("Dialog", u"\u0422\u043e\u043b\u0449\u0438\u043d\u0430 \u0447\u0438\u0441\u0442\u043e\u0432\u043e\u0433\u043e \u043f\u0440\u043e\u043a\u0430\u0442\u0430", None))
        self.spinBox_4.setSuffix(QCoreApplication.translate("Dialog", u" \u043c\u043c", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"\u0414\u043e\u043f\u0443\u0441\u0442\u0438\u043c\u0430\u044f \u0434\u0435\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u044f", None))
        self.doubleSpinBox_2.setSuffix(QCoreApplication.translate("Dialog", u" %", None))
        self.save.setText(QCoreApplication.translate("Dialog", u"\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c", None))
        self.cancel.setText(QCoreApplication.translate("Dialog", u"\u041e\u0442\u043c\u0435\u043d\u0430", None))
    # retranslateUi

