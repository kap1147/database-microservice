import logging

def setup_logger(name, log_file, level=logging.INFO):
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        # Logger already has handlers, no need to add another
        return logger

    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
