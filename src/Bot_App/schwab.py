import schwabdev
import logging
from . import util

from . import data

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class Schwab_client():
    def __init__(self, account, secret):
        self.client = create_client(account, secret)

    def say_hello(self):
        logging.debug("Hello from Schwab_client!")

    def get_account_positions(self, filter=None, hours=1):
        orders = None
        try:
            to_date_str = util.get_start_time(hours)
            from_date_str = util.get_end_time(hours)

            response = self.client.account_orders_all( 
                from_date_str,
                to_date_str,
                None,  # Optional: set to limit number of results    
                filter # Optional: Filter by status
            )

            if response.status_code == 200:
                # Parse the JSON content
                orders = response.json()
                return orders
            else:
                logging.error(f"Error getting account positions: {response} \n {from_date_str} \n {to_date_str}")
                return None
            
        except Exception as e:
            logging.error(f"Error getting account positions: {e} response: {response}")
            return None

def create_client(app_key, app_secret):
    logging.debug("Initializing Schwabdev client")
    return schwabdev.Client(app_key, app_secret)


def sort_data_schwab(position):
    """
    Extracts relevant data from a given position and returns it in a neat dictionary.

    :param position: The position to extract data from.
    :return: A dictionary with the extracted data.
    """
    # Extract the symbol, quantity and description from the position
    symbol = data.get_value_from_data(position, "underlyingSymbol")
    quantity = data.get_value_from_data(position, "quantity")
    description = data.get_value_from_data(position, "description")

    # Extract the put/call, price, instruction, complexOrderStrategy, orderStrategyType, legId, instrumentId and time from the position
    putCall = data.get_value_from_data(position, "putCall")
    price = data.get_value_from_data(position, "price")
    instruction = data.get_value_from_data(position, "instruction")
    comlexOrderStrategy = data.get_value_from_data(position, "complexOrderStrategy")
    orderStrategyType = data.get_value_from_data(position, "orderStrategyType")
    legId = data.get_value_from_data(position, "legId")
    instrumentId = data.get_value_from_data(position, "instrumentId")
    time = data.get_value_from_data(position, "time")

    # Parse the description to get the date and strike
    date = data.parse_option_description(description, 2)
    strike = data.parse_option_description(description, 3)

    # Create a dictionary with the extracted data
    dict = {
        "symbol": symbol,
        "quantity": quantity,
        "description": description,
        "putCall": putCall,
        "date": date,
        "strike": strike,
        "price": price,
        "instruction": instruction,
        "complexOrderStrategy": comlexOrderStrategy,
        "orderStrategyType": orderStrategyType,
        "legId": legId,
        "instrumentId": instrumentId,
        "executionTime": time,
    }
    return dict
