# src/your_library/schwab.py
import schwabdev
import logging

class Schwab_client():
    def __init__(self, account, secret):
        self.client = create_client(account, secret)

    def say_hello(self):
        logging.debug("Hello from Schwab_client!")






def create_client(app_key, app_secret):
    return schwabdev.Client(app_key, app_secret)