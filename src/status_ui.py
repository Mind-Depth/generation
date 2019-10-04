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
        MainWindow.setStyleSheet("background-color: #090909;")
        self.MainWidget = QtWidgets.QWidget(MainWindow)
        self.MainWidget.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.MainWidget.setObjectName("MainWidget")
        self.Logo = QtWidgets.QLabel(self.MainWidget)
        self.Logo.setGeometry(QtCore.QRect(20, 20, 100, 100))
        self.Logo.setText("")
        self.Logo.setPixmap(QtGui.QPixmap(":/image/logo-small.jpg"))
        self.Logo.setScaledContents(True)
        self.Logo.setAlignment(QtCore.Qt.AlignCenter)
        self.Logo.setObjectName("Logo")
        self.Stop = QtWidgets.QPushButton(self.MainWidget)
        self.Stop.setGeometry(QtCore.QRect(620, 20, 75, 75))
        self.Stop.setStyleSheet("QPushButton\n"
"{\n"
"   background-color:#ffffff;\n"
"}\n"
"\n"
"QPushButton:hover\n"
"{\n"
"   background-color:#bbbbbb;\n"
"}")
        self.Stop.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/image/stop.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.Stop.setIcon(icon)
        self.Stop.setIconSize(QtCore.QSize(125, 125))
        self.Stop.setObjectName("Stop")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.MainWidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(9, 609, 1181, 281))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.GraphLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.GraphLayout.setContentsMargins(0, 0, 0, 0)
        self.GraphLayout.setSpacing(0)
        self.GraphLayout.setObjectName("GraphLayout")
        self.FrameTop = QtWidgets.QFrame(self.MainWidget)
        self.FrameTop.setGeometry(QtCore.QRect(500, 10, 200, 100))
        self.FrameTop.setStyleSheet("background-color: #111111;")
        self.FrameTop.setFrameShape(QtWidgets.QFrame.Box)
        self.FrameTop.setFrameShadow(QtWidgets.QFrame.Raised)
        self.FrameTop.setLineWidth(2)
        self.FrameTop.setMidLineWidth(2)
        self.FrameTop.setObjectName("FrameTop")
        self.Play = QtWidgets.QPushButton(self.MainWidget)
        self.Play.setGeometry(QtCore.QRect(510, 20, 75, 75))
        self.Play.setStyleSheet("QPushButton\n"
"{\n"
"   background-color:#ffffff;\n"
"}\n"
"\n"
"QPushButton:hover\n"
"{\n"
"   background-color:#bbbbbb;\n"
"}")
        self.Play.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/image/play.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.Play.setIcon(icon1)
        self.Play.setIconSize(QtCore.QSize(150, 150))
        self.Play.setObjectName("Play")
        self.FrameBottom = QtWidgets.QFrame(self.MainWidget)
        self.FrameBottom.setGeometry(QtCore.QRect(5, 605, 1190, 290))
        self.FrameBottom.setStyleSheet("background-color: #111111;")
        self.FrameBottom.setFrameShape(QtWidgets.QFrame.Box)
        self.FrameBottom.setFrameShadow(QtWidgets.QFrame.Raised)
        self.FrameBottom.setLineWidth(2)
        self.FrameBottom.setMidLineWidth(2)
        self.FrameBottom.setObjectName("FrameBottom")
        self.FrameRight = QtWidgets.QFrame(self.MainWidget)
        self.FrameRight.setGeometry(QtCore.QRect(740, 140, 455, 455))
        self.FrameRight.setStyleSheet("background-color: #111111;")
        self.FrameRight.setFrameShape(QtWidgets.QFrame.Box)
        self.FrameRight.setFrameShadow(QtWidgets.QFrame.Raised)
        self.FrameRight.setLineWidth(2)
        self.FrameRight.setMidLineWidth(2)
        self.FrameRight.setObjectName("FrameRight")
        self.FrameLeft = QtWidgets.QFrame(self.MainWidget)
        self.FrameLeft.setGeometry(QtCore.QRect(5, 140, 730, 455))
        self.FrameLeft.setStyleSheet("background-color: #111111;")
        self.FrameLeft.setFrameShape(QtWidgets.QFrame.Box)
        self.FrameLeft.setFrameShadow(QtWidgets.QFrame.Raised)
        self.FrameLeft.setLineWidth(2)
        self.FrameLeft.setMidLineWidth(2)
        self.FrameLeft.setObjectName("FrameLeft")
        self.test = QtWidgets.QLabel(self.MainWidget)
        self.test.setGeometry(QtCore.QRect(745, 145, 445, 445))
        self.test.setText("")
        self.test.setPixmap(QtGui.QPixmap(":/image/TMP-placeholder.jpg"))
        self.test.setObjectName("test")
        self.FrameBottom.raise_()
        self.FrameTop.raise_()
        self.Logo.raise_()
        self.Stop.raise_()
        self.verticalLayoutWidget.raise_()
        self.Play.raise_()
        self.FrameRight.raise_()
        self.FrameLeft.raise_()
        self.test.raise_()
        MainWindow.setCentralWidget(self.MainWidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Mind Depths"))
import resource_rc
