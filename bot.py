import requests
import asyncio
import os
from telegram import Bot
from datetime import datetime

# ====== CONFIG (do NOT touch) ======
TOKEN = os.getenv("TOKEN")        # Your bot token from BotFather
CHAT_ID = int(os.getenv("CHAT_ID"))  # Your Telegram chat ID

bot = Bot(token=TOKEN)

URL = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
HEADERS = {"Content-Type": "application/json"}

# ====== Fetch Offers Function ======
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

    response = requests.post(URL, json=payload, headers=HEADERS)
    data = response.json()

    offers = []
    if "data" in data:
        for item in data["data"]:
            adv = item["adv"]
            price = float(adv["price"])
            min_limit = float(adv.get("minSingleTransAmount", 0))
            max_limit = float(adv.get("maxSingleTransAmount", 0))
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
            sell_tab = fetch_offers("SELL", pay_types=[], top_n=10)
            sell_tab.sort(key=lambda x: x["price"])

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"🇦🇪 USDT/AED P2P Market\n🕒 {now}\n\n"

            if sell_tab:
                best_price = sell_tab[0]['price']
                worst_price = sell_tab[-1]['price']
                spread = round(worst_price - best_price, 4)

                message += "🛒 SELL TAB — People Selling USDT (You BUY here)\n"
                message += f"✅ Best Buy Price (Cheapest): {best_price} AED\n"
                message += f"📊 Price Spread (Top 10): {spread} AED\n\n"

                for i, offer in enumerate(sell_tab, start=1):
                    min_aed = f"{offer['min_limit']:.2f}"
                    max_aed = f"{offer['max_limit']:.2f}"
                    message += f"{i}. 💵 {offer['price']} AED | Min: {min_aed} | Max: {max_aed} AED\n"
            else:
                message += "⚠️ No sell offers found.\n"

            await bot.send_message(chat_id=CHAT_ID, text=message)

        except Exception as e:
            await bot.send_message(chat_id=CHAT_ID, text=f"⚠️ Error: {e}")

        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main_loop())