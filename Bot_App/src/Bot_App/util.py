
import os
import sys
from dotenv import load_dotenv
import logging

def get_secret(key, FILE_PATH=""):
    try:
        load_dotenv(FILE_PATH)
        value = os.getenv(key)
        if value == None:
            #throw error if key not found
            raise Exception ("Key not found / is None")
        return os.getenv(key)
    except Exception as e:
        logging.error(f"Error getting secret from {FILE_PATH}: {e}")
        return None