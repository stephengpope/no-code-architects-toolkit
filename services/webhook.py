import requests
import logging

logger = logging.getLogger(__name__)

def send_webhook(webhook_url, data):
    """Send a POST request to a webhook URL with the provided data."""
    try:
        logger.info(f"Attempting to send webhook to {webhook_url} with data: {data}")
        response = requests.post(webhook_url, json=data)
        response.raise_for_status()
        logger.info(f"Webhook sent: {data}")
    except requests.RequestException as e:
        logger.error(f"Webhook failed: {e}")
