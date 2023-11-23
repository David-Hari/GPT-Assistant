import json
from datetime import datetime
from typing import List, Optional, TextIO

from openai.types.beta import Thread

from data.ChatMessage import ChatMessage


RecordSeparator = '\x1E'


class ChatThread:
	id: str
	"""The identifier, which can be referenced in API endpoints."""

	createdTimestamp: datetime
	"""The timestamp for when the thread was created."""

	title: str
	"""The title of the thread"""

	isUserTitle: bool
	"""True if the user has given the title for this thread. If false, the AI can choose the title."""

	messages: List[ChatMessage] = []
	"""The list of messages in the thread, in ascending order of creation time."""


	@classmethod
	def fromDictionary(cls, dictionary):
		"""
		Creates a ChatThread object from the properties in a dictionary.
		"""
		obj = cls()
		obj.id = dictionary['id']
		obj.createdTimestamp = dictionary['created']
		obj.title = dictionary['title']
		obj.isUserTitle = bool(dictionary['userTitle'])
		return obj


	def __init__(self, apiObject: Optional[Thread] = None):
		self.apiObject = None
		if apiObject:
			self.setAPIObject(apiObject)


	def setAPIObject(self, apiObject: Thread):
		"""
		Sets the properties from an API object that came from a request to get this thread from the server.
		"""
		self.apiObject = apiObject
		self.id = apiObject.id
		self.createdTimestamp = datetime.utcfromtimestamp(apiObject.created_at)
		self.title = apiObject.metadata.get('title', 'Untitled')


	def toDictionary(self):
		"""
		Returns a dictionary with the properties of this chat thread object.
		"""
		return {
			'id': self.id,
			'created': self.createdTimestamp,
			'title': self.title,
			'userTitle': int(self.isUserTitle)
		}
