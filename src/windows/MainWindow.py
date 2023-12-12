from PySide6.QtCore import Qt, QModelIndex
from PySide6.QtGui import QAction, QTextCursor
from PySide6.QtWidgets import QMainWindow, QMenu

from core.GPTClient import GPTClient
from data.ChatThread import ChatThread
from ui.ChatThreadList import ChatThreadListModel, ChatThreadItemDelegate
from ui.HtmlMessageView import HtmlMessageView
from ui.ui_MainWindow import Ui_MainWindow
from utils import logger



class MainWindow(QMainWindow):

	def __init__(self, chatClient: GPTClient):
		super(MainWindow, self).__init__()
		self.chatClient = chatClient
		self.currentChatThreadId = None

		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)

		with open('styles\\MainWindow.css', 'r', encoding='utf-8') as file:
			self.setStyleSheet(file.read())

		self.messageView = HtmlMessageView(self.ui.messageView)
		self.chatThreadListModel = ChatThreadListModel()
		self.chatThreadDelegate = ChatThreadItemDelegate(self.ui.chatThreadsList)
		self.ui.chatThreadsList.setModel(self.chatThreadListModel)
		self.ui.chatThreadsList.setItemDelegate(self.chatThreadDelegate)
		self.ui.chatThreadsList.customContextMenuRequested.connect(self.showChatThreadMenu)
		self.ui.chatThreadsList.selectionModel().currentChanged.connect(self.chatThreadChanged)
		self.chatThreadListModel.titleEdited.connect(self.handleTitleEditFinished)

		self.chatClient.chatThreadListLoaded.connect(self.chatThreadListLoaded)
		self.chatClient.chatThreadAdded.connect(self.chatThreadCreated)
		self.chatClient.messageAdded.connect(self.messageView.appendMessage)

		self.messageView.clear()


	def chatThreadListLoaded(self):
		""" Populate the sidebar with the chat threads """
		self.chatThreadListModel.populateList(self.chatClient.chatThreads.values())
		self.currentChatThreadId = self.chatThreadListModel.chatThreads[0].id


	def createNewChat(self):
		self.chatClient.createNewChat('New Chat')


	def chatThreadCreated(self, chatThread: ChatThread):
		self.chatThreadListModel.addItem(chatThread)
		self.selectChatThread(chatThread.id)


	def chatThreadChanged(self, current: QModelIndex, previous: QModelIndex = None):
		self.selectChatThread(current.data(Qt.UserRole))


	def selectChatThread(self, chatThreadId):
		self.currentChatThreadId = chatThreadId
		self.messageView.setMessages(self.chatClient.getMessages(self.currentChatThreadId))


	def editChatThreadTitle(self, index: QModelIndex):
		logger.debug('Start editing title')
		self.ui.chatThreadsList.edit(index)


	def handleTitleEditFinished(self, chatThreadId, newTitle):
		logger.debug('Finished editing title')
		self.chatClient.updateChatThreadTitle(chatThreadId, newTitle, True)


	def deleteChatThread(self, index: QModelIndex):
		self.chatClient.deleteChatThread(index.data(Qt.UserRole))
		self.chatThreadListModel.deleteItem(index)
		# TODO: If current thread is deleted, either select next one or make message window blank


	def showChatThreadMenu(self, position):
		index = self.ui.chatThreadsList.indexAt(position)
		if index.isValid():
			menu = QMenu(self.ui.chatThreadsList)

			editTitleAction = QAction("Edit Title", self)
			editTitleAction.triggered.connect(lambda: self.editChatThreadTitle(index))
			menu.addAction(editTitleAction)

			menu.addSeparator()

			deleteAction = QAction("Delete", self)
			deleteAction.triggered.connect(lambda: self.deleteChatThread(index))
			menu.addAction(deleteAction)

			menu.exec(self.ui.chatThreadsList.mapToGlobal(position))


	def sendMessage(self):
		messageText = self.ui.messageTextBox.document().toPlainText()
		if messageText != '':
			self.chatClient.sendMessage(self.currentChatThreadId, messageText)
			self.ui.messageTextBox.clear()
