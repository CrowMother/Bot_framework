import schwabdev
import logging
from . import util

class Schwab_client():
    def __init__(self, account, secret):
        self.client = create_client(account, secret)
        self.test = "test"

    def say_hello(self):
        logging.debug("Hello from Schwab_client!")

    def get_account_positions(self, filter=None, hours=1):
        logging.info("Getting account positions now")
        orders = None
        try:
            from_date_str = util.get_start_time(hours)
            to_date_str = util.get_end_time(hours)

            logging.info(f"from_date_str: {from_date_str}, to_date_str: {to_date_str}")
            logging.info(f"filter: {filter}")

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
    logging.info("Initializing Schwabdev client")
    client = schwabdev.Client(app_key, app_secret)
    logging.info("Schwabdev client initialized")
    return client