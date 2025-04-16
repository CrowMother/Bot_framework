import requests
import logging
import sqlite3
import json

from . import util
from . import data


def post_to_discord(order_json, DISCORD_WEBHOOK_URL, DISCORD_CHANNEL_ID, suffix=""):
    content = format_discord_message(order_json, suffix)
    payload = {
        "channel": DISCORD_CHANNEL_ID,
        "content": content
    }

    def do_post():
        return requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)

    response = util.retry_request(do_post)
    return response is not None and (response.status_code == 204 or response.status_code == 200)


def format_discord_message(order, suffix=""):
    """
    Format a Schwab order dictionary into a string suitable for posting to Discord.

    :param order: A dictionary of a Schwab order
    :return: A string representation of the order
    """
    legs = order.get("orderLegCollection", [])
    price = order.get("price", "?")
    position_effects = []
    leg_lines = []

    total_qty = get_total_quantity(order)

    for leg in legs:
        instruction = leg.get("instruction", "UNKNOWN")
        position_effect = leg.get("positionEffect", "")
        position_effect = get_open_close_symbol(position_effect)
        instrument = leg.get("instrument", {})
        symbol = instrument.get("symbol", "???").split(" ")[0]
        description = instrument.get("description", "")
        quantity = leg.get("quantity", 0)

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
        leg_lines.append(f"> **{date} ${strike} {put_call}** \n>{sizing_order(total_qty, quantity)} *{instruction}*")
        effect = get_position_context(order)
        if effect is None:
            position_effects.append(position_effect)
        else:
            position_effects.append(effect)
    # format message for the order
    effect_summary = ', '.join(set(position_effects)) or "UNKNOWN"
    body = "\n".join(leg_lines)

    gain_line = ""
    if any("closing" in pe.lower() for pe in position_effects):
        opening_price = find_opening_price(order)
        if opening_price and price:
            pct_change = ((price - opening_price) / opening_price) * 100
            emoji = ":chart_with_upwards_trend:" if pct_change >= 0 else ":chart_with_downwards_trend: "
            gain_line = f"\n{emoji} **{pct_change:+.2f}%** vs open"
    if suffix == "":
        return f"{body}\n@ ${price} *{effect_summary}*{gain_line}"
    else:
        return f"{body}\n@ ${price} *{effect_summary}*{gain_line}\n{suffix}"
#-----------------------------------------------------------------------------

def sizing_order(total_qty, quantity):
    if total_qty <= 1:
        return ""
    elif quantity == 0:
        return ""
    else:
        size = (quantity / total_qty) * 100
        return f" ({size:.0f}%)"


def get_total_quantity(order):
    legs = order.get("orderLegCollection", [])
    total_qty = 0
    for leg in legs:
        quantity = leg.get("quantity", 0)
        total_qty += quantity
    return total_qty

def get_open_close_symbol(effect):
    if effect == "OPENING":
        return f"{effect} 🟢"
    elif effect == "CLOSING":
        return f"{effect} 🔴"
    else:
        return f"{effect} 🟡"
    
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

def extract_quantity(order):
    legs = order.get("orderLegCollection", [])
    if legs:
        return float(legs[0].get("quantity", 0))
    return 0

def find_opening_order(order, db_path="orders.db"):
    leg = order.get("orderLegCollection", [{}])[0]
    instrument = leg.get("instrument", {})
    symbol = instrument.get("symbol", None)
    entry_time = order.get("enteredTime", None)
    description = instrument.get("description", None)
    #get the price from the description
    if description:
        strike = data.parse_option_description(description, 3)
        print(strike)

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
        for r in row:
            
            open_order = json.loads(r)
            instrument = open_order.get("orderLegCollection", [{}])[0].get("instrument", {})
            open_description = instrument.get("description")
            print(open_description)
            open_strike = data.parse_option_description(open_description, 3)
            if "VIX" in symbol:
                print("VIX")
            if open_strike == "N/A" or open_strike == "N/A":
                return open_order
            if open_strike == strike:
                return open_order

    return None

def get_position_context(order, db_path="orders.db"):
    leg = order.get("orderLegCollection", [{}])[0]
    position_effect = leg.get("positionEffect", "")
    current_qty = leg.get("quantity", 0)

    instrument = leg.get("instrument", {})
    symbol = instrument.get("symbol", None)
    description = instrument.get("description", None)
    entry_time = order.get("enteredTime", None)

    if not symbol or not description or not entry_time:
        return None

    if position_effect == "CLOSING":
        # Get original opened quantity
        opening_order = find_opening_order(order, db_path)
        if not opening_order:
            return "Closing 🔴"  # fallback

        open_qty = extract_quantity(opening_order)

        # Get all previously closed quantity before this order
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT SUM(quantity) FROM schwab_orders
            WHERE instruction IN ('SELL_TO_CLOSE', 'BUY_TO_CLOSE')
            AND ticker = ? AND description = ?
            AND entered_time < ?
        """, (symbol, description, entry_time))
        result = cursor.fetchone()
        conn.close()

        prev_closed_qty = result[0] if result and result[0] else 0
        total_closed_qty = prev_closed_qty + current_qty

        if total_closed_qty < open_qty:
            return "Partially Closing :orange_circle:"
        elif total_closed_qty == open_qty:
            return "Fully Closed ✅"
        else:
            return "Over Closed ⚠️"  # Optional: detect bugs or double-posting

    elif position_effect == "OPENING":
        # Check how much has already been opened before this order
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT SUM(quantity) FROM schwab_orders
            WHERE instruction IN ('BUY_TO_OPEN', 'SELL_TO_OPEN')
            AND ticker = ? AND description = ?
            AND entered_time < ?
        """, (symbol, description, entry_time))
        result = cursor.fetchone()
        conn.close()

        prev_opened_qty = result[0] if result and result[0] else 0
        total_opened_qty = prev_opened_qty + current_qty

        if prev_opened_qty > 0:
            return "Scaling Up :green_circle:"

    return None



