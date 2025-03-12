#function for processing and cleaning Schwab data

import pandas as pd
import logging
from . import util
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Union

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

@dataclass
class trade:
    """A recursive dataclass that dynamically stores and converts nested dictionaries."""
    __annotations__ = {}  # Allows dynamic attributes
    data: Dict[str, Any] = field(default_factory=dict, repr=False)  # Internal raw storage

    def __init__(self, data: Dict[str, Any]):
        self.data = data  # Store raw data for reference
        
        for key, value in data.items():
            if isinstance(value, dict):
                # Recursively convert dictionary to trade object
                setattr(self, key, trade(value))
            elif isinstance(value, list) and all(isinstance(i, dict) for i in value):
                # Convert list of dictionaries to list of trade objects
                setattr(self, key, [trade(item) for item in value])
            else:
                setattr(self, key, value)  # Directly store primitive values

    def to_dict(self) -> Dict[str, Any]:
        """Recursively converts trade object back into a dictionary."""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, trade):
                result[key] = value.to_dict()  # Convert nested trade objects
            elif isinstance(value, list) and all(isinstance(i, trade) for i in value):
                result[key] = [i.to_dict() for i in value]  # Convert list of objects
            else:
                result[key] = value  # Store primitive values
        return result

def get_value_from_data(data, target_key):
    """
    Recursively searches through a nested dictionary or list to find the value
    associated with the given key.

    :param data: The data to search (dict or list)
    :param target_key: The key to search for
    :return: The value associated with the target_key, or None if not found
    """
    try:
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
        return "N/A"
    except Exception as e:
        logging.error(f"Error in get_value_from_data: {e}")
        return "N/A"

def parse_option_description(description, position):
    try:
        # Regex to capture parts of the string
        pattern = r"^(.*?) (\d{2}/\d{2}/\d{4}) \$(\d+\.?\d*) (Call|Put)$"
        match = re.match(pattern, description)

        if match:
            return match.group(position)

        else:
            raise ValueError("Description format is invalid")

    except Exception as e:
        logging.error(f"Error in parse_option_description: {e}")
        return "N/A"
    
