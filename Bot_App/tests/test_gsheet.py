from unittest.mock import MagicMock

from Bot_App.services.gsheet import insert_data


def test_insert_data_calls_insert_row():
    sheet = MagicMock()
    insert_data(sheet, 2, ["a", "b"])
    sheet.insert_row.assert_called_once_with(["a", "b"], 2)
