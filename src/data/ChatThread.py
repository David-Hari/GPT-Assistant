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

	messages: List[ChatMessage] = []
	"""The list of messages in the thread, in ascending order of creation time."""


	@classmethod
	def fromStream(cls, stream: TextIO):
		"""
		Reads a thread of chat messages from a text stream and returns a ChatThread object.
		:param stream: A text stream (file-like object) containing the messages.
		:return: A ChatThread object.
		"""
		obj = cls()

		# Read metadata header
		header = readChunk(stream)
		metadata = json.loads(header)
		if 'id' not in metadata:
			raise ValueError('Chat thread is missing the \'id\' field.')
		if 'created' not in metadata:
			raise ValueError('Chat thread is missing the \'created\' field.')
		obj.id = metadata.get('id')
		obj.createdTimestamp = datetime.fromisoformat(metadata.get('created'))
		obj.title = metadata.get('title', 'Untitled')

		# Read the messages
		obj.messages = []
		message = ChatMessage.fromStream(stream)
		while message:
			obj.messages.append(message)
			message = ChatMessage.fromStream(stream)

		return obj


	def __init__(self, apiObject: Optional[Thread] = None):
		if apiObject:
			self.id = apiObject.id
			self.createdTimestamp = datetime.utcfromtimestamp(apiObject.created_at)
			self.title = apiObject.metadata.get('title', 'Untitled')
			self.apiObject = apiObject  # Hold on to API object if we have it, as we might need additional properties from it


	def toStream(self, stream: TextIO):
		"""
		Writes the thread of chat messages to a text stream.
		:param stream: A text stream (file-like object) to write the message to.
		"""

		# Write metadata header
		metadata = {
			'id': self.id,
			'created': self.createdTimestamp.isoformat(),
			'title': self.title,
		}
		stream.write(json.dumps(metadata))
		stream.write('\n' + RecordSeparator)

		# Write each message
		for message in self.messages:
			message.toStream(stream)
		pass


def readChunk(stream: TextIO):
	"""
	Reads from the stream until it reaches either the end of a message (newline then record separator)
	or the end of the stream.
	"""
	result = ''
	lastChar = ''
	while True:
		char = stream.read(1)
		if char == '':
			return
		if char == RecordSeparator and lastChar == '\n':
			return result[:-1]
		result += char
		lastChar = char