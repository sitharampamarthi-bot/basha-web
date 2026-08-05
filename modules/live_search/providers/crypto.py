import requests

URL = "https://api.coingecko.com/api/v3/simple/price"


def get_crypto_price(symbol="bitcoin"):

    ids = {
        "bitcoin": "bitcoin",
        "btc": "bitcoin",
        "ethereum": "ethereum",
        "eth": "ethereum",
        "solana": "solana",
        "bnb": "binancecoin",
        "dogecoin": "dogecoin"
    }

    symbol = symbol.lower()

    coin = "bitcoin"

    for key, value in ids.items():

        if key in symbol:

            coin = value

            break

    try:

        response = requests.get(

            URL,

            params={
                "ids": coin,
                "vs_currencies": "usd,inr",
                "include_24hr_change": "true"
            },

            timeout=10

        )

        data = response.json()[coin]

        return {

            "success": True,

            "coin": coin.title(),

            "usd": data["usd"],

            "inr": data["inr"],

            "change24h": round(
                data.get("usd_24h_change", 0),
                2
            )

        }

    except Exception as e:

        return {

            "success": False,

            "error": str(e)

        }