import asyncio
import logging
import signal
import sys
from pathlib import Path

from PySide6.QtCore import qInstallMessageHandler, QtMsgType
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
from utils import logger

logLevelMapping = {
	QtMsgType.QtCriticalMsg: logging.CRITICAL,
	QtMsgType.QtFatalMsg:    logging.FATAL,
	QtMsgType.QtWarningMsg:  logging.WARNING,
	QtMsgType.QtInfoMsg:     logging.INFO,
	QtMsgType.QtDebugMsg:    logging.DEBUG,
}
def customMessageHandler(msgType, context, message):
	logger.log(logLevelMapping.get(msgType, logging.INFO), f"Qt: {message}")

qInstallMessageHandler(customMessageHandler)


# These need to be imported after the logger is initialized
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
# TODO: Maybe this should be signalled from MainWindow
#asyncio.ensure_future(chatClient.loadChatThreadList())
chatClient.loadChatThreadList()
asyncio.get_event_loop().run_forever()