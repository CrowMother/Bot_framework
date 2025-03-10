
import os
import sys
from dotenv import load_dotenv
import logging
from datetime import datetime, timezone, timedelta
import re

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
            raise Exception ("Key not found / is None")
        return value
    except Exception as e:
        logging.error(f"Error getting secret from {FILE_PATH}: {e}")
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