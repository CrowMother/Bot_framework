import requests
import logging
import sqlite3
import json

from . import data


def post_to_discord(order_json, DISCORD_WEBHOOK_URL, DISCORD_CHANNEL_ID):
    content = format_discord_message(order_json)
    payload = {
        "channel": DISCORD_CHANNEL_ID,
        "content": content}

    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
    return response.status_code == 204 or response.status_code == 200

def format_discord_message(order):
    """
    Format a Schwab order dictionary into a string suitable for posting to Discord.

    :param order: A dictionary of a Schwab order
    :return: A string representation of the order
    """
    legs = order.get("orderLegCollection", [])
    price = order.get("price", "?")
    position_effects = []
    leg_lines = []

    for leg in legs:
        instruction = leg.get("instruction", "UNKNOWN")
        position_effect = leg.get("positionEffect", "")
        position_effect = get_open_close_symbol(position_effect)
        instrument = leg.get("instrument", {})
        symbol = instrument.get("symbol", "???").split(" ")[0]
        description = instrument.get("description", "")
        # Extract important parts of the option description
        # date is the first part of the description
        # strike is the second part
        # put or call is the fourth part
        date = data.parse_option_description(description, 2)
        strike = data.parse_option_description(description, 3)
        put_call = data.parse_option_description(description, 4)
#------------------------------------------------------------------------------
#   # format message for each leg
        leg_lines.append(f"## {symbol}")
        # Add the symbol and strike price
        leg_lines.append(f"> **{date} ${strike} {put_call}**")
        position_effects.append(position_effect)
    # format message for the order
    effect_summary = ', '.join(set(position_effects)) or "UNKNOWN"
    body = "\n".join(leg_lines)

    gain_line = ""
    if any(pe == "CLOSING 🔴" for pe in position_effects):
        opening_price = find_opening_price(order)
        if opening_price and price:
            pct_change = ((price - opening_price) / opening_price) * 100
            emoji = ":chart_with_upwards_trend:" if pct_change >= 0 else ":chart_with_downwards_trend: "
            gain_line = f"\n{emoji} **{pct_change:+.2f}%** vs open"

    return f"{body}\n@ ${price} *{effect_summary}*{gain_line}"
#-----------------------------------------------------------------------------

def get_open_close_symbol(position_effect):
    if position_effect == "OPENING":
        return f"{position_effect} 🟢"
    elif position_effect == "CLOSING":
        return f"{position_effect} 🔴"
    else:
        return f"{position_effect} 🟡"
    
def find_opening_price(order, db_path="orders.db"):
    leg = order.get("orderLegCollection", [{}])[0]
    instrument = leg.get("instrument", {})
    symbol = instrument.get("symbol", None)
    entry_time = order.get("enteredTime", None)

    if not symbol or not entry_time:
        return None

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT full_json FROM schwab_orders
        WHERE ticker = ? AND position_effect = 'OPENING'
        AND entered_time < ?
        ORDER BY entered_time DESC
        LIMIT 1
    """, (symbol, entry_time))

    row = cursor.fetchone()
    conn.close()

    if row:
        opening_order = json.loads(row[0])
        return extract_execution_price(opening_order)
    return None

def extract_execution_price(order):
    activities = order.get("orderActivityCollection", [])
    if activities:
        legs = activities[0].get("executionLegs", [])
        if legs:
            return float(legs[0].get("price", 0))
    return None