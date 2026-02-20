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

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    # Chennai gold rate API used by financial portals
    url = "https://priceapi.moneycontrol.com/pricefeed/commodity/gold"

    data = requests.get(url, headers=headers, timeout=10).json()

    # MCX gold price ₹ per 10 grams
    price_10g = float(data["data"]["pricecurrent"])

    # convert to per gram
    price24 = price_10g / 10

    # convert to 22K jewellery purity
    price22 = price24 * 0.916

    return round(price22, 2), round(price24, 2)


def main():
    g22,g24 = get_gold_rate()

    if not g22:
        send("Gold bot error fetching price")
        return

    send(f"📊 Gold Price {datetime.now().date()}\n22K ₹{g22}/g\n24K ₹{g24}/g")

main()













