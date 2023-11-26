from datetime import datetime, timezone
from typing import List, Optional

from openai.types.beta.threads import MessageContentText
from openai.types.beta.threads.message_content_text import Text
from openai.types.beta.threads.thread_message import ThreadMessage, Content


RecordSeparator = '\x1E'
UnitSeparator = '\x1F'


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
		obj.role = dictionary['role']
		obj.content = [ MessageContentText(type='text', text=Text(value=dictionary['content'], annotations=[])) ]
		return obj


	@classmethod
	def fromAPIObject(cls, apiObject: ThreadMessage):
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

		self.role: Optional[str] = None
		"""The entity that produced the message. One of `user` or `assistant`."""

		self.content: List[Content] = []
		"""The content of the message in array of text and/or images."""

		self.fileIds: List[str] = []
		"""A list of file IDs that the assistant should use. For tools that can access files."""

		self.apiObject = None


	def setAPIObject(self, apiObject: ThreadMessage):
		"""
		Sets the properties from an API object that came from a request to get this message from the server.
		"""
		self.apiObject = apiObject
		self.id = apiObject.id
		self.threadId = apiObject.thread_id
		self.createdTimestamp = datetime.fromtimestamp(apiObject.created_at, timezone.utc)
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


	def __str__(self):
		return 'ChatMessage(' + '\n'.join(content.text.value for content in self.content) + ')'