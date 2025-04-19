import unittest
import logging
from src.logging.logger import Logger

class TestLogger(unittest.TestCase):

    def setUp(self):
        self.logger = Logger(name="TestLogger")

    def test_singleton_instance(self):
        logger1 = Logger(name="Logger1")
        logger2 = Logger(name="Logger2")
        self.assertIs(logger1, logger2, "Logger should implement the singleton pattern.")

    def test_set_log_level(self):
        self.logger.set_log_level(logging.DEBUG)
        self.assertEqual(self.logger.logger.level, logging.DEBUG, "Log level should be DEBUG.")