from datetime import datetime

from markdown2 import markdown
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel

from data.ChatMessage import ChatMessage


class HtmlMessageView:

	def __init__(self, view: QWebEngineView):
		self.view = view

		with open('src\\templates\\page.html', 'r', encoding='utf-8') as file:
			self.pageHtml = file.read()
		with open('styles\\messages.css', 'r', encoding='utf-8') as file:
			self.pageHtml = self.pageHtml.replace('{{styles}}', file.read())
		with open('src\\templates\\message.html', 'r', encoding='utf-8') as file:
			self.messageHtml = file.read()

		#channel = QWebChannel()
		#channel.registerObject('messageHandler', self.message_handler)
		# OR
		#channel.connectTo(transport), where I implement a subclass of QWebChannelAbstractTransport
		#self.view.page().setWebChannel(channel)


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
		self.view.page().runJavaScript('document.getElementById("messageList").innerHTML += ' + htmlStr)


	def renderHtmlForMessage(self, message: ChatMessage):
		localNow = datetime.now().astimezone()
		localMessageTime = message.createdTimestamp.astimezone()
		messageHtml = markdown(message.content[0].text.value, extras = ['fenced-code-blocks'])
		html = self.messageHtml.replace('{{roleClass}}', message.role)
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