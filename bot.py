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
    url = "https://www.google.com/search?q=gold+price+today+india"
    headers = {"User-Agent":"Mozilla/5.0"}

    html = requests.get(url,headers=headers).text

    import re
    m = re.search(r'₹\s?([0-9,]+\.\d+)', html)

    if not m:
        return None,None

    price24 = float(m.group(1).replace(",",""))
    price22 = price24*0.916
    return round(price22,2),round(price24,2)

def main():
    g22,g24 = get_gold_rate()

    if not g22:
        send("Gold bot error fetching price")
        return

    send(f"📊 Gold Price {datetime.now().date()}\n22K ₹{g22}/g\n24K ₹{g24}/g")

main()
