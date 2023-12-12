from PySide6.QtWidgets import QApplication
from markdown2 import markdown
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage, QWebEngineScript
from PySide6.QtWebEngineWidgets import QWebEngineView

from data.ChatMessage import ChatMessage


class HtmlMessageView:

	def __init__(self, view: QWebEngineView):
		self.view = view

		self.startHtml = """
			<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
			<html><head>
			<meta charset="utf-8"/>
			<style type="text/css">
		"""
		with open('styles\\messages.css', 'r', encoding='utf-8') as file:
			self.startHtml += file.read()
		self.startHtml += '</style></head><body><div id="messageList">'
		self.endHtml = '</div></body></html>'

		scriptSource = """
		function appendMessage(message) {
			document.getElementById("messageList").innerHTML += \'<div class="message">\' + message + \'</div>\';
		}
		"""
		appendMessageScript = QWebEngineScript()
		appendMessageScript.setName("appendMessage")
		appendMessageScript.setSourceCode(scriptSource)
		appendMessageScript.setWorldId(QWebEngineScript.MainWorld)

		profile = QWebEngineProfile(QApplication.applicationName())
		profile.scripts().insert(appendMessageScript)
		self.view.setPage(QWebEnginePage(profile))


	def clear(self):
		self.view.setHtml(self.startHtml + self.endHtml)


	def setMessages(self, messages: list[ChatMessage]):
		htmlStr = self.startHtml
		for message in messages:
			messageHtml = markdown(message.content[0].text.value, extras = ['fenced-code-blocks'])
			htmlStr += '<div class="message"><p>===================================================</p>' + messageHtml + '</div>'
		htmlStr += self.endHtml
		self.view.setHtml(htmlStr)


	def appendMessage(self, message: ChatMessage):
		# TODO: json.dumps(message.toDictionary()), but need to handle datetime
		self.view.page().runJavaScript('appendMessage(\'test\')')