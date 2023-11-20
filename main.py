import asyncio
import signal
import sys
from pathlib import Path

from omegaconf import OmegaConf
from PySide6.QtAsyncio import QAsyncioEventLoopPolicy
from PySide6.QtWidgets import QApplication
from openai import OpenAI

from core.GPTClient import GPTClient
from windows.MainWindow import MainWindow


config = OmegaConf.load('config.yaml')

app = QApplication(sys.argv)

# TODO: AsyncOpenAI()
chatClient = GPTClient(OpenAI(), config.model, Path('data/chats'), Path('data/system'))

window = MainWindow(chatClient)
window.show()

signal.signal(signal.SIGINT, signal.SIG_DFL)

asyncio.set_event_loop_policy(QAsyncioEventLoopPolicy())
#asyncio.ensure_future(chatClient.loadChatThreadList())
chatClient.loadChatThreadList()
asyncio.get_event_loop().run_forever()