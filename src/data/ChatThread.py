from datetime import datetime, timezone
from typing import List, Optional

from openai.types.beta import Thread

from data.ChatMessage import ChatMessage


RecordSeparator = '\x1E'


class ChatThread:

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


	@classmethod
	def fromAPIObject(cls, apiObject: Thread):
		obj = cls()
		obj.setAPIObject(apiObject)
		return obj


	def __init__(self):
		self.id: Optional[str] = None
		"""The identifier, which can be referenced in API endpoints."""

		self.createdTimestamp: Optional[datetime] = None
		"""The timestamp for when the thread was created."""

		self.title: Optional[str]
		"""The title of the thread"""

		self.isUserTitle: bool = False
		"""True if the user has given the title for this thread. If false, the AI can choose the title."""

		self.messages: List[ChatMessage] = []
		"""The list of messages in the thread, in ascending order of creation time."""

		self.apiObject = None


	def setAPIObject(self, apiObject: Thread):
		"""
		Sets the properties from an API object that came from a request to get this thread from the server.
		"""
		self.apiObject = apiObject
		self.id = apiObject.id
		self.createdTimestamp = datetime.fromtimestamp(apiObject.created_at, timezone.utc)
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
