import time
from pathlib import Path

from PySide6.QtCore import QObject, Signal
from openai import OpenAI

from data.ChatMessage import ChatMessage
from data.ChatThread import ChatThread


class GPTClient(QObject):
	messageReceived = Signal(str)
	chatThreadAdded = Signal(object)


	def __init__(self, api: OpenAI, defaultModel, chatsDirectory: Path, systemDirectory: Path):
		super().__init__()
		self.chatsDirectory = chatsDirectory
		self.systemDirectory = systemDirectory
		self.chatsDirectory.mkdir(exist_ok=True)
		self.systemDirectory.mkdir(exist_ok=True)

		self.api = api
		self.modelName = defaultModel
		self.chatThreadList = []
		self.mainAssistant = None

		self.retrieveAssistants()
		self.loadChatThreadList()


	def retrieveAssistants(self):
		"""
		Retrieve the assistants
		"""
		for filePath in self.systemDirectory.iterdir():
			if filePath.is_file() and filePath.name.startswith('asst') and filePath.suffix == '.txt':
				try:
					self.mainAssistant = self.api.beta.assistants.retrieve(filePath.stem)
					# TODO: Handle other assistants
				except Exception as e:
					print(f'Error retrieving assistant {filePath.stem}: {str(e)}')


	def loadChatThreadList(self):
		"""
		Gets the list of chat threads stored in the local data directory,
		retrieving information from the API if necessary.
		"""
		self.chatThreadList.clear()
		for filePath in self.chatsDirectory.iterdir():
			if filePath.is_file() and filePath.suffix == '.txt':
				try:
					thread = self.api.beta.threads.retrieve(filePath.stem)
					self.chatThreadList.append(thread)
				except Exception as e:
					print(f'Error retrieving chat thread {filePath.stem}: {str(e)}')
		# TODO: Sort by date, first is most recent


	def createNewChat(self, title):
		"""
		Starts a new chat thread with the given title.
		:emits: chatThreadAdded
		"""
		thread = ChatThread(self.api.beta.threads.create(metadata = {'title': title}))
		self.chatThreadList.append(thread)
		with open(self.chatsDirectory / f'{thread.id}.txt', 'w', encoding='utf-8') as file:
			file.write('')
		self.chatThreadAdded.emit(thread)


	def deleteChatThread(self, chatThreadId):
		"""
		Deletes a chat thread and all it's messages from the server and from disk
		:param chatThreadId: The ID of the chat thread
		"""
		self.api.beta.threads.delete(chatThreadId)
		file = self.chatsDirectory / f'{chatThreadId}.txt'
		file.unlink(missing_ok = True)


	def sendMessage(self, chatThreadId, messageText):
		"""
		Sends a user message to the server.
		:param chatThreadId: The ID of the chat thread with which this message is associated.
		:param messageText: Message text to send
		:emits: messageReceived
		"""
		message = ChatMessage(self.api.beta.threads.messages.create(chatThreadId, role = 'user', content = messageText))
		# TODO: Log message
		run = self.api.beta.threads.runs.create(
			thread_id = chatThreadId,
			assistant_id = self.mainAssistant.id
		)
		while run.status != 'completed':
			time.sleep(1)
			run = self.api.beta.threads.runs.retrieve(
				thread_id = chatThreadId,
				run_id = run.id
			)
		messages = self.api.beta.threads.messages.list(chatThreadId)
		self.messageReceived.emit(messages.data[0].content[0].text.value)


	def retrieveMessages(self, chatThreadId, numLimit):
		"""
		Retrieves a number of messages from the server in descending order of creation time.
		:param chatThreadId: The ID of the chat thread the messages belong to.
		:param numLimit: A limit on the number of objects to be returned. Limit can range between 1 and 100
		:return: list of message objects
		"""
		result = self.api.beta.threads.messages.list(chatThreadId, limit = numLimit, order = 'desc')
		return reversed(result.data)