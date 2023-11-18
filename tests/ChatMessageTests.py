from datetime import datetime
from io import StringIO
from unittest import TestCase

from openai.types.beta.threads import MessageContentText
from openai.types.beta.threads.message_content_text import Text

from src.data.ChatMessage import ChatMessage


class ChatMessageTests(TestCase):

	def testReadingSimpleMessage(self):
		messageString = '{"id": "abc123", "created": "2023-11-16T19:33:14", "role": "user"}\n\x1F'\
		                'This is a message\n\x1F\n\x1E'
		message = ChatMessage.fromStream(StringIO(messageString))
		self.assertEqual(message.id, 'abc123')
		self.assertEqual(message.createdTimestamp, datetime(2023, 11, 16, 19, 33, 14))
		self.assertEqual(message.role, 'user')
		self.assertEqual(len(message.content), 1)
		self.assertEqual(message.content[0].text.value, 'This is a message')


	def testReadingSimpleAssistantMessage(self):
		messageString = '{"id": "abc123", "created": "2023-11-16T19:33:14", "role": "assistant"}\n\x1F' \
		                'This is a message\n\x1F\n\x1E'
		message = ChatMessage.fromStream(StringIO(messageString))
		self.assertEqual(message.role, 'assistant')


	def testReadingComplexMessage(self):
		messageString = '{"id": "abc123", "created": "2023-11-16T19:33:14", "role": "user"}\n\x1F' \
		                'This is a message\n\x1F'\
		                'And another part\n\x1F'\
		                'Some more\n\x1F\n\x1E'
		message = ChatMessage.fromStream(StringIO(messageString))
		self.assertEqual(len(message.content), 3)
		self.assertEqual(message.content[0].text.value, 'This is a message')
		self.assertEqual(message.content[1].text.value, 'And another part')
		self.assertEqual(message.content[2].text.value, 'Some more')


	def testReadingMissingId(self):
		messageString = '{"created": "2023-11-16T19:33:14", "role": "user"}\n\x1F' \
		                'This is a message\n\x1F\n\x1E'
		with self.assertRaises(ValueError) as context:
			ChatMessage.fromStream(StringIO(messageString))
		self.assertEqual(str(context.exception), 'Message is missing the \'id\' field.')


	def testReadingMissingCreated(self):
		messageString = '{"id": "abc123", "role": "user"}\n\x1F' \
		                'This is a message\n\x1F\n\x1E'
		with self.assertRaises(ValueError) as context:
			ChatMessage.fromStream(StringIO(messageString))
		self.assertEqual(str(context.exception), 'Message is missing the \'created\' field.')


	def testReadingMissingRole(self):
		messageString = '{"id": "abc123", "created": "2023-11-16T19:33:14"}\n\x1F' \
		                'This is a message\n\x1F\n\x1E'
		with self.assertRaises(ValueError) as context:
			ChatMessage.fromStream(StringIO(messageString))
		self.assertEqual(str(context.exception), 'Message is missing the \'role\' field.')


	def testReadingMissingContent(self):
		messageString = '{"id": "abc123", "created": "2023-11-16T19:33:14", "role": "user"}\n\x1F\n\x1E'
		message = ChatMessage.fromStream(StringIO(messageString))
		self.assertEqual(len(message.content), 0)


	def testWritingSimpleMessage(self):
		message = ChatMessage()
		message.id = 'abc123'
		message.createdTimestamp = datetime(2023, 11, 16, 19, 33, 14)
		message.role = 'user'
		message.content = [ MessageContentText(type='text', text=Text(value='This is a message', annotations=[])) ]

		stream = StringIO()
		message.toStream(stream)

		expected = '{"id": "abc123", "created": "2023-11-16T19:33:14", "role": "user"}\n\x1F' \
		           'This is a message\n\x1F\n\x1E'
		self.assertEqual(stream.getvalue(), expected)