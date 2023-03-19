import unittest
import os
from unittest.mock import patch, mock_open


from poke_api import save_response, __name__ as module_name


class TestSaveResponse(unittest.TestCase):
    @patch(f"{module_name}.open", mock_open())
    @patch(f"{module_name}.json.dump")
    def test_save_response(self, mock_json_dump, mock_file_open):
        data = [1, 2, 3]
        file_name = "test_file.txt"
        directory_name = "test_dir"

        save_response(data, file_name, directory_name)

        # check that the file was opened and saved correctly
        filename = os.path.join(directory_name, file_name)
        mock_file_open.assert_called_with(filename, mode="w", encoding="utf-8")
        mock_json_dump.assert_called_with(data, mock_file_open())


if __name__ == "__main__":
    unittest.main()
