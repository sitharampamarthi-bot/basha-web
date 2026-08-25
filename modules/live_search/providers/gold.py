from __future__ import annotations

from typing import Any

import requests


GOLD_API_URL = (
    "https://api.gold-api.com/price/XAU"
)


GRAMS_PER_TROY_OUNCE = (
    31.1034768
)


def safe_float(
    value: Any,
) -> float | None:

    try:
        if value is None:
            return None

        return float(
            value
        )

    except (
        TypeError,
        ValueError,
    ):
        return None


def get_gold_price(
    question: str = "",
) -> dict[str, Any]:

    try:

        response = requests.get(
            GOLD_API_URL,

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


        usd_per_ounce = (
            safe_float(
                payload.get(
                    "price"
                )
            )
        )


        if usd_per_ounce is None:

            return {
                "success": False,
                "error": (
                    "Gold price was not returned."
                ),
            }


        usd_per_gram = round(
            usd_per_ounce /
            GRAMS_PER_TROY_OUNCE,
            4,
        )


        return {
            "success": True,

            "symbol":
                payload.get(
                    "symbol",
                    "XAU"
                ),

            "name":
                payload.get(
                    "name",
                    "Gold"
                ),

            "usdPerOunce":
                usd_per_ounce,

            "usdPerGram":
                usd_per_gram,

            "updatedAt":
                (
                    payload.get(
                        "updatedAt"
                    )
                    or
                    payload.get(
                        "updated_at"
                    )
                    or
                    payload.get(
                        "timestamp"
                    )
                ),

            "source":
                "Gold API",

            "note":
                (
                    "International spot gold price. "
                    "Indian retail jewellery price may differ "
                    "because of USD/INR, import duty, GST, "
                    "purity and dealer premium."
                ),
        }


    except requests.RequestException as error:

        return {
            "success": False,
            "error": (
                "Gold service failed: "
                f"{error}"
            ),
        }


    except (
        TypeError,
        ValueError,
    ) as error:

        return {
            "success": False,
            "error": (
                "Invalid gold response: "
                f"{error}"
            ),
        }