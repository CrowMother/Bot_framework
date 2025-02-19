import requests
import logging

def format_webhook(order, DISCORD_CHANNEL_ID, MESSAGE_TEMPLATE_OPENING, MESSAGE_TEMPLATE_CLOSING):
    """
    Formats the order data for sending to the webhook dynamically based on an environment variable template.

    Args:
        order (dict): The order data to be formatted.

    Returns:
        message (dict): Discord channel ID and message content.
    """
    try:
        print(order)

        # Calculate percentage gain if order has an open price
        order["percentage_gain"] = (
            f"{((order['price'] - order['open_price']) / order['open_price'] * 100):.2f}%" 
            if "open_price" in order else "N/A"
        )

        # Determine which message template to use
        if "open_price" in order:
            message_content = MESSAGE_TEMPLATE_CLOSING.format(**order)
        else:
            message_content = MESSAGE_TEMPLATE_OPENING.format(**order)

        message = {
            "channel": DISCORD_CHANNEL_ID,
            "content": message_content
        }

        return message

    except KeyError as e:
        logging.error(f"Missing key in order data: {e}")
    except Exception as e:
        logging.error(f"Error formatting webhook message: {str(e)}")


def send_to_discord_webhook(message, webhook_url):
    """
    Sends the given order to the specified webhook URL.
    Logs success or failure of the request.
    """
    try:
        print(f"Sending order to {webhook_url}:\n {message}")
        response = requests.post(webhook_url, json=message)
        if response.status_code == 200:
            logging.info("Successfully sent order to webhook.")
        else:
            logging.error(f"Failed to send order to webhook. Status code: {response.status_code}")
    except Exception as e:
        logging.error(f"Error sending data to webhook: {str(e)}")