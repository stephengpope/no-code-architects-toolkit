import requests

def send_webhook(webhook_url, data):
    """Send a POST request to a webhook URL with the provided data."""
    try:
        print(f"Attempting to send webhook to {webhook_url} with data: {data}")
        response = requests.post(webhook_url, json=data)
        response.raise_for_status()
        print(f"Webhook sent: {data}")
    except requests.RequestException as e:
        print(f"Webhook failed: {e}")
