import sys
from pathlib import Path

from omegaconf import OmegaConf
from PySide6.QtWidgets import QApplication
from openai import OpenAI

from core.GPTClient import GPTClient
from windows.MainWindow import MainWindow



config = OmegaConf.load('config.yaml')

app = QApplication(sys.argv)

chatClient = GPTClient(OpenAI(), config.model, Path('data/chats'), Path('data/system'))

window = MainWindow(chatClient)
window.show()

sys.exit(app.exec())