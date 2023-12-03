from typing import Collection

from PySide6.QtCore import Qt, QAbstractListModel, QModelIndex, Signal
from PySide6.QtWidgets import QStyledItemDelegate, QLineEdit

from data.ChatThread import ChatThread



class ChatThreadListModel(QAbstractListModel):
	titleEdited = Signal(str, str)

	def __init__(self, parent = None):
		super(ChatThreadListModel, self).__init__(parent)
		self.chatThreads: list[ChatThread] = []


	def rowCount(self, parent = QModelIndex()):
		return len(self.chatThreads)


	def flags(self, index: QModelIndex):
		return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemNeverHasChildren


	def data(self, index, role = Qt.DisplayRole):
		chatThread = self.chatThreads[index.row()]
		if role == Qt.UserRole:
			return chatThread.id
		if role == Qt.DisplayRole or role == Qt.EditRole:
			return chatThread.title
		if role == Qt.ToolTipRole:
			return 'Created: ' + chatThread.createdTimestamp.strftime("%Y-%m-%d %H:%M:%S")
		return None


	def setData(self, index, value, role = Qt.EditRole):
		if role == Qt.EditRole:
			chatThread = self.chatThreads[index.row()]
			if chatThread and chatThread.title != value:
				chatThread.title = value
				self.dataChanged.emit(index, index, [role])
				self.titleEdited.emit(chatThread.id, chatThread.title)
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
		return QLineEdit(parent)


	def setEditorData(self, editor: QLineEdit, index: QModelIndex):
		""" Set the current text of the editor to the existing data """
		editor.setText(index.data(Qt.DisplayRole))


	def setModelData(self, editor: QLineEdit, model, index):
		""" Update the model data when editing is finished """
		model.setData(index, editor.text(), Qt.EditRole)