from datetime import datetime
from io import StringIO
from pathlib import Path
from unittest import TestCase

from openai.types.beta.threads import MessageContentText
from openai.types.beta.threads.message_content_text import Text

from data.ChatMessage import ChatMessage
from data.ChatThread import ChatThread


class ChatThreadTests(TestCase):
	messagesDir = Path(__file__).parent / 'expected'

	def testReadingEmpty(self):
		threadString = '{"id": "thread123", "created": "2023-11-16T19:33:14", "title": "Test Chat"}\n\x1E'
		chatThread = ChatThread.fromStream(StringIO(threadString))
		self.assertEqual(chatThread.id, 'thread123')
		self.assertEqual(chatThread.createdTimestamp, datetime(2023, 11, 16, 19, 33, 14))
		self.assertEqual(len(chatThread.messages), 0)


	def testReadingMessages(self):
		threadString = '{"id": "thread123", "created": "2023-11-16T19:33:14", "title": "Test Chat"}\n\x1E' \
		               '{"id": "abc123", "created": "2023-11-16T19:33:14", "role": "user"}\n\x1F' \
		               'This is a message\n\x1F\n\x1E' \
		               '{"id": "abc456", "created": "2023-11-16T19:43:34", "role": "user"}\n\x1F' \
		               'This is a another message\n\x1F\n\x1E' \
		               '{"id": "abc789", "created": "2023-11-16T19:47:46", "role": "user"}\n\x1F' \
		               'Final message\n\x1F\n\x1E'
		chatThread = ChatThread.fromStream(StringIO(threadString))
		self.assertEqual(chatThread.id, 'thread123')
		self.assertEqual(chatThread.createdTimestamp, datetime(2023, 11, 16, 19, 33, 14))
		self.assertEqual(len(chatThread.messages), 3)


	def testReadingMissingId(self):
		threadString = '{"created": "2023-11-16T19:33:14", "title": "Test Chat"}\n\x1E' \
		               '{"id": "abc123", "created": "2023-11-16T19:33:14", "role": "user"}\n\x1F' \
		               'This is a message\n\x1F\n\x1E'
		with self.assertRaises(ValueError) as context:
			ChatThread.fromStream(StringIO(threadString))
		self.assertEqual(str(context.exception), 'Chat thread is missing the \'id\' field.')


	def testReadingMissingCreated(self):
		threadString = '{"id": "thread123", "title": "Test Chat"}\n\x1E' \
		               '{"id": "abc123", "created": "2023-11-16T19:33:14", "role": "user"}\n\x1F' \
		               'This is a message\n\x1F\n\x1E'
		with self.assertRaises(ValueError) as context:
			ChatThread.fromStream(StringIO(threadString))
		self.assertEqual(str(context.exception), 'Chat thread is missing the \'created\' field.')


	def testReadingMissingTitle(self):
		threadString = '{"id": "thread123", "created": "2023-11-16T19:33:14"}\n\x1E' \
		               '{"id": "abc123", "created": "2023-11-16T19:33:14", "role": "user"}\n\x1F' \
		               'This is a message\n\x1F\n\x1E'
		chatThread = ChatThread.fromStream(StringIO(threadString))
		self.assertEqual(chatThread.title, 'Untitled')


	def testWritingSingleMessage(self):
		chatThread = ChatThread()
		chatThread.id = 'thread123'
		chatThread.createdTimestamp = datetime(2023, 2, 13, 4, 55, 36)
		chatThread.title = 'Test Chat'
		chatThread.messages = [ makeTestMessage('abc123') ]

		stream = StringIO()
		chatThread.toStream(stream)

		expected = '{"id": "thread123", "created": "2023-02-13T04:55:36", "title": "Test Chat"}\n\x1E' \
		           '{"id": "abc123", "created": "2023-11-16T19:33:14", "role": "user"}\n\x1F' \
		           'This is a message\n\x1F\n\x1E'
		self.assertEqual(stream.getvalue(), expected)


	def testWritingMultipleMessages(self):
		chatThread = ChatThread()
		chatThread.id = 'thread123'
		chatThread.createdTimestamp = datetime(2023, 2, 13, 4, 55, 36)
		chatThread.title = 'Test Chat'
		chatThread.messages = [
			makeTestMessage('abc123'),
			makeTestMessage('abc456'),
			makeTestMessage('abc789')
		]

		stream = StringIO()
		chatThread.toStream(stream)

		expected = '{"id": "thread123", "created": "2023-02-13T04:55:36", "title": "Test Chat"}\n\x1E' \
		           '{"id": "abc123", "created": "2023-11-16T19:33:14", "role": "user"}\n\x1F' \
		           'This is a message\n\x1F\n\x1E' \
		           '{"id": "abc456", "created": "2023-11-16T19:33:14", "role": "user"}\n\x1F' \
		           'This is a message\n\x1F\n\x1E' \
		           '{"id": "abc789", "created": "2023-11-16T19:33:14", "role": "user"}\n\x1F' \
		           'This is a message\n\x1F\n\x1E'
		self.assertEqual(stream.getvalue(), expected)


	def testWritingMultiPartMessage(self):
		chatThread = ChatThread()
		chatThread.id = 'thread123'
		chatThread.createdTimestamp = datetime(2023, 2, 13, 4, 55, 36)
		chatThread.title = 'Test Chat'
		chatThread.messages = [ makeTestMessage('abc123') ]
		chatThread.messages[0].content = [
			MessageContentText(type='text', text=Text(value='This is a message', annotations=[])),
			MessageContentText(type='text', text=Text(value='Another message', annotations=[])),
			MessageContentText(type='text', text=Text(value='This the last message', annotations=[]))
		]

		stream = StringIO()
		chatThread.toStream(stream)

		expected = '{"id": "thread123", "created": "2023-02-13T04:55:36", "title": "Test Chat"}\n\x1E' \
		           '{"id": "abc123", "created": "2023-11-16T19:33:14", "role": "user"}\n\x1F' \
		           'This is a message\n\x1F' \
		           'Another message\n\x1F' \
		           'This the last message\n\x1F\n\x1E'
		self.assertEqual(stream.getvalue(), expected)


def makeTestMessage(msgId):
	message = ChatMessage()
	message.id = msgId
	message.createdTimestamp = datetime(2023, 11, 16, 19, 33, 14)
	message.role = 'user'
	message.content = [ MessageContentText(type='text', text=Text(value='This is a message', annotations=[])) ]
	return message