import logging

def get_logger(name: str, logfile: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger
