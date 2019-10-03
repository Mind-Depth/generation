# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\EIP\generation_qt\launcher.ui'
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
        self.Logo = QtWidgets.QLabel(self.MainWidget)
        self.Logo.setGeometry(QtCore.QRect(0, 0, 1200, 380))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Logo.sizePolicy().hasHeightForWidth())
        self.Logo.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("MS Serif")
        self.Logo.setFont(font)
        self.Logo.setText("")
        self.Logo.setPixmap(QtGui.QPixmap(":/image/logo.jpg"))
        self.Logo.setScaledContents(True)
        self.Logo.setAlignment(QtCore.Qt.AlignCenter)
        self.Logo.setWordWrap(False)
        self.Logo.setIndent(0)
        self.Logo.setObjectName("Logo")
        self.Start = QtWidgets.QPushButton(self.MainWidget)
        self.Start.setGeometry(QtCore.QRect(475, 500, 250, 90))
        self.Start.setStyleSheet("QPushButton {\n"
"    background-color: rgba(0, 0, 0, 0);\n"
"    border-style: solid;\n"
"    color:white;\n"
"    border-color:rgba(0, 0, 0, 0);\n"
"    border-width: 2px;\n"
"    border-top:0px;\n"
"    border-left:0px;\n"
"    border-right:0px;\n"
"    font-family:gorestep;\n"
"    font-size:72px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    border-color: #94191c;\n"
"}\n"
"")
        self.Start.setObjectName("Start")
        self.Quit = QtWidgets.QPushButton(self.MainWidget)
        self.Quit.setGeometry(QtCore.QRect(475, 700, 250, 90))
        self.Quit.setStyleSheet("QPushButton {\n"
"    background-color: rgba(0, 0, 0, 0);\n"
"    border-style: solid;\n"
"    color:white;\n"
"    border-color:rgba(0, 0, 0, 0);\n"
"    border-width: 2px;\n"
"    border-top:0px;\n"
"    border-left:0px;\n"
"    border-right:0px;\n"
"    font-family:gorestep;\n"
"    font-size:72px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    border-color: #94191c;\n"
"}\n"
"")
        self.Quit.setObjectName("Quit")
        MainWindow.setCentralWidget(self.MainWidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Mind Depths"))
        self.Start.setText(_translate("MainWindow", "Start"))
        self.Quit.setText(_translate("MainWindow", "Quit"))
import resource_rc
