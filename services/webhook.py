import requests

def send_webhook(webhook_url, data):
    try:
        response = requests.post(webhook_url, json=data)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Webhook failed: {e}")
