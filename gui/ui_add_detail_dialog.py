# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'add_detail_dialogdwWkze.ui'
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
        Dialog.resize(514, 322)
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
        self.designation = QLabel(self.parentParameters)
        self.designation.setObjectName(u"designation")

        self.gridLayout.addWidget(self.designation, 2, 1, 1, 1)

        self.label = QLabel(self.parentParameters)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.register_number = QLabel(self.parentParameters)
        self.register_number.setObjectName(u"register_number")

        self.gridLayout.addWidget(self.register_number, 0, 1, 1, 1)

        self.label_3 = QLabel(self.parentParameters)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)

        self.label_2 = QLabel(self.parentParameters)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.product_type = QLabel(self.parentParameters)
        self.product_type.setObjectName(u"product_type")

        self.gridLayout.addWidget(self.product_type, 1, 1, 1, 1)

        self.gridLayout.setColumnStretch(1, 1)
        self.gridLayout.setColumnMinimumWidth(0, 110)

        self.verticalLayout_2.addWidget(self.parentParameters)

        self.parameters_1 = QFrame(self.frame)
        self.parameters_1.setObjectName(u"parameters_1")
        self.parameters_1.setFrameShape(QFrame.StyledPanel)
        self.parameters_1.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.parameters_1)
        self.horizontalLayout_3.setSpacing(10)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.name = QLineEdit(self.parameters_1)
        self.name.setObjectName(u"name")
        self.name.setMinimumSize(QSize(320, 0))
        self.name.setMaximumSize(QSize(16777215, 16777215))

        self.horizontalLayout_3.addWidget(self.name)

        self.fusions = QComboBox(self.parameters_1)
        self.fusions.setObjectName(u"fusions")
        self.fusions.setMinimumSize(QSize(110, 0))
        self.fusions.setMaximumSize(QSize(110, 16777215))

        self.horizontalLayout_3.addWidget(self.fusions)


        self.verticalLayout_2.addWidget(self.parameters_1)

        self.parameters_2 = QFrame(self.frame)
        self.parameters_2.setObjectName(u"parameters_2")
        self.parameters_2.setFrameShape(QFrame.StyledPanel)
        self.parameters_2.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.parameters_2)
        self.horizontalLayout_2.setSpacing(10)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.sizes = QGroupBox(self.parameters_2)
        self.sizes.setObjectName(u"sizes")
        self.sizes.setMaximumSize(QSize(180, 16777215))
        self.formLayout = QFormLayout(self.sizes)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setHorizontalSpacing(10)
        self.formLayout.setVerticalSpacing(5)
        self.formLayout.setContentsMargins(10, 10, 10, 10)
        self.label_4 = QLabel(self.sizes)
        self.label_4.setObjectName(u"label_4")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label_4)

        self.height = QSpinBox(self.sizes)
        self.height.setObjectName(u"height")
        self.height.setMaximum(3000)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.height)

        self.label_5 = QLabel(self.sizes)
        self.label_5.setObjectName(u"label_5")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_5)

        self.width = QSpinBox(self.sizes)
        self.width.setObjectName(u"width")
        self.width.setMaximum(3000)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.width)

        self.label_6 = QLabel(self.sizes)
        self.label_6.setObjectName(u"label_6")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_6)

        self.depth = QDoubleSpinBox(self.sizes)
        self.depth.setObjectName(u"depth")
        self.depth.setMaximum(3000.000000000000000)

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.depth)


        self.horizontalLayout_2.addWidget(self.sizes)

        self.extra = QGroupBox(self.parameters_2)
        self.extra.setObjectName(u"extra")
        self.formLayout_2 = QFormLayout(self.extra)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.label_7 = QLabel(self.extra)
        self.label_7.setObjectName(u"label_7")

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.label_7)

        self.direction = QComboBox(self.extra)
        self.direction.addItem("")
        self.direction.addItem("")
        self.direction.addItem("")
        self.direction.setObjectName(u"direction")

        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.direction)

        self.label_8 = QLabel(self.extra)
        self.label_8.setObjectName(u"label_8")

        self.formLayout_2.setWidget(1, QFormLayout.LabelRole, self.label_8)

        self.priority = QSpinBox(self.extra)
        self.priority.setObjectName(u"priority")

        self.formLayout_2.setWidget(1, QFormLayout.FieldRole, self.priority)

        self.label_9 = QLabel(self.extra)
        self.label_9.setObjectName(u"label_9")

        self.formLayout_2.setWidget(2, QFormLayout.LabelRole, self.label_9)

        self.amount = QSpinBox(self.extra)
        self.amount.setObjectName(u"amount")

        self.formLayout_2.setWidget(2, QFormLayout.FieldRole, self.amount)


        self.horizontalLayout_2.addWidget(self.extra)


        self.verticalLayout_2.addWidget(self.parameters_2)


        self.verticalLayout.addWidget(self.frame)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

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
        self.designation.setText(QCoreApplication.translate("Dialog", u"...", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"\u041d\u043e\u043c\u0435\u0440 \u0432\u0435\u0434\u043e\u043c\u043e\u0441\u0442\u0438:", None))
        self.register_number.setText(QCoreApplication.translate("Dialog", u"...", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", u"\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u043f\u0440\u043e\u0434\u0443\u043a\u0446\u0438\u0438:", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"\u0422\u0438\u043f \u043f\u0440\u043e\u0434\u0443\u043a\u0446\u0438\u0438:", None))
        self.product_type.setText(QCoreApplication.translate("Dialog", u"...", None))
        self.name.setPlaceholderText(QCoreApplication.translate("Dialog", u"\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u0434\u0435\u0442\u0430\u043b\u0438...", None))
        self.sizes.setTitle(QCoreApplication.translate("Dialog", u"\u0413\u0430\u0431\u0430\u0440\u0438\u0442\u043d\u044b\u0435 \u0440\u0430\u0437\u043c\u0435\u0440\u044b", None))
        self.label_4.setText(QCoreApplication.translate("Dialog", u"\u0414\u043b\u0438\u043d\u0430:", None))
        self.height.setSuffix(QCoreApplication.translate("Dialog", u" \u043c\u043c", None))
        self.label_5.setText(QCoreApplication.translate("Dialog", u"\u0428\u0438\u0440\u0438\u043d\u0430:", None))
        self.width.setSuffix(QCoreApplication.translate("Dialog", u" \u043c\u043c", None))
        self.label_6.setText(QCoreApplication.translate("Dialog", u"\u0422\u043e\u043b\u0449\u0438\u043d\u0430:", None))
        self.depth.setSuffix(QCoreApplication.translate("Dialog", u" \u043c\u043c", None))
        self.extra.setTitle(QCoreApplication.translate("Dialog", u"\u0414\u043e\u043f\u043e\u043b\u043d\u0438\u0442\u0435\u043b\u044c\u043d\u044b\u0435 \u043f\u0430\u0440\u0430\u043c\u0435\u0442\u0440\u044b", None))
        self.label_7.setText(QCoreApplication.translate("Dialog", u"\u041f\u043e\u0432\u043e\u0440\u043e\u0442:", None))
        self.direction.setItemText(0, QCoreApplication.translate("Dialog", u"\u041b\u044e\u0431\u043e\u0439", None))
        self.direction.setItemText(1, QCoreApplication.translate("Dialog", u"\u041f\u043e \u043d\u0430\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u044e \u043f\u0440\u043e\u043a\u0430\u0442\u0430", None))
        self.direction.setItemText(2, QCoreApplication.translate("Dialog", u"\u041f\u0440\u043e\u0442\u0438\u0432 \u043d\u0430\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u044f \u043f\u0440\u043e\u043a\u0430\u0442\u0430", None))

        self.label_8.setText(QCoreApplication.translate("Dialog", u"\u041f\u0440\u0438\u043e\u0440\u0438\u0442\u0435\u0442:", None))
        self.label_9.setText(QCoreApplication.translate("Dialog", u"\u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e:", None))
        self.add.setText(QCoreApplication.translate("Dialog", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c", None))
        self.ok.setText(QCoreApplication.translate("Dialog", u"OK", None))
        self.cancel.setText(QCoreApplication.translate("Dialog", u"\u041e\u0442\u043c\u0435\u043d\u0430", None))
    # retranslateUi

