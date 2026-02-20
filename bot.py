import requests
import os
from datetime import datetime

TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def send(msg):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": msg}
    )
def get_gold_rate():
    import requests

    url = "https://api.exchangerate.host/latest?base=XAU&symbols=INR"

    data = requests.get(url, timeout=10).json()

    # INR per ounce
    inr_per_oz = data["rates"]["INR"]

    # convert ounce → gram
    price24 = inr_per_oz / 31.1035
    price22 = price24 * 0.916

    return round(price22,2), round(price24,2)
def main():
    g22,g24 = get_gold_rate()

    if not g22:
        send("Gold bot error fetching price")
        return

    send(f"📊 Gold Price {datetime.now().date()}\n22K ₹{g22}/g\n24K ₹{g24}/g")

main()


