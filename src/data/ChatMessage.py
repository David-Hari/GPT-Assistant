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
	def fromStream(cls, stream: TextIO):
		"""
		Reads a chat message from a text stream and returns a ChatMessage object.
		:param stream: A text stream (file-like object) containing the message.
		:return: A ChatMessage object or None if the stream is at the end.
		"""
		obj = cls()

		# Read metadata header
		header = readChunk(stream)
		if not header or header == '':
			return None
		metadata = json.loads(header)
		if 'id' not in metadata:
			raise ValueError('Message is missing the \'id\' field.')
		if 'created' not in metadata:
			raise ValueError('Message is missing the \'created\' field.')
		if 'role' not in metadata:
			raise ValueError('Message is missing the \'role\' field.')
		obj.id = metadata.get('id')
		obj.createdTimestamp = datetime.fromisoformat(metadata.get('created'))
		obj.role = metadata.get('role')

		# Read message contents
		obj.content = []
		chunkData = readChunk(stream)
		while chunkData and chunkData != '':
			content = MessageContentText(type='text', text=Text(value=chunkData, annotations=[]))
			obj.content.append(content)
			chunkData = readChunk(stream)

		return obj


	def __init__(self, apiObject: Optional[ThreadMessage] = None):
		if apiObject:
			self.id = apiObject.id
			self.dateCreated = datetime.utcfromtimestamp(apiObject.created_at)
			self.apiObject = apiObject  # Hold on to API object if we have it, as we might need additional properties from it


	def toStream(self, stream: TextIO):
		"""
		Writes the chat message to a text stream.
		:param stream: A text stream (file-like object) to write the message to.
		"""

		# Write metadata header
		metadata = {
			'id': self.id,
			'created': self.createdTimestamp.isoformat(),
			'role': self.role,
		}
		stream.write(json.dumps(metadata))
		stream.write('\n' + UnitSeparator)

		# Write message content
		for content in self.content:
			stream.write(content.text.value if content.text else '')
			stream.write('\n' + UnitSeparator)

		# End of message
		stream.write('\n' + RecordSeparator)


def readChunk(stream: TextIO):
	"""
	Reads from the stream until it reaches either the end of a message section
	(newline then unit separator), the end of the message (newline then record separator)
	or the end of the stream.
	"""
	result = ''
	lastChar = ''
	while True:
		char = stream.read(1)
		if char == '':
			return
		if (char == UnitSeparator or char == RecordSeparator) and lastChar == '\n':
			return result[:-1]
		result += char
		lastChar = char