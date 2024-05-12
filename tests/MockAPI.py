import time
import uuid

from openai.types.beta import Thread, Assistant
from openai.types.beta.threads import TextContentBlock, Run
from openai.types.beta.threads.text import Text
from openai.types.beta.threads.message import Message


class MockPage:
	def __init__(self, d):
		self._data = d

	@property
	def data(self):
		return self._data


class MockAssistants:
	@staticmethod
	def list():
		dummyAssistant = Assistant(
			object = 'assistant',
			id = 'test_assistant_' + str(uuid.uuid1()),
			name = 'Desktop Assistant',
			model = 'gpt-4',
			created_at = int(time.time()),
			tools = []
		)
		return MockPage([dummyAssistant])


class MockMessages:
	@staticmethod
	def create(thread_id, content, role) -> Message:
		obj = Message(
			object = 'thread.message',
			id = 'test_message_' + str(uuid.uuid1()),
			thread_id = thread_id,
			created_at = int(time.time()),
			role = role,
			content = [ TextContentBlock(type='text', text=Text(value=content, annotations=[])) ],
			status = 'completed'
		)
		return obj

	@staticmethod
	def list(thread_id, **kwargs):
		obj = Message(
			object = 'thread.message',
			id = 'test_message_' + str(uuid.uuid1()),
			thread_id = thread_id,
			created_at = int(time.time()),
			role = 'assistant',
			content = [ TextContentBlock(type='text', text=Text(value='Hello', annotations=[])) ],
			status = 'completed'
		)
		return MockPage([obj])


class MockRuns:
	@staticmethod
	def create(thread_id, assistant_id) -> Run:
		obj = Run(
			object = 'thread.run',
			id = 'test_run_' + str(uuid.uuid1()),
			assistant_id = assistant_id,
			thread_id = thread_id,
			created_at = int(time.time()),
			instructions = '',
			model = 'test',
			status = 'completed',
			tools = []
		)
		return obj


class MockThreads:
	messages = MockMessages
	runs = MockRuns

	@staticmethod
	def create() -> Thread:
		obj = Thread(
			object = 'thread',
			id = 'test_thread_' + str(uuid.uuid1()),
			created_at = int(time.time())
		)
		return obj


class MockBeta:
	assistants = MockAssistants()
	threads = MockThreads()


class MockOpenAI:
	beta = MockBeta()
