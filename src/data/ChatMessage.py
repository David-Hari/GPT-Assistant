import json
from datetime import datetime
from typing import List, Literal, Optional, TextIO

from openai.types.beta.threads import MessageContentText
from openai.types.beta.threads.message_content_text import Text
from openai.types.beta.threads.thread_message import ThreadMessage, Content


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
		:return: A ChatMessage object.
		"""
		obj = cls()

		# Read metadata header
		header = readChunk(stream)
		metadata = json.loads(header)
		obj.id = metadata.get('id')
		obj.createdTimestamp = datetime.fromisoformat(metadata.get('created'))
		obj.role = metadata.get('role')

		# Read message contents
		obj.content = []
		while True:
			chunkData = readChunk(stream)
			if chunkData == '\n\x1E':
				break
			content = MessageContentText()
			content.text = Text()
			content.text.value = chunkData

		return obj


	def __init__(self, apiObject: Optional[ThreadMessage] = None):
		if apiObject:
			self.id = apiObject.id
			self.dateCreated = datetime.utcfromtimestamp(apiObject.created_at)
			self.apiObject = apiObject  # Hold on to API object if we have it, as we might need additional properties from it


	def toStream(self, stream: TextIO):
		#TODO: Accept stream to write to
		pass


def readChunk(stream: TextIO):
	"""
	Reads from the stream until it reaches either the end of a message section
	(newline then unit separator \x1F), the end of the message (newline then record separator \x1E)
	or the end of the stream.
	"""
	result = ''
	lastChar = ''
	while True:
		char = stream.read(1)
		if char == '':
			return
		if (char == '\x1F' or char == '\x1E') and lastChar == '\n':
			return result
		result += char
		lastChar = char