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
    price24 = base_price * 1.066
    price22 = price24 * 0.9166613

    return round(price22, 2), round(price24, 2)


# ---------------- SILVER PRICE ----------------
def get_silver_rate():
    import requests

    headers = {"User-Agent": "Mozilla/5.0"}

    # Spot Silver (XAGUSD) - USD per troy ounce
    silver_csv = requests.get(
        "https://stooq.com/q/l/?s=xagusd&f=sd2t2ohlcv&h&e=csv",
        headers=headers,
        timeout=10
    ).text

    lines = silver_csv.strip().split("\n")
    last_line = lines[-1]
    usd_per_oz = float(last_line.split(",")[6])

    # USD → INR conversion
    fx_csv = requests.get(
        "https://stooq.com/q/l/?s=usdinr&f=sd2t2ohlcv&h&e=csv",
        headers=headers,
        timeout=10
    ).text

    fx_lines = fx_csv.strip().split("\n")
    fx_last = fx_lines[-1]
    usd_inr = float(fx_last.split(",")[6])

    # Base bullion price ₹/gram
    bullion_per_g = (usd_per_oz * usd_inr) / 31.1035

    # Indian pricing structure
    bullion_per_g *= 1.10   # Import Duty (10%)
    bullion_per_g *= 1.05   # AIDC (5%)
    bullion_per_g *= 1.03   # GST (3%)

    # Tamil Nadu market normalization factor
    retail_price = bullion_per_g * 0.968

    return round(retail_price, 2)

# ---------------- FUEL (STATIC SAMPLE) ----------------
def get_fuel_price(city="Chennai"):
    import requests

    try:
        url = "https://www.iocl.com/fuel-price-data"
        data = requests.get(url, timeout=15).json()

        city = city.lower()

        for item in data["data"]:
            if item["city"].lower() == city:
                petrol = float(item["petrol"])
                diesel = float(item["diesel"])
                return {"petrol": petrol, "diesel": diesel}

    except Exception:
        pass

    return {"petrol": "N/A", "diesel": "N/A"}

#----------------get today price------------------------
def get_today_prices():
    import json, os
    from datetime import date

    today = str(date.today())
    file = "today_price.json"

    # if already calculated today → reuse
    if os.path.exists(file):
        with open(file, "r") as f:
            data = json.load(f)
            if data.get("date") == today:
                return data["gold22"], data["gold24"], data["silver"]

    # otherwise calculate fresh
    g22, g24 = get_gold_rate()
    silver = get_silver_rate()

    data = {
        "date": today,
        "gold22": g22,
        "gold24": g24,
        "silver": silver
    }

    with open(file, "w") as f:
        json.dump(data, f)

    return g22, g24, silver


# ---------------- MAIN ----------------
def main():
    g22, g24, silver = get_today_prices()
    fuel = get_fuel_price("Chennai")

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
























