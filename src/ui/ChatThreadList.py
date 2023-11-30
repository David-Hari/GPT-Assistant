from typing import Collection

from PySide6.QtCore import Qt, QAbstractListModel, QModelIndex, QEvent, QSize, QRect
from PySide6.QtWidgets import QStyledItemDelegate, QLineEdit, QStyleOptionButton, QStyle, QApplication

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
		if role == Qt.DisplayRole:
			return chatThread.title
		if role == Qt.UserRole:
			return chatThread.id
		return None


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
		# Create a custom editor widget (in this case, a QLineEdit)
		editor = QLineEdit(parent)
		return editor


	def setEditorData(self, editor, index):
		# Set data to the editor widget based on the model index
		text = index.data(Qt.DisplayRole)
		editor.setText(text)


	def setModelData(self, editor, model, index):
		# Set data back to the model when editing is finished
		model.setData(index, editor.text(), Qt.DisplayRole)


	def updateEditorGeometry(self, editor, option, index):
		# Update the geometry of the editor widget
		editor.setGeometry(option.rect)


	def editorEvent(self, event, model, option, index):
		# Decide if the mouse event is on your button, and call delete if it is
		if event.type() == QEvent.MouseButtonRelease:
			return True
			# Check if the click is on the button's rect and perform action
			#if button_rect.contains(event.pos()):
				#self.parent().deleteChatThread(index.row())  # Call the delete slot on MainWindow
		return False


	def paint(self, painter, option, index):
		super(ChatThreadItemDelegate, self).paint(painter, option, index)

		#editButtonOption = QStyleOptionButton()
		#editButtonOption.state = QStyle.State_Enabled
		#editButtonOption.text = 'E'
		#editButtonOption.rect = buttonRect(option.rect, 1)

		# Draw the button using the current style
		#QApplication.style().drawControl(QStyle.CE_PushButton, editButtonOption, painter)

		deleteButtonOption = QStyleOptionButton()
		deleteButtonOption.state = QStyle.State_Enabled
		deleteButtonOption.text = 'X'
		deleteButtonOption.rect = buttonRect(option.rect, 0)

		# Draw the button using the current style
		QApplication.style().drawControl(QStyle.CE_PushButton, deleteButtonOption, painter)



def buttonRect(parentRect, position):
	"""
	Helper method to define the button rect. Align to the right, vertically centered.
	:param parentRect: Rectangle of the parent item
	:param position: Numeric position from right side (i.e. 0 = farthest to the right)
	"""
	buttonSize = QSize(16, 16)
	spacing = 4
	x = parentRect.right() - ((position + 1) * (buttonSize.width() + spacing))
	y = parentRect.center().y() - buttonSize.height() / 2
	return QRect(x, y, buttonSize.width(), buttonSize.height())