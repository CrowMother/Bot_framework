import re
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

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
