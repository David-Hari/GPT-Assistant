import asyncio
import time
from typing import Optional

from PySide6.QtCore import QObject, Signal, Slot
from openai import OpenAI, APIError

from core.Database import Database
from data.ChatMessage import ChatMessage
from data.ChatThread import ChatThread
from utils import logger



class GPTAssistant(QObject):
	chatThreadListLoaded = Signal()
	chatThreadAdded = Signal(ChatThread)
	messageAdded = Signal(ChatMessage)
	errorOccurred = Signal(str)


	# TODO: api: AsyncOpenAI
	def __init__(self, api: OpenAI, database: Database):
		super().__init__()

		self.api = api
		self.modelName = None  # Assistant model will be used
		self.database = database
		self.chatThreads: dict[str, ChatThread] = {}
		self.mainAssistant = None


	def startUp(self):
		logger.debug('Starting up GPT')
		self.retrieveAssistants()
		self.loadChatThreadList()
		logger.debug('Done starting up GPT')


	def retrieveAssistants(self):
		"""
		Retrieve the assistants
		"""
		logger.debug(f'Loading assistants')
		#assistants = self.database.getAssistants()
		assistants = self.api.beta.assistants.list().data
		self.database.updateAssistants(assistants)
		self.mainAssistant = next(each for each in assistants if each.name == 'Desktop Assistant')


	def loadChatThreadList(self):
		"""
		Gets the list of chat threads stored in the local data directory.
		"""
		logger.debug(f'Loading chat threads')
		for chatThread in self.database.getChatThreads():
			self.chatThreads[chatThread.id] = chatThread

		# Notify that we are done
		self.chatThreadListLoaded.emit()
	#@Slot()
	#async def loadChatThreadList(self):
	#	"""
	#	Gets the list of chat threads stored in the local data directory,
	#	retrieving information from the API if necessary.
	#	"""
	#	... synchronous database retrieval here
	#	# Concurrently retrieve chat threads
	#	tasks = [self.api.beta.threads.retrieve(id) for file in filePaths]
	#	chatThreads = await asyncio.gather(*tasks, return_exceptions=True)
	#	for chatThread in chatThreads:
	#		self.chatThreads[chatThread.id] = ChatThread.fromAPIObject(chatThread)
	#   ...


	def createNewChat(self, title):
		"""
		Starts a new chat thread with the given title.
		:emits: chatThreadAdded
		"""
		logger.debug(f'Creating new chat named {title}')
		chatThread = ChatThread.fromAPIObject(self.api.beta.threads.create(metadata = {'title': title}))
		self.chatThreads[chatThread.id] = chatThread
		self.database.insertChatThread(chatThread)
		self.chatThreadAdded.emit(chatThread)


	def updateChatThreadTitle(self, chatThreadId, newTitle, isFromUser):
		logger.info(('User' if isFromUser else 'Assistant') + f' updating title of chat thread {chatThreadId} to "{newTitle}"')
		chatThread = self.chatThreads[chatThreadId]
		chatThread.title = newTitle
		chatThread.isUserTitle = isFromUser
		self.api.beta.threads.update(chatThreadId, metadata = {'title': chatThread.title})
		self.database.updateChatThread(chatThread)


	def deleteChatThread(self, chatThreadId):
		"""
		Deletes a chat thread and all it's messages from the server and from disk
		:param chatThreadId: The ID of the chat thread
		"""
		logger.info(f'Deleting chat thread {chatThreadId}')
		self.api.beta.threads.delete(chatThreadId)
		self.database.deleteChatThread(chatThreadId)


	def getMessages(self, chatThreadId: str) -> list[ChatMessage]:
		"""
		Gets the messages for the given thread, loading them if necessary.
		:param chatThreadId: The ID of the chat thread the messages belong to.
		:return: list of message objects
		"""
		chatThread = self.chatThreads[chatThreadId]
		if not chatThread.messages:
			self.loadMessagesFor(chatThread)
		return chatThread.messages


	def loadMessagesFor(self, chatThread: ChatThread):
		"""
		Loads the messages from disk and retrieves newer messages from the server.
		:param chatThread: The chat thread the messages belong to.
		"""
		logger.debug(f'Loading messages for {chatThread.id}')

		# Get existing messages from database.
		chatThread.messages = self.database.getMessagesForThread(chatThread.id)

		# TODO: make this async and emit signal here with messages, then again once updates

		# Retrieve recent messages from server and update database if there are any newer messages.
		result = self.api.beta.threads.messages.list(chatThread.id, limit = 20, order = 'desc')
		for apiMessage in reversed(result.data):
			# Check if the message already exists, looking backward through existing messages since it's likely to be near the end
			existing = next((msg for msg in reversed(chatThread.messages) if msg.id == apiMessage.id), None)
			if existing:
				existing.setAPIObject(apiMessage)
				# TODO:
				#if existing.isSame(apiMessage):
				#   self.database.updateMessage(existing)
			else:
				logger.info(f'Adding new message from server: {apiMessage.id}')
				newMessage = ChatMessage.fromAPIObject(apiMessage)
				self.addNewMessage(chatThread, newMessage)


	def sendMessage(self, chatThreadId, messageText):
		"""
		Sends a user message to the server.
		:param chatThreadId: The ID of the chat thread with which this message is associated.
		:param messageText: Message text to send
		:emits: messageAdded
		"""
		logger.debug(f'Sending message for {chatThreadId}')
		chatThread = self.chatThreads[chatThreadId]

		userMessage = ChatMessage.fromAPIObject(self.api.beta.threads.messages.create(chatThreadId, role = 'user', content = messageText))
		self.addNewMessage(chatThread, userMessage)
		self.messageAdded.emit(userMessage)

		try:
			run = self.api.beta.threads.runs.create(
				thread_id = chatThreadId,
				assistant_id = self.mainAssistant.id,
				model = self.modelName
			)
			while run.status != 'completed' and run.status != 'failed':
				time.sleep(1)
				run = self.api.beta.threads.runs.retrieve(
					thread_id = chatThreadId,
					run_id = run.id
				)
			if run.status == 'failed':
				self.handleError('Failed to retrieve chat response. ' + run.last_error.message)
			else:
				responseMessage = ChatMessage.fromAPIObject(self.api.beta.threads.messages.list(chatThreadId).data[0])
				self.addNewMessage(chatThread, responseMessage)
				self.messageAdded.emit(responseMessage)
		except APIError as e:
			self.handleError('Failed to generate response.', e)


	def addNewMessage(self, chatThread: ChatThread, message: ChatMessage):
		chatThread.messages.append(message)
		self.database.insertMessage(message)


	def handleError(self, message, error: Optional[APIError]):
		logger.error(message + (' ' + str(error)) if error else '')
		self.errorOccurred.emit(message + (' ' + error.body['message']) if error else '')
