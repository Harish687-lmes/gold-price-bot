import requests
import os
import json
from datetime import datetime

TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
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
            ["Chennai", "Coimbatore"],
            ["Madurai", "Bangalore"],
            ["Hyderabad", "Mumbai"]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": True
    }


# ---------------- TELEGRAM UPDATES ----------------
def handle_updates():
    users = load_users()

    # load last update id
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

        # /start command
        if text == "/start":
            send_message(chat_id, "Welcome 👋\nSelect your city:", city_keyboard())

        # City selected
        elif text in ["Chennai", "Coimbatore", "Madurai", "Bangalore", "Hyderabad", "Mumbai"]:
            users[chat_id] = {"city": text}
            save_users(users)
            send_message(chat_id, f"✅ City saved: {text}\nYou will receive daily prices at 9 AM")

        # save next offset
        offset = update_id + 1

    # store offset so updates are not repeated
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


# ---------------- DAILY SEND ----------------
def send_daily_prices():
    users = load_users()
    g22, g24 = get_gold_rate()

    for chat_id in users:
        city = users[chat_id]["city"]
        msg = f"📊 {city} Daily Gold Price ({datetime.now().date()})\n22K ₹{g22}/g\n24K ₹{g24}/g"
        send_message(chat_id, msg)


# ---------------- MAIN ----------------
def main():
    handle_updates()
    send_daily_prices()


if __name__ == "__main__":
    main()

