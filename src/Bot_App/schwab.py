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



def process_closing_orders(sql, orders):
    """
    Processes closing orders, updating `open_positions` and tracking closed orders.
    Returns a list of closed orders.
    """
    closed_orders = []

    for order in orders:
        if order['instruction'] in ["BUY_TO_OPEN", "SELL_TO_OPEN"]:
            continue

        # Find matching open positions
        matches = sql.get_data(
            query="SELECT * FROM open_positions WHERE instrumentId = ? AND quantity > 0 ORDER BY executionTime ASC",
            params=(order['instrumentId'],)
        )

        if matches:
            closing_quantity = order['quantity']

            # Iterate through matching open positions
            for match in matches:
                execution_time = match[0]
                open_id = match[1]
                open_quantity = match[2]
                open_avg_price = match[3]

                if closing_quantity <= 0:
                    break

                processed_quantity = min(open_quantity, closing_quantity)
                closing_quantity -= processed_quantity
                partial_close = open_quantity > processed_quantity

                # Add to closed orders
                closed_orders.append({
                    "symbol": order["symbol"],
                    "quantity": processed_quantity,
                    "description": order["description"],
                    "putCall": order["putCall"],
                    "date": order["date"],
                    "strike": order["strike"],
                    "price": order["price"],
                    "instruction": order["instruction"],
                    "complexOrderStrategy": order["complexOrderStrategy"],
                    "orderStrategyType": order["orderStrategyType"],
                    "legId": order["legId"],
                    "instrumentId": order["instrumentId"],
                    "executionTime": execution_time,
                    "open_quantity": open_quantity,
                    "open_price": open_avg_price,
                    "partial_close": partial_close
                })

                # Update or delete open positions
                if partial_close:
                    sql.execute_query(
                        "UPDATE open_positions SET quantity = quantity - ? WHERE instrumentId = ? AND executionTime = ?",
                        params=(processed_quantity, open_id, execution_time)
                    )
                else:
                    sql.execute_query(
                        "DELETE FROM open_positions WHERE instrumentId = ? AND executionTime = ?",
                        params=(open_id, execution_time)
                    )

            if closing_quantity > 0:
                logging.warning(f"Remaining closing quantity of {closing_quantity} could not be fully matched.")
        else:
            logging.info(f"No matching open positions found for instrumentId: {order['instrumentId']}")

    sql.commit()
    return closed_orders


def populate_open_positions(sql, orders):
    """
    Populates the `open_positions` table with BUY_TO_OPEN and SELL_TO_OPEN orders.
    """
    for order in orders:
        if order['instruction'] in ["BUY_TO_OPEN", "SELL_TO_OPEN"]:
            sql.execute_query(
                "INSERT INTO open_positions VALUES (?, ?, ?, ?, ?)",
                (order['executionTime'], order['instrumentId'], order['quantity'], order['price'], order['symbol'])
            )
    sql.commit()


def save_orders_to_db(sql, orders):
    """
    Saves the given list of orders to the `orders` table in the database.
    """
    if not orders:
        logging.warning("No orders to save to the database.")
        return

    for order in orders:
        logging.debug(f"Saving order to database...")  # Debugging log
        query = """
        INSERT INTO orders (
            order_id, symbol, quantity, description, putCall, date, strike, price, instruction,
            complexOrderStrategy, orderStrategyType, legId, instrumentId, executionTime
        ) VALUES (
            NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        """
        params = (
            order['symbol'], order['quantity'], order['description'], order['putCall'],
            order['date'], order['strike'], order['price'], order['instruction'],
            order['complexOrderStrategy'], order['orderStrategyType'],
            order['legId'], order['instrumentId'], order['executionTime']
        )
        try:
            sql.execute_query(query, params)
        except Exception as e:
            logging.error(f"Error saving order to database: {e}")

    sql.commit()  # Commit changes to ensure data is saved
    logging.info(f"Successfully saved {len(orders)} orders to the database.")

def initialize_database(sql, DROP_TABLES=False):
    """
    Initializes the database by creating necessary tables and dropping existing ones (for testing).
    """
    # Drop existing tables (for testing purposes)
    if DROP_TABLES:
        sql.execute_query("DROP TABLE IF EXISTS orders")
        sql.execute_query("DROP TABLE IF EXISTS positions")
        sql.execute_query("DROP TABLE IF EXISTS open_positions")

    # Create `orders` table
    sql.execute_query("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY,
        symbol TEXT,
        quantity INTEGER,
        description TEXT,
        putCall TEXT,
        date TEXT,
        strike REAL,
        price REAL,
        instruction TEXT,
        complexOrderStrategy TEXT,
        orderStrategyType TEXT,
        legId INTEGER,
        instrumentId INTEGER,
        executionTime TEXT
    )""")

    # Create `open_positions` table
    sql.execute_query("""
    CREATE TABLE IF NOT EXISTS open_positions (
        executionTime TEXT PRIMARY KEY,
        instrumentId TEXT,
        quantity INTEGER,
        avg_price REAL,
        symbol TEXT
    );
    """)
    sql.commit()