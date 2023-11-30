from PySide6.QtCore import Qt, Slot, QModelIndex
from PySide6.QtWidgets import QMainWindow, QListWidgetItem

from core.GPTClient import GPTClient
from ui.ChatThreadList import ChatThreadListModel, ChatThreadItemDelegate
from ui.ui_MainWindow import Ui_MainWindow



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
		self.ui.chatThreadsList.setModel(self.chatThreadListModel)
		self.ui.chatThreadsList.setItemDelegate(ChatThreadItemDelegate(self.ui.chatThreadsList))
		self.ui.chatThreadsList.selectionModel().currentChanged.connect(self.chatThreadChanged)

		self.chatClient.chatThreadListLoaded.connect(self.chatThreadListLoaded)
		self.chatClient.chatThreadAdded.connect(self.addChatThreadToList)
		self.chatClient.messageReceived.connect(self.appendMessage)


	@Slot()
	def addChatThreadToList(self, chatThread):
		self.chatThreadListModel.addItem(chatThread)



	@Slot()
	def chatThreadListLoaded(self):
		""" Populate the sidebar with the chat threads """
		self.chatThreadListModel.populateList(self.chatClient.chatThreads.values())
		self.currentChatThreadId = self.chatThreadListModel.chatThreads[0].id


	@Slot()
	def createNewChat(self):
		self.chatClient.createNewChat('New Chat')


	@Slot()
	def chatThreadChanged(self, current: QModelIndex, previous: QModelIndex = None):
		self.selectChatThread(current.data(Qt.UserRole))


	def selectChatThread(self, chatThreadId):
		self.currentChatThreadId = chatThreadId
		self.ui.chatArea.clear()
		messages = self.chatClient.getMessages(self.currentChatThreadId)
		for message in messages:
			self.appendMessage('[' + message.role + ']  ' + message.content[0].text.value)


	@Slot()
	def deleteChatThread(self, item: QListWidgetItem):
		self.chatClient.deleteChatThread(item.data(Qt.UserRole))
		self.chatThreadListModel.deleteItem(item)  # TODO: Pass index
		# TODO: If current thread is deleted, either select next one or blank


	@Slot()
	def sendMessage(self):
		message = self.ui.messageTextBox.document().toPlainText()
		if message != '':
			self.appendMessage('You: ' + message)
			self.chatClient.sendMessage(self.currentChatThreadId, message)
			self.ui.messageTextBox.clear()


	@Slot(str)
	def appendMessage(self, messageText):
		"""
		Appends the given message text to the chat window
		"""
		#TODO: Accept object/dict that contains role ('user', 'AI')
		self.ui.chatArea.append('\n===================================================\n' + messageText)
