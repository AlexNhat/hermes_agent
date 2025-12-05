
import os
import logging


def set_logger():

    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)   # create once, no drama

    log_path = os.path.join(log_dir, "hermes_app.log")

    logger = logging.getLogger("hermes_logger")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        console_handler = logging.StreamHandler()

        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger