#function for processing and cleaning Schwab data

import pandas as pd
import logging
from . import util
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Union
import sqlite3
import json
from datetime import datetime

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

    if isinstance(data, dict):
        for key, value in data.items():
            if key == target_key:
                return value
            elif isinstance(value, (dict, list)):
                result = get_value_from_data(value, target_key)
                if result is not None:
                    return result
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                result = get_value_from_data(item, target_key)
                if result is not None:
                    return result

    # If we get here, not found:
    return None

def get_value_or_na(data, target_key):
    # Wrapper that returns 'N/A' if the recursion didn't find anything
    result = get_value_from_data(data, target_key)
    return result if result is not None else "N/A"


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
    

def store_orders(orders, db_path="orders.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
# make this more generic and lass hardcoded so it can be used for parsing open orders
    for order in orders:
        # Default values
        instruction = None
        position_effect = None
        symbol = None

        # Extract from orderLegCollection if available
        if 'orderLegCollection' in order and len(order['orderLegCollection']) > 0:
            first_leg = order['orderLegCollection'][0]
            instruction = first_leg.get('instruction', None)
            position_effect = first_leg.get('positionEffect', None)
            instrument = first_leg.get('instrument', {})
            symbol = instrument.get('symbol', None)
            description = instrument.get('description', None)

        order_id = util.generate_order_id(order)
        full_json = json.dumps(order)

        try:
            cursor.execute("""
                INSERT INTO schwab_orders (
                    id, entered_time, ticker, instruction, position_effect, 
                    order_status, quantity, tag, full_json, posted_to_discord, posted_at, description
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                order_id,
                order.get('enteredTime'),
                symbol,
                instruction,
                position_effect,
                order.get('status'),
                order.get('quantity'),
                order.get('tag'),
                full_json,
                0,  # posted_to_discord default
                None,  # posted_at default
                description
            ))
        except sqlite3.IntegrityError:
            pass  # Order already exists

    conn.commit()
    conn.close()

def get_unposted_orders(db_path="orders.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, full_json FROM schwab_orders
        WHERE posted_to_discord = FALSE
    """)

    orders = cursor.fetchall()
    conn.close()

    return orders


def mark_as_posted(order_id, db_path="orders.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE schwab_orders
        SET posted_to_discord = TRUE, posted_at = ?
        WHERE id = ?
    """, (datetime.utcnow().isoformat(), order_id))

    conn.commit()
    conn.close()