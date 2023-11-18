from io import StringIO
from pathlib import Path
from unittest import TestCase

from src.data.ChatThread import ChatThread


class ChatThreadTests(TestCase):
	messagesDir = Path(__file__).parent / 'expected'

	def testReading(self):
		threadString = '{"id": "thread123", "created": "2023-11-16T19:33:14", "title": "Test Chat"}\n\x1E' \
		               '{"id": "abc123", "created": "2023-11-16T19:33:14", "role": "user"}\n\x1F' \
		               'This is a message\n\x1F\n\x1E' \
		               '{"id": "abc456", "created": "2023-11-16T19:43:14", "role": "user"}\n\x1F' \
		               'This is a another message\n\x1F\n\x1E'

		message = ChatThread.fromStream(StringIO(threadString))

		self.assertEqual(message.id, 'testMessage1')

	def testWriting(self):
		pass
		#TODO: Write to StringIO then get using stream.getvalue()
		#ChatThread().toStream()