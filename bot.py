import requests
import os
import json
from datetime import datetime

TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"


# ---------------- SEND MESSAGE ----------------
def send_message(text):
    requests.post(
        f"{BASE_URL}/sendMessage",
        data={"chat_id": CHAT_ID, "text": text}
    )


# ---------------- GOLD PRICE ----------------
def get_gold_rate():
    headers = {"User-Agent": "Mozilla/5.0"}

    gold_csv = requests.get(
        "https://stooq.com/q/l/?s=gc.f&f=sd2t2ohlcv&h&e=csv",
        headers=headers,
        timeout=10
    ).text

    last_line = gold_csv.strip().split("\n")[-1]
    usd_per_oz = float(last_line.split(",")[6])

    fx_csv = requests.get(
        "https://stooq.com/q/l/?s=usdinr&f=sd2t2ohlcv&h&e=csv",
        headers=headers,
        timeout=10
    ).text

    fx_line = fx_csv.strip().split("\n")[-1]
    usd_inr = float(fx_line.split(",")[6])

    base_price = usd_per_oz * usd_inr / 31.1035
    price24 = base_price * 1.07
    price22 = price24 * 0.916

    return round(price22, 2), round(price24, 2)


# ---------------- SILVER PRICE ----------------
def get_silver_rate():
    import requests

    headers = {"User-Agent": "Mozilla/5.0"}

    # Spot silver XAGUSD (not futures)
    silver_csv = requests.get(
        "https://stooq.com/q/l/?s=xagusd&f=sd2t2ohlcv&h&e=csv",
        headers=headers,
        timeout=10
    ).text

    last_line = silver_csv.strip().split("\n")[-1]
    usd_per_oz = float(last_line.split(",")[6])

    # USD to INR
    fx_csv = requests.get(
        "https://stooq.com/q/l/?s=usdinr&f=sd2t2ohlcv&h&e=csv",
        headers=headers,
        timeout=10
    ).text

    fx_line = fx_csv.strip().split("\n")[-1]
    usd_inr = float(fx_line.split(",")[6])

    # Spot bullion ₹/g
    bullion_per_g = (usd_per_oz * usd_inr) / 31.1035

    # Apply Indian structure
    bullion_per_g *= 1.10   # import duty
    bullion_per_g *= 1.05   # AIDC
    bullion_per_g *= 1.03   # GST
    bullion_per_g *= 1.20   # Tamil Nadu dealer premium

    return round(bullion_per_g, 2)

# ---------------- FUEL (STATIC SAMPLE) ----------------
def get_fuel_price():
    return {
        "petrol": 102.63,
        "diesel": 94.24
    }


# ---------------- MAIN ----------------
def main():
    g22, g24 = get_gold_rate()
    silver = get_silver_rate()
    fuel = get_fuel_price()

    message = (
        f"📊 Chennai Daily Prices ({datetime.now().date()})\n\n"
        f"Gold 22K ₹{g22}/g\n"
        f"Gold 24K ₹{g24}/g\n"
        f"Silver ₹{silver}/g\n\n"
        f"Petrol ₹{fuel['petrol']}\n"
        f"Diesel ₹{fuel['diesel']}"
    )

    send_message(message)


if __name__ == "__main__":
    main()






