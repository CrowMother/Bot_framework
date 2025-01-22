
import os
import sys
from dotenv import load_dotenv
import logging
from datetime import datetime, timezone, timedelta

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