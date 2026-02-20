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

    # Get gold futures price
    url = "https://query1.finance.yahoo.com/v8/finance/chart/GC=F"
    data = requests.get(url, headers=headers, timeout=10).json()

    price_per_oz = data["chart"]["result"][0]["meta"]["regularMarketPrice"]

    # Detect currency automatically
    if price_per_oz < 10000:
        # USD → INR
        fx_url = "https://query1.finance.yahoo.com/v8/finance/chart/USDINR=X"
        fx_data = requests.get(fx_url, headers=headers, timeout=10).json()
        usd_inr = fx_data["chart"]["result"][0]["meta"]["regularMarketPrice"]
        base_price24 = price_per_oz * usd_inr / 31.1035
    else:
        # Already INR
        base_price24 = price_per_oz / 31.1035

    # Convert to Indian retail approximation
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









