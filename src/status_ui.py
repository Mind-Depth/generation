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
        self.Stop.setGeometry(QtCore.QRect(612, 22, 75, 75))
        self.Stop.setStyleSheet('QPushButton { background-color:#330000 } QPushButton:hover { background-color:#990000 } :disabled { background-color:#333333 }')
        self.Stop.setEnabled(False)
        self.Stop.setText("")
        self.iconPx = QtGui.QPixmap(":/image/stop.png")
        icon = QtGui.QIcon()
        icon.addPixmap(self.iconPx, QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon.addPixmap(self.iconPx, QtGui.QIcon.Disabled, QtGui.QIcon.Off)
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
        self.Start = QtWidgets.QPushButton(self.MainWidget)
        self.Start.setGeometry(QtCore.QRect(512, 22, 75, 75))
        self.Start.setStyleSheet('QPushButton { background-color:#003300 } QPushButton:hover { background-color:#009900 } :disabled { background-color:#333333 }')
        self.Start.setEnabled(False)
        self.Start.setText("")
        self.icon1Px = QtGui.QPixmap(":/image/play.png")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(self.icon1Px, QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon1.addPixmap(self.icon1Px, QtGui.QIcon.Disabled, QtGui.QIcon.Off)
        self.Start.setIcon(icon1)
        self.Start.setIconSize(QtCore.QSize(150, 150))
        self.Start.setObjectName("Start")
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
        self.Achluophobia = QtWidgets.QProgressBar(self.FrameLeft)
        self.Achluophobia.setGeometry(QtCore.QRect(190, 60, 500, 30))
        self.Achluophobia.setStyleSheet("QProgressBar:horizontal {\n"
"border: 1px solid gray;\n"
"border-radius: 3px;\n"
"background: black;\n"
"}\n"
"QProgressBar::chunk:horizontal {\n"
"background: qlineargradient(x1: 0, y1: 0.5, x2: 1, y2: 0.5, stop: 0 #900000, stop: 1 #000000);\n"
"width: 10px;\n"
"}")
        self.Achluophobia.setMaximum(100)
        self.Achluophobia.setProperty("value", 0)
        self.Achluophobia.setTextVisible(False)
        self.Achluophobia.setOrientation(QtCore.Qt.Horizontal)
        self.Achluophobia.setInvertedAppearance(False)
        self.Achluophobia.setTextDirection(QtWidgets.QProgressBar.TopToBottom)
        self.Achluophobia.setObjectName("Achluophobia")
        self.Arachnophobia_ = QtWidgets.QLabel(self.FrameLeft)
        self.Arachnophobia_.setGeometry(QtCore.QRect(20, 160, 150, 30))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.Arachnophobia_.setFont(font)
        self.Arachnophobia_.setStyleSheet("QLabel {\n"
"color: #bbbbbb;\n"
"}")
        self.Arachnophobia_.setAlignment(QtCore.Qt.AlignCenter)
        self.Arachnophobia_.setObjectName("Arachnophobia_")
        self.Claustrophobia = QtWidgets.QProgressBar(self.FrameLeft)
        self.Claustrophobia.setGeometry(QtCore.QRect(190, 260, 500, 30))
        self.Claustrophobia.setStyleSheet("QProgressBar:horizontal {\n"
"border: 1px solid gray;\n"
"border-radius: 3px;\n"
"background: black;\n"
"}\n"
"QProgressBar::chunk:horizontal {\n"
"background: qlineargradient(x1: 0, y1: 0.5, x2: 1, y2: 0.5, stop: 0 #900000, stop: 1 #000000);\n"
"width: 10px;\n"
"}")
        self.Claustrophobia.setMaximum(100)
        self.Claustrophobia.setProperty("value", 0)
        self.Claustrophobia.setTextVisible(False)
        self.Claustrophobia.setOrientation(QtCore.Qt.Horizontal)
        self.Claustrophobia.setInvertedAppearance(False)
        self.Claustrophobia.setTextDirection(QtWidgets.QProgressBar.TopToBottom)
        self.Claustrophobia.setObjectName("Claustrophobia")
        self.Arachnophobia = QtWidgets.QProgressBar(self.FrameLeft)
        self.Arachnophobia.setGeometry(QtCore.QRect(190, 160, 500, 30))
        self.Arachnophobia.setStyleSheet("QProgressBar:horizontal {\n"
"border: 1px solid gray;\n"
"border-radius: 3px;\n"
"background: black;\n"
"}\n"
"QProgressBar::chunk:horizontal {\n"
"background: qlineargradient(x1: 0, y1: 0.5, x2: 1, y2: 0.5, stop: 0 #900000, stop: 1 #000000);\n"
"width: 10px;\n"
"}")
        self.Arachnophobia.setMaximum(100)
        self.Arachnophobia.setProperty("value", 0)
        self.Arachnophobia.setTextVisible(False)
        self.Arachnophobia.setOrientation(QtCore.Qt.Horizontal)
        self.Arachnophobia.setInvertedAppearance(False)
        self.Arachnophobia.setTextDirection(QtWidgets.QProgressBar.TopToBottom)
        self.Arachnophobia.setObjectName("Arachnophobia")
        self.Vertigo = QtWidgets.QProgressBar(self.FrameLeft)
        self.Vertigo.setGeometry(QtCore.QRect(190, 360, 500, 30))
        self.Vertigo.setStyleSheet("QProgressBar:horizontal {\n"
"border: 1px solid gray;\n"
"border-radius: 3px;\n"
"background: black;\n"
"}\n"
"QProgressBar::chunk:horizontal {\n"
"background: qlineargradient(x1: 0, y1: 0.5, x2: 1, y2: 0.5, stop: 0 #900000, stop: 1 #000000);\n"
"width: 10px;\n"
"}")
        self.Vertigo.setMaximum(100)
        self.Vertigo.setProperty("value", 0)
        self.Vertigo.setTextVisible(False)
        self.Vertigo.setOrientation(QtCore.Qt.Horizontal)
        self.Vertigo.setInvertedAppearance(False)
        self.Vertigo.setTextDirection(QtWidgets.QProgressBar.TopToBottom)
        self.Vertigo.setObjectName("Vertigo")
        self.Claustrophobia_ = QtWidgets.QLabel(self.FrameLeft)
        self.Claustrophobia_.setGeometry(QtCore.QRect(20, 260, 150, 30))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.Claustrophobia_.setFont(font)
        self.Claustrophobia_.setStyleSheet("QLabel {\n"
"color: #bbbbbb;\n"
"}")
        self.Claustrophobia_.setAlignment(QtCore.Qt.AlignCenter)
        self.Claustrophobia_.setObjectName("Claustrophobia_")
        self.Vertigo_ = QtWidgets.QLabel(self.FrameLeft)
        self.Vertigo_.setGeometry(QtCore.QRect(20, 360, 150, 30))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.Vertigo_.setFont(font)
        self.Vertigo_.setStyleSheet("QLabel {\n"
"color: #bbbbbb;\n"
"}")
        self.Vertigo_.setAlignment(QtCore.Qt.AlignCenter)
        self.Vertigo_.setObjectName("Vertigo_")
        self.Achluophobia_ = QtWidgets.QLabel(self.FrameLeft)
        self.Achluophobia_.setGeometry(QtCore.QRect(20, 60, 150, 30))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.Achluophobia_.setFont(font)
        self.Achluophobia_.setStyleSheet("QLabel {\n"
"color: #bbbbbb;\n"
"}")
        self.Achluophobia_.setAlignment(QtCore.Qt.AlignCenter)
        self.Achluophobia_.setObjectName("Achluophobia_")
        self.Preview = QtWidgets.QLabel(self.MainWidget)
        self.Preview.setGeometry(QtCore.QRect(745, 145, 445, 445))
        self.Preview.setText("")
        self.Preview.setAlignment(QtCore.Qt.AlignCenter)
        self.Preview.setObjectName("Preview")
        self.FrameBottom.raise_()
        self.FrameTop.raise_()
        self.Logo.raise_()
        self.Stop.raise_()
        self.verticalLayoutWidget.raise_()
        self.Start.raise_()
        self.FrameRight.raise_()
        self.FrameLeft.raise_()
        self.Preview.raise_()
        MainWindow.setCentralWidget(self.MainWidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Mind Depths"))
        self.Achluophobia.setFormat(_translate("MainWindow", "%p%"))
        self.Arachnophobia_.setText(_translate("MainWindow", "Arachnophobia"))
        self.Claustrophobia.setFormat(_translate("MainWindow", "%p%"))
        self.Arachnophobia.setFormat(_translate("MainWindow", "%p%"))
        self.Vertigo.setFormat(_translate("MainWindow", "%p%"))
        self.Claustrophobia_.setText(_translate("MainWindow", "Claustrophobia"))
        self.Vertigo_.setText(_translate("MainWindow", "Vertigo"))
        self.Achluophobia_.setText(_translate("MainWindow", "Achluophobia"))
import resource_rc
