# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\QtProjects\oci\gui\assign_ingot_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(640, 275)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setContentsMargins(10, 0, 10, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label.setFont(font)
        self.label.setStyleSheet("QLabel {\n"
"    background-color: rgb(234, 234, 234);\n"
"    margin-top: 10px;\n"
"}")
        self.label.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.ingots_view = QtWidgets.QListView(Dialog)
        self.ingots_view.setMinimumSize(QtCore.QSize(0, 195))
        self.ingots_view.setMaximumSize(QtCore.QSize(16777215, 195))
        self.ingots_view.setStyleSheet("")
        self.ingots_view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.ingots_view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.ingots_view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.ingots_view.setProperty("showDropIndicator", False)
        self.ingots_view.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.ingots_view.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.ingots_view.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.ingots_view.setFlow(QtWidgets.QListView.LeftToRight)
        self.ingots_view.setObjectName("ingots_view")
        self.verticalLayout.addWidget(self.ingots_view)
        self.button_area = QtWidgets.QFrame(Dialog)
        self.button_area.setMinimumSize(QtCore.QSize(0, 40))
        self.button_area.setMaximumSize(QtCore.QSize(16777215, 40))
        self.button_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.button_area.setFrameShadow(QtWidgets.QFrame.Raised)
        self.button_area.setObjectName("button_area")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.button_area)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setSpacing(10)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.add = QtWidgets.QPushButton(self.button_area)
        self.add.setMinimumSize(QtCore.QSize(80, 0))
        self.add.setObjectName("add")
        self.horizontalLayout_2.addWidget(self.add)
        self.predict = QtWidgets.QPushButton(self.button_area)
        self.predict.setMinimumSize(QtCore.QSize(80, 0))
        self.predict.setObjectName("predict")
        self.horizontalLayout_2.addWidget(self.predict)
        self.verticalLayout.addWidget(self.button_area)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Добавление слитков"))
        self.label.setText(_translate("Dialog", "Свободные слитки"))
        self.add.setText(_translate("Dialog", "Добавить"))
        self.predict.setText(_translate("Dialog", "Рассчитать"))
