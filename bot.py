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

    headers = {"User-Agent": "Mozilla/5.0"}

    # IBJA India bullion benchmark (₹ per 10g)
    url = "https://www.goodreturns.in/gold-rates/chennai.html"
    html = requests.get(url, headers=headers, timeout=10).text

    import re

    # extract 24K price
    m24 = re.search(r'24 Carat Gold Rate.*?₹\s*([0-9,]+)', html, re.S)
    m22 = re.search(r'22 Carat Gold Rate.*?₹\s*([0-9,]+)', html, re.S)

    if not m24 or not m22:
        raise Exception("Could not fetch Chennai gold rate")

    price24 = float(m24.group(1).replace(",", ""))
    price22 = float(m22.group(1).replace(",", ""))

    # website gives per 10g → convert to per gram
    price24 = price24 / 10
    price22 = price22 / 10

    return round(price22, 2), round(price24, 2)


def main():
    g22,g24 = get_gold_rate()

    if not g22:
        send("Gold bot error fetching price")
        return

    send(f"📊 Gold Price {datetime.now().date()}\n22K ₹{g22}/g\n24K ₹{g24}/g")

main()












