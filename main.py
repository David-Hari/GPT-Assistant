import asyncio
import logging
import signal
import sys
from pathlib import Path

from PySide6.QtCore import qInstallMessageHandler, QtMsgType
from omegaconf import OmegaConf
import PySide6.QtAsyncio as QtAsyncio
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
qInstallMessageHandler(lambda msgType, context, message: logger.log(logLevelMapping.get(msgType, logging.INFO), f"Qt: {message}"))


# These need to be imported after the logger is initialized
from core.Database import Database
from core.GPTAssistant import GPTAssistant
from windows.MainWindow import MainWindow


logger.debug('Starting application')
app = QApplication(sys.argv)
app.setApplicationName('AI Assistant')

dbPath = Path("data/chats.db")
database = Database(dbPath, not dbPath.exists())

# TODO: AsyncOpenAI()
api = OpenAI()
#from MockAPI import MockOpenAI
#api = MockOpenAI()
chatClient = GPTAssistant(api, database)

logger.debug('Opening window')
window = MainWindow(chatClient)
window.show()

signal.signal(signal.SIGINT, signal.SIG_DFL)

chatClient.startUp()
QtAsyncio.run()