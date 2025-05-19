import requests
import logging
import json
import sqlite3

from Bot_App.core.order_utils import (
    find_matching_open_order,
    calculate_percentage_gain,
    extract_execution_price,
    parse_option_description
)
from Bot_App.core.position_tracker import consume_open_position
from Bot_App.config import secrets

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def send_discord_alert(order_json, webhook_url, channel_id, suffix=""):
    content = format_discord_message(order_json)
    gain = None
    suffix_line = suffix if suffix else ""

    # Calculate gain
    if order_json.get("orderLegCollection", [{}])[0].get("positionEffect") == "CLOSING":
        avg_open, used_qty = consume_open_position(order_json)
        close_price = extract_execution_price(order_json)
        gain = calculate_percentage_gain(avg_open, close_price)

    # Add gain line
    if gain is not None:
        emoji = ":chart_with_upwards_trend:" if gain >= 0 else ":chart_with_downwards_trend:"
        gain_line = f"\n{emoji} **{gain:+.2f}%** vs open @ ${avg_open}"
    else:
        gain_line = ""

    # Final formatted message
    payload = {
        "channel": channel_id,
        "content": f"{content}{gain_line}\n{suffix_line}".strip()
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

        date = parse_option_description(description, 2)
        strike = parse_option_description(description, 3)
        put_call = parse_option_description(description, 4)

        leg_lines.append(f"## {symbol}")
        leg_lines.append(f"> **{date} ${strike} {put_call}** \n>{sizing_order(total_qty, quantity)} *{instruction}*")

        effect_label = get_open_close_symbol(position_effect)
        position_effects.append(effect_label)

    effect_summary = ', '.join(set(position_effects)) or "UNKNOWN"
    body = "\n".join(leg_lines)
    return f"{body}\n@ ${price} *{effect_summary}*"

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
