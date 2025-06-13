import imapclient
import email
import re
import requests
import html2text
from bs4 import BeautifulSoup

# ========== CONFIG ==========
EMAIL = "czdzhatablet@zohomail.com"
PASSWORD = "3Monday3!"
IMAP_SERVER = "imap.zoho.com"
AFTERSHIP_API_KEY = "asat_07d6a1ebbb344426a3bc2a8880b85316"
SEARCH_KEYWORDS = ["tracking", "shipped", "out for delivery", "package", "delivered"]
# ============================

def extract_tracking_numbers(text):
    patterns = [
        r"\b1Z[0-9A-Z]{16}\b",  # UPS
        r"\b\d{12,22}\b"        # FedEx, USPS, Amazon
    ]
    found = set()
    for pattern in patterns:
        found.update(re.findall(pattern, text))
    return list(found)

def detect_carrier(tracking_number):
    if tracking_number.startswith("1Z"):
        return "ups"
    elif tracking_number.startswith("9") or len(tracking_number) == 22:
        return "usps"
    elif len(tracking_number) == 12 or tracking_number.startswith("7"):
        return "fedex"
    return "unknown"

def submit_to_aftership(tracking_number, carrier):
    headers = {
        "aftership-api-key": AFTERSHIP_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "tracking": {
            "tracking_number": tracking_number,
            "carrier_code": carrier
        }
    }
    try:
        response = requests.post("https://api.aftership.com/v4/trackings", json=data, headers=headers)
        print(f"Submitted {tracking_number} ({carrier}): {response.status_code}")
    except Exception as e:
        print(f"AfterShip submission failed: {e}")

def process_email(msg):
    try:
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    body = html2text.html2text(part.get_payload(decode=True).decode())
                    break
        else:
            body = html2text.html2text(msg.get_payload(decode=True).decode())
        tracking_numbers = extract_tracking_numbers(body)
        for number in tracking_numbers:
            carrier = detect_carrier(number)
            if carrier != "unknown":
                submit_to_aftership(number, carrier)
    except Exception as e:
        print(f"Failed to process email: {e}")

def run_tracker():
    try:
        client = imapclient.IMAPClient(IMAP_SERVER, ssl=True)
        client.login(EMAIL, PASSWORD)
        client.select_folder("INBOX", readonly=True)
        uids = client.search(["UNSEEN"])
        print(f"Found {len(uids)} new emails")
        for uid in uids:
            raw = client.fetch([uid], ["RFC822"])[uid][b"RFC822"]
            msg = email.message_from_bytes(raw)
            subject = msg["subject"] or ""
            if any(keyword.lower() in subject.lower() for keyword in SEARCH_KEYWORDS):
                print(f"Processing email: {subject}")
                process_email(msg)
        client.logout()
    except Exception as e:
        print(f"Email check failed: {e}")

# 🔁 Continuous loop
if __name__ == "__main__":
    print("Starting AfterShip Email Tracker loop...")
    while True:
        run_tracker()
        print(f"Waiting {CHECK_INTERVAL_SECONDS} seconds before next check...\n")
        time.sleep(CHECK_INTERVAL_SECONDS)
