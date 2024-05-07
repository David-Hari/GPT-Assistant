from datetime import datetime
from unittest import TestCase

from data.ChatThread import ChatThread


class ChatThreadTests(TestCase):

	def testFromDict(self):
		dictionary = {
			'id': 'thread123',
			'created': datetime.fromisoformat('2023-11-16T19:33:14'),
			'title': 'Test Chat',
			'userTitle': 0
		}
		chatThread = ChatThread.fromDictionary(dictionary)
		self.assertEqual(chatThread.id, 'thread123')
		self.assertEqual(chatThread.createdTimestamp, datetime.fromisoformat('2023-11-16T19:33:14'))
		self.assertEqual(chatThread.isUserTitle, False)


	def testUserTitleFromDict(self):
		dictionary = {
			'id': 'thread123',
			'created': datetime.fromisoformat('2023-11-16T19:33:14'),
			'title': 'Test Chat',
			'userTitle': 1
		}
		chatThread = ChatThread.fromDictionary(dictionary)
		self.assertEqual(chatThread.id, 'thread123')
		self.assertEqual(chatThread.createdTimestamp, datetime.fromisoformat('2023-11-16T19:33:14'))
		self.assertEqual(chatThread.isUserTitle, True)


	def testToDict(self):
		chatThread = ChatThread()
		chatThread.id = 'thread123'
		chatThread.createdTimestamp = datetime.fromisoformat('2023-11-16T19:33:14')
		chatThread.title = 'Test Chat'
		chatThread.isUserTitle = False

		dictionary = chatThread.toDictionary()

		expected = {
			'id': 'thread123',
			'created': datetime.fromisoformat('2023-11-16T19:33:14'),
			'title': 'Test Chat',
			'userTitle': 0
		}
		self.assertEqual(dictionary, expected)


	def testUserTitleToDict(self):
		chatThread = ChatThread()
		chatThread.id = 'thread123'
		chatThread.createdTimestamp = datetime.fromisoformat('2023-11-16T19:33:14')
		chatThread.title = 'Test Chat'
		chatThread.isUserTitle = True

		dictionary = chatThread.toDictionary()

		expected = {
			'id': 'thread123',
			'created': datetime.fromisoformat('2023-11-16T19:33:14'),
			'title': 'Test Chat',
			'userTitle': 1
		}
		self.assertEqual(dictionary, expected)