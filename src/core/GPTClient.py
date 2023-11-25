import asyncio
import time
from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot
from openai import OpenAI

from core.Database import Database
from data.ChatMessage import ChatMessage
from data.ChatThread import ChatThread


class GPTClient(QObject):
	chatThreadListLoaded = Signal()
	chatThreadAdded = Signal(object)
	messageReceived = Signal(str)


	# TODO: api: AsyncOpenAI
	def __init__(self, api: OpenAI, defaultModel, database: Database, chatsDirectory: Path):
		super().__init__()
		self.chatsDirectory = chatsDirectory
		self.chatsDirectory.mkdir(exist_ok=True)

		self.api = api
		self.modelName = defaultModel
		self.database = database
		self.chatThreads: dict[str, ChatThread] = {}
		self.mainAssistant = None

		self.retrieveAssistants()


	def retrieveAssistants(self):
		"""
		Retrieve the assistants
		"""
		assistants = self.api.beta.assistants.list()
		self.database.updateAssistants(assistants.data)
		self.mainAssistant = next(each for each in assistants.data if each.name == 'Desktop Assistant')


	def loadChatThreadList(self):
		"""
		Gets the list of chat threads stored in the local data directory,
		retrieving information from the API if necessary.
		"""
		for filePath in self.chatsDirectory.iterdir():
			if filePath.is_file() and filePath.suffix == '.txt':
				try:
					chatThread = ChatThread(self.api.beta.threads.retrieve(filePath.stem))
					self.chatThreads[chatThread.id] = chatThread
				except Exception as e:
					print(f'Error retrieving chat thread {filePath.stem}: {str(e)}')
		self.chatThreadListLoaded.emit()
	#@Slot()
	#async def loadChatThreadList(self):
	#	"""
	#	Gets the list of chat threads stored in the local data directory,
	#	retrieving information from the API if necessary.
	#	"""
	#	# Get all file paths synchronously
	#	filePaths = [filePath for filePath in self.chatsDirectory.iterdir() if filePath.is_file() and filePath.suffix == '.txt']

	#	# Concurrently retrieve chat threads
	#	tasks = [self.api.beta.threads.retrieve(file.stem) for file in filePaths]
	#	chatThreads = await asyncio.gather(*tasks, return_exceptions=True)
	#	for chatThread in chatThreads:
	#		self.chatThreads[chatThread.id] = ChatThread(chatThread)

	#	# Notify that we are done
	#	self.chatThreadListLoaded.emit()


	def createNewChat(self, title):
		"""
		Starts a new chat thread with the given title.
		:emits: chatThreadAdded
		"""
		chatThread = ChatThread(self.api.beta.threads.create(metadata = {'title': title}))
		self.chatThreads[chatThread.id] = chatThread
		self.database.insertChatThread(chatThread)
		self.chatThreadAdded.emit(chatThread)


	def deleteChatThread(self, chatThreadId):
		"""
		Deletes a chat thread and all it's messages from the server and from disk
		:param chatThreadId: The ID of the chat thread
		"""
		self.api.beta.threads.delete(chatThreadId)
		file = self.chatsDirectory / f'{chatThreadId}.txt'
		file.unlink(missing_ok = True)


	def loadMessages(self, chatThreadId: str) -> list[ChatMessage]:
		"""
		Loads the messages from disk and retrieves and newer messages from the server.
		:param chatThreadId: The ID of the chat thread the messages belong to.
		:return: list of message objects
		"""
		chatThread = self.chatThreads[chatThreadId]
		# TODO: Load from database first, then retrieve 20 from server and check if any are newer. If so, add to database.
		result = self.api.beta.threads.messages.list(chatThreadId, limit = 20, order = 'desc')
		for each in reversed(result.data):
			chatThread.messages.append(ChatMessage(each))
		return chatThread.messages


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