# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'add_product_dialogzyCZxP.ui'
##
## Created by: Qt User Interface Compiler version 6.0.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(514, 175)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(10, 10, 10, 0)
        self.parameters = QGroupBox(Dialog)
        self.parameters.setObjectName(u"parameters")
        self.gridLayout = QGridLayout(self.parameters)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setHorizontalSpacing(10)
        self.gridLayout.setVerticalSpacing(5)
        self.gridLayout.setContentsMargins(10, 10, 10, 10)
        self.label_3 = QLabel(self.parameters)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)

        self.register_number = QLineEdit(self.parameters)
        self.register_number.setObjectName(u"register_number")
        self.register_number.setClearButtonEnabled(True)

        self.gridLayout.addWidget(self.register_number, 0, 1, 1, 1)

        self.product_type = QLineEdit(self.parameters)
        self.product_type.setObjectName(u"product_type")
        self.product_type.setClearButtonEnabled(True)

        self.gridLayout.addWidget(self.product_type, 1, 1, 1, 1)

        self.label_1 = QLabel(self.parameters)
        self.label_1.setObjectName(u"label_1")

        self.gridLayout.addWidget(self.label_1, 0, 0, 1, 1)

        self.label_2 = QLabel(self.parameters)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.designation = QLineEdit(self.parameters)
        self.designation.setObjectName(u"designation")
        self.designation.setClearButtonEnabled(True)

        self.gridLayout.addWidget(self.designation, 2, 1, 1, 1)

        self.verticalSpacer_1 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer_1, 3, 1, 1, 1)


        self.verticalLayout.addWidget(self.parameters)

        self.buttonArea = QFrame(Dialog)
        self.buttonArea.setObjectName(u"buttonArea")
        self.buttonArea.setMaximumSize(QSize(16777215, 40))
        self.buttonArea.setFrameShape(QFrame.StyledPanel)
        self.buttonArea.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.buttonArea)
        self.horizontalLayout.setSpacing(10)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 10)
        self.horizontalSpacer_1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_1)

        self.add = QPushButton(self.buttonArea)
        self.add.setObjectName(u"add")
        self.add.setMinimumSize(QSize(90, 0))

        self.horizontalLayout.addWidget(self.add)

        self.ok = QPushButton(self.buttonArea)
        self.ok.setObjectName(u"ok")

        self.horizontalLayout.addWidget(self.ok)

        self.cancel = QPushButton(self.buttonArea)
        self.cancel.setObjectName(u"cancel")

        self.horizontalLayout.addWidget(self.cancel)


        self.verticalLayout.addWidget(self.buttonArea)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.parameters.setTitle(QCoreApplication.translate("Dialog", u"\u041f\u0430\u0440\u0430\u043c\u0435\u0442\u0440\u044b \u043f\u0440\u043e\u0434\u0443\u043a\u0446\u0438\u0438", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", u"\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u043f\u0440\u043e\u0434\u0443\u043a\u0446\u0438\u0438:", None))
        self.register_number.setPlaceholderText(QCoreApplication.translate("Dialog", u"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u043d\u043e\u043c\u0435\u0440 \u0432\u0435\u0434\u043e\u043c\u043e\u0441\u0442\u0438...", None))
        self.product_type.setPlaceholderText(QCoreApplication.translate("Dialog", u"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u0442\u0438\u043f \u043f\u0440\u043e\u0434\u0443\u043a\u0446\u0438\u0438...", None))
        self.label_1.setText(QCoreApplication.translate("Dialog", u"\u041d\u043e\u043c\u0435\u0440 \u0432\u0435\u0434\u043e\u043c\u043e\u0441\u0442\u0438:", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"\u0422\u0438\u043f \u043f\u0440\u043e\u0434\u0443\u043a\u0446\u0438\u0438:", None))
        self.designation.setPlaceholderText(QCoreApplication.translate("Dialog", u"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u043f\u0440\u043e\u0434\u0443\u043a\u0446\u0438\u0438...", None))
        self.add.setText(QCoreApplication.translate("Dialog", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c", None))
        self.ok.setText(QCoreApplication.translate("Dialog", u"OK", None))
        self.cancel.setText(QCoreApplication.translate("Dialog", u"\u041e\u0442\u043c\u0435\u043d\u0430", None))
    # retranslateUi

