import logging
import os
from datetime import datetime
from pathlib import Path

from src.utils.file_vars import DEFAULT_LOGS_DIR


class Logger:
    _instance = None  # Singleton instance

    def __new__(cls, name="ApplicationLogger", default_log_level=logging.INFO):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialize(name, default_log_level)
        return cls._instance

    def _initialize(self, name, log_level):
        # initializes the logger only once
        self.logger = logging.getLogger(name)
        if not self.logger.hasHandlers():
            self.logger.setLevel(log_level)
            self.formatter = logging.Formatter(
                "%(asctime)s - %(name)s - [%(levelname)s] - (%(funcName)s): %(message)s"
            )
            self.__set_console_handler()

    def set_log_level(self, log_level):
        self.logger.setLevel(log_level)

    def __set_console_handler(self):
        # console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)

    def set_file_handler(self, log_to_file=False, log_dir=DEFAULT_LOGS_DIR):
        # file handler
        if log_to_file:
            Path(log_dir).mkdir(parents=True, exist_ok=True)
            log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log")
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(self.formatter)
            self.logger.addHandler(file_handler)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)