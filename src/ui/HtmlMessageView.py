from datetime import datetime
from typing import Optional

from markdown2 import markdown
from PySide6.QtCore import QObject, Signal
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel

from data.ChatMessage import ChatMessage


class WebPageBridge(QObject):
	"""
	Simple class to facilitate sending HTML to the web page
	"""
	messageAdded = Signal(str)

	def __init__(self, parent: Optional[QObject] = None):
		super().__init__(parent)



class HtmlMessageView(QObject):
	def __init__(self, view: QWebEngineView):
		super().__init__()
		self.view = view

		with open('src\\templates\\page.html', 'r', encoding='utf-8') as file:
			self.pageHtml = file.read()
		with open('styles\\messages.css', 'r', encoding='utf-8') as file:
			self.pageHtml = self.pageHtml.replace('{{styles}}', file.read())
		with open('src\\templates\\message.html', 'r', encoding='utf-8') as file:
			self.messageHtml = file.read()

		self.bridge = WebPageBridge(self)
		self.channel = QWebChannel(self)
		self.view.page().setWebChannel(self.channel)
		self.channel.registerObject('bridge', self.bridge)


	def clear(self):
		html = self.pageHtml.replace('{{messages}}', '')
		self.view.setHtml(html)


	def setMessages(self, messages: list[ChatMessage]):
		messagesHtml = ''
		for message in messages:
			messagesHtml += self.renderHtmlForMessage(message)
		html = self.pageHtml.replace('{{messages}}', messagesHtml)
		self.view.setHtml(html)


	def appendMessage(self, message: ChatMessage):
		htmlStr = self.renderHtmlForMessage(message)
		self.bridge.messageAdded.emit(htmlStr)


	def renderHtmlForMessage(self, message: ChatMessage):
		# TODO: Escape HTML tags like <script> in the message. Probably use whitelist.
		localNow = datetime.now().astimezone()
		localMessageTime = message.createdTimestamp.astimezone()
		messageHtml = markdown(message.content[0].text.value, extras = ['fenced-code-blocks'])
		html = self.messageHtml.replace('{{authorClass}}', message.authorType )
		html = html.replace('{{timestamp}}', self.formatDateTime(localNow, localMessageTime))
		html = html.replace('{{content}}', messageHtml)
		return html


	@staticmethod
	def formatDateTime(current, other):
		timeStr = '<p>%H:%M:%S</p>'
		if other.date() == current.date():   # Today
			return other.strftime(timeStr)
		elif (current - other).days < 7:     # Within a week
			return other.strftime('<p>%A</p>' + timeStr)
		elif other.year == current.year and other.month == current.month:  # This month
			return other.strftime('<p>%e %b</p>' + timeStr)
		else:
			return other.strftime('<p>%Y-%m-%d</p>' + timeStr)