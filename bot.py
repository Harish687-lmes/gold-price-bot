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
    import csv
    from io import StringIO

    headers = {"User-Agent": "Mozilla/5.0"}

    # LBMA Gold Price USD per ounce (official benchmark)
    url = "https://data-asg.goldprice.org/dbXRates/USD"
    data = requests.get(url, headers=headers, timeout=10).json()

    usd_per_oz = data["items"][0]["xauPrice"]

    # Get live USDINR
    fx_url = "https://open.er-api.com/v6/latest/USD"
    fx = requests.get(fx_url, headers=headers, timeout=10).json()
    usd_inr = fx["rates"]["INR"]

    # Convert to INR per gram
    base_price24 = usd_per_oz * usd_inr / 31.1035

    # India import duty + GST + premium (~17.5%)
    price24 = base_price24 * 1.175
    price22 = price24 * 0.916

    return round(price22, 2), round(price24, 2)


def main():
    g22,g24 = get_gold_rate()

    if not g22:
        send("Gold bot error fetching price")
        return

    send(f"📊 Gold Price {datetime.now().date()}\n22K ₹{g22}/g\n24K ₹{g24}/g")

main()














