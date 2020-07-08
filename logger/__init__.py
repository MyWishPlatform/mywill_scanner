import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('logger/err.log')
fh.setLevel(logging.ERROR)

# ch = logging.StreamHandler()
# ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s: %(levelname)s: %(message)s')
fh.setFormatter(formatter)
# ch.setFormatter(formatter)

logger.addHandler(fh)
# logger.addHandler(ch)
