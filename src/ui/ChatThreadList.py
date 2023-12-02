from typing import Collection

from PySide6.QtCore import Qt, QAbstractListModel, QModelIndex
from PySide6.QtWidgets import QStyledItemDelegate, QLineEdit, QAbstractItemDelegate

from data.ChatThread import ChatThread


"""
Implements a custom widget for items in the chat thread list.
It shows an edit and delete button when hovered over, and the title can be edited.
"""

class ChatThreadListModel(QAbstractListModel):

	def __init__(self, parent = None):
		super(ChatThreadListModel, self).__init__(parent)
		self.chatThreads: list[ChatThread] = []


	def rowCount(self, parent = QModelIndex()):
		return len(self.chatThreads)


	def data(self, index, role = Qt.DisplayRole):
		chatThread = self.chatThreads[index.row()]
		if role == Qt.UserRole:
			return chatThread.id
		if role == Qt.DisplayRole:
			return chatThread.title
		if role == Qt.ToolTipRole:
			return 'Created: ' + chatThread.createdTimestamp.strftime("%Y-%m-%d %H:%M:%S")
		return None


	def setData(self, index, value, role = Qt.EditRole):
		if role == Qt.EditRole:
			chatThread = self.chatThreads[index.row()]
			#chatThread.setTitle(value)
			self.dataChanged.emit(index, index, [role])
			return True
		return False


	def populateList(self, chatThreads: Collection[ChatThread]):
		self.chatThreads = sorted(chatThreads, key = lambda each: each.createdTimestamp, reverse = True)
		self.layoutChanged.emit()


	def addItem(self, chatThread: ChatThread):
		self.chatThreads.insert(0, chatThread)
		self.layoutChanged.emit()


	def deleteItem(self, index: QModelIndex):
		del self.chatThreads[index.row()]
		self.layoutChanged.emit()




class ChatThreadItemDelegate(QStyledItemDelegate):

	def __init__(self, parent = None):
		super(ChatThreadItemDelegate, self).__init__(parent)


	def createEditor(self, parent, option, index):
		editor = QLineEdit(parent)
		editor.editingFinished.connect(self.commitAndCloseEditor)
		return editor


	def setEditorData(self, editor: QLineEdit, index):
		# Set the current text of the editor to the existing data
		editor.setText(index.model().data(index, Qt.DisplayRole))


	def setModelData(self, editor: QLineEdit, model, index):
		# Update the model data when editing is finished
		model.setData(index, editor.text())


	def commitAndCloseEditor(self):
		editor = self.sender()
		self.commitData.emit(editor)
		self.closeEditor.emit(editor, QAbstractItemDelegate.NoHint)