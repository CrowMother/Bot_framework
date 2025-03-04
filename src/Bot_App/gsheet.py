import re
import logging
import datetime

import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import logging
import os

SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']


# Look into refactoring this into a class for better encapsulation

def insert_data(worksheet, location, data):
    """
    Inserts data into a Google Sheet at the specified location.

    Args:
        worksheet (gspread.Worksheet): The worksheet to update.
        location (str): The location to update (e.g. "A17").
        data (list of lists): 2D array of data to insert into the worksheet.
    """
    try:
        logging.info("Attempting to update Google Sheet")
        worksheet.update(location, data)
        logging.info("Google Sheet updated successfully")
    except gspread.exceptions.APIError as e:
        logging.error(f"API error occurred: {e.response.text}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

def get_next_empty_row(worksheet, column):
    """
    Gets the index of the next empty row in the specified column of the given worksheet.

    Args:
        worksheet (gspread.Worksheet): The worksheet to search.
        column (int): The column to search.

    Returns:
        int: The index of the next empty row in the column, or None if an error occurred.
    """
    try:
        # Fetch all values in the specified column
        values = worksheet.col_values(column)
        logging.info(f"Values in column {column}: {values}")

        # Find the index of the first empty cell in the column
        empty_index = len(values) + 1
        logging.info(f"Next empty row in column {column}: {empty_index}")
        return empty_index
    except Exception as e:
        logging.error(f"An error occurred while getting the next empty row: {e}")
        return None
    
def get_all_records(worksheet):
    """
    Fetches all records from a Google Sheet worksheet and returns them as a Pandas DataFrame

    Args:
        worksheet (gspread.Worksheet): The worksheet to fetch records from

    Returns:
        pd.DataFrame: The fetched records as a Pandas DataFrame

    Raises:
        gspread.exceptions.APIError: If an error occurs while communicating with the Google Sheets API
        Exception: If any other error occurs
    """

    try:
        # Fetch the header row
        logging.info("Fetching header row from Google Sheet")
        headers = worksheet.row_values(1)
        logging.info(f"Headers: {headers}")

        # Fetch data into a Pandas DataFrame
        logging.info("Fetching data from Google Sheet")
        data = worksheet.get_all_records(expected_headers=headers)
        df = pd.DataFrame(data)
        logging.info(f"Data fetched:\n{df}")
        return df
    except gspread.exceptions.APIError as e:
        logging.error(f"API error occurred: {e.response.text}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

def connect_gsheets_account(file_path):
    """
    Authenticate with Google Sheets API using a service account key file.

    Parameters
    ----------
    file_path : str
        The path to the service account key file.

    Returns
    -------
    client : gspread.Client
        The authenticated client that can be used to access Google Sheets.

    Raises
    ------
    Exception
        If any error occurs during authentication.
    """
    try:
        # Authenticate using the service account key file
        logging.info("Authenticating with Google Sheets API")
        credentials = Credentials.from_service_account_file(
            file_path, scopes=SCOPES)
        client = gspread.authorize(credentials)
        return client
    except Exception as e:
        logging.error(f"An error occurred: {e}")

def copy_headers(worksheet, location):
    # Use the inbuilt gsheet function to set the value at a given row and column to the headers
    # Example A17 [=A1, =B1, ...]
    """
    Copies the headers from the first row to a given location in the Google Sheet.

    Args:
        worksheet (gspread.Worksheet): The worksheet to copy the headers to.
        location (str): The location to copy the headers to (e.g. "A17").
    """
    try:
        worksheet.update(
        location,
        [
            ['=A1', '=B1', '=C1', '=D1', '=E1', '=F1', '=G1', '=H1', '=I1', '=J1']
        ],
        value_input_option='USER_ENTERED'
    )
    except gspread.exceptions.APIError as e:
        logging.error(f"API error occurred: {e.response.text}")

def connect_to_sheet(client, spreadsheet_name, worksheet_name):
    """
    Connects to a specific worksheet within a Google Spreadsheet.

    Args:
        client (gspread.Client): An authenticated gspread client.
        spreadsheet_name (str): The name of the Google Spreadsheet.
        worksheet_name (str): The name of the worksheet within the spreadsheet.

    Returns:
        gspread.Worksheet: The worksheet object for the specified sheet.

    Raises:
        Exception: If an error occurs while opening the spreadsheet or worksheet.
    """

    try:
        # Open the Google Sheet
        logging.info("Opening Google Sheet")
        spreadsheet = client.open(spreadsheet_name)
        worksheet = spreadsheet.worksheet(worksheet_name)
        return worksheet
    except Exception as e:
        logging.error(f"An error occurred: {e}")

def format_data(order):
    """
    Formats order data into a list of strings suitable for insertion into a Google Sheet.

    Args:
        order (dict): A dictionary containing order details, including keys 'symbol',
                      'date', 'strike', 'putCall', 'open_price', and 'price'.

    Returns:
        list: A list of strings representing the formatted order data.

    Raises:
        Exception: If an error occurs during the formatting process, it logs the error.
    """

    try:
        row_data = [
                str(order['symbol']),
                str(order['date']),
                str(f"{order['strike']} {order['putCall']}"),
                str(order['open_price']),
                str(order['price']),
            ]
        return row_data
    except Exception as e:
        logging.error(f"An error occurred in format_data: {e}")



def write_row_at_next_empty_row(worksheet, row_data):
    """
    Writes a row of data to the next empty row in the Google Sheet.

    Args:
        worksheet (gspread.Worksheet): The worksheet to write the data to.
        row_data (list): The data to write to the next empty row.

    Returns:
        None

    Raises:
        Exception: If an error occurs while writing the data.
    """
    try:
        row = get_next_empty_row(worksheet, 2)
        row = f"B{row}"
        insert_data(worksheet, row, [row_data])
    except Exception as e:
        logging.error(f"An error occurred writing row_data to Google Sheet: {e}")
    
def create_id(order):
    """
    Creates a unique ID for an order from execution time and instrument ID.
    """
    id = f"{order['open_price']}-{order['price']}-{order['instrumentId']}"
    return id