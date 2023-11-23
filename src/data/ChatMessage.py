import json
from datetime import datetime
from typing import List, Literal, Optional, TextIO

from openai.types.beta.threads import MessageContentText
from openai.types.beta.threads.message_content_text import Text
from openai.types.beta.threads.thread_message import ThreadMessage, Content


RecordSeparator = '\x1E'
UnitSeparator = '\x1F'


class ChatMessage:
	id: str
	"""The identifier, which can be referenced in API endpoints."""

	threadId: str
	"""The chat thread ID that this message belongs to."""

	createdTimestamp: datetime
	"""The timestamp for when the message was created."""

	role: Literal['user', 'assistant']
	"""The entity that produced the message. One of `user` or `assistant`."""

	content: List[Content] = []
	"""The content of the message in array of text and/or images."""

	fileIds: List[str] = []
	"""A list of file IDs that the assistant should use. For tools that can access files."""


	@classmethod
	def fromDictionary(cls, dictionary):
		"""
		Creates a ChatMessage object from the properties in a dictionary.
		"""
		obj = cls()
		obj.id = dictionary['id']
		obj.threadId = dictionary['threadId']
		obj.createdTimestamp = dictionary['created']
		obj.role = dictionary['role']
		obj.content = [ MessageContentText(type='text', text=Text(value=dictionary['content'], annotations=[])) ]
		return obj


	def __init__(self, apiObject: Optional[ThreadMessage] = None):
		self.apiObject = None
		if apiObject:
			self.setAPIObject(apiObject)


	def setAPIObject(self, apiObject: ThreadMessage):
		"""
		Sets the properties from an API object that came from a request to get this message from the server.
		"""
		self.apiObject = apiObject
		self.id = apiObject.id
		self.threadId = apiObject.thread_id
		self.createdTimestamp = datetime.utcfromtimestamp(apiObject.created_at)
		self.role = apiObject.role
		self.content = apiObject.content


	def toDictionary(self):
		"""
		Returns a dictionary with the properties of this message object.
		"""
		return {
			'id': self.id,
			'threadId': self.threadId,
			'created': self.createdTimestamp,
			'role': self.role,
			'content': self.content[0].text.value
		}
