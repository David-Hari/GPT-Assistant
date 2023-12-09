import html

from PySide6.QtCore import Qt, QModelIndex
from PySide6.QtGui import QAction, QTextCursor
from PySide6.QtWidgets import QMainWindow, QMenu
from markdown2 import markdown

from core.GPTClient import GPTClient
from ui.ChatThreadList import ChatThreadListModel, ChatThreadItemDelegate
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

		self.blankHtml = """
			<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
			<html><head>
			<meta charset="utf-8"/>
			<style type="text/css">
		"""
		with open('styles\\messages.css', 'r', encoding='utf-8') as file:
			self.blankHtml += file.read()
		self.blankHtml += '</style></head><body><div id="messageList"></div></body></html>'
		self.ui.messageView.setHtml(self.blankHtml)

		self.chatThreadListModel = ChatThreadListModel()
		self.chatThreadDelegate = ChatThreadItemDelegate(self.ui.chatThreadsList)
		self.ui.chatThreadsList.setModel(self.chatThreadListModel)
		self.ui.chatThreadsList.setItemDelegate(self.chatThreadDelegate)
		self.ui.chatThreadsList.setContextMenuPolicy(Qt.CustomContextMenu)
		self.ui.chatThreadsList.customContextMenuRequested.connect(self.showChatThreadMenu)
		self.ui.chatThreadsList.selectionModel().currentChanged.connect(self.chatThreadChanged)
		self.chatThreadListModel.titleEdited.connect(self.handleTitleEditFinished)

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
		self.ui.messageView.clear()
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
		# TODO: Need to html.escape(messageText) if it's going into a HTML view, but not for QTextBrowser
		messageHtml = markdown(messageText, extras = ['fenced-code-blocks'])
		self.ui.messageView.textCursor().movePosition(QTextCursor.End, QTextCursor.MoveAnchor)
		self.ui.messageView.insertHtml('<br /><div class="message"><p>===================================================</p>' + messageHtml + '</div>')
