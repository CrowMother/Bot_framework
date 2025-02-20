
import os
import sys
from dotenv import load_dotenv
import logging
from datetime import datetime, timezone, timedelta
import re

def get_secret(key, FILE_PATH=""):
    try:
        load_dotenv(FILE_PATH)
        value = os.getenv(key)
        if value == None:
            #throw error if key not found
            raise Exception ("Key not found / is None")
        return value
    except Exception as e:
        logging.error(f"Error getting secret from {FILE_PATH}: {e}")
        return None
    


def get_end_time(delta=1):
    to_date = datetime.now(timezone.utc)
    from_date = to_date - timedelta(hours=delta)
    
    # Format dates as ISO 8601 strings with milliseconds and timezone
    return from_date.strftime('%Y-%m-%dT%H:%M:%S.000Z')
     
def get_start_time(delta=1):
    to_date = datetime.now(timezone.utc)
    # Format dates as ISO 8601 strings with milliseconds and timezone
    return to_date.strftime('%Y-%m-%dT%H:%M:%S.000Z')

def get_current_time():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')
            
def check_time_of_week(day, hour, minute):
    """
    Checks if the current time matches the given day, hour, and minute of the week.

    Args:
        day: int (0-6) representing day of the week (0=Monday, 1=Tuesday, etc)
        hour: int (0-23) representing hour of the day
        minute: int (0-59) representing minute of the day

    Returns:
        bool: True if the current time matches, False otherwise
    """
    now = datetime.datetime.now()
    if now.weekday() == day and now.hour == hour and now.minute == minute:
        return True
    else:
        return False