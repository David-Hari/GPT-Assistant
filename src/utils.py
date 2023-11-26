import logging


logger = logging.getLogger('app')
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
#handler = logging.FileHandler(log_file)

handler.setLevel(logging.DEBUG)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
logger.addHandler(handler)
