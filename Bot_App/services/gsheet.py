"""Utilities for interacting with Google Sheets."""

from typing import Sequence


def insert_data(sheet, row: int, values: Sequence):
    """Insert values into a worksheet at the given row.

    Parameters
    ----------
    sheet : Any
        Worksheet-like object with an ``insert_row`` method.
    row : int
        Target row index starting at 1.
    values : Sequence
        Data to insert in the row.
    """
    if sheet is None:
        raise ValueError("sheet cannot be None")
    if row < 1:
        raise ValueError("row must be >= 1")

    sheet.insert_row(list(values), row)
