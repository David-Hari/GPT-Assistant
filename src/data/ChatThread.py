from datetime import datetime
from typing import List, Optional, TextIO

from openai.types.beta import Thread

from data.ChatMessage import ChatMessage


class ChatThread:
	id: str
	"""The identifier, which can be referenced in API endpoints."""

	createdTimestamp: datetime
	"""The timestamp for when the thread was created."""

	title: str
	"""The title of the thread"""

	messages: List[ChatMessage] = []
	"""The list of messages in the thread, in ascending order of creation time."""


	@classmethod
	def fromStream(cls, stream: TextIO):
		obj = cls()
		#TODO: Implement deserialization logic here
		# Return an instance of the class based on the deserialized data
		return obj


	def __init__(self, apiObject: Optional[Thread] = None):
		if apiObject:
			self.id = apiObject.id
			self.dateCreated = datetime.utcfromtimestamp(apiObject.created_at)
			self.title = apiObject.metadata.get('title', 'Untitled')
			self.apiObject = apiObject  # Hold on to API object if we have it, as we might need additional properties from it


	def toStream(self, stream: TextIO):
		#TODO: json id, created, title
		for message in self.messages:
			message.toStream(stream)
		pass


def readChunk(stream: TextIO):
	"""
	Reads from the stream until it reaches either the end of a message (newline then record separator \x1E)
	or the end of the stream.
	"""
	result = ''
	lastChar = ''
	while True:
		char = stream.read(1)
		if not char or (char == '\x1E' and lastChar == '\n') or char == '':
			break
		result += char
		lastChar = char
	return result