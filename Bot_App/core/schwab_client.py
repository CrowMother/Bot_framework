import logging
from schwabdev import Client
from Bot_App.config.secrets import get_start_time, get_end_time
from Bot_App.config.secrets import retry_request

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class SchwabClient:
    def __init__(self, app_key, app_secret):
        self.client = Client(app_key, app_secret)

    def get_account_positions(self, status_filter="FILLED", hours=1):
        def fetch_orders():
            from_time = get_end_time(hours)
            to_time = get_start_time(hours)
            return self.client.account_orders_all(from_time, to_time, None, status_filter)

        response = retry_request(fetch_orders, raise_on_fail=True)
        if response is not None and response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Failed to get positions after retries. Response: {response}")
            return []
