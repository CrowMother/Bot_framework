import re
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def calculate_percentage_gain(open_price, close_price):
    try:
        if open_price is None or close_price is None:
            return None
        gain = ((close_price - open_price) / open_price) * 100
        return round(gain, 2)
    except ZeroDivisionError:
        return None

def get_value_from_data(data, target_key):
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
    return None

def get_value_or_na(data, target_key):
    result = get_value_from_data(data, target_key)
    return result if result is not None else "N/A"

def generate_order_id(order):
    from hashlib import sha256
    entered_time = order.get('enteredTime', '')
    instruction = ''
    symbol = ''

    if 'orderLegCollection' in order and len(order['orderLegCollection']) > 0:
        first_leg = order['orderLegCollection'][0]
        instruction = first_leg.get('instruction', '')
        symbol = first_leg.get('instrument', {}).get('symbol', '')

    raw = f"{entered_time}_{instruction}_{symbol}"
    return sha256(raw.encode()).hexdigest()

def parse_option_description(description, position):
    try:
        pattern = r"^(.*?) (\d{2}/\d{2}/\d{4}) \$(\d+\.?\d*) (Call|Put)$"
        match = re.match(pattern, description)
        if match:
            return match.group(position)
        else:
            raise ValueError("Invalid option description format.")
    except Exception as e:
        logging.error(f"parse_option_description error: {e}")
        return "N/A"

def find_matching_open_order(order, db_path="orders.db"):
    import sqlite3
    import json

    symbol = order.get("orderLegCollection", [{}])[0].get("instrument", {}).get("symbol")
    description = order.get("orderLegCollection", [{}])[0].get("instrument", {}).get("description")
    entry_time = order.get("enteredTime")

    if not symbol or not description or not entry_time:
        return None

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT full_json FROM schwab_orders
        WHERE instruction IN ('BUY_TO_OPEN', 'SELL_TO_OPEN')
        AND ticker = ? AND description = ?
        AND entered_time < ?
        ORDER BY entered_time DESC
        LIMIT 1
    """, (symbol, description, entry_time))

    row = cursor.fetchone()
    conn.close()

    if row:
        return json.loads(row[0])
    return None

def extract_execution_price(order):
    """
    Extracts the first available executionLegs price from an order.
    Returns float or None.
    """
    try:
        activities = order.get("orderActivityCollection", [])
        for activity in activities:
            for leg in activity.get("executionLegs", []):
                if "price" in leg:
                    return float(leg["price"])
    except Exception as e:
        logging.error(f"Failed to extract execution price: {e}")
    return None


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
    from datetime import timezone, datetime, timedelta
    
    to_date = datetime.now(timezone.utc)
    from_date = to_date - timedelta(hours=delta)
    
    # Format dates as ISO 8601 strings with milliseconds and timezone
    return from_date.strftime('%Y-%m-%dT%H:%M:%S.000Z')