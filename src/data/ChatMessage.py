from datetime import datetime, timezone
from typing import List, Optional

from openai.types.beta.threads import MessageContent, TextContentBlock
from openai.types.beta.threads.text import Text
from openai.types.beta.threads.message import Message



class ChatMessage:

	@classmethod
	def fromDictionary(cls, dictionary):
		"""
		Creates a ChatMessage object from the properties in a dictionary.
		"""
		obj = cls()
		obj.id = dictionary['id']
		obj.threadId = dictionary['threadId']
		obj.createdTimestamp = dictionary['created']
		obj.author = dictionary['author']
		obj.content = [ TextContentBlock(type='text', text=Text(value=dictionary['content'], annotations=[])) ]
		return obj


	@classmethod
	def fromAPIObject(cls, apiObject: Message):
		obj = cls()
		obj.setAPIObject(apiObject)
		return obj


	def __init__(self):
		self.id: Optional[str] = None
		"""The identifier, which can be referenced in API endpoints."""

		self.threadId: Optional[str] = None
		"""The chat thread ID that this message belongs to."""

		self.createdTimestamp: Optional[datetime] = None
		"""The timestamp for when the message was created."""

		self.author: Optional[str] = None
		"""The entity that produced the message. Either `user` or an assistant id."""

		self.content: List[MessageContent] = []
		"""The content of the message in array of text and/or images."""

		self.fileIds: List[str] = []
		"""A list of file IDs that the assistant should use. For tools that can access files."""

		self.apiObject = None


	@property
	def authorType(self):
		return 'user' if self.author == 'user' else 'assistant'


	def setAPIObject(self, apiObject: Message):
		"""
		Sets the properties from an API object that came from a request to get this message from the server.
		"""
		self.apiObject = apiObject
		self.id = apiObject.id
		self.threadId = apiObject.thread_id
		self.createdTimestamp = datetime.fromtimestamp(apiObject.created_at, timezone.utc)
		self.author = 'user' if apiObject.role == 'user' else apiObject.assistant_id
		self.content = apiObject.content


	def toDictionary(self):
		"""
		Returns a dictionary with the properties of this message object.
		"""
		return {
			'id': self.id,
			'threadId': self.threadId,
			'created': self.createdTimestamp,
			'author': self.author,
			'content': self.content[0].text.value
		}


	def __str__(self):
		return 'ChatMessage(' + '\n'.join(content.text.value for content in self.content) + ')'