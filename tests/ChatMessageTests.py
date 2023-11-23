from datetime import datetime
from unittest import TestCase

from openai.types.beta.threads import MessageContentText
from openai.types.beta.threads.message_content_text import Text

from data.ChatMessage import ChatMessage


class ChatMessageTests(TestCase):

	def testSimpleMessageFromDict(self):
		dictionary  = {
			'id': 'abc123',
			'threadId': 'thread123',
			'created': datetime.fromisoformat('2023-11-16T19:33:14'),
			'role': 'user',
			'content': 'This is a message'
		}
		message = ChatMessage.fromDictionary(dictionary)
		self.assertEqual(message.id, 'abc123')
		self.assertEqual(message.threadId, 'thread123')
		self.assertEqual(message.createdTimestamp, datetime.fromisoformat('2023-11-16T19:33:14'))
		self.assertEqual(message.role, 'user')
		self.assertEqual(len(message.content), 1)
		self.assertEqual(message.content[0].text.value, 'This is a message')


	def testSimpleAssistantMessageFromDict(self):
		dictionary  = {
			'id': 'abc123',
			'threadId': 'thread123',
			'created': datetime.fromisoformat('2023-11-16T19:33:14'),
			'role': 'assistant',
			'content': 'This is a message'
		}
		message = ChatMessage.fromDictionary(dictionary)
		self.assertEqual(message.role, 'assistant')


	def testSimpleMessageToDict(self):
		message = ChatMessage()
		message.id = 'abc123'
		message.threadId = 'thread123'
		message.createdTimestamp = datetime.fromisoformat('2023-11-16T19:33:14')
		message.role = 'user'
		message.content = [ MessageContentText(type='text', text=Text(value='This is a message', annotations=[])) ]

		dictionary = message.toDictionary()

		expected  = {
			'id': 'abc123',
			'threadId': 'thread123',
			'created': datetime.fromisoformat('2023-11-16T19:33:14'),
			'role': 'user',
			'content': 'This is a message'
		}
		self.assertEqual(dictionary, expected)


	def testSimpleAssistantMessageToDict(self):
		message = ChatMessage()
		message.id = 'abc123'
		message.threadId = 'thread123'
		message.createdTimestamp = datetime.fromisoformat('2023-12-08T19:33:14')
		message.role = 'assistant'
		message.content = [ MessageContentText(type='text', text=Text(value='This is a message', annotations=[])) ]

		dictionary = message.toDictionary()

		expected  = {
			'id': 'abc123',
			'threadId': 'thread123',
			'created': datetime.fromisoformat('2023-12-08T19:33:14'),
			'role': 'assistant',
			'content': 'This is a message'
		}
		self.assertEqual(dictionary, expected)
