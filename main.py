import asyncio
import signal
import sys
from pathlib import Path

from omegaconf import OmegaConf
from PySide6.QtAsyncio import QAsyncioEventLoopPolicy
from PySide6.QtWidgets import QApplication
from openai import OpenAI

from utils import setupLogger


defaultConf = {
	'logLevel': 'INFO',
	'logOutput': 'console'
}
config = OmegaConf.merge(defaultConf, OmegaConf.load('config.yaml'))

setupLogger(config)

# These need to be imported after the logger is initialized
from utils import logger
from core.Database import Database
from core.GPTClient import GPTClient
from windows.MainWindow import MainWindow


logger.debug('Starting application')
app = QApplication(sys.argv)

dbPath = Path("data/chats.db")
database = Database(dbPath, not dbPath.exists())

# TODO: AsyncOpenAI()
chatClient = GPTClient(OpenAI(), config.model, database)

logger.debug('Opening window')
window = MainWindow(chatClient)
window.show()

signal.signal(signal.SIGINT, signal.SIG_DFL)

asyncio.set_event_loop_policy(QAsyncioEventLoopPolicy())
#asyncio.ensure_future(chatClient.loadChatThreadList())
chatClient.loadChatThreadList()
asyncio.get_event_loop().run_forever()