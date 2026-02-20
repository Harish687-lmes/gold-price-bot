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

    # Stooq gold futures (USD per ounce)
    url = "https://stooq.com/q/l/?s=gc.f&f=sd2t2ohlcv&h&e=csv"
    text = requests.get(url, headers=headers, timeout=10).text

    # CSV format: Symbol,Date,Time,Open,High,Low,Close,Volume
    last_line = text.strip().split("\n")[-1]
    close_price = float(last_line.split(",")[6])  # USD per ounce

    # USD → INR
    fx = requests.get("https://stooq.com/q/l/?s=usdinr&f=sd2t2ohlcv&h&e=csv",
                      headers=headers, timeout=10).text
    fx_line = fx.strip().split("\n")[-1]
    usd_inr = float(fx_line.split(",")[6])

    # Convert ounce → gram
    base_price24 = close_price * usd_inr / 31.1035

    # India retail conversion (~17.5%)
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















