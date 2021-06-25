# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'add_ingot_dialogzjpdoZ.ui'
##
## Created by: Qt User Interface Compiler version 6.0.3
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
        Dialog.resize(328, 237)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(10, 10, 10, 0)
        self.parameters = QGroupBox(Dialog)
        self.parameters.setObjectName(u"parameters")
        self.formLayout = QFormLayout(self.parameters)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setHorizontalSpacing(10)
        self.formLayout.setVerticalSpacing(5)
        self.formLayout.setContentsMargins(10, 10, 10, 10)
        self.label_5 = QLabel(self.parameters)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setMinimumSize(QSize(80, 0))
        self.label_5.setMaximumSize(QSize(80, 16777215))
        self.label_5.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label_5)

        self.batch = QLineEdit(self.parameters)
        self.batch.setObjectName(u"batch")
        self.batch.setStyleSheet(u"")
        self.batch.setClearButtonEnabled(True)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.batch)

        self.label = QLabel(self.parameters)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(80, 0))
        self.label.setMaximumSize(QSize(80, 16777215))
        self.label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label)

        self.height = QDoubleSpinBox(self.parameters)
        self.height.setObjectName(u"height")
        self.height.setDecimals(1)
        self.height.setMinimum(1.000000000000000)
        self.height.setMaximum(1000.000000000000000)
        self.height.setValue(160.000000000000000)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.height)

        self.label_2 = QLabel(self.parameters)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMinimumSize(QSize(80, 0))
        self.label_2.setMaximumSize(QSize(80, 16777215))
        self.label_2.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_2)

        self.width = QDoubleSpinBox(self.parameters)
        self.width.setObjectName(u"width")
        self.width.setDecimals(1)
        self.width.setMinimum(1.000000000000000)
        self.width.setMaximum(1000.000000000000000)
        self.width.setValue(180.000000000000000)

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.width)

        self.label_3 = QLabel(self.parameters)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setMinimumSize(QSize(80, 0))
        self.label_3.setMaximumSize(QSize(80, 16777215))
        self.label_3.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.label_3)

        self.depth = QDoubleSpinBox(self.parameters)
        self.depth.setObjectName(u"depth")
        self.depth.setDecimals(1)
        self.depth.setMinimum(1.000000000000000)
        self.depth.setMaximum(1000.000000000000000)
        self.depth.setValue(28.000000000000000)

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.depth)

        self.label_4 = QLabel(self.parameters)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setMinimumSize(QSize(80, 0))
        self.label_4.setMaximumSize(QSize(80, 16777215))
        self.label_4.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.label_4)

        self.fusion = QComboBox(self.parameters)
        self.fusion.setObjectName(u"fusion")

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.fusion)

        self.verticalSpacer_1 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.formLayout.setItem(5, QFormLayout.FieldRole, self.verticalSpacer_1)


        self.verticalLayout.addWidget(self.parameters)

        self.buttonArea = QFrame(Dialog)
        self.buttonArea.setObjectName(u"buttonArea")
        self.buttonArea.setFrameShape(QFrame.StyledPanel)
        self.buttonArea.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.buttonArea)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer_1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_1)

        self.add = QPushButton(self.buttonArea)
        self.add.setObjectName(u"add")
        self.add.setMinimumSize(QSize(90, 0))

        self.horizontalLayout.addWidget(self.add)

        self.cancel = QPushButton(self.buttonArea)
        self.cancel.setObjectName(u"cancel")
        self.cancel.setMinimumSize(QSize(90, 0))
        self.cancel.setStyleSheet(u"")

        self.horizontalLayout.addWidget(self.cancel)


        self.verticalLayout.addWidget(self.buttonArea)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.parameters.setTitle(QCoreApplication.translate("Dialog", u"\u041f\u0430\u0440\u0430\u043c\u0435\u0442\u0440\u044b \u0441\u043b\u0438\u0442\u043a\u0430", None))
        self.label_5.setText(QCoreApplication.translate("Dialog", u"\u041d\u043e\u043c\u0435\u0440 \u043f\u0430\u0440\u0442\u0438\u0438", None))
#if QT_CONFIG(tooltip)
        self.batch.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.batch.setPlaceholderText(QCoreApplication.translate("Dialog", u"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u043d\u043e\u043c\u0435\u0440 \u043f\u0430\u0440\u0442\u0438\u0438...", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"\u0414\u043b\u0438\u043d\u0430", None))
        self.height.setSuffix(QCoreApplication.translate("Dialog", u" \u043c\u043c", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"\u0428\u0438\u0440\u0438\u043d\u0430", None))
        self.width.setSuffix(QCoreApplication.translate("Dialog", u" \u043c\u043c", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", u"\u0422\u043e\u043b\u0449\u0438\u043d\u0430", None))
        self.depth.setSuffix(QCoreApplication.translate("Dialog", u" \u043c\u043c", None))
        self.label_4.setText(QCoreApplication.translate("Dialog", u"\u0421\u043f\u043b\u0430\u0432", None))
        self.add.setText(QCoreApplication.translate("Dialog", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c", None))
        self.cancel.setText(QCoreApplication.translate("Dialog", u"\u041e\u0442\u043c\u0435\u043d\u0430", None))
    # retranslateUi

