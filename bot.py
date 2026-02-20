import requests
import os
import json
from datetime import datetime

TOKEN = os.environ.get("BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"
USERS_FILE = "users.json"


# ---------------- TELEGRAM SEND ----------------
def send_message(chat_id, text, keyboard=None):
    data = {
        "chat_id": chat_id,
        "text": text
    }
    if keyboard:
        data["reply_markup"] = json.dumps(keyboard)

    requests.post(f"{BASE_URL}/sendMessage", data=data)


# ---------------- USERS STORAGE ----------------
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)


# ---------------- CITY MENU ----------------
def city_keyboard():
    return {
        "keyboard": [
            ["Chennai", "Bangalore"],
            ["Hyderabad", "Mumbai"],
            ["Delhi", "Kolkata"]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": True
    }


# ---------------- HANDLE UPDATES ----------------
def handle_updates():
    users = load_users()

    offset = 0
    if os.path.exists("offset.txt"):
        with open("offset.txt", "r") as f:
            offset = int(f.read().strip())

    updates = requests.get(f"{BASE_URL}/getUpdates?offset={offset}").json()

    if not updates["result"]:
        return

    for update in updates["result"]:
        update_id = update["update_id"]
        message = update.get("message")
        if not message:
            continue

        chat_id = str(message["chat"]["id"])
        text = message.get("text", "")

        if text == "/start":
            send_message(chat_id, "Welcome 👋\nSelect your city:", city_keyboard())

        elif text in ["Chennai", "Bangalore", "Hyderabad", "Mumbai", "Delhi", "Kolkata"]:
            users[chat_id] = {"city": text}
            save_users(users)
            send_message(chat_id, f"✅ City saved: {text}\nYou will receive daily prices at 9 AM")

        offset = update_id + 1

    with open("offset.txt", "w") as f:
        f.write(str(offset))


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

    base_price24 = usd_per_oz * usd_inr / 31.1035

    ibja_factor = 1.070
    price24 = base_price24 * ibja_factor
    price22 = price24 * 0.916

    return round(price22, 2), round(price24, 2)


# ---------------- SILVER PRICE ----------------
def get_silver_rate():
    import requests

    headers = {"User-Agent": "Mozilla/5.0"}

    # Silver futures USD per ounce
    silver_csv = requests.get(
        "https://stooq.com/q/l/?s=si.f&f=sd2t2ohlcv&h&e=csv",
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

    # international price per gram
    base_price = usd_per_oz * usd_inr / 31.1035

    # Indian bullion conversion (kg market)
    india_factor = 3.15
    price_per_kg = base_price * india_factor

    # convert to gram
    price_per_g = price_per_kg / 1000

    return round(price_per_g, 2)



# ---------------- PETROL & DIESEL ----------------
def get_fuel_price(city):
    fuel_prices = {
        "Chennai": {"petrol": 102.63, "diesel": 94.24},
        "Bangalore": {"petrol": 101.94, "diesel": 87.89},
        "Hyderabad": {"petrol": 109.66, "diesel": 97.82},
        "Mumbai": {"petrol": 106.31, "diesel": 94.27},
        "Delhi": {"petrol": 96.72, "diesel": 89.62},
        "Kolkata": {"petrol": 106.03, "diesel": 92.76}
    }

    return fuel_prices.get(city, {"petrol": "-", "diesel": "-"})


# ---------------- DAILY SEND ----------------
def send_daily_prices():
    users = load_users()
    g22, g24 = get_gold_rate()
    silver = get_silver_rate()

    for chat_id in users:
        city = users[chat_id]["city"]
        fuel = get_fuel_price(city)

        msg = (
            f"📊 {city} Daily Prices ({datetime.now().date()})\n\n"
            f"Gold 22K ₹{g22}/g\n"
            f"Gold 24K ₹{g24}/g\n"
            f"Silver ₹{silver}/g\n\n"
            f"Petrol ₹{fuel['petrol']}\n"
            f"Diesel ₹{fuel['diesel']}"
        )

        send_message(chat_id, msg)


# ---------------- MAIN ----------------
def main():
    handle_updates()
    send_daily_prices()


if __name__ == "__main__":
    main()


