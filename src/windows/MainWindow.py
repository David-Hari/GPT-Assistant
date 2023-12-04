from PySide6.QtCore import Qt, QModelIndex
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QMenu
from markdown2 import markdown
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import html

from core.GPTClient import GPTClient
from ui.ChatThreadList import ChatThreadListModel, ChatThreadItemDelegate
from ui.MessageList import MessageListModel, MessageItemDelegate
from ui.ui_MainWindow import Ui_MainWindow
from utils import logger



class MainWindow(QMainWindow):

	def __init__(self, chatClient: GPTClient):
		super(MainWindow, self).__init__()
		self.chatClient = chatClient
		self.currentChatThreadId = None

		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)

		with open('src\\ui\\MainWindow.css', 'r', encoding='utf-8') as file:
			self.setStyleSheet(file.read())

		self.chatThreadListModel = ChatThreadListModel()
		self.chatThreadDelegate = ChatThreadItemDelegate(self.ui.chatThreadsList)
		self.ui.chatThreadsList.setModel(self.chatThreadListModel)
		self.ui.chatThreadsList.setItemDelegate(self.chatThreadDelegate)
		self.ui.chatThreadsList.setContextMenuPolicy(Qt.CustomContextMenu)
		self.ui.chatThreadsList.customContextMenuRequested.connect(self.showChatThreadMenu)
		self.ui.chatThreadsList.selectionModel().currentChanged.connect(self.chatThreadChanged)
		self.chatThreadListModel.titleEdited.connect(self.handleTitleEditFinished)

		# TODO: Different model for each thread? Maybe if it is too slow to switch between threads.
		#self.messageListModel = MessageListModel()
		#self.messageDelegate = MessageItemDelegate(self.ui.messageList)
		#self.ui.messageList.setModel(self.messageListModel)
		#self.ui.messageList.setItemDelegate(self.messageDelegate)

		self.chatClient.chatThreadListLoaded.connect(self.chatThreadListLoaded)
		self.chatClient.chatThreadAdded.connect(self.chatThreadCreated)
		self.chatClient.messageReceived.connect(self.appendMessage)


	def chatThreadListLoaded(self):
		""" Populate the sidebar with the chat threads """
		self.chatThreadListModel.populateList(self.chatClient.chatThreads.values())
		self.currentChatThreadId = self.chatThreadListModel.chatThreads[0].id


	def createNewChat(self):
		self.chatClient.createNewChat('New Chat')


	def chatThreadCreated(self, chatThread):
		self.chatThreadListModel.addItem(chatThread)
		self.selectChatThread(chatThread.id)


	def chatThreadChanged(self, current: QModelIndex, previous: QModelIndex = None):
		self.selectChatThread(current.data(Qt.UserRole))


	def selectChatThread(self, chatThreadId):
		self.currentChatThreadId = chatThreadId
		#self.messageListModel.updateList(self.chatClient.getMessages(self.currentChatThreadId))
		self.ui.messageList.clear()
		messages = self.chatClient.getMessages(self.currentChatThreadId)
		for message in messages:
			self.appendMessage('[' + message.role + ']  ' + message.content[0].text.value)


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
		message = self.ui.messageTextBox.document().toPlainText()
		if message != '':
			self.appendMessage('You: ' + message)
			self.chatClient.sendMessage(self.currentChatThreadId, message)
			self.ui.messageTextBox.clear()


	def appendMessage(self, messageText):
		"""
		Appends the given message text to the chat window
		"""
		# TODO: Accept object/dict that contains role ('user', 'AI')
		# TODO: Insert at the end, not where cursor is. self.ui.messageList.moveCursor()
		# TODO: Show text selection 'I' cursor.
		messageHtml = markdown(messageText, extras = ['fenced-code-blocks'])
		self.ui.messageList.insertHtml('<br /><b>===================================================</b><br />' + messageHtml)


# TODO: Not sure if needed, or how to use
def highlightCode(match):
	""" Function to highlight code blocks using Pygments """
	lang, code = match.groups()
	lexer = get_lexer_by_name(lang, stripall=True)
	formatter = html.HtmlFormatter()
	return highlight(code, lexer, formatter)