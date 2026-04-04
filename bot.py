import requests
import asyncio
import os
from telegram import Bot
from datetime import datetime

# ====== CONFIG (do NOT touch) ======
TOKEN = os.getenv("TOKEN")        # Your bot token from BotFather
CHAT_ID = int(os.getenv("CHAT_ID"))  # Your Telegram chat ID

bot = Bot(token=TOKEN)

P2P_URL = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
PRICE_URL = "https://api.binance.com/api/v3/ticker/price"
HEADERS = {"Content-Type": "application/json"}

# ====== Fetch Live USDT/AED Price ======
def fetch_live_price():
    try:
        response = requests.get(PRICE_URL, params={"symbol": "USDTAED"})
        data = response.json()
        return float(data["price"])
    except:
        return None

# ====== Fetch P2P Offers ======
def fetch_offers(trade_type, pay_types=None, top_n=10):
    payload = {
        "asset": "USDT",
        "fiat": "AED",
        "merchantCheck": False,
        "payTypes": pay_types or [],
        "tradeType": trade_type,
        "page": 1,
        "rows": top_n
    }

    response = requests.post(P2P_URL, json=payload, headers=HEADERS)
    data = response.json()

    offers = []
    if "data" in data:
        for item in data["data"]:
            adv = item["adv"]
            price = float(adv["price"])
            min_limit = float(adv.get("minSingleTransAmountInFiatCurrency") or adv.get("minSingleTransAmount", 0))
            raw_max = adv.get("maxSingleTransAmountInFiatCurrency") or adv.get("maxSingleTransAmount", 0)
            max_fiat = adv.get("maxSingleTransAmountInFiatCurrency")
            max_limit = float(raw_max) if max_fiat else float(adv.get("maxSingleTransAmount", 0)) * price
            offers.append({
                "price": price,
                "min_limit": min_limit,
                "max_limit": max_limit
            })

    return offers

# ====== MAIN BOT LOOP ======
async def main_loop():
    while True:
        try:
            # BUY = people selling USDT = where YOU buy from
            offers = fetch_offers("BUY", pay_types=[], top_n=10)
            offers.sort(key=lambda x: x["price"])

            live_price = fetch_live_price()

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"🇦🇪 USDT/AED P2P Market\n🕒 {now}\n\n"

            # Live Binance price
            if live_price:
                message += f"📡 Live Binance Price: {live_price:.4f} AED\n\n"
            else:
                message += "📡 Live Binance Price: N/A\n\n"

            if offers:
                message += f"🛒 Top 10 Sellers (Cheapest First)\n"
                message += f"✅ Best Price: {offers[0]['price']} AED\n\n"

                for i, offer in enumerate(offers, start=1):
                    min_aed = f"{offer['min_limit']:.2f}"
                    max_aed = f"{offer['max_limit']:.2f}"
                    message += f"{i}. 💵 {offer['price']} AED | Min: {min_aed} | Max: {max_aed} AED\n"
            else:
                message += "⚠️ No offers found.\n"

            await bot.send_message(chat_id=CHAT_ID, text=message)

        except Exception as e:
            await bot.send_message(chat_id=CHAT_ID, text=f"⚠️ Error: {e}")

        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main_loop())