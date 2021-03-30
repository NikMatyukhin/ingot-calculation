# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'add_article_dialogorkteU.ui'
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
        Dialog.resize(514, 259)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 10, 0, 0)
        self.frame = QFrame(Dialog)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame)
        self.verticalLayout_2.setSpacing(10)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(10, 0, 10, 0)
        self.parentParameters = QGroupBox(self.frame)
        self.parentParameters.setObjectName(u"parentParameters")
        self.gridLayout = QGridLayout(self.parentParameters)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setHorizontalSpacing(10)
        self.gridLayout.setVerticalSpacing(5)
        self.gridLayout.setContentsMargins(10, 10, 10, 10)
        self.product_type = QLabel(self.parentParameters)
        self.product_type.setObjectName(u"product_type")

        self.gridLayout.addWidget(self.product_type, 1, 1, 1, 1)

        self.designation = QLabel(self.parentParameters)
        self.designation.setObjectName(u"designation")

        self.gridLayout.addWidget(self.designation, 2, 1, 1, 1)

        self.label_1 = QLabel(self.parentParameters)
        self.label_1.setObjectName(u"label_1")

        self.gridLayout.addWidget(self.label_1, 0, 0, 1, 1)

        self.register_number = QLabel(self.parentParameters)
        self.register_number.setObjectName(u"register_number")

        self.gridLayout.addWidget(self.register_number, 0, 1, 1, 1)

        self.label_2 = QLabel(self.parentParameters)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.label_3 = QLabel(self.parentParameters)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)


        self.verticalLayout_2.addWidget(self.parentParameters)

        self.parameters = QGroupBox(self.frame)
        self.parameters.setObjectName(u"parameters")
        self.gridLayout_2 = QGridLayout(self.parameters)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setHorizontalSpacing(10)
        self.gridLayout_2.setVerticalSpacing(5)
        self.gridLayout_2.setContentsMargins(10, 10, 10, 10)
        self.label_4 = QLabel(self.parameters)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_2.addWidget(self.label_4, 0, 0, 1, 1)

        self.rent = QCheckBox(self.parameters)
        self.rent.setObjectName(u"rent")

        self.gridLayout_2.addWidget(self.rent, 1, 1, 1, 1)

        self.nomenclature = QLineEdit(self.parameters)
        self.nomenclature.setObjectName(u"nomenclature")
        self.nomenclature.setClearButtonEnabled(True)

        self.gridLayout_2.addWidget(self.nomenclature, 0, 1, 1, 1)

        self.gridLayout_2.setColumnMinimumWidth(0, 120)

        self.verticalLayout_2.addWidget(self.parameters)


        self.verticalLayout.addWidget(self.frame)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_2)

        self.buttonArea = QFrame(Dialog)
        self.buttonArea.setObjectName(u"buttonArea")
        self.buttonArea.setMaximumSize(QSize(16777215, 40))
        self.buttonArea.setFrameShape(QFrame.StyledPanel)
        self.buttonArea.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.buttonArea)
        self.horizontalLayout.setSpacing(10)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 10, 10)
        self.horizontalSpacer_1 = QSpacerItem(142, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

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
        self.parentParameters.setTitle(QCoreApplication.translate("Dialog", u"\u041f\u0430\u0440\u0430\u043c\u0435\u0442\u0440\u044b \u043f\u0440\u043e\u0434\u0443\u043a\u0446\u0438\u0438", None))
        self.product_type.setText(QCoreApplication.translate("Dialog", u"...", None))
        self.designation.setText(QCoreApplication.translate("Dialog", u"...", None))
        self.label_1.setText(QCoreApplication.translate("Dialog", u"\u041d\u043e\u043c\u0435\u0440 \u0432\u0435\u0434\u043e\u043c\u043e\u0441\u0442\u0438:", None))
        self.register_number.setText(QCoreApplication.translate("Dialog", u"...", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"\u0422\u0438\u043f \u043f\u0440\u043e\u0434\u0443\u043a\u0446\u0438\u0438:", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", u"\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u043f\u0440\u043e\u0434\u0443\u043a\u0446\u0438\u0438:", None))
        self.parameters.setTitle(QCoreApplication.translate("Dialog", u"\u041f\u0430\u0440\u0430\u043c\u0435\u0442\u0440\u044b \u0438\u0437\u0434\u0435\u043b\u0438\u044f", None))
        self.label_4.setText(QCoreApplication.translate("Dialog", u"\u041d\u043e\u043c\u0435\u043d\u043a\u043b\u0430\u0442\u0443\u0440\u0430:", None))
        self.rent.setText(QCoreApplication.translate("Dialog", u"\u0412 \u0430\u0440\u0435\u043d\u0434\u0443", None))
        self.nomenclature.setPlaceholderText(QCoreApplication.translate("Dialog", u"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u0430\u0440\u0442\u0438\u043a\u0443\u043b\u0430...", None))
        self.add.setText(QCoreApplication.translate("Dialog", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c", None))
        self.ok.setText(QCoreApplication.translate("Dialog", u"OK", None))
        self.cancel.setText(QCoreApplication.translate("Dialog", u"\u041e\u0442\u043c\u0435\u043d\u0430", None))
    # retranslateUi

