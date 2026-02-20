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
    import base64

    token = os.environ.get("GH_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")

    if not token or not repo:
        return {}

    url = f"https://api.github.com/repos/{repo}/contents/users.json"
    headers = {"Authorization": f"token {token}"}

    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        return {}

    content = base64.b64decode(r.json()["content"])
    return json.loads(content)

def save_users(users):
    import base64

    token = os.environ.get("GH_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")

    if not token or not repo:
        return

    content = base64.b64encode(json.dumps(users).encode()).decode()

    url = f"https://api.github.com/repos/{repo}/contents/users.json"
    headers = {"Authorization": f"token {token}"}

    # check if file exists
    r = requests.get(url, headers=headers)
    sha = r.json()["sha"] if r.status_code == 200 else None

    data = {
        "message": "update users",
        "content": content,
        "sha": sha
    }

    requests.put(url, headers=headers, json=data)



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

            send_message(chat_id, f"✅ City saved: {text}")

            # Immediately send today's prices
            g22, g24 = get_gold_rate()
            silver = get_silver_rate()
            fuel = get_fuel_price(text)

            msg = (
                f"📊 {text} Daily Prices\n\n"
                f"Gold 22K ₹{g22}/g\n"
                f"Gold 24K ₹{g24}/g\n"
                f"Silver ₹{silver}/g\n\n"
                f"Petrol ₹{fuel['petrol']}\n"
                f"Diesel ₹{fuel['diesel']}"
            )

            send_message(chat_id, msg)

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

    try:
        headers = {"User-Agent": "Mozilla/5.0"}

        url = "https://priceapi.moneycontrol.com/pricefeed/commodity/silver"
        r = requests.get(url, headers=headers, timeout=10)

        if r.status_code != 200:
            return "N/A"

        data = r.json()
        price_per_kg = float(data["data"]["pricecurrent"])

        return round(price_per_kg / 1000, 2)

    except Exception:
        return "N/A"




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
            f"Silver ₹{silver}/g\n" if silver != "N/A" else "Silver price unavailable\n"
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












