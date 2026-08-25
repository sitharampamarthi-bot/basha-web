from __future__ import annotations

from typing import Any

import requests


URL = (
    "https://api.coingecko.com/api/v3/simple/price"
)


COINS = {
    "bitcoin": "bitcoin",
    "btc": "bitcoin",

    "ethereum": "ethereum",
    "eth": "ethereum",

    "solana": "solana",
    "sol": "solana",

    "bnb": "binancecoin",
    "binance coin": "binancecoin",

    "dogecoin": "dogecoin",
    "doge": "dogecoin",

    "xrp": "ripple",
    "ripple": "ripple",

    "cardano": "cardano",
    "ada": "cardano",
}


def clean_text(
    value: Any,
) -> str:
    return str(
        value or ""
    ).strip()


def resolve_coin(
    question: str,
) -> str:

    text = clean_text(
        question
    ).casefold()

    for name in sorted(
        COINS,
        key=len,
        reverse=True,
    ):

        if name in text:
            return COINS[
                name
            ]

    return "bitcoin"


def get_crypto_price(
    question: str = "",
) -> dict[str, Any]:

    coin = resolve_coin(
        question
    )

    try:

        response = requests.get(
            URL,

            params={
                "ids":
                    coin,

                "vs_currencies":
                    "usd,inr",

                "include_market_cap":
                    "true",

                "include_24hr_vol":
                    "true",

                "include_24hr_change":
                    "true",

                "include_last_updated_at":
                    "true",
            },

            headers={
                "Accept":
                    "application/json",

                "User-Agent":
                    "Basha-Messenger/1.0",
            },

            timeout=10,
        )

        response.raise_for_status()

        payload = response.json()

        data = payload.get(
            coin
        )

        if not data:

            return {
                "success": False,
                "error": (
                    "Crypto price was not returned."
                ),
            }


        return {
            "success": True,

            "coin":
                coin.replace(
                    "-",
                    " "
                ).title(),

            "coinId":
                coin,

            "usd":
                data.get(
                    "usd"
                ),

            "inr":
                data.get(
                    "inr"
                ),

            "change24hUsd":
                round(
                    float(
                        data.get(
                            "usd_24h_change"
                        ) or 0
                    ),
                    2,
                ),

            "change24hInr":
                round(
                    float(
                        data.get(
                            "inr_24h_change"
                        ) or 0
                    ),
                    2,
                ),

            "marketCapUsd":
                data.get(
                    "usd_market_cap"
                ),

            "marketCapInr":
                data.get(
                    "inr_market_cap"
                ),

            "volume24hUsd":
                data.get(
                    "usd_24h_vol"
                ),

            "volume24hInr":
                data.get(
                    "inr_24h_vol"
                ),

            "lastUpdatedAt":
                data.get(
                    "last_updated_at"
                ),

            "source":
                "CoinGecko",
        }


    except requests.RequestException as error:

        return {
            "success": False,
            "coin": coin,
            "error": (
                "Crypto service failed: "
                f"{error}"
            ),
        }


    except (
        TypeError,
        ValueError,
    ) as error:

        return {
            "success": False,
            "coin": coin,
            "error": (
                "Invalid crypto response: "
                f"{error}"
            ),
        }