import unittest
from unittest.mock import patch, MagicMock
import os
import logging
from datetime import datetime, timedelta

# Import the function to test
from Bot_App.util import check_file_changed  # Replace 'your_module' with the actual module name

class TestCheckFileChanged(unittest.TestCase):

    @patch("os.stat")
    def test_file_modified(self, mock_stat):
        """Test when file has been modified after last_modified timestamp"""
        mock_stat.return_value.st_mtime = (datetime.now() - timedelta(minutes=5)).timestamp()
        last_modified = (datetime.now() - timedelta(minutes=10)).timestamp()

        result = check_file_changed("dummy_path.txt", last_modified)
        self.assertTrue(result)

    @patch("os.stat")
    def test_file_not_modified(self, mock_stat):
        """Test when file has not been modified since last_modified timestamp"""
        mock_stat.return_value.st_mtime = (datetime.now() - timedelta(minutes=15)).timestamp()
        last_modified = (datetime.now() - timedelta(minutes=10)).timestamp()

        result = check_file_changed("dummy_path.txt", last_modified)
        self.assertFalse(result)

    @patch("os.stat")
    def test_file_checked_first_time(self, mock_stat):
        """Test when last_modified is None (should always return True)"""
        mock_stat.return_value.st_mtime = datetime.now().timestamp()

        result = check_file_changed("dummy_path.txt", None)
        self.assertTrue(result)

    @patch("os.stat")
    def test_file_does_not_exist(self, mock_stat):
        """Test when the file does not exist or raises an error"""
        mock_stat.side_effect = FileNotFoundError

        with self.assertLogs(level="ERROR") as log:
            result = check_file_changed("non_existent.txt", None)
            self.assertFalse(result)
            self.assertIn("Error checking file non_existent.txt", log.output[0])

if __name__ == "__main__":
    unittest.main()
