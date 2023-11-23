from pathlib import Path

from PySide6.QtCore import QDateTime
from PySide6.QtSql import QSqlDatabase, QSqlQuery
from openai.types.beta import Assistant


assistantsTableSchema = """
Assistants (
    id           text       primary key,
    created      timestamp,
    name         text,
    instructions text
)
"""
threadTableSchema = """
ChatThreads (
    id        text       primary key,
    created   timestamp,
    title     text
)
"""
messageTableSchema = """
ChatMessages (
    id        text       primary key,
    threadId  text,
    created   timestamp,
    role      text,
    content   text,
    foreign   key (threadId) references Thread(id)
)
"""

class ChatDatabase:

	def __init__(self, dbPath: Path):
		self.db = QSqlDatabase.addDatabase("QSQLITE")
		self.db.setDatabaseName(str(dbPath))

		if not dbPath.exists():
			self.createDatabase(dbPath)


	def createDatabase(self, dbPath: Path):
		dbPath.touch()

		if not self.db.open():
			raise Exception('Unable to open the chats database. ' + self.db.lastError().text())

		query = QSqlQuery(self.db)
		query.exec('create table if not exists ' + assistantsTableSchema)
		query.exec('create table if not exists ' + threadTableSchema)
		query.exec('create table if not exists ' + messageTableSchema)

		self.db.close()


	def updateAssistants(self, assistants: list[Assistant]):
		self.db.open()

		query = QSqlQuery(self.db)
		query.prepare('INSERT OR REPLACE INTO Assistants (id, created, name, instructions) VALUES (:id, :created, :name, :instructions)')

		for assistant in assistants:
			query.bindValue(':id', assistant.id)
			query.bindValue(':created', QDateTime.fromSecsSinceEpoch(assistant.created_at))
			query.bindValue(':name', assistant.name)
			query.bindValue(':instructions', assistant.instructions)
			query.exec()

		self.db.close()