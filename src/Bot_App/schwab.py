import schwabdev
import logging
from . import util
import hashlib
import datetime

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

    return ["assetType",
            "underlyingSymbol",
            "description",
            "putCall",
            "instrumentId",
            "instruction",
            "legId",]

def split_description(order):
    try:
        description = order["description"]
        if not description:
            return order
        order["date"] = data.parse_option_description(description, 2)
        order["strike"] = data.parse_option_description(description, 3)
        return order
    
    except Exception as e:
        logging.error(f"Error formatting description: {e}")
        return


def generate_order_id(order):
    """
    Generates a unique identifier for an order based on the underlying symbol and the symbols of the
    legs in the orderLegCollection. The identifier is a SHA-256 hash of the concatenated strings.

    Args:
        order (dict): A dictionary containing the order details.

    Returns:
        str: A unique identifier for the order.
    """
    leg_symbols = sorted(
        [leg['instrument']['symbol'] for leg in order['orderLegCollection']]
    )
    raw_string = order['underlyingSymbol'] + ''.join(leg_symbols) + order.get('complexOrderStrategyType', '')
    return hashlib.sha256(raw_string.encode()).hexdigest()

def extract_and_normailze_legs(order):
    """
    Extracts and normalizes the legs of an order, generating a unique identifier for each leg.

    Args:
        order (dict): A dictionary containing order details, including the "orderLegCollection" key
                      which holds a list of legs to be processed.

    Returns:
        list: A list of dictionaries, each representing a normalized leg with keys such as "order_id",
              "leg_id", "order_leg_type", "symbol", "cusip", "description", "instrument_id", "type",
              "put_call", "underlying_symbol", "instruction", "position_effect", and "quantity".
    """
    try:
        # Generate unique identifier for the order
        order_id = generate_order_id(order)

        # Extract and normalize legs
        legs = []
        for leg in order["orderLegCollection"]:
            instrument = leg["instrument"]
            legs.append({
                "orderId": order_id,
                "legId": leg.get("legId"),
                "orderLegType": leg.get("orderLegType"),
                "symbol": instrument.get("symbol"),
                "cusip": instrument.get("cusip"),
                "description": instrument.get("description"),
                "instrumentId": instrument.get("instrumentId"),
                "type": instrument.get("type"),
                "putCall": instrument.get("putCall"),
                "underlyingSymbol": instrument.get("underlyingSymbol"),
                "instruction": leg.get("instruction"),
                "positionEffect": leg.get("positionEffect"),
                "quantity": leg.get("quantity"),
                "strategyType": order.get("complexOrderStrategyType"),
                "orderStrategyType": order.get("orderStrategyType"),
                "orderPrice": order.get("price"),
                "orderQuantity": order.get("quantity")
            })

        return legs

    except Exception as e:
        logging.error(f"Error extracting and normalizing legs: {e}")
        return []