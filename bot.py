import requests
import json

URL = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
HEADERS = {"Content-Type": "application/json"}

payload = {
    "asset": "USDT",
    "fiat": "AED",
    "merchantCheck": False,
    "payTypes": [],
    "tradeType": "BUY",
    "page": 1,
    "rows": 1  # just 1 result is enough
}

response = requests.post(URL, json=payload, headers=HEADERS)
data = response.json()

# Print ALL fields of the first offer's adv object
if data.get("data"):
    adv = data["data"][0]["adv"]
    print("=== ALL ADV FIELDS ===")
    for key, value in adv.items():
        print(f"{key}: {value}")