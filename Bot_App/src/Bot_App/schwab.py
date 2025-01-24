import schwabdev
import logging
from . import util
import re

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class Schwab_client():
    def __init__(self, account, secret):
        self.client = create_client(account, secret)
        self.test = "test"

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

def parse_option_description(description):
    # Regex to capture parts of the string
    pattern = r"^(.*?) (\d{2}/\d{2}/\d{4}) \$(\d+\.?\d*) (Call|Put)$"
    match = re.match(pattern, description)

    if match:
        symbol = match.group(1)  # Symbol can have spaces
        date = match.group(2)    # Option expiration date
        strike = match.group(3)  # Strike price
        option_type = match.group(4)  # Call or Put

        return {
            "symbol": symbol,
            "date": date,
            "strike": strike,
            "type": option_type
        }
    else:
        raise ValueError("Description format is invalid")