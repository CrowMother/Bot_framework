
import os
import sys
from dotenv import load_dotenv
import logging
from datetime import datetime, timezone, timedelta
import re
from typing import List, Dict, Any
import time
import requests
import hashlib
import json
import sqlite3

# example usage:
# logger = setup_logging(level=logging.DEBUG, name=__name__)
# setup the function calls in other files
def setup_logging(level=logging.INFO, name=None):
    """
    Sets up logging with a given level and optional logger name.

    Parameters:
    - level: logging level (e.g., logging.DEBUG, logging.INFO)
    - name: logger name (if None, uses root logger)
    """
    logger = logging.getLogger(name)

    # Prevent duplicate handlers if already configured
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(level)
    return logger

def generate_order_id(order):
    entered_time = order.get('enteredTime', '')
    # Safely extract instruction from first leg
    instruction = ''
    symbol = ''

    if 'orderLegCollection' in order and len(order['orderLegCollection']) > 0:
        first_leg = order['orderLegCollection'][0]
        instruction = first_leg.get('instruction', '')
        symbol = first_leg.get('instrument', {}).get('symbol', '')

    unique_string = f"{entered_time}_{instruction}_{symbol}"
    return hashlib.sha256(unique_string.encode()).hexdigest()


def retry_request(request_func, retries=3, delay=5, backoff=2, retry_on=(requests.exceptions.RequestException,), raise_on_fail=False):
    for attempt in range(1, retries + 1):
        try:
            return request_func()
        except retry_on as e:
            logging.warning(f"[Attempt {attempt}] Request failed: {e}. Retrying in {delay}s...")
            time.sleep(delay)
            delay *= backoff

    logging.error("All retry attempts failed.")
    if raise_on_fail:
        raise e  # re-raise the last exception
    return None



def get_secret(key, FILE_PATH="", default=None):
    """
    Retrieves the value of a specified environment variable from a .env file.

    Args:
        key (str): The name of the environment variable to retrieve.
        FILE_PATH (str, optional): The file path to the .env file. Defaults to an empty string.

    Returns:
        str or None: The value of the environment variable if found, otherwise None.

    Raises:
        Exception: If the key is not found or its value is None.
    """

    try:
        load_dotenv(FILE_PATH)
        value = os.getenv(key)
        if value == None:
            #throw error if key not found
            logging.debug(f"Key {key} not found / is None")
        return value
    except Exception as e:
        logging.error(f"Get_secret() Error getting secret from {FILE_PATH}: {key}: {e}")
        return default
    


def get_end_time(delta=1):
    """
    Returns the current time minus the given delta hours as a string in ISO 8601 format with milliseconds and timezone.

    Args:
        delta: int, optional
            The number of hours to subtract from the current time. Defaults to 1.

    Returns:
        str
            The current time minus delta hours as an ISO 8601 string.
    """
    
    to_date = datetime.now(timezone.utc)
    from_date = to_date - timedelta(hours=delta)
    
    # Format dates as ISO 8601 strings with milliseconds and timezone
    return from_date.strftime('%Y-%m-%dT%H:%M:%S.000Z')
     
def get_start_time(delta=1):
    """
    Returns the current time as a string in ISO 8601 format with milliseconds and timezone,
    adjusted by the given delta hours.

    Args:
        delta: int, optional
            The number of hours to subtract from the current time. Defaults to 1.

    Returns:
        str
            The current time minus delta hours as an ISO 8601 string.
    """
    to_date = datetime.now(timezone.utc)
    # Format dates as ISO 8601 strings with milliseconds and timezone
    return to_date.strftime('%Y-%m-%dT%H:%M:%S.000Z')

def get_current_time():
    """
    Returns the current time as a string in ISO 8601 format with milliseconds and timezone.

    Returns:
        str
            The current time as an ISO 8601 string.
    """
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')
            
def check_time_of_week(day, hour):
    """
    Checks if the current time matches the given day and hour of the week.

    Args:
        day: int (0-6) representing day of the week (0=Monday, 1=Tuesday, etc)
        hour: int (0-23) representing hour of the day
        
    Returns:
        bool: True if the current time matches, False otherwise
    """
    now = datetime.now()
    logging.debug(f"Current time: {now.weekday()} {now.hour} vs {day} {hour}")
    if now.weekday() == day and now.hour == hour:
        return True
    else:
        return False
    

def get_monday_of_current_week():
    """
    Returns the date of Monday of the current week.

    Returns:
        str: The date of Monday of the current week in the format M/D/YY.
    """
    today = datetime.now().date()
    monday = today - timedelta(days=today.weekday())
    return monday.strftime('%m/%d/%y')

def check_time_of_day(hour, minute=0):
    """
    Checks if the current time matches the given hour and minute.

    Args:
        hour: int (0-23) representing hour of the day
        minute: int (0-59), optional
        
    Returns:
        bool: True if the current time matches, False otherwise
    """
    now = datetime.now()
    logging.debug(f"Current time: {now.hour} {now.minute} vs {hour} {minute}")
    if now.hour == hour and now.minute == minute:
        return True
    else:    
        return False
    

def check_file_changed(file_path, last_modified=None):
    """Return ``True`` if ``file_path`` was modified after ``last_modified``.

    If ``last_modified`` is ``None`` the function always returns ``True``. Any
    exception while obtaining the modification time is logged and ``False`` is
    returned.
    """
    try:
        mtime = get_file_last_modified(file_path)
        if mtime is None:
            logging.error(f"Error checking file {file_path}")
            return False
        if last_modified is None or mtime > last_modified:
            return True
        return False
    except Exception as e:  # pragma: no cover - defensive
        logging.error(f"Error checking file {file_path}: {e}")
        return False

def get_file_last_modified(file_path):
    """
    Returns the last modified time of the file.

    Args:
        file_path: str, the path to the file to check.

    Returns:
        datetime, the last modified time of the file.
    """
    try:
        stat = os.stat(file_path)
        return stat.st_mtime
    except Exception:
        # Caller will handle logging to avoid duplicate log entries during tests
        return None

def flatten_dict(d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

    

def str_to_bool(value):
    """
    Converts a value to a boolean based on its string representation.

    Args:
        value: The value to convert to a boolean.

    Returns:
        bool: True if the string representation of the value is "true" (case-insensitive),
              False otherwise.
    """
    return str(value).strip().lower() == "true"
