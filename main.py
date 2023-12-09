import asyncio
import logging
import signal
import sys
from pathlib import Path

from PySide6.QtCore import qInstallMessageHandler, QtMsgType
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from omegaconf import OmegaConf
from PySide6.QtAsyncio import QAsyncioEventLoopPolicy
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
qInstallMessageHandler(lambda msgType, context, message: logger.log(logLevelMapping.get(msgType, logging.INFO), f"Qt: {message}"))


# These need to be imported after the logger is initialized
from core.Database import Database
from core.GPTClient import GPTClient


logger.debug('Starting application')
app = QGuiApplication(sys.argv)
engine = QQmlApplicationEngine()

dbPath = Path("data/chats.db")
database = Database(dbPath, not dbPath.exists())

# TODO: AsyncOpenAI()
chatClient = GPTClient(OpenAI(), config.model, database)

logger.debug('Opening window')
engine.load("src\\ui\\MainWindow.qml")
if not engine.rootObjects():
	raise Exception("Unable to load main window")

signal.signal(signal.SIGINT, signal.SIG_DFL)

asyncio.set_event_loop_policy(QAsyncioEventLoopPolicy())
# TODO: Maybe this should be signalled from MainWindow
#asyncio.ensure_future(chatClient.loadChatThreadList())
chatClient.loadChatThreadList()
asyncio.get_event_loop().run_forever()