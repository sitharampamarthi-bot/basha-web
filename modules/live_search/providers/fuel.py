from __future__ import annotations

import re
from typing import Any


def extract_city(
    question: str,
) -> str:

    text = str(
        question or ""
    ).strip()


    phrases = {
        "petrol price",
        "diesel price",
        "petrol rate",
        "diesel rate",
        "fuel price",
        "cng price",

        "petrol",
        "diesel",
        "fuel",
        "cng",

        "today",
        "current",
        "live",
        "price",
        "rate",

        "పెట్రోల్ ధర",
        "డీజిల్ ధర",
        "పెట్రోల్",
        "డీజిల్",
        "ఇంధనం",

        "ఈరోజు",
        "ధర",
        "రేటు",
    }


    for phrase in sorted(
        phrases,
        key=len,
        reverse=True,
    ):

        text = re.sub(
            re.escape(
                phrase
            ),
            " ",
            text,
            flags=re.IGNORECASE,
        )


    return re.sub(
        r"\s+",
        " ",
        text,
    ).strip()


def get_fuel_price(
    question: str,
) -> dict[str, Any]:

    city = extract_city(
        question
    )


    return {
        "success": False,

        "configurationRequired":
            True,

        "city":
            city,

        "error": (
            "Reliable live city-wise "
            "petrol/diesel data provider "
            "is not configured yet."
        ),

        "source":
            "Fuel provider pending",
    }