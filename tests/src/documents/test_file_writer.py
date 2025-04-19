import os
import unittest
from unittest.mock import patch, mock_open
from parameterized import parameterized
from src.file.file_writer import FileWriter

class TestFileWriter(unittest.TestCase):

    @parameterized.expand([
        ("valid_paths", "/valid/journal", "timeframe", "test.txt", "Test content", "w", True, True),
        ("different_mode", "/valid/journal", "timeframe", "test.txt", "Test content", "a", True, True),
        ("missing_journal_dir", "", "timeframe", "test.txt", "Test content", "w", ValueError, False),
        ("missing_timeframe_dir", "/valid/journal", "", "test.txt", "Test content", "w", ValueError, False),
        ("missing_file_name", "/valid/journal", "timeframe", "", "Test content", "w", ValueError, False),
        ("wrong_write_mode", "/valid/journal", "timeframe", "test.txt", "Test content", "z", ValueError, False),
        ("missing_content", "/valid/journal", "timeframe", "test.txt", "", "w", ValueError, False),
    ])
    @patch("os.path.isdir", return_value=True)
    @patch("os.makedirs")
    @patch("builtins.open", new_callable=mock_open)
    def test_file_writer(self, _, journal_dir, timeframe_dir, file_name, content, write_mode, expected_result,
                         is_valid, mock_open_fn, mock_makedirs, mock_isdir):
        if not is_valid:
            with self.assertRaises(expected_result):
                writer = FileWriter(journal_dir, timeframe_dir)
                writer.write_to_file(content, file_name, write_mode)
        else:
            writer = FileWriter(journal_dir, timeframe_dir)
            writer.write_to_file(content, file_name, write_mode)

            # dir and file handling validation
            mock_isdir.assert_any_call(journal_dir)
            mock_isdir.assert_any_call(os.path.join(journal_dir, timeframe_dir))
            mock_open_fn.assert_called_with(os.path.join(journal_dir, timeframe_dir, file_name), write_mode)

            mock_open_fn().write.assert_called_once_with(content)