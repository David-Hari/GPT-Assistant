from datetime import datetime
from pathlib import Path
import sqlite3

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

class Database:

	def __init__(self, dbPath: Path):
		shouldCreate = not dbPath.exists()  # Need to check this first, as connecting will automatically create the file

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


	def updateAssistants(self, assistants: list[Assistant]):
		with self.connection:
			cursor = self.connection.cursor()

			values = [
				{
					'id': assistant.id,
					'created': datetime.utcfromtimestamp(assistant.created_at),
					'name': assistant.name,
					'instructions': assistant.instructions
				} for assistant in assistants
			]
			cursor.executemany('INSERT OR REPLACE INTO Assistants (id, created, name, instructions) ' +
			                  'VALUES (:id, :created, :name, :instructions)', values)
