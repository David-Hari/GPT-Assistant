from datetime import datetime
from io import StringIO
from pathlib import Path
from unittest import TestCase

from src.data.ChatThread import ChatThread


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


	def testWriting(self):
		pass
		#TODO: Write to StringIO then get using stream.getvalue()
		#ChatThread().toStream()