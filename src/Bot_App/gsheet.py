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

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

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
        logging.info(f"Worksheet title: {worksheet.title}")
        return worksheet
    except Exception as e:
        logging.error(f"An error occurred: {e}")

def format_data(pair):
    """
    Formats a pair of open and close orders into a row for Google Sheets.
    
    Args:
        pair (dict): A dictionary with 'open' and 'close' order objects.
        
    Returns:
        list: [symbol, expiration, contract, open price, max close price]
    """
    try:
        open_order = pair["open"]
        close_order = pair["close"]

        open_leg = open_order["orderLegCollection"][0]
        close_leg = close_order["orderLegCollection"][0]
        instrument = open_leg["instrument"]

        symbol = instrument["underlyingSymbol"]
        exp_raw = instrument["symbol"].split()[1]  # e.g., 250425
        formatted_exp = f"{exp_raw[2:4]}/{exp_raw[4:6]}/20{exp_raw[0:2]}"
        strike = instrument["symbol"][-8:-3].lstrip("0")
        put_call = instrument["putCall"]
        contract = f"{strike} {put_call}"

        # Entry (open) price
        entry_price = next(
            (leg["price"]
             for act in open_order.get("orderActivityCollection", [])
             for leg in act.get("executionLegs", [])),
            None
        )

        # Max exit price
        max_exit_price = max([
            leg["price"]
            for act in close_order.get("orderActivityCollection", [])
            for leg in act.get("executionLegs", [])
        ])

        return [
            symbol,
            formatted_exp,
            contract,
            round(entry_price, 2) if entry_price is not None else "",
            round(max_exit_price, 2)
        ]

    except Exception as e:
        logging.error(f"An error occurred in format_data: {e}")
        return ["ERROR", "", "", "", ""]


def pair_orders(orders):
    """
    Pairs open and close orders by instrumentId.

    Args:
        orders (list): List of order dictionaries.

    Returns:
        list of dicts: Each dict contains both open and close info.
    """
    from collections import defaultdict

    pairs = []
    grouped = defaultdict(dict)  # {instrumentId: {"open": order, "close": order}}

    for order in orders:
        try:
            leg = order["orderLegCollection"][0]
            instrument_id = leg["instrument"]["instrumentId"]
            instruction = leg["instruction"]

            if instruction == "BUY_TO_OPEN":
                grouped[instrument_id]["open"] = order
            elif instruction == "SELL_TO_CLOSE":
                # Only keep the highest close if multiple
                current_close = grouped[instrument_id].get("close")
                new_price = max([
                    exec_leg["price"]
                    for act in order.get("orderActivityCollection", [])
                    for exec_leg in act.get("executionLegs", [])
                ])

                if not current_close:
                    grouped[instrument_id]["close"] = order
                else:
                    existing_price = max([
                        exec_leg["price"]
                        for act in current_close.get("orderActivityCollection", [])
                        for exec_leg in act.get("executionLegs", [])
                    ])
                    if new_price > existing_price:
                        grouped[instrument_id]["close"] = order

        except Exception as e:
            logging.error(f"Error in pairing logic: {e}")

    # Filter for complete pairs
    for instrument_id, orders in grouped.items():
        if "open" in orders and "close" in orders:
            pairs.append(orders)

    return pairs


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
