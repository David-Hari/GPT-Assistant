# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MainWindow.ui'
##
## Created by: Qt User Interface Compiler version 6.6.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox, QFrame,
    QGridLayout, QHBoxLayout, QListView, QMainWindow,
    QPlainTextEdit, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1500, 1200)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.sidebar = QFrame(self.centralwidget)
        self.sidebar.setObjectName(u"sidebar")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sidebar.sizePolicy().hasHeightForWidth())
        self.sidebar.setSizePolicy(sizePolicy)
        self.sidebar.setMaximumSize(QSize(300, 16777215))
        self.sidebar.setFrameShape(QFrame.StyledPanel)
        self.sidebar.setFrameShadow(QFrame.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.sidebar)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(9, 9, 9, 9)
        self.newChatButton = QPushButton(self.sidebar)
        self.newChatButton.setObjectName(u"newChatButton")

        self.verticalLayout_3.addWidget(self.newChatButton)

        self.chatThreadsList = QListView(self.sidebar)
        self.chatThreadsList.setObjectName(u"chatThreadsList")
        self.chatThreadsList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.chatThreadsList.setEditTriggers(QAbstractItemView.EditKeyPressed)
        self.chatThreadsList.setUniformItemSizes(True)

        self.verticalLayout_3.addWidget(self.chatThreadsList)


        self.horizontalLayout.addWidget(self.sidebar)

        self.mainFrame = QFrame(self.centralwidget)
        self.mainFrame.setObjectName(u"mainFrame")
        self.mainFrame.setFrameShape(QFrame.StyledPanel)
        self.mainFrame.setFrameShadow(QFrame.Raised)
        self.gridLayout_2 = QGridLayout(self.mainFrame)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.messageLayout = QHBoxLayout()
        self.messageLayout.setObjectName(u"messageLayout")
        self.messageTextBox = QPlainTextEdit(self.mainFrame)
        self.messageTextBox.setObjectName(u"messageTextBox")

        self.messageLayout.addWidget(self.messageTextBox)

        self.sendButton = QPushButton(self.mainFrame)
        self.sendButton.setObjectName(u"sendButton")

        self.messageLayout.addWidget(self.sendButton)


        self.gridLayout_2.addLayout(self.messageLayout, 2, 0, 1, 2)

        self.topBar = QFrame(self.mainFrame)
        self.topBar.setObjectName(u"topBar")
        self.topBar.setFrameShape(QFrame.StyledPanel)
        self.topBar.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.topBar)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.comboBox = QComboBox(self.topBar)
        self.comboBox.setObjectName(u"comboBox")

        self.horizontalLayout_2.addWidget(self.comboBox)

        self.hSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.hSpacer)


        self.gridLayout_2.addWidget(self.topBar, 0, 0, 1, 2)

        self.messageView = QWebEngineView(self.mainFrame)
        self.messageView.setObjectName(u"messageView")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(1)
        sizePolicy1.setHeightForWidth(self.messageView.sizePolicy().hasHeightForWidth())
        self.messageView.setSizePolicy(sizePolicy1)
        self.messageView.setAcceptDrops(False)

        self.gridLayout_2.addWidget(self.messageView, 1, 0, 1, 2)


        self.horizontalLayout.addWidget(self.mainFrame)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.newChatButton.clicked.connect(MainWindow.createNewChat)
        self.sendButton.clicked.connect(MainWindow.sendMessage)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"AI Assistant", None))
        self.newChatButton.setText(QCoreApplication.translate("MainWindow", u"New Chat", None))
        self.sendButton.setText(QCoreApplication.translate("MainWindow", u"Send", None))
    # retranslateUi

