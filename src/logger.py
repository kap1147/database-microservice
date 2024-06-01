import logging
from pathlib import Path

def setup_logger(name, log_file, level=logging.INFO):
    logger = logging.getLogger(name)
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.touch(exist_ok=True)
    if logger.hasHandlers():
        # Logger already has handlers, no need to add another
        return logger

    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
