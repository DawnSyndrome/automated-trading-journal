import unittest
from unittest.mock import patch, mock_open
from src.config.config_loader import ConfigLoader, TOMLConfigLoader, INIConfigLoader

class TestConfigLoader(unittest.TestCase):

    @patch("src.config.config_loader.load_dotenv", return_value=True)
    def test_load_dotenv_success(self, mock_load_dotenv):
        loader = ConfigLoader("test.env")
        mock_load_dotenv.assert_called_once_with("test.env")

    @patch("src.config.config_loader.load_dotenv", return_value=False)
    def test_load_dotenv_failure(self, mock_load_dotenv):
        with self.assertRaises(Exception):
            ConfigLoader("invalid.env")

class TestTOMLConfigLoader(unittest.TestCase):

    def setUp(self):
        self.patcher = patch("src.config.config_loader.load_dotenv", return_value=True)
        self.mock_load_dotenv = self.patcher.start()
        self.addCleanup(self.patcher.stop) # to ensure patch is cleaned up after each test

    @patch("builtins.open", new_callable=mock_open, read_data=b'[section]\nname="value"')
    def test_load_configuration_success(self, mock_open):
        loader = TOMLConfigLoader("test.env", "test.toml")
        self.assertEqual(loader.params, {"section": {"name": "value"}})

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_load_configuration_file_not_found(self, mock_open):
        with self.assertRaises(FileNotFoundError):
            TOMLConfigLoader("test.env", "missing.toml")

    @patch("builtins.open", new_callable=mock_open, read_data=b'[section]\nname="value"')
    def test_get_value(self, mock_open):
        loader = TOMLConfigLoader("test.env", "test.toml")
        self.assertEqual(loader.get_value("section", "name"), "value")
        self.assertEqual(loader.get_value("section", "missing"), {})

"""
# TODO update if we are to use INI again
class TestINIConfigLoader(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open, read_data="[section]\nname=value\n")
    @patch("src.config.config_loader.ConfigParser.read", return_value=["test.ini"])
    def test_load_configuration_success(self, mock_read, mock_open):
        # Should correctly parse a valid INI file
        loader = INIConfigLoader("test.env", "test.ini")
        self.assertTrue(mock_read.called)
        self.assertEqual(loader.params.get("section", "name"), "value")

    @patch("builtins.open", side_effect=FileNotFoundError) 
    def test_load_configuration_file_not_found(self, mock_open):
        # Should raise a FileNotFoundError for missing INI file
        with self.assertRaises(FileNotFoundError):
            INIConfigLoader("test.env", "missing.ini")

    @patch("builtins.open", new_callable=mock_open, read_data="[section]\nname=value\n")
    @patch("src.config.config_loader.ConfigParser.read", return_value=["test.ini"])
    def test_get_value(self, mock_read, mock_open):
        # Should correctly retrieve a value from the loaded INI file
        loader = INIConfigLoader("test.env", "test.ini")
        self.assertEqual(loader.get_value("section", "name"), "value")
        self.assertIsNone(loader.get_value("section", "missing"))"""
