import os
import time
import requests
import logging
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def get_secret(key, FILE_PATH="", default=None):
    try:
        load_dotenv(FILE_PATH)
        value = os.getenv(key)
        if value is None:
            logging.debug(f"Key {key} not found or is None")
        return value if value is not None else default
    except Exception as e:
        logging.error(f"Error loading {key} from {FILE_PATH}: {e}")
        return default


def retry_request(request_func, retries=3, delay=5, backoff=2, retry_on=(requests.exceptions.RequestException,), raise_on_fail=False):
    for attempt in range(1, retries + 1):
        try:
            return request_func()
        except retry_on as e:
            logging.warning(f"[Attempt {attempt}] Request failed: {e}. Retrying in {delay}s...")
            time.sleep(delay)
            delay *= backoff

    logging.error("All retry attempts failed.")
    if raise_on_fail:
        raise e
    return None


def get_start_time(delta=1):
    now = datetime.now(timezone.utc)
    return now.strftime('%Y-%m-%dT%H:%M:%S.000Z')


def get_end_time(delta=1):
    now = datetime.now(timezone.utc)
    past = now - timedelta(hours=delta)
    return past.strftime('%Y-%m-%dT%H:%M:%S.000Z')


def get_current_time():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')


def flatten_dict(d, parent_key='', sep='.'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def check_time_of_week(day, hour):
    now = datetime.now()
    return now.weekday() == day and now.hour == hour


def check_time_of_day(hour, minute=0):
    now = datetime.now()
    return now.hour == hour and now.minute == minute


def check_file_changed(file_path, last_modified=None):
    try:
        stat = os.stat(file_path)
        return last_modified is None or stat.st_mtime > last_modified
    except Exception as e:
        logging.error(f"Error checking file {file_path}: {e}")
        return False


def get_file_last_modified(file_path):
    try:
        return os.stat(file_path).st_mtime
    except Exception as e:
        logging.error(f"Error getting last modified time: {e}")
        return 0


def str_to_bool(value):
    return str(value).strip().lower() == "true"
