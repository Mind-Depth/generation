# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\EIP\generation_qt\status.ui'
#
# Created by: PyQt5 UI code generator 5.13.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1200, 900)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Gabriola")
        font.setPointSize(72)
        MainWindow.setFont(font)
        MainWindow.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.MainWidget = QtWidgets.QWidget(MainWindow)
        self.MainWidget.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.MainWidget.setObjectName("MainWidget")
        MainWindow.setCentralWidget(self.MainWidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Mind Depths"))
import resource_rc
