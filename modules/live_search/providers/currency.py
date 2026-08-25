from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Any

import requests


RATE_URL = "https://api.frankfurter.dev/v2/rates"


CURRENCY_ALIASES = {
    "usd": "USD",
    "dollar": "USD",
    "us dollar": "USD",
    "డాలర్": "USD",

    "inr": "INR",
    "rupee": "INR",
    "rupees": "INR",
    "రూపాయి": "INR",
    "రూపాయలు": "INR",

    "eur": "EUR",
    "euro": "EUR",

    "gbp": "GBP",
    "pound": "GBP",
    "british pound": "GBP",

    "aed": "AED",
    "dirham": "AED",
    "uae dirham": "AED",

    "sar": "SAR",
    "riyal": "SAR",
    "saudi riyal": "SAR",

    "jpy": "JPY",
    "yen": "JPY",

    "cad": "CAD",
    "canadian dollar": "CAD",

    "aud": "AUD",
    "australian dollar": "AUD",

    "sgd": "SGD",
    "singapore dollar": "SGD",

    "chf": "CHF",
    "swiss franc": "CHF",
}


SUPPORTED_CODES = {
    "USD",
    "INR",
    "EUR",
    "GBP",
    "AED",
    "SAR",
    "JPY",
    "CAD",
    "AUD",
    "SGD",
    "CHF",
}


def clean_text(value: Any) -> str:
    return str(value or "").strip()


def detect_amount(question: str) -> Decimal:
    match = re.search(
        r"(?<![A-Za-z])(\d+(?:\.\d+)?)",
        str(question or ""),
    )

    if not match:
        return Decimal("1")

    try:
        return Decimal(
            match.group(1)
        )

    except InvalidOperation:
        return Decimal("1")


def find_currency_codes(
    question: str,
) -> list[str]:

    original = clean_text(
        question
    )

    normalized = original.casefold()

    found: list[
        tuple[int, str]
    ] = []


    for match in re.finditer(
        r"\b[A-Za-z]{3}\b",
        original,
    ):

        code = (
            match.group(0)
            .upper()
        )

        if code in SUPPORTED_CODES:
            found.append(
                (
                    match.start(),
                    code,
                )
            )


    for alias, code in sorted(
        CURRENCY_ALIASES.items(),
        key=lambda item:
            len(item[0]),
        reverse=True,
    ):

        position = normalized.find(
            alias.casefold()
        )

        if position >= 0:
            found.append(
                (
                    position,
                    code,
                )
            )


    found.sort(
        key=lambda item:
            item[0]
    )


    result = []

    for _, code in found:
        if code not in result:
            result.append(
                code
            )

    return result


def resolve_currency_pair(
    question: str,
) -> tuple[
    str,
    str,
    Decimal,
]:

    codes = find_currency_codes(
        question
    )

    amount = detect_amount(
        question
    )


    if len(codes) >= 2:
        return (
            codes[0],
            codes[1],
            amount,
        )


    if len(codes) == 1:

        if codes[0] == "INR":
            return (
                "USD",
                "INR",
                amount,
            )

        return (
            codes[0],
            "INR",
            amount,
        )


    return (
        "USD",
        "INR",
        amount,
    )


def get_currency_rate(
    question: str,
) -> dict[str, Any]:

    (
        base,
        quote,
        amount,
    ) = resolve_currency_pair(
        question
    )


    if base == quote:
        return {
            "success": True,
            "base": base,
            "quote": quote,
            "rate": 1.0,
            "amount": float(amount),
            "convertedAmount":
                float(amount),
            "date": None,
            "source":
                "Identity conversion",
        }


    try:

        response = requests.get(
            RATE_URL,
            params={
                "base": base,
                "quotes": quote,
            },
            timeout=10,
        )

        response.raise_for_status()

        payload = response.json()


        if not payload:
            raise ValueError(
                "No exchange rate returned."
            )


        row = payload[0]

        rate = Decimal(
            str(
                row.get("rate")
            )
        )


        converted = (
            amount * rate
        )


        return {
            "success": True,

            "base":
                base,

            "quote":
                quote,

            "rate":
                float(rate),

            "amount":
                float(amount),

            "convertedAmount":
                round(
                    float(converted),
                    4,
                ),

            "date":
                row.get("date"),

            "source":
                "Frankfurter",

            "rateType":
                "Reference exchange rate",
        }


    except (
        requests.RequestException,
        InvalidOperation,
        TypeError,
        ValueError,
        IndexError,
    ) as error:

        return {
            "success": False,
            "base": base,
            "quote": quote,
            "error": (
                "Currency service failed: "
                f"{error}"
            ),
        }