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

    # Fetch gold futures data
    url = "https://query1.finance.yahoo.com/v8/finance/chart/GC=F"
    data = requests.get(url, headers=headers, timeout=10).json()

    price_raw = data["chart"]["result"][0]["meta"]["regularMarketPrice"]

    # ---------- UNIT DETECTION ----------
    if price_raw < 10000:
        # USD per ounce
        fx_url = "https://query1.finance.yahoo.com/v8/finance/chart/USDINR=X"
        fx_data = requests.get(fx_url, headers=headers, timeout=10).json()
        usd_inr = fx_data["chart"]["result"][0]["meta"]["regularMarketPrice"]
        base_price24 = price_raw * usd_inr / 31.1035

    elif price_raw < 100000:
        # INR per 10 grams (MCX)
        base_price24 = price_raw / 10

    else:
        # INR per ounce
        base_price24 = price_raw / 31.1035

    # ---------- RETAIL ADJUSTMENT ----------
    # Converts bullion → Indian jewellery shop rate
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










