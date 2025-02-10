#function for processing and cleaning Schwab data

import pandas as pd
import logging
from . import util
import re

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def get_value_from_data(data, target_key):
    """
    Recursively searches through a nested dictionary or list to find the value
    associated with the given key.

    :param data: The data to search (dict or list)
    :param target_key: The key to search for
    :return: The value associated with the target_key, or None if not found
    """
    if isinstance(data, dict):
        for key, value in data.items():
            if key == target_key:
                return value
            if isinstance(value, (dict, list)):
                result = get_value_from_data(value, target_key)
                if result is not None:
                    return result
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                result = get_value_from_data(item, target_key)
                if result is not None:
                    return result
    return None

def parse_option_description(description, position):
    # Regex to capture parts of the string
    pattern = r"^(.*?) (\d{2}/\d{2}/\d{4}) \$(\d+\.?\d*) (Call|Put)$"
    match = re.match(pattern, description)

    if match:
        return match.group(position)

    else:
        raise ValueError("Description format is invalid")
    
