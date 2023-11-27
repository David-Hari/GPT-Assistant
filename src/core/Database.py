from datetime import datetime, timezone
from pathlib import Path
import sqlite3

from openai.types.beta import Assistant

from data.ChatMessage import ChatMessage
from data.ChatThread import ChatThread


assistantsTableSchema = """
Assistants (
    id           text    primary key,
    created      timestamp,
    name         text,
    model        text,
    instructions text
)
"""
threadTableSchema = """
ChatThreads (
    id        text    primary key,
    created   timestamp,
    title     text,
    userTitle integer
)
"""
messageTableSchema = """
ChatMessages (
    id        text    primary key,
    threadId  text,
    created   timestamp,
    role      text,
    content   text,
    foreign key (threadId) references Thread(id)
)
"""

class Database:

	def __init__(self, dbPath: Path, shouldCreate):
		self.connection = sqlite3.connect(dbPath, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
		self.connection.row_factory = sqlite3.Row
		if shouldCreate:
			self.createDatabase()


	def createDatabase(self):
		with self.connection:
			cursor = self.connection.cursor()
			cursor.execute('create table if not exists ' + assistantsTableSchema)
			cursor.execute('create table if not exists ' + threadTableSchema)
			cursor.execute('create table if not exists ' + messageTableSchema)
			cursor.close()


	def getAssistants(self) -> list[Assistant]:
		with self.connection:
			cursor = self.connection.execute('select * from Assistants')
			return [
				Assistant(
					object = 'assistant',
					id = row['id'],
					created_at = row['created'].timestamp(),
					name = row['name'],
					model = row['model'],
					description = '',
					file_ids = [],
					tools = []
				) for row in cursor.fetchall()
			]


	def updateAssistants(self, assistants: list[Assistant]):
		with self.connection:
			cursor = self.connection.cursor()

			values = [
				{
					'id': assistant.id,
					'created': datetime.fromtimestamp(assistant.created_at, timezone.utc),
					'name': assistant.name,
					'model': assistant.model,
					'instructions': assistant.instructions
				} for assistant in assistants
			]
			sql = 'insert or replace into Assistants (id, created, name, model, instructions) values (:id, :created, :name, :model, :instructions)'
			cursor.executemany(sql, values)


	def insertChatThread(self, chatThread: ChatThread):
		with self.connection:
			sql = 'insert into ChatThreads (id, created, title, userTitle) values (:id, :created, :title, :userTitle)'
			self.connection.execute(sql, chatThread.toDictionary())


	def insertMessage(self, message: ChatMessage):
		with self.connection:
			sql = 'insert into ChatMessages (id, threadId, created, role, content) values (:id, :threadId, :created, :role, :content)'
			self.connection.execute(sql, message.toDictionary())


	def getChatThread(self, threadId: str) -> ChatThread:
		with self.connection:
			cursor = self.connection.execute('select * from ChatThreads where id = ?', (threadId,))
			row = cursor.fetchone()
			return ChatThread.fromDictionary(dict(row)) if row else None


	def getChatThreads(self) -> list[ChatThread]:
		with self.connection:
			cursor = self.connection.execute('select * from ChatThreads order by created desc')
			return [ChatThread.fromDictionary(dict(row)) for row in cursor.fetchall()]


	def getMessage(self, messageId: str) -> ChatMessage:
		with self.connection:
			cursor = self.connection.execute('select * from ChatMessages where id = ?', (messageId,))
			row = cursor.fetchone()
			return ChatMessage.fromDictionary(dict(row)) if row else None


	def getMessagesForThread(self, threadId: str) -> list[ChatMessage]:
		with self.connection:
			cursor = self.connection.execute('select * from ChatMessages where threadId = ? order by created asc', (threadId,))
			return [ChatMessage.fromDictionary(dict(row)) for row in cursor.fetchall()]


	def deleteChatThread(self, threadId: str):
		with self.connection:
			self.connection.execute('delete from ChatThreads where id = ?', (threadId,))


	def deleteMessage(self, messageId: str):
		with self.connection:
			self.connection.execute('delete from ChatMessages where id = ?', (messageId,))
