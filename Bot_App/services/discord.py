import requests
import logging
import json
import sqlite3

from Bot_App.core import order_utils
from Bot_App.config import secrets

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def send_discord_alert(order_json, webhook_url, channel_id, suffix=""):
    content = format_discord_message(order_json, suffix)
    payload = {
        "channel": channel_id,
        "content": content
    }

    def do_post():
        return requests.post(webhook_url, json=payload, timeout=10)

    response = secrets.retry_request(do_post)
    return response is not None and response.status_code in (200, 204)


def format_discord_message(order, suffix=""):
    legs = order.get("orderLegCollection", [])
    price = order.get("price", "?")
    position_effects = []
    leg_lines = []
    total_qty = get_total_quantity(order)

    for leg in legs:
        instrument = leg.get("instrument", {})
        symbol = instrument.get("symbol", "???").split(" ")[0]
        description = instrument.get("description", "")
        quantity = leg.get("quantity", 0)
        instruction = leg.get("instruction", "UNKNOWN")
        position_effect = leg.get("positionEffect", "")

        date = order_utils.parse_option_description(description, 2)
        strike = order_utils.parse_option_description(description, 3)
        put_call = order_utils.parse_option_description(description, 4)

        leg_lines.append(f"## {symbol}")
        leg_lines.append(f"> **{date} ${strike} {put_call}** \n>{sizing_order(total_qty, quantity)} *{instruction}*")

        effect_label = get_open_close_symbol(position_effect)
        position_effects.append(effect_label)

    effect_summary = ', '.join(set(position_effects)) or "UNKNOWN"
    body = "\n".join(leg_lines)
    gain_line = ""  # Can be updated later if needed

    if suffix == "":
        return f"{body}\n@ ${price} *{effect_summary}*{gain_line}"
    else:
        return f"{body}\n@ ${price} *{effect_summary}*{gain_line}\n{suffix}"


def get_total_quantity(order):
    return sum(leg.get("quantity", 0) for leg in order.get("orderLegCollection", []))

def sizing_order(total_qty, quantity):
    if total_qty <= 1 or quantity == 0:
        return ""
    size = (quantity / total_qty) * 100
    return f" ({size:.0f}%)"

def get_open_close_symbol(effect):
    if effect == "OPENING":
        return f"{effect} 🟢"
    elif effect == "CLOSING":
        return f"{effect} 🔴"
    else:
        return f"{effect} 🟡"
