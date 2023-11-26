import logging
from typing import Optional


logger: Optional[logging.Logger] = None

def setupLogger(config):
	global logger
	logger = logging.getLogger('app')
	logger.setLevel(config.logLevel)

	if config.logOutput == 'console':
		handler = logging.StreamHandler()
	elif config.logOutput == 'file':
		handler = logging.FileHandler(config.logFilePath)
	else:
		raise Exception(f'Unknown log output: {config.logOutput}')

	handler.setLevel(logging.DEBUG)
	handler.setFormatter(logging.Formatter('%(asctime)s  %(levelname)s  %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
	logger.addHandler(handler)
